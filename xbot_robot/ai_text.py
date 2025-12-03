import xbot
from xbot import print, sleep
from typing import Optional, List, Tuple
import time
import re
import requests
from urllib import parse
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import threading
import random
import json

from zhipuai import ZhipuAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===============================================
# 增强的思考过程清理函数
# ===============================================

def _clean_thinking_process(content: str) -> str:
    """
    增强的思考过程清理函数，支持多种格式
    处理: <think>...</think>, <thinking>...</thinking>, 等各种变体
    不禁用思考功能，仅清理输出中的思考过程标签
    """
    if not content:
        return content
    
    original_length = len(content)
    
    # 模式列表 - 处理各种可能的思考标签格式（优先级从高到低）
    cleaning_patterns = [
        # XML/HTML标签格式
        (r'<think\s*>.*?</think\s*>', 'think标签'),
        (r'<thinking\s*>.*?</thinking\s*>', 'thinking标签'),
        (r'<analysis\s*>.*?</analysis\s*>', 'analysis标签'),
        (r'<reflection\s*>.*?</reflection\s*>', 'reflection标签'),
        (r'<internal\s*>.*?</internal\s*>', 'internal标签'),
        (r'<thought\s*>.*?</thought\s*>', 'thought标签'),
        (r'<reasoning\s*>.*?</reasoning\s*>', 'reasoning标签'),
        (r'<consider\s*>.*?</consider\s*>', 'consider标签'),
        (r'<deepthink\s*>.*?</deepthink\s*>', 'deepthink标签'),
        (r'<reflect\s*>.*?</reflect\s*>', 'reflect标签'),
        
        # Markdown格式
        (r'\*\*思考过程\*\*[\s\S]*?(?=\*\*|$)', 'markdown思考标题'),
        (r'##\s*思考.*?(?=##|$)', 'markdown思考section'),
        (r'\*\*thinking.*?\*\*[\s\S]*?(?=\*\*|[^\s])', 'markdown thinking标题'),
        
        # HTML注释
        (r'<!--[\s\S]*?-->', 'HTML注释'),
        
        # 中文标记
        (r'【思考】[\s\S]*?(?=【|$)', '中文思考标记'),
        (r'『思考』[\s\S]*?(?=『|$)', '中文思考标记2'),
    ]
    
    # 应用所有清理模式
    for pattern, pattern_name in cleaning_patterns:
        matches = re.findall(pattern, content, flags=re.DOTALL | re.IGNORECASE)
        if matches:
            logger.debug(f"检测到 {len(matches)} 个{pattern_name}，进行清理")
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 清理多余的空行（保留适度的分隔）
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # 3个或以上空行改为2个
    content = re.sub(r'^\s+|\s+$', '', content, flags=re.MULTILINE)  # 行首尾空格
    
    # 最后的整体strip
    content = content.strip()
    
    cleaned_length = len(content)
    if cleaned_length < original_length:
        reduction = original_length - cleaned_length
        logger.debug(f"思考过程清理完成 - 清理前: {original_length} 字符, 清理后: {cleaned_length} 字符 (减少: {reduction})")
    
    return content

# ===============================================
# 优化版API密钥管理器（支持多平台）
# ===============================================

class OptimizedAPIKeyManager:
    """优化的API密钥管理器，支持多平台"""

    def __init__(self, blacklist_duration=180):
        self.blacklist_duration = blacklist_duration
        self.blacklisted_keys = {}
        self.lock = threading.RLock()
        self.usage_stats = {}
        self.last_cleanup_time = 0
        self.last_used_index = -1
        self.consecutive_failures = {}
        self.key_performance = {}

    def add_to_blacklist(self, api_key, reason="并发限制"):
        """更精确的黑名单添加逻辑"""
        with self.lock:
            current_time = time.time()

            if api_key in self.blacklisted_keys:
                time_diff = current_time - self.blacklisted_keys[api_key]
                if time_diff < 10:
                    self.blacklisted_keys[api_key] = current_time
                    return

            self.blacklisted_keys[api_key] = current_time

            if api_key not in self.usage_stats:
                self.usage_stats[api_key] = {'blacklist_count': 0, 'last_blacklist': current_time}
            self.usage_stats[api_key]['blacklist_count'] += 1
            self.usage_stats[api_key]['last_blacklist'] = current_time

            logger.warning(
                f"密钥加入黑名单({reason}): ...{api_key[-8:]} (第{self.usage_stats[api_key]['blacklist_count']}次, 3分钟)")

    def is_blacklisted(self, api_key):
        """检查是否在黑名单中，自动清理过期"""
        with self.lock:
            if api_key not in self.blacklisted_keys:
                return False

            current_time = time.time()
            blacklist_time = self.blacklisted_keys[api_key]

            if current_time - blacklist_time >= self.blacklist_duration:
                del self.blacklisted_keys[api_key]
                logger.info(f"密钥黑名单过期，重新可用: ...{api_key[-8:]}")
                return False

            return True

    def get_next_available_key_with_rotation(self, all_keys):
        """获取下一个可用密钥（真正的轮换机制）"""
        with self.lock:
            if not all_keys:
                return None

            current_time = time.time()
            if current_time - self.last_cleanup_time > 30:
                self._cleanup_expired_blacklist()
                self.last_cleanup_time = current_time

            available_keys = [key for key in all_keys if not self.is_blacklisted(key)]

            if not available_keys:
                logger.error(f"所有密钥都在黑名单中！总数:{len(all_keys)}, 黑名单:{len(self.blacklisted_keys)}")
                return None

            total_keys = len(available_keys)

            if total_keys != getattr(self, '_last_available_count', 0):
                self.last_used_index = -1
                self._last_available_count = total_keys

            self.last_used_index = (self.last_used_index + 1) % total_keys
            selected_key = available_keys[self.last_used_index]

            self._record_key_usage(selected_key)

            logger.info(f"轮换选择密钥[{self.last_used_index + 1}/{total_keys}]: ...{selected_key[-8:]}")
            return selected_key

    def get_available_keys_count(self, all_keys):
        """获取当前可用密钥数量（未在黑名单中的）"""
        with self.lock:
            if not all_keys:
                return 0
            available_keys = [key for key in all_keys if not self.is_blacklisted(key)]
            return len(available_keys)

    def _record_key_usage(self, api_key):
        """记录密钥使用情况"""
        if api_key not in self.key_performance:
            self.key_performance[api_key] = {
                'total_uses': 0,
                'successes': 0,
                'failures': 0,
                'last_used': 0
            }

        self.key_performance[api_key]['total_uses'] += 1
        self.key_performance[api_key]['last_used'] = time.time()

    def record_success(self, api_key):
        """记录成功调用"""
        with self.lock:
            if api_key in self.key_performance:
                self.key_performance[api_key]['successes'] += 1

            if api_key in self.consecutive_failures:
                self.consecutive_failures[api_key] = 0

    def record_failure(self, api_key, error_msg=""):
        """记录失败调用，智能判断是否需要加入黑名单"""
        with self.lock:
            if api_key in self.key_performance:
                self.key_performance[api_key]['failures'] += 1

            if api_key not in self.consecutive_failures:
                self.consecutive_failures[api_key] = 0
            self.consecutive_failures[api_key] += 1

            error_lower = error_msg.lower()
            is_rate_limit = any([
                '1302' in error_msg and '并发数过高' in error_msg,
                'rate limit' in error_lower,
                'too many requests' in error_lower,
                'quota exceeded' in error_lower,
                '429' in error_msg,
                'concurrent' in error_lower and 'limit' in error_lower,
                '并发' in error_msg and '限制' in error_msg,
                'requests per minute' in error_lower
            ])

            if is_rate_limit:
                self.add_to_blacklist(api_key, "并发限制")
            elif self.consecutive_failures[api_key] >= 5:
                self.add_to_blacklist(api_key, f"连续失败{self.consecutive_failures[api_key]}次")

    def _cleanup_expired_blacklist(self):
        """清理过期的黑名单"""
        current_time = time.time()
        expired_keys = [
            key for key, blacklist_time in self.blacklisted_keys.items()
            if current_time - blacklist_time >= self.blacklist_duration
        ]

        for key in expired_keys:
            del self.blacklisted_keys[key]
            logger.info(f"黑名单过期恢复: ...{key[-8:]}")

    def force_clear_blacklist(self):
        """强制清空黑名单（紧急情况使用）"""
        with self.lock:
            cleared_count = len(self.blacklisted_keys)
            self.blacklisted_keys.clear()
            logger.warning(f"强制清空黑名单，清除了 {cleared_count} 个密钥")

# 创建全局密钥管理器实例（两个平台共享同一个管理器）
zhipu_key_manager = OptimizedAPIKeyManager(blacklist_duration=180)
siliconflow_key_manager = OptimizedAPIKeyManager(blacklist_duration=180)

# ===============================================
# API调用管理器
# ===============================================

class APICallManager:
    """API调用管理器，处理超时和防止卡死"""
    
    def __init__(self, max_workers: int = 1):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def call_with_timeout(self, func, *args, timeout: int = 30, **kwargs):
        """
        带超时控制的函数调用，防止卡死
        """
        try:
            future = self.executor.submit(func, *args, **kwargs)
            result = future.result(timeout=timeout)
            return result
        except FutureTimeoutError:
            logger.warning(f"函数调用超过 {timeout} 秒，强制终止")
            future.cancel()
            return None
        except Exception as e:
            logger.error(f"函数调用异常: {str(e)}")
            return None

# 全局API调用管理器
api_manager = APICallManager()

# ===============================================
# 获取API密钥
# ===============================================

def fetch_zhipu_keys():
    """
    从API接口获取ZhipuAI的API密钥列表
    返回：API密钥列表
    """
    requestUrl = 'http://47.95.157.46:8520/api/tracking_iw_key'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {}
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and "data" in result:
                keys = [item["key"] for item in result["data"]]
                logger.info(f"成功获取 {len(keys)} 个ZhipuAI API密钥")
                return keys
        
        logger.warning(f"获取ZhipuAI密钥失败: {response.status_code}, {response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"获取ZhipuAI密钥出错: {e}")
        return []

def fetch_siliconflow_keys():
    """
    从API接口获取硅基流动的API密钥列表
    返回：API密钥列表
    """
    requestUrl = 'http://47.95.157.46:8520/api/gj_key'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {}
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("success") and "data" in result:
                keys = [item["key"] for item in result["data"]]
                logger.info(f"成功获取 {len(keys)} 个硅基流动 API密钥")
                return keys
        
        logger.warning(f"获取硅基流动密钥失败: {response.status_code}, {response.text[:200]}")
        return []
    except Exception as e:
        logger.error(f"获取硅基流动密钥出错: {e}")
        return []

# ===============================================
# 硅基流动可用模型列表
# ===============================================

SILICONFLOW_MODELS = [
    "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"
]

# ===============================================
# ZhipuAI API调用
# ===============================================

def _zhipu_api_call(api_key: str, prompt: str, timeout: int = 60) -> Optional[str]:
    """
    实际的ZhipuAI API调用（内部函数）
    """
    client = ZhipuAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="glm-z1-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=32768,
            timeout=timeout
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            # 使用增强的思考过程清理函数
            cleaned_content = _clean_thinking_process(content)
            return cleaned_content
            
    except Exception as e:
        logger.error(f"ZhipuAI调用异常: {str(e)}")
        raise

# ===============================================
# 硅基流动API调用
# ===============================================

def _siliconflow_api_call(api_key: str, prompt: str, timeout: int = 60) -> Optional[str]:
    """
    实际的硅基流动API调用（内部函数）
    """
    base_url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 随机选择一个模型
    model = random.choice(SILICONFLOW_MODELS)
    logger.info(f"🔧 硅基流动使用模型: {model}")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.1,
        "top_p": 0.7,
        "enable_thinking": False
    }
    
    # 禁用代理
    proxies = {
        "http": None,
        "https": None
    }
    
    try:
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            proxies=proxies,
            timeout=timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('choices') and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                # 使用增强的思考过程清理函数
                cleaned_content = _clean_thinking_process(content)
                return cleaned_content
            else:
                raise Exception("响应中没有有效的choices数据")
        else:
            raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"硅基流动调用异常: {str(e)}")
        raise

# ===============================================
# 主函数 - 方案B：双平台轮换机制
# ===============================================

def analyze_with_fallback(prompt: str, backup_retries: int = 3, timeout: int = 60) -> str:
    """
    方案B：双平台轮换机制
    优先使用ZhipuAI，当所有密钥黑名单时自动切换到硅基流动，反之亦然
    
    Args:
        prompt: 要分析的提示词
        backup_retries: 已废弃参数（保持接口兼容）
        timeout: 单次API调用的超时时间（秒）
        
    Returns:
        分析结果（保证成功返回）
    """
    
    # 平台配置
    platforms = {
        'zhipu': {
            'name': 'ZhipuAI',
            'emoji': '🧠',
            'manager': zhipu_key_manager,
            'fetch_func': fetch_zhipu_keys,
            'api_func': _zhipu_api_call,
            'keys': [],
            'last_fetch_time': 0
        },
        'siliconflow': {
            'name': '硅基流动',
            'emoji': '🌊',
            'manager': siliconflow_key_manager,
            'fetch_func': fetch_siliconflow_keys,
            'api_func': _siliconflow_api_call,
            'keys': [],
            'last_fetch_time': 0
        }
    }
    
    # 初始平台选择：优先ZhipuAI
    current_platform_key = 'zhipu'
    
    attempt_count = 0
    key_refresh_interval = 300  # 5分钟刷新一次密钥列表
    platform_switch_count = 0  # 平台切换计数
    consecutive_platform_failures = 0  # 当前平台连续失败次数
    
    # 显示初始平台
    platform = platforms[current_platform_key]
    print(f"\n{'='*60}")
    print(f"🎯 初始平台选择: {platform['emoji']} {platform['name']}")
    print(f"💡 策略: 优先ZhipuAI，智能切换到硅基流动")
    print(f"{'='*60}\n")
    logger.info(f"🎯 初始平台: {platform['emoji']} {platform['name']}")
    
    while True:
        attempt_count += 1
        current_time = time.time()
        
        platform = platforms[current_platform_key]
        key_manager = platform['manager']
        fetch_keys_func = platform['fetch_func']
        api_call_func = platform['api_func']
        
        # 定期刷新当前平台密钥列表或首次获取
        if not platform['keys'] or (current_time - platform['last_fetch_time'] > key_refresh_interval):
            print(f"🔑 第 {attempt_count} 次尝试：获取 {platform['emoji']} {platform['name']} API密钥...")
            logger.info(f"===== 第 {attempt_count} 次尝试：获取{platform['name']} API密钥... =====")
            
            # 使用超时控制获取密钥，防止卡死
            new_keys = api_manager.call_with_timeout(
                fetch_keys_func,
                timeout=15
            )
            
            if new_keys:
                platform['keys'] = new_keys
                platform['last_fetch_time'] = current_time
                print(f"✅ 成功刷新 {platform['emoji']} {platform['name']} 密钥列表，共 {len(new_keys)} 个密钥")
                logger.info(f"成功刷新密钥列表，共 {len(new_keys)} 个密钥")
            else:
                print(f"❌ 未能获取到新的 {platform['emoji']} {platform['name']} 密钥列表")
                logger.warning("未能获取到新的密钥列表")
        
        # 检查当前平台是否有可用密钥
        if platform['keys']:
            available_count = key_manager.get_available_keys_count(platform['keys'])
            
            # 关键逻辑：如果当前平台所有密钥都在黑名单中，立即切换平台
            if available_count == 0:
                consecutive_platform_failures += 1
                
                print(f"\n{'='*60}")
                print(f"⚠️ {platform['emoji']} {platform['name']} 所有密钥都在黑名单中！")
                print(f"🔄 准备切换平台... (第 {platform_switch_count + 1} 次切换)")
                print(f"{'='*60}\n")
                logger.warning(f"⚠️ {platform['name']} 所有密钥都在黑名单中，准备切换平台")
                
                # 切换到另一个平台
                if current_platform_key == 'zhipu':
                    current_platform_key = 'siliconflow'
                else:
                    current_platform_key = 'zhipu'
                
                platform_switch_count += 1
                consecutive_platform_failures = 0  # 重置连续失败计数
                
                new_platform = platforms[current_platform_key]
                print(f"🔄 已切换到: {new_platform['emoji']} {new_platform['name']}")
                logger.info(f"🔄 平台切换: {platform['name']} → {new_platform['name']}")
                
                # 如果两个平台都试过了还是全黑，等待一段时间
                if platform_switch_count > 0 and platform_switch_count % 2 == 0:
                    wait_time = 10
                    print(f"⏳ 两个平台都暂时不可用，等待 {wait_time} 秒后重试...")
                    logger.warning(f"两个平台都暂时不可用，等待 {wait_time} 秒")
                    time.sleep(wait_time)
                
                # 强制刷新新平台的密钥列表
                platforms[current_platform_key]['last_fetch_time'] = 0
                continue
        
        # 获取当前平台的可用密钥
        selected_key = key_manager.get_next_available_key_with_rotation(platform['keys'])
        
        if not selected_key:
            # 理论上不应该到这里，因为上面已经检查过了
            print(f"⚠️ {platform['emoji']} {platform['name']} 没有可用密钥")
            logger.warning(f"{platform['name']} 没有可用密钥")
            time.sleep(5)
            continue
        
        try:
            print(f"🚀 第 {attempt_count} 次尝试，使用 {platform['emoji']} {platform['name']} 密钥 ...{selected_key[-8:]}")
            logger.info(f"===== 第 {attempt_count} 次尝试，使用{platform['name']}密钥 ...{selected_key[-8:]} =====")
            
            # 使用防卡死的API调用
            result = api_manager.call_with_timeout(
                api_call_func,
                selected_key,
                prompt,
                timeout,
                timeout=timeout + 10
            )
            
            if result:
                # 记录成功
                key_manager.record_success(selected_key)
                consecutive_platform_failures = 0  # 重置连续失败
                
                print(f"\n{'='*60}")
                print(f"🎉 {platform['emoji']} {platform['name']} API调用成功！")
                print(f"📊 使用密钥: ...{selected_key[-8:]}，共尝试 {attempt_count} 次")
                print(f"🔄 平台切换次数: {platform_switch_count} 次")
                print("✨ 分析完成！")
                print(f"{'='*60}\n")
                
                logger.info(f"✓ {platform['name']} API调用成功！密钥 ...{selected_key[-8:]}，共尝试{attempt_count}次")
                logger.info("===== 分析完成 =====")
                return result
            else:
                print(f"⏰ {platform['emoji']} {platform['name']} 密钥 ...{selected_key[-8:]} 调用超时或返回空结果")
                logger.warning(f"✗ {platform['name']} 密钥 ...{selected_key[-8:]} 调用超时或返回空结果")
                key_manager.record_failure(selected_key, "调用超时或返回空结果")
                consecutive_platform_failures += 1
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ {platform['emoji']} {platform['name']} 密钥 ...{selected_key[-8:]} 调用失败: {error_msg}")
            logger.error(f"✗ {platform['name']} 密钥 ...{selected_key[-8:]} 调用失败: {error_msg}")
            
            # 记录失败
            key_manager.record_failure(selected_key, error_msg)
            consecutive_platform_failures += 1
        
        # 智能切换：如果当前平台连续失败3次，尝试切换平台
        if consecutive_platform_failures >= 3:
            print(f"\n⚠️ {platform['emoji']} {platform['name']} 连续失败 {consecutive_platform_failures} 次，尝试切换平台")
            logger.warning(f"{platform['name']} 连续失败 {consecutive_platform_failures} 次，尝试切换平台")
            
            # 切换平台
            if current_platform_key == 'zhipu':
                current_platform_key = 'siliconflow'
            else:
                current_platform_key = 'zhipu'
            
            platform_switch_count += 1
            consecutive_platform_failures = 0
            
            new_platform = platforms[current_platform_key]
            print(f"🔄 切换到: {new_platform['emoji']} {new_platform['name']}")
            logger.info(f"🔄 平台切换: {platform['name']} → {new_platform['name']}")
            
            # 强制刷新新平台的密钥
            platforms[current_platform_key]['last_fetch_time'] = 0
        
        # 短暂等待后继续下一次尝试
        time.sleep(1)
        
        # 每50次尝试强制刷新当前平台密钥
        if attempt_count % 50 == 0:
            print(f"🔄 达到50次尝试，强制刷新 {platform['emoji']} {platform['name']} 密钥列表...")
            logger.info("达到50次尝试，强制刷新密钥列表...")
            platform['last_fetch_time'] = 0

# ===============================================
# 简化的调用函数 - 保持原有接口
# ===============================================

def quick_analyze(prompt: str) -> str:
    """
    快速分析函数，使用默认参数，保证返回结果
    """
    return analyze_with_fallback(prompt, backup_retries=3, timeout=60)

# ===============================================
# 使用示例
# ===============================================

if __name__ == "__main__":
    # 示例1：基本使用（双平台轮换）
    prompt = "请介绍一下Python编程语言的特点"
    result = analyze_with_fallback(prompt)
    print("\n分析结果：")
    print("-" * 50)
    print(result)
    print("-" * 50)
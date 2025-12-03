# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

def main(args):
    pass

from zhipuai import ZhipuAI
import base64
import requests
from urllib import parse
import json
import time
import threading
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ===============================================
# 优化版API密钥管理器
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


# 创建全局密钥管理器实例（两个平台独立管理）
zhipu_vision_key_manager = OptimizedAPIKeyManager(blacklist_duration=180)
siliconflow_vision_key_manager = OptimizedAPIKeyManager(blacklist_duration=180)


# ===============================================
# API密钥获取函数
# ===============================================

def get_zhipu_api_keys():
    """
    从API接口获取ZhipuAI的API密钥列表
    
    Returns:
        list: API密钥列表
    """
    request_url = 'http://47.95.157.46:8520/api/tracking_iw_key'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {}
    data = parse.urlencode(form_data, True)
    
    try:
        response = requests.post(request_url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            if response_data.get('success'):
                keys = [item['key'] for item in response_data.get('data', [])]
                logger.info(f"成功获取 {len(keys)} 个ZhipuAI API密钥")
                return keys
        logger.error(f"获取ZhipuAI密钥失败: {response.status_code}, {response.text}")
        return []
    except Exception as e:
        logger.error(f"获取ZhipuAI密钥出错: {e}")
        return []


def get_siliconflow_api_keys():
    """
    从API接口获取硅基流动的API密钥列表
    
    Returns:
        list: API密钥列表
    """
    request_url = 'http://47.95.157.46:8520/api/gj_key'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {}
    data = parse.urlencode(form_data, True)
    
    try:
        response = requests.post(request_url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            response_data = json.loads(response.text)
            if response_data.get('success'):
                keys = [item['key'] for item in response_data.get('data', [])]
                logger.info(f"成功获取 {len(keys)} 个硅基流动 API密钥")
                return keys
        logger.error(f"获取硅基流动密钥失败: {response.status_code}, {response.text}")
        return []
    except Exception as e:
        logger.error(f"获取硅基流动密钥出错: {e}")
        return []


# ===============================================
# ZhipuAI视觉API调用
# ===============================================

def _call_zhipu_vision(api_key, image1_base64, image2_base64, prompt_text):
    """
    调用ZhipuAI视觉API
    
    Args:
        api_key: API密钥
        image1_base64: 第一张图片的base64编码
        image2_base64: 第二张图片的base64编码
        prompt_text: 提示词
        
    Returns:
        str: 分析结果
    """
    client = ZhipuAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="GLM-4V-Flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image1_base64}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image2_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_text
                    }
                ]
            }
        ]
    )
    
    result = response.choices[0].message.content
    return result


# ===============================================
# 硅基流动视觉API调用
# ===============================================

def _call_siliconflow_vision(api_key, image1_base64, image2_base64, prompt_text):
    """
    调用硅基流动视觉API
    
    Args:
        api_key: API密钥
        image1_base64: 第一张图片的base64编码
        image2_base64: 第二张图片的base64编码
        prompt_text: 提示词
        
    Returns:
        str: 分析结果（只返回content，不包含推理过程）
    """
    base_url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    model = "THUDM/GLM-4.1V-9B-Thinking"
    logger.info(f"硅基流动使用模型: {model}")
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image1_base64}"
                        }
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image2_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_text
                    }
                ]
            }
        ],
        "stream": False,
        "temperature": 0.7,
        "top_p": 0.7
    }
    
    # 禁用代理
    proxies = {
        "http": None,
        "https": None
    }
    
    response = requests.post(
        base_url,
        headers=headers,
        json=payload,
        proxies=proxies,
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('choices') and len(result['choices']) > 0:
            # 只返回content字段，不返回reasoning_content推理过程
            content = result['choices'][0]['message']['content']
            return content
        else:
            raise Exception("响应中没有有效的choices数据")
    else:
        raise Exception(f"API请求失败: {response.status_code} - {response.text}")


# ===============================================
# 主函数 - 方案B：双平台轮换机制
# ===============================================

def analyze_two_images(image1_path, image2_path, prompt_text):
    """
    方案B：双平台轮换机制
    使用视觉模型分析两张本地图片，支持ZhipuAI和硅基流动双平台
    优先使用ZhipuAI，当所有密钥黑名单时自动切换到硅基流动，反之亦然
    
    参数:
        image1_path (str): 第一张图片的本地路径
        image2_path (str): 第二张图片的本地路径
        prompt_text (str): 提示词，用于指导模型如何分析图片
        
    返回:
        str: 模型的分析结果（保证成功返回）
    """
    
    # 平台配置
    platforms = {
        'zhipu': {
            'name': 'ZhipuAI',
            'emoji': '🧠',
            'manager': zhipu_vision_key_manager,
            'fetch_func': get_zhipu_api_keys,
            'api_func': _call_zhipu_vision,
            'keys': [],
            'last_fetch_time': 0
        },
        'siliconflow': {
            'name': '硅基流动',
            'emoji': '🌊',
            'manager': siliconflow_vision_key_manager,
            'fetch_func': get_siliconflow_api_keys,
            'api_func': _call_siliconflow_vision,
            'keys': [],
            'last_fetch_time': 0
        }
    }
    
    # 初始平台选择：优先ZhipuAI
    current_platform_key = 'zhipu'
    
    # 读取并编码图片（只做一次，避免重复读取）
    logger.info("正在读取并编码图片...")
    with open(image1_path, 'rb') as img_file:
        image1_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    with open(image2_path, 'rb') as img_file:
        image2_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    logger.info("图片编码完成")
    
    attempt_count = 0
    key_refresh_interval = 300  # 5分钟刷新一次密钥列表
    platform_switch_count = 0  # 平台切换计数
    consecutive_platform_failures = 0  # 当前平台连续失败次数
    
    # 显示初始平台
    platform = platforms[current_platform_key]
    logger.info("========================================")
    logger.info(f"🎯 初始平台选择: {platform['emoji']} {platform['name']}")
    logger.info("💡 策略: 优先ZhipuAI，智能切换到硅基流动")
    logger.info("========================================")
    
    while True:
        attempt_count += 1
        current_time = time.time()
        
        platform = platforms[current_platform_key]
        key_manager = platform['manager']
        fetch_keys_func = platform['fetch_func']
        api_call_func = platform['api_func']
        
        # 定期刷新当前平台密钥列表或首次获取
        if not platform['keys'] or (current_time - platform['last_fetch_time'] > key_refresh_interval):
            logger.info(f"===== 第 {attempt_count} 次尝试：获取{platform['name']} API密钥... =====")
            
            new_keys = fetch_keys_func()
            
            if new_keys:
                platform['keys'] = new_keys
                platform['last_fetch_time'] = current_time
                logger.info(f"✅ 成功刷新 {platform['name']} 密钥列表，共 {len(new_keys)} 个密钥")
            else:
                logger.warning(f"❌ 未能获取到新的 {platform['name']} 密钥列表")
        
        # 检查当前平台是否有可用密钥
        if platform['keys']:
            available_count = key_manager.get_available_keys_count(platform['keys'])
            
            # 关键逻辑：如果当前平台所有密钥都在黑名单中，立即切换平台
            if available_count == 0:
                consecutive_platform_failures += 1
                
                logger.warning("========================================")
                logger.warning(f"⚠️ {platform['emoji']} {platform['name']} 所有密钥都在黑名单中！")
                logger.warning(f"🔄 准备切换平台... (第 {platform_switch_count + 1} 次切换)")
                logger.warning("========================================")
                
                # 切换到另一个平台
                if current_platform_key == 'zhipu':
                    current_platform_key = 'siliconflow'
                else:
                    current_platform_key = 'zhipu'
                
                platform_switch_count += 1
                consecutive_platform_failures = 0  # 重置连续失败计数
                
                new_platform = platforms[current_platform_key]
                logger.info(f"🔄 已切换到: {new_platform['emoji']} {new_platform['name']}")
                
                # 如果两个平台都试过了还是全黑，等待一段时间
                if platform_switch_count > 0 and platform_switch_count % 2 == 0:
                    wait_time = 10
                    logger.warning(f"⏳ 两个平台都暂时不可用，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
                # 强制刷新新平台的密钥列表
                platforms[current_platform_key]['last_fetch_time'] = 0
                continue
        
        # 获取当前平台的可用密钥
        selected_key = key_manager.get_next_available_key_with_rotation(platform['keys'])
        
        if not selected_key:
            # 理论上不应该到这里，因为上面已经检查过了
            logger.warning(f"⚠️ {platform['name']} 没有可用密钥")
            time.sleep(5)
            continue
        
        try:
            logger.info(f"===== 第 {attempt_count} 次尝试，使用{platform['name']}密钥 ...{selected_key[-8:]} =====")
            
            # 调用API
            result = api_call_func(selected_key, image1_base64, image2_base64, prompt_text)
            
            # 成功获取响应
            key_manager.record_success(selected_key)
            consecutive_platform_failures = 0  # 重置连续失败
            
            logger.info("========================================")
            logger.info(f"🎉 {platform['emoji']} {platform['name']} API调用成功！")
            logger.info(f"📊 使用密钥: ...{selected_key[-8:]}，共尝试 {attempt_count} 次")
            logger.info(f"🔄 平台切换次数: {platform_switch_count} 次")
            logger.info("✨ 图片分析完成！")
            logger.info("========================================")
            
            # 返回结果
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ {platform['emoji']} {platform['name']} 密钥 ...{selected_key[-8:]} 调用失败: {error_msg}")
            
            # 记录失败
            key_manager.record_failure(selected_key, error_msg)
            consecutive_platform_failures += 1
        
        # 智能切换：如果当前平台连续失败3次，尝试切换平台
        if consecutive_platform_failures >= 3:
            logger.warning(f"\n⚠️ {platform['emoji']} {platform['name']} 连续失败 {consecutive_platform_failures} 次，尝试切换平台")
            
            # 切换平台
            if current_platform_key == 'zhipu':
                current_platform_key = 'siliconflow'
            else:
                current_platform_key = 'zhipu'
            
            platform_switch_count += 1
            consecutive_platform_failures = 0
            
            new_platform = platforms[current_platform_key]
            logger.info(f"🔄 切换到: {new_platform['emoji']} {new_platform['name']}")
            
            # 强制刷新新平台的密钥
            platforms[current_platform_key]['last_fetch_time'] = 0
        
        # 短暂等待后继续下一次尝试
        time.sleep(1)
        
        # 每50次尝试强制刷新当前平台密钥
        if attempt_count % 50 == 0:
            logger.info(f"🔄 达到50次尝试，强制刷新 {platform['name']} 密钥列表...")
            platform['last_fetch_time'] = 0


# ===============================================
# 示例用法 - 调用方式完全不变
# ===============================================

if __name__ == "__main__":
    # 图片路径
    image1 = r"F:\Facebook\1.jpg"  # 替换为您的第一张图片路径
    image2 = r"F:\Facebook\2.jpg"  # 替换为您的第二张图片路径
    
    # 提示词
    prompt = "请比较这两张图片的内容并指出它们的区别和相似之处。"
    
    try:
        # 调用分析函数 - 接口完全不变，内部自动：
        # 1. 优先使用ZhipuAI，智能切换到硅基流动
        # 2. 自动轮换key直至成功
        # 3. 智能管理黑名单
        # 4. 双平台动态切换
        result = analyze_two_images(image1, image2, prompt)
        
        # 打印结果
        print("\n" + "="*50)
        print("分析结果：")
        print("="*50)
        print(result)
        print("="*50)
    except Exception as e:
        print(f"分析失败: {e}")
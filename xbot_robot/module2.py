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
    request_url = 'http://47.95.157.46:8520/api/zhipuai_key'
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
# 主函数 - 支持双平台随机选择
# ===============================================

def analyze_two_images(image1_path, image2_path, prompt_text):
    """
    使用视觉模型分析两张本地图片，支持ZhipuAI和硅基流动双平台
    启动时随机选择平台，支持API密钥自动轮换，直至成功
    
    参数:
        image1_path (str): 第一张图片的本地路径
        image2_path (str): 第二张图片的本地路径
        prompt_text (str): 提示词，用于指导模型如何分析图片
        
    返回:
        str: 模型的分析结果（保证成功返回）
    """
    # 随机选择使用哪个平台
    use_zhipu = random.choice([True, False])
    platform_name = "ZhipuAI" if use_zhipu else "硅基流动"
    
    logger.info(f"========================================")
    logger.info(f"本次调用随机选择: {platform_name}")
    logger.info(f"========================================")
    
    # 读取并编码第一张图片（只做一次）
    with open(image1_path, 'rb') as img_file:
        image1_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    # 读取并编码第二张图片（只做一次）
    with open(image2_path, 'rb') as img_file:
        image2_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    # 根据平台选择对应的组件
    if use_zhipu:
        key_manager = zhipu_vision_key_manager
        get_keys_func = get_zhipu_api_keys
        api_call_func = _call_zhipu_vision
    else:
        key_manager = siliconflow_vision_key_manager
        get_keys_func = get_siliconflow_api_keys
        api_call_func = _call_siliconflow_vision
    
    # 无限循环，直至成功
    attempt_count = 0
    last_key_fetch_time = 0
    api_keys = []
    key_refresh_interval = 300  # 5分钟刷新一次密钥列表
    
    while True:
        attempt_count += 1
        current_time = time.time()
        
        # 定期刷新密钥列表或首次获取
        if not api_keys or (current_time - last_key_fetch_time > key_refresh_interval):
            logger.info(f"===== 第 {attempt_count} 次尝试：获取{platform_name} API密钥... =====")
            new_keys = get_keys_func()
            
            if new_keys:
                api_keys = new_keys
                last_key_fetch_time = current_time
            else:
                logger.warning("未能获取到新的密钥列表")
                if not api_keys:
                    # 如果完全没有密钥，等待后重试
                    logger.warning("没有可用密钥，等待10秒后重试...")
                    time.sleep(10)
                    continue
        
        # 使用key管理器获取下一个可用的key
        selected_key = key_manager.get_next_available_key_with_rotation(api_keys)
        
        if not selected_key:
            # 所有密钥都在黑名单中，等待后重试
            logger.warning(f"所有密钥都在黑名单中，等待10秒后重试... (第{attempt_count}次尝试)")
            time.sleep(10)
            continue
        
        try:
            logger.info(f"===== 第 {attempt_count} 次尝试，使用{platform_name}密钥 ...{selected_key[-8:]} =====")
            
            # 调用API
            result = api_call_func(selected_key, image1_base64, image2_base64, prompt_text)
            
            # 成功获取响应
            # 记录成功
            key_manager.record_success(selected_key)
            
            logger.info(f"✓ {platform_name} API调用成功！密钥 ...{selected_key[-8:]}，共尝试{attempt_count}次")
            logger.info("===== 分析完成 =====")
            
            # 返回结果
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ {platform_name} 密钥 ...{selected_key[-8:]} 调用失败: {error_msg}")
            
            # 记录失败（管理器会自动判断是否加入黑名单）
            key_manager.record_failure(selected_key, error_msg)
            
            # 短暂等待后继续下一次尝试
            time.sleep(1)
            continue
        
        # 每50次尝试强制刷新一次密钥
        if attempt_count % 50 == 0:
            logger.info("达到50次尝试，强制刷新密钥列表...")
            last_key_fetch_time = 0


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
        # 1. 随机选择平台（ZhipuAI或硅基流动）
        # 2. 自动轮换key直至成功
        # 3. 智能管理黑名单
        result = analyze_two_images(image1, image2, prompt)
        
        # 打印结果
        print("\n" + "="*50)
        print("分析结果：")
        print("="*50)
        print(result)
        print("="*50)
    except Exception as e:
        print(f"分析失败: {e}")
"""
API服务层 - 直接向店小秘服务器发送HTTP请求
所有功能集成在一个文件中，无需外部依赖
"""
import os
import json
import time
import requests
import re
from datetime import datetime, timedelta
from typing import List, Optional


# ==================== 配置常量 ====================
COOKIE_URL = "https://ceshi-1300392622.cos.ap-beijing.myqcloud.com/dxm_cookie.json"
COOKIE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cookie_cache")
LOCAL_COOKIE_PATH = os.path.join(COOKIE_CACHE_DIR, "dxm_cookie.json")
COOKIE_CACHE_MINUTES = 30
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 3
RETRY_DELAY = 2


# ==================== Cookie管理 ====================
class _CookieManager:
    """Cookie管理器 - 自动下载和缓存"""

    def __init__(self):
        self.cookie_url = COOKIE_URL
        self.local_path = LOCAL_COOKIE_PATH
        self.cache_dir = COOKIE_CACHE_DIR
        self.cache_minutes = COOKIE_CACHE_MINUTES
        self.timeout = DOWNLOAD_TIMEOUT
        self.retry_times = RETRY_TIMES
        self.retry_delay = RETRY_DELAY
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except:
                pass

    def _is_cache_valid(self):
        """检查缓存是否有效"""
        if not os.path.exists(self.local_path):
            return False

        try:
            file_mtime = os.path.getmtime(self.local_path)
            file_time = datetime.fromtimestamp(file_mtime)
            if datetime.now() - file_time > timedelta(minutes=self.cache_minutes):
                return False

            with open(self.local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return 'cookies' in data and data['cookies']
        except:
            return False

    def _download_cookie(self):
        """下载Cookie"""
        for attempt in range(self.retry_times):
            try:
                response = requests.get(self.cookie_url, timeout=self.timeout)
                response.raise_for_status()
                cookie_data = response.json()

                if 'cookies' not in cookie_data:
                    continue

                with open(self.local_path, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, ensure_ascii=False, indent=2)
                return True
            except:
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
        return False

    def get_cookies_dict(self):
        """获取Cookies字典"""
        # 如果缓存无效则下载
        if not self._is_cache_valid():
            if not self._download_cookie():
                if not os.path.exists(self.local_path):
                    return None

        # 读取并转换Cookie
        try:
            with open(self.local_path, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)

            cookies = {}
            if 'cookies' in cookie_data:
                for cookie in cookie_data['cookies']:
                    cookies[cookie['name']] = cookie['value']
                return cookies
        except:
            return None


# 创建全局Cookie管理器
_cookie_manager = _CookieManager()


def _get_cookies():
    """获取Cookies（内部使用）"""
    return _cookie_manager.get_cookies_dict()


# ==================== API函数 - 直接发送HTTP请求 ====================

def get_package_numbers(content: str) -> Optional[List[str]]:
    """
    获取包裹号列表

    Args:
        content: 搜索内容（订单号）

    Returns:
        包裹号列表，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = "https://www.dianxiaomi.com/package/searchPackage.htm"

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1',
        'isRemoved': '-1',
        'isSearch': '1',
        'orderField': 'order_create_time',
        'orderSearchType': '1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        response.raise_for_status()

        # 提取packageNumber
        pattern = r'data-packageNumber="([^"]+)"'
        matches = re.findall(pattern, response.text)
        return matches if matches else []
    except:
        return None


# TODO: 其他21个函数待实现
# 每个函数都按照相同模式：获取Cookie -> 发送HTTP请求 -> 返回结果


if __name__ == "__main__":
    # 测试
    result = get_package_numbers("LYS-SP00001-15fe2a-c9-2156-A")
    print(f"结果: {result}")

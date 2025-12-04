#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用API服务 - 支持任意HTTP请求，自动注入Cookie，限流8次/秒
"""
import sys
import os
import time
import json
import requests
from threading import Lock
from collections import deque

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from cookie_manager import get_cookie_path


class RateLimiter:
    """速率限制器 - 8次/秒"""

    def __init__(self, max_calls=8, time_window=1.0):
        """
        Args:
            max_calls: 时间窗口内最大调用次数
            time_window: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self.lock = Lock()

    def wait_if_needed(self):
        """如果超过速率限制，等待"""
        with self.lock:
            now = time.time()

            # 移除时间窗口外的调用记录
            while self.calls and self.calls[0] <= now - self.time_window:
                self.calls.popleft()

            # 如果达到限制，计算需要等待的时间
            if len(self.calls) >= self.max_calls:
                sleep_time = self.time_window - (now - self.calls[0])
                if sleep_time > 0:
                    print(f"[RateLimiter] 达到速率限制，等待 {sleep_time:.2f} 秒...")
                    time.sleep(sleep_time)
                    # 重新计算
                    now = time.time()
                    while self.calls and self.calls[0] <= now - self.time_window:
                        self.calls.popleft()

            # 记录本次调用
            self.calls.append(now)


class GenericAPIService:
    """通用API服务类 - 执行任意HTTP请求"""

    def __init__(self):
        """初始化服务"""
        self.cookie_path = None
        self.rate_limiter = RateLimiter(max_calls=8, time_window=1.0)
        self._refresh_cookie()
        print("[GenericAPIService] ✓ 服务初始化成功")

    def _refresh_cookie(self):
        """刷新Cookie路径"""
        self.cookie_path = get_cookie_path()
        if not self.cookie_path:
            raise Exception("无法获取Cookie，请检查网络连接")
        return self.cookie_path

    def _ensure_cookie(self):
        """确保Cookie可用"""
        if not self.cookie_path:
            self._refresh_cookie()
        return self.cookie_path

    def _get_cookie_string(self):
        """获取Cookie字符串"""
        cookie_path = self._ensure_cookie()

        try:
            with open(cookie_path, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)

            # 提取cookies
            cookies_dict = {}
            if 'cookies' in cookie_data and isinstance(cookie_data['cookies'], list):
                for cookie in cookie_data['cookies']:
                    if 'name' in cookie and 'value' in cookie:
                        cookies_dict[cookie['name']] = cookie['value']

            # 构建cookie字符串
            cookie_string = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
            return cookie_string

        except Exception as e:
            raise Exception(f"读取Cookie失败: {e}")

    def execute_request(self, url, headers=None, data=None, method='POST', params=None):
        """
        通用HTTP请求执行器

        Args:
            url (str): 完整的API URL
            headers (dict): 请求头（不含cookie，由服务器自动注入）
            data (dict): POST请求的表单数据
            method (str): HTTP方法，'POST'或'GET'，默认'POST'
            params (dict): GET请求的URL参数

        Returns:
            dict: 完整的响应信息，包含：
                - success: 是否成功
                - status_code: HTTP状态码
                - response: 响应数据（JSON或文本）
                - headers: 响应头
                - error: 错误信息（如果有）
                - request_info: 请求信息（调试用）
        """

        # 等待速率限制
        self.rate_limiter.wait_if_needed()

        # 准备headers
        if headers is None:
            headers = {}

        # 自动注入Cookie
        try:
            cookie_string = self._get_cookie_string()
            headers['cookie'] = cookie_string
            print(f"[GenericAPIService] ✓ Cookie已注入")
        except Exception as e:
            return {
                'success': False,
                'error': f'Cookie注入失败: {str(e)}',
                'request_info': {
                    'url': url,
                    'method': method
                }
            }

        # 记录请求信息
        request_info = {
            'url': url,
            'method': method,
            'headers': {k: v for k, v in headers.items() if k.lower() != 'cookie'},  # 不记录cookie
            'data': data if method == 'POST' else None,
            'params': params if method == 'GET' else None,
            'timestamp': time.time()
        }

        print(f"[GenericAPIService] 发送 {method} 请求: {url}")

        # 执行HTTP请求
        try:
            if method.upper() == 'POST':
                response = requests.post(
                    url=url,
                    headers=headers,
                    data=data,
                    timeout=30
                )
            elif method.upper() == 'GET':
                response = requests.get(
                    url=url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
            else:
                return {
                    'success': False,
                    'error': f'不支持的HTTP方法: {method}',
                    'request_info': request_info
                }

            # 解析响应
            result = {
                'success': True,
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'request_info': request_info
            }

            # 尝试解析JSON
            try:
                result['response'] = response.json()
                result['response_type'] = 'json'
            except json.JSONDecodeError:
                result['response'] = response.text
                result['response_type'] = 'text'

            print(f"[GenericAPIService] ✓ 响应成功: {response.status_code}")

            return result

        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': '请求超时',
                'request_info': request_info
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'请求失败: {str(e)}',
                'request_info': request_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知错误: {str(e)}',
                'request_info': request_info
            }


# 全局服务实例
_service = None


def get_service():
    """获取服务实例"""
    global _service
    if _service is None:
        _service = GenericAPIService()
    return _service


# 便捷函数
def execute(url, headers=None, data=None, method='POST', params=None):
    """
    便捷函数 - 执行HTTP请求

    Args:
        url: API URL
        headers: 请求头（不含cookie）
        data: POST数据
        method: HTTP方法
        params: GET参数

    Returns:
        完整的响应信息
    """
    service = get_service()
    return service.execute_request(url, headers, data, method, params)


if __name__ == "__main__":
    print("=" * 60)
    print("通用API服务测试")
    print("=" * 60)

    try:
        # 测试初始化
        service = GenericAPIService()
        print("\n✓ 服务初始化成功")
        print(f"✓ Cookie路径: {service.cookie_path}")

        # 测试速率限制
        print("\n测试速率限制 (8次/秒)...")
        for i in range(10):
            start = time.time()
            service.rate_limiter.wait_if_needed()
            elapsed = time.time() - start
            print(f"  请求 {i+1}: 等待 {elapsed:.3f}秒")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

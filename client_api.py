#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用API客户端 - 完全自包含，无需外部依赖
只需要这一个文件即可使用

特点：
- 自包含：所有逻辑都在这个文件内
- 简单：只需调用 api_call() 函数
- 自动重试：遇到速率限制自动重试
- 完整错误处理：返回详细的错误信息

使用方法：
    from client_api import api_call

    result = api_call(
        url="https://api.example.com/endpoint",
        headers={"Content-Type": "application/json"},
        data={"key": "value"},
        method="POST"
    )

    if result['success']:
        print(result['response'])
    else:
        print(result['error'])
"""

import time
import json

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    exit(1)


# ==================== 配置 ====================
SERVER_URL = "http://47.104.72.198:5000/api/execute"
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAYS = [2, 4, 8]  # 重试延迟（秒），指数退避


# ==================== 核心函数 ====================

def api_call(url, headers=None, data=None, method='POST', params=None, timeout=30, verbose=False):
    """
    统一的API调用函数 - 自动处理Cookie注入和速率限制

    参数：
        url (str): 目标API的完整URL（必填）
        headers (dict): 请求头，不含cookie（可选）
        data (dict): POST请求的表单数据（可选）
        method (str): HTTP方法，'POST'或'GET'，默认'POST'（可选）
        params (dict): GET请求的URL参数（可选）
        timeout (int): 请求超时时间（秒），默认30秒（可选）
        verbose (bool): 是否显示详细日志，默认False（可选）

    返回：
        dict: API响应，包含以下字段：
            - success (bool): 请求是否成功
            - response: 目标API返回的数据（成功时）
            - response_type (str): 响应类型，'json'或'text'（成功时）
            - status_code (int): HTTP状态码
            - error (str): 错误信息（失败时）
            - retries (int): 实际重试次数

    示例：
        # POST请求
        result = api_call(
            url="https://www.dianxiaomi.com/api/package/searchPackage.json",
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
            },
            data={
                'pageNo': '1',
                'searchType': 'orderId',
                'content': 'ORDER123'
            },
            method='POST'
        )

        # GET请求
        result = api_call(
            url="https://www.dianxiaomi.com/some/endpoint",
            headers={'accept': 'text/html'},
            method='GET'
        )
    """

    # 验证参数
    if not url:
        return {
            'success': False,
            'error': '参数错误: url 不能为空',
            'retries': 0
        }

    if method.upper() not in ['POST', 'GET']:
        return {
            'success': False,
            'error': f'参数错误: 不支持的HTTP方法 {method}，仅支持POST和GET',
            'retries': 0
        }

    # 准备请求数据
    request_payload = {
        'url': url,
        'method': method.upper()
    }

    if headers:
        request_payload['headers'] = headers

    if data:
        request_payload['data'] = data

    if params:
        request_payload['params'] = params

    # 重试逻辑
    retry_count = 0
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            if verbose:
                print(f"[Client] 尝试 {attempt + 1}/{MAX_RETRIES + 1}: {method} {url}")

            # 发送请求到代理服务器
            response = requests.post(
                SERVER_URL,
                json=request_payload,
                timeout=timeout
            )

            # 解析响应
            try:
                result = response.json()
            except json.JSONDecodeError:
                return {
                    'success': False,
                    'error': f'服务器响应格式错误: {response.text[:200]}',
                    'status_code': response.status_code,
                    'retries': retry_count
                }

            # 检查是否成功
            if result.get('success'):
                if verbose:
                    print(f"[Client] ✓ 请求成功: {result.get('status_code')}")

                result['retries'] = retry_count
                return result

            # 检查是否是速率限制（429）
            status_code = result.get('status_code', 500)

            if status_code == 429 and attempt < MAX_RETRIES:
                # 速率限制，自动重试
                retry_count += 1
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]

                if verbose:
                    print(f"[Client] 速率限制，等待 {delay} 秒后重试...")

                time.sleep(delay)
                continue

            # 其他错误，不重试
            result['retries'] = retry_count
            return result

        except requests.exceptions.Timeout:
            last_error = f'请求超时（超过{timeout}秒）'

            if attempt < MAX_RETRIES:
                retry_count += 1
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]

                if verbose:
                    print(f"[Client] 超时，等待 {delay} 秒后重试...")

                time.sleep(delay)
                continue

        except requests.exceptions.ConnectionError as e:
            last_error = f'连接错误: 无法连接到服务器 {SERVER_URL}'

            if attempt < MAX_RETRIES:
                retry_count += 1
                delay = RETRY_DELAYS[min(attempt, len(RETRY_DELAYS) - 1)]

                if verbose:
                    print(f"[Client] 连接失败，等待 {delay} 秒后重试...")

                time.sleep(delay)
                continue

        except requests.exceptions.RequestException as e:
            last_error = f'请求错误: {str(e)}'
            break

        except Exception as e:
            last_error = f'未知错误: {str(e)}'
            break

    # 所有重试都失败
    return {
        'success': False,
        'error': last_error or '请求失败',
        'retries': retry_count
    }


# ==================== 便捷函数 ====================

def post(url, headers=None, data=None, **kwargs):
    """
    POST请求的便捷函数

    参数：
        url: 目标URL
        headers: 请求头
        data: 请求数据
        **kwargs: 其他参数（timeout, verbose等）

    返回：
        API响应
    """
    return api_call(url=url, headers=headers, data=data, method='POST', **kwargs)


def get(url, headers=None, params=None, **kwargs):
    """
    GET请求的便捷函数

    参数：
        url: 目标URL
        headers: 请求头
        params: URL参数
        **kwargs: 其他参数（timeout, verbose等）

    返回：
        API响应
    """
    return api_call(url=url, headers=headers, params=params, method='GET', **kwargs)


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    print("=" * 60)
    print("客户端API使用示例")
    print("=" * 60)

    # 示例1：POST请求 - 搜索包裹
    print("\n示例1：POST请求 - 搜索包裹")
    print("-" * 60)

    result = api_call(
        url="https://www.dianxiaomi.com/api/package/searchPackage.json",
        headers={
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/x-www-form-urlencoded'
        },
        data={
            'pageNo': '1',
            'pageSize': '100',
            'searchType': 'orderId',
            'content': 'LYS-SP00001-15fe2a-c9-2156-A'
        },
        method='POST',
        verbose=True
    )

    if result['success']:
        print(f"✓ 请求成功")
        print(f"  状态码: {result['status_code']}")
        print(f"  响应类型: {result['response_type']}")
        print(f"  重试次数: {result['retries']}")
        print(f"  响应数据: {json.dumps(result['response'], ensure_ascii=False, indent=2)[:500]}...")
    else:
        print(f"✗ 请求失败")
        print(f"  错误: {result['error']}")
        print(f"  重试次数: {result['retries']}")

    # 示例2：GET请求 - 获取SKU代码
    print("\n示例2：GET请求 - 获取SKU代码")
    print("-" * 60)

    result = api_call(
        url="https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm",
        headers={
            'accept': 'text/html,application/xhtml+xml,application/xml'
        },
        method='GET',
        verbose=True
    )

    if result['success']:
        print(f"✓ 请求成功")
        print(f"  状态码: {result['status_code']}")
        print(f"  响应类型: {result['response_type']}")
        print(f"  响应长度: {len(result['response'])} 字符")
    else:
        print(f"✗ 请求失败")
        print(f"  错误: {result['error']}")

    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    # 运行示例
    example_usage()

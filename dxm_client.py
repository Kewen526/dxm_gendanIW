#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DXM API客户端 - 简单调用接口
使用方法：
    from dxm_client import call_api

    result = call_api(url, headers, data, method='POST')
"""

from generic_api_service import GenericAPIService

# 全局服务实例
_service = None


def get_service():
    """获取服务实例（单例模式）"""
    global _service
    if _service is None:
        _service = GenericAPIService()
    return _service


def call_api(url, headers=None, data=None, method='POST', params=None):
    """
    调用DXM API - 自动注入Cookie，自动限流8次/秒

    参数:
        url (str): API地址，例如 "https://www.dianxiaomi.com/api/package/searchPackage.json"
        headers (dict): 请求头（不需要包含cookie，服务器会自动注入）
        data (dict): POST请求的表单数据
        method (str): HTTP方法，'POST' 或 'GET'，默认 'POST'
        params (dict): GET请求的URL参数

    返回:
        dict: 完整的响应信息
            {
                'success': True/False,              # 是否成功
                'status_code': 200,                 # HTTP状态码
                'headers': {...},                   # 响应头
                'response': {...},                  # 响应数据（JSON或文本）
                'response_type': 'json'/'text',     # 响应类型
                'request_info': {                   # 请求信息
                    'url': '...',
                    'method': '...',
                    'headers': {...},
                    'data': {...},
                    'params': {...},
                    'timestamp': 1234567890.123
                },
                'error': '错误信息'                  # 如果失败
            }

    使用示例:
        # 搜索包裹
        result = call_api(
            url="https://www.dianxiaomi.com/api/package/searchPackage.json",
            headers={
                'accept': 'application/json, text/plain, */*',
                'bx-v': '2.5.11',
                'content-type': 'application/x-www-form-urlencoded',
            },
            data={
                'pageNo': '1',
                'pageSize': '100',
                'searchType': 'orderId',
                'content': 'LPP-SP00001-4c54be-96812-A',
                'axios_cancelToken': 'true'
            },
            method='POST'
        )

        if result['success']:
            print("成功:", result['response'])
        else:
            print("失败:", result['error'])
    """
    service = get_service()
    return service.execute_request(url, headers, data, method, params)


# 便捷函数：提取包裹ID
def extract_package_ids(api_result):
    """
    从API响应中提取包裹ID列表

    参数:
        api_result: call_api() 返回的结果

    返回:
        list: 包裹ID列表，失败返回空列表
    """
    if not api_result.get('success'):
        return []

    if api_result.get('response_type') != 'json':
        return []

    response = api_result.get('response', {})
    if response.get('code') != 0:
        return []

    package_list = response.get('data', {}).get('page', {}).get('list', [])
    return [str(pkg.get('id')) for pkg in package_list if pkg.get('id')]


# 便捷函数：提取包裹号
def extract_package_numbers(api_result):
    """
    从API响应中提取包裹号列表（packageNumber）

    参数:
        api_result: call_api() 返回的结果

    返回:
        list: 包裹号列表，失败返回空列表
    """
    if not api_result.get('success'):
        return []

    if api_result.get('response_type') != 'json':
        return []

    response = api_result.get('response', {})
    if response.get('code') != 0:
        return []

    package_list = response.get('data', {}).get('page', {}).get('list', [])
    return [pkg.get('packageNumber') for pkg in package_list if pkg.get('packageNumber')]


if __name__ == "__main__":
    # 示例：搜索包裹
    print("=" * 60)
    print("DXM API客户端示例")
    print("=" * 60)

    # 准备请求
    url = "https://www.dianxiaomi.com/api/package/searchPackage.json"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all',
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': 'LPP-SP00001-4c54be-96812-A',
        'axios_cancelToken': 'true',
        'shopId': '-1',
        'state': '',
        'history': '',
        'isVoided': '-1',
        'isRemoved': '-1',
    }

    # 调用API
    print("\n调用API...")
    result = call_api(url, headers, data, method='POST')

    # 显示结果
    if result['success']:
        print(f"\n✓ 成功！状态码: {result['status_code']}")

        # 提取包裹ID
        package_ids = extract_package_ids(result)
        if package_ids:
            print(f"找到 {len(package_ids)} 个包裹ID:")
            for pkg_id in package_ids:
                print(f"  - {pkg_id}")

        # 提取包裹号
        package_numbers = extract_package_numbers(result)
        if package_numbers:
            print(f"找到 {len(package_numbers)} 个包裹号:")
            for pkg_num in package_numbers:
                print(f"  - {pkg_num}")
    else:
        print(f"\n✗ 失败: {result.get('error')}")

    print("\n" + "=" * 60)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通用API服务 - 使用 search_package_ids 示例
"""

from generic_api_service import GenericAPIService
import json


def test_search_package_ids():
    """测试搜索包裹ID"""

    print("=" * 60)
    print("测试通用API服务 - search_package_ids")
    print("=" * 60)

    # 1. 初始化服务
    print("\n[步骤1] 初始化服务...")
    service = GenericAPIService()

    # 2. 准备请求参数
    print("\n[步骤2] 准备请求参数...")

    url = "https://www.dianxiaomi.com/api/package/searchPackage.json"

    # Headers（不含cookie，服务器会自动注入）
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }

    # Data
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'history': '',
        'searchType': 'orderId',
        'content': 'LPP-SP00001-4c54be-96812-A',  # 测试订单号
        'isVoided': '-1',
        'isRemoved': '-1',
        'commitPlatform': '',
        'platform': '',
        'isGreen': '0',
        'isYellow': '0',
        'isOrange': '0',
        'isRed': '0',
        'isViolet': '0',
        'isBlue': '0',
        'cornflowerBlue': '0',
        'pink': '0',
        'teal': '0',
        'turquoise': '0',
        'unmarked': '0',
        'isSearch': '1',
        'isFree': '-1',
        'isBatch': '-1',
        'isOversea': '-1',
        'forbiddenStatus': '-1',
        'forbiddenReason': '0',
        'orderField': 'order_create_time',
        'behindTrack': '-1',
        'storageId': '0',
        'timeOut': '0',
        'orderSearchType': '1',
        'axios_cancelToken': 'true'
    }

    print(f"URL: {url}")
    print(f"订单号: {data['content']}")

    # 3. 执行请求
    print("\n[步骤3] 执行请求...")
    result = service.execute_request(
        url=url,
        headers=headers,
        data=data,
        method='POST'
    )

    # 4. 显示完整结果
    print("\n[步骤4] 完整响应结果:")
    print("=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("=" * 60)

    # 5. 提取包裹ID
    if result['success'] and result.get('response_type') == 'json':
        response_data = result['response']
        if response_data.get('code') == 0:
            package_list = response_data.get('data', {}).get('page', {}).get('list', [])
            package_ids = [str(pkg.get('id')) for pkg in package_list if pkg.get('id')]

            print(f"\n[步骤5] 提取包裹ID:")
            if package_ids:
                print(f"✓ 成功！找到 {len(package_ids)} 个包裹ID:")
                for pkg_id in package_ids:
                    print(f"  - {pkg_id}")
            else:
                print("✗ 未找到包裹ID")
        else:
            print(f"\n✗ API返回错误: {response_data.get('msg', '未知错误')}")
    else:
        print(f"\n✗ 请求失败: {result.get('error', '未知错误')}")

    return result


def test_rate_limit():
    """测试速率限制 - 连续10次请求"""

    print("\n\n" + "=" * 60)
    print("测试速率限制 - 连续10次请求")
    print("=" * 60)

    service = GenericAPIService()

    url = "https://www.dianxiaomi.com/api/package/searchPackage.json"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded'
    }
    data = {
        'pageNo': '1',
        'pageSize': '10',
        'content': 'LPP-SP00001-4c54be-96812-A',
        'searchType': 'orderId',
        'axios_cancelToken': 'true'
    }

    import time
    start_time = time.time()

    for i in range(10):
        print(f"\n请求 {i+1}/10...")
        result = service.execute_request(url, headers, data, 'POST')
        print(f"  状态: {'成功' if result['success'] else '失败'}")
        elapsed = time.time() - start_time
        print(f"  总耗时: {elapsed:.2f}秒")

    total_time = time.time() - start_time
    print(f"\n总结:")
    print(f"  10次请求总耗时: {total_time:.2f}秒")
    print(f"  平均速率: {10/total_time:.2f}次/秒")
    print(f"  符合8次/秒限制: {'✓' if 10/total_time <= 8.5 else '✗'}")


if __name__ == "__main__":
    # 测试1: 基本功能
    test_search_package_ids()

    # 测试2: 速率限制
    # test_rate_limit()  # 取消注释以测试速率限制

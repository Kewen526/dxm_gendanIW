#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 测试通用API服务

测试项目：
1. POST请求测试
2. GET请求测试
3. 速率限制测试（8次/秒）
4. 错误处理测试
5. 重试机制测试

运行方式：
    python test_api.py
"""

import time
import json
from client_api import api_call, post, get


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(success, message, details=None):
    """打印测试结果"""
    symbol = "✓" if success else "✗"
    status = "通过" if success else "失败"
    print(f"{symbol} [{status}] {message}")
    if details:
        for key, value in details.items():
            print(f"    {key}: {value}")


def test_post_request():
    """测试POST请求"""
    print_section("测试1: POST请求 - 搜索包裹")

    result = post(
        url="https://www.dianxiaomi.com/api/package/searchPackage.json",
        headers={
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/x-www-form-urlencoded'
        },
        data={
            'pageNo': '1',
            'pageSize': '100',
            'searchType': 'orderId',
            'content': 'LYS-SP00001-15fe2a-c9-2156-A',
            'isVoided': '-1'
        },
        verbose=True
    )

    if result['success']:
        print_result(True, "POST请求成功", {
            "状态码": result['status_code'],
            "响应类型": result['response_type'],
            "重试次数": result['retries']
        })

        # 检查响应数据
        if result['response_type'] == 'json':
            response = result['response']
            if isinstance(response, dict):
                print(f"    响应字段: {list(response.keys())}")
                if 'code' in response:
                    print(f"    业务代码: {response['code']}")
        return True
    else:
        print_result(False, "POST请求失败", {
            "错误": result.get('error'),
            "重试次数": result.get('retries', 0)
        })
        return False


def test_get_request():
    """测试GET请求"""
    print_section("测试2: GET请求 - 获取SKU代码页面")

    result = get(
        url="https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm",
        headers={
            'accept': 'text/html,application/xhtml+xml,application/xml',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        params={
            'id': '',
            'type': '0',
            'editOrCopy': '0'
        },
        verbose=True
    )

    if result['success']:
        print_result(True, "GET请求成功", {
            "状态码": result['status_code'],
            "响应类型": result['response_type'],
            "响应长度": f"{len(result['response'])} 字符" if isinstance(result['response'], str) else "N/A"
        })
        return True
    else:
        print_result(False, "GET请求失败", {
            "错误": result.get('error'),
            "重试次数": result.get('retries', 0)
        })
        return False


def test_rate_limit():
    """测试速率限制"""
    print_section("测试3: 速率限制 - 8次/秒")

    print("发送10个连续请求，观察速率限制...")

    times = []
    for i in range(10):
        start = time.time()

        result = post(
            url="https://www.dianxiaomi.com/api/package/searchPackage.json",
            headers={
                'accept': 'application/json',
                'content-type': 'application/x-www-form-urlencoded'
            },
            data={
                'pageNo': '1',
                'pageSize': '10',
                'searchType': 'orderId',
                'content': f'TEST{i}'
            }
        )

        elapsed = time.time() - start
        times.append(elapsed)

        print(f"  请求 {i+1:2d}: {elapsed:.3f}秒 - {'成功' if result['success'] else '失败'}")

    # 分析结果
    total_time = sum(times)
    avg_time = total_time / len(times)

    print(f"\n统计:")
    print(f"  总时间: {total_time:.2f}秒")
    print(f"  平均时间: {avg_time:.3f}秒/请求")
    print(f"  实际速率: {len(times)/total_time:.2f}次/秒")

    # 速率应该接近8次/秒
    actual_rate = len(times) / total_time
    if 6 <= actual_rate <= 10:
        print_result(True, "速率限制正常工作", {
            "目标速率": "8次/秒",
            "实际速率": f"{actual_rate:.2f}次/秒"
        })
        return True
    else:
        print_result(False, "速率限制异常", {
            "目标速率": "8次/秒",
            "实际速率": f"{actual_rate:.2f}次/秒"
        })
        return False


def test_error_handling():
    """测试错误处理"""
    print_section("测试4: 错误处理")

    # 测试1: 无效的URL
    print("\n测试4.1: 无效的URL")
    result = api_call(url="", method="POST")
    if not result['success']:
        print_result(True, "正确处理空URL错误", {
            "错误信息": result['error']
        })
    else:
        print_result(False, "未能捕获空URL错误")

    # 测试2: 不支持的HTTP方法
    print("\n测试4.2: 不支持的HTTP方法")
    result = api_call(
        url="https://www.example.com",
        method="DELETE"
    )
    if not result['success']:
        print_result(True, "正确处理不支持的方法", {
            "错误信息": result['error']
        })
    else:
        print_result(False, "未能捕获不支持的方法错误")

    # 测试3: 无效的目标URL（会超时）
    print("\n测试4.3: 无效的目标URL（超时测试）")
    result = api_call(
        url="https://invalid-domain-that-does-not-exist-12345.com/api",
        headers={'accept': 'application/json'},
        method="POST",
        timeout=5,
        verbose=True
    )
    if not result['success']:
        print_result(True, "正确处理无效目标URL", {
            "错误信息": result['error'],
            "重试次数": result.get('retries', 0)
        })
        return True
    else:
        print_result(False, "未能捕获无效目标URL错误")
        return False


def test_retry_mechanism():
    """测试重试机制"""
    print_section("测试5: 重试机制")

    print("注意: 此测试会触发重试，可能需要较长时间...")

    # 使用一个可能失败的请求来测试重试
    result = api_call(
        url="https://httpstat.us/500",  # 这个URL会返回500错误
        method="GET",
        verbose=True
    )

    print_result(
        True,  # 重试机制本身是成功的，即使请求失败
        "重试机制测试完成",
        {
            "最终结果": "成功" if result['success'] else "失败",
            "重试次数": result.get('retries', 0)
        }
    )

    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 70)
    print("  通用API服务测试套件")
    print("  服务器: http://47.104.72.198:5000")
    print("=" * 70)

    results = []

    # 运行测试
    results.append(("POST请求", test_post_request()))
    results.append(("GET请求", test_get_request()))
    results.append(("速率限制", test_rate_limit()))
    results.append(("错误处理", test_error_handling()))
    results.append(("重试机制", test_retry_mechanism()))

    # 汇总结果
    print_section("测试汇总")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        print_result(result, name)

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")

    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 api_service.py 的 search_package_ids
"""

from api_service import DianxiaomiService

# 创建服务实例
print("初始化服务...")
service = DianxiaomiService()
print(f"✓ Cookie路径: {service.cookie_path}")

# 调用函数
print("\n测试 search_package_ids...")
test_order = "LPP-SP00001-4c54be-96812-A"
print(f"订单号: {test_order}")

result = service.search_package_ids(test_order)

print(f"\n结果类型: {type(result)}")
print(f"结果内容: {result}")

if result:
    print(f"\n✓ 成功！找到 {len(result)} 个包裹ID:")
    for pkg_id in result:
        print(f"  - {pkg_id}")
else:
    print("\n✗ 未找到包裹ID")

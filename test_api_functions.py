"""
测试 api_functions.py 的各个函数
"""
import api_functions

# 测试订单号
test_orders = [
    "LPP-SP00001-4c54be-96812-A",
    "LYN-SP00001-62e3fd-22346-A"
]

print("=" * 60)
print("测试 api_functions.py")
print("=" * 60)

# 测试1：get_package_numbers
print("\n【测试1】get_package_numbers")
print("-" * 60)
for order_id in test_orders:
    print(f"\n订单号: {order_id}")
    result = api_functions.get_package_numbers(order_id)
    
    if result is None:
        print("  ✗ 请求失败 (返回None)")
    elif len(result) == 0:
        print("  ⚠ 未找到包裹 (返回空列表)")
    else:
        print(f"  ✓ 成功！找到 {len(result)} 个包裹号:")
        for pkg in result[:3]:  # 只显示前3个
            print(f"    - {pkg}")

# 测试2：search_package_ids
print("\n\n【测试2】search_package_ids")
print("-" * 60)
test_order = test_orders[0]
print(f"\n订单号: {test_order}")
result = api_functions.search_package_ids(test_order)

if result:
    print(f"  ✓ 成功！找到 {len(result)} 个包裹ID:")
    for pkg_id in result[:3]:
        print(f"    - {pkg_id}")
else:
    print("  ⚠ 未找到包裹ID")

# 测试3：get_shop_dict
print("\n\n【测试3】get_shop_dict")
print("-" * 60)
try:
    result = api_functions.get_shop_dict()
    if result:
        print(f"  ✓ 成功！找到 {len(result)} 个店铺")
        # 只显示前3个
        for i, (name, shop_id) in enumerate(list(result.items())[:3], 1):
            print(f"    {i}. {name}: {shop_id}")
    else:
        print("  ⚠ 未找到店铺")
except Exception as e:
    print(f"  ✗ 错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

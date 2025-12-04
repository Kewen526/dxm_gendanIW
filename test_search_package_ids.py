#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 search_package_ids 函数
使用订单号: LPP-SP00001-4c54be-96812-A
"""

from api_service import DianxiaomiService

def main():
    print("=" * 60)
    print("测试 search_package_ids")
    print("=" * 60)

    # 测试订单号
    test_order_id = "LPP-SP00001-4c54be-96812-A"

    try:
        # 创建服务实例
        print("\n[1] 初始化服务...")
        service = DianxiaomiService()
        print(f"✓ 服务初始化成功")
        print(f"✓ Cookie路径: {service.cookie_path}")

        # 调用 search_package_ids
        print(f"\n[2] 搜索包裹ID...")
        print(f"订单号: {test_order_id}")

        result = service.search_package_ids(test_order_id)

        # 显示结果
        print(f"\n[3] 结果:")
        if result:
            print(f"✓ 成功！找到 {len(result)} 个包裹ID:")
            for i, package_id in enumerate(result, 1):
                print(f"  {i}. {package_id}")
        else:
            print("✗ 未找到包裹ID或返回为空")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

        return result

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()

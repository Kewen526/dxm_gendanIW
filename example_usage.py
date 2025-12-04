"""
api_service.py 函数式接口使用示例

这个文件展示了如何使用 api_service.py 提供的 22 个函数。
所有函数都使用 xbot_robot 的原始函数名，并且 Cookie 自动管理，无需手动传入。
"""

from api_service import (
    # 搜索类函数
    search_dxm_product,
    search_dxm_product_all,
    search_package,
    search_package_ids,
    search_package2,
    get_package_numbers,
    get_dianxiaomi_order_id,

    # 商品管理类函数
    add_product_to_dianxiaomi,
    add_product_sg_dxm,
    add_product_to_warehouse,

    # 订单操作类函数
    set_dianxiaomi_comment,
    batch_commit_platform_packages,
    batch_set_voided,
    update_dianxiaomi_warehouse,
    update_dianxiaomi_provider_batch,

    # 信息查询类函数
    get_supplier_ids,
    get_shop_dict_with_cookie,
    request_dianxiaomi_provider_auth,
    get_ail_link,
    fetch_sku_code,

    # 文件上传类函数
    upload_excel_to_dianxiaomi,

    # 数据抓取类函数
    run_scraper,
)


# ==================== 使用示例 ====================

def example_1_search_product():
    """示例1：搜索商品"""
    print("=" * 60)
    print("示例1：搜索商品")
    print("=" * 60)

    # 搜索单个商品（返回第一个匹配结果）
    # Cookie 自动从 URL 下载并缓存，无需传入
    result = search_dxm_product(
        search_value="iPhone 15",
        shop_code="SH001",
        variant="黑色",
        debug=True
    )
    print(f"搜索结果: {result}")

    # 搜索所有匹配的商品
    all_results = search_dxm_product_all(
        search_value="iPhone 15",
        shop_code="SH001",
        variant="黑色",
        debug=True
    )
    print(f"所有匹配结果: {all_results}")


def example_2_get_shop_dict():
    """示例2：获取店铺字典"""
    print("\n" + "=" * 60)
    print("示例2：获取店铺字典")
    print("=" * 60)

    # 无需传入任何参数，Cookie 自动处理
    shops = get_shop_dict_with_cookie()
    print(f"店铺字典: {shops}")


def example_3_search_package():
    """示例3：搜索包裹"""
    print("\n" + "=" * 60)
    print("示例3：搜索包裹")
    print("=" * 60)

    # 方法1：搜索包裹并提取运单号
    tracking_number = search_package(content="6385553-1124")
    print(f"运单号: {tracking_number}")

    # 方法2：搜索包裹ID列表
    package_ids = search_package_ids(content="6385553-1124")
    print(f"包裹ID列表: {package_ids}")

    # 方法3：搜索包裹（备用方法）
    package_num = search_package2(content="6385553-1124")
    print(f"包裹号: {package_num}")

    # 方法4：获取包裹号列表
    package_numbers = get_package_numbers(content="6385553-1124")
    print(f"包裹号列表: {package_numbers}")


def example_4_batch_commit():
    """示例4：批量提交订单"""
    print("\n" + "=" * 60)
    print("示例4：批量提交订单")
    print("=" * 60)

    result = batch_commit_platform_packages(
        package_ids=["123", "456", "789"]  # 或者字符串 "123,456,789"
    )
    print(f"批量提交结果: {result}")


def example_5_add_product():
    """示例5：添加商品"""
    print("\n" + "=" * 60)
    print("示例5：添加商品")
    print("=" * 60)

    result = add_product_to_dianxiaomi(
        name="苹果手机",
        name_en="iPhone",
        price="999",
        url="https://example.com/product",
        custom_zn="手机",
        custom_en="Mobile Phone",
        sb_weight="200",
        sb_price="100",
        supplier='["54280071577953030"]',
        main_supplier="54280071577953030",
        img_url="https://example.com/image.jpg",
        id="",
        pid_pair="123456",
        vid_pair="789",
        shop_id_pair="001",
        sku="SKU-001"
    )
    print(f"添加商品结果: {result}")


def example_6_update_warehouse():
    """示例6：更新仓库"""
    print("\n" + "=" * 60)
    print("示例6：更新仓库")
    print("=" * 60)

    result = update_dianxiaomi_warehouse(
        package_ids=["123", "456"],
        storage_id="warehouse_001"
    )
    print(f"更新仓库结果: {result}")


def example_7_get_supplier_ids():
    """示例7：获取供应商ID"""
    print("\n" + "=" * 60)
    print("示例7：获取供应商ID")
    print("=" * 60)

    supplier_ids = get_supplier_ids(supplier_name="阿里巴巴")
    print(f"供应商ID列表: {supplier_ids}")


def example_8_upload_excel():
    """示例8：上传Excel文件"""
    print("\n" + "=" * 60)
    print("示例8：上传Excel文件")
    print("=" * 60)

    uuid = upload_excel_to_dianxiaomi(file_path="/path/to/your/file.xlsx")
    print(f"上传成功，UUID: {uuid}")


def example_9_run_scraper():
    """示例9：运行订单爬虫"""
    print("\n" + "=" * 60)
    print("示例9：运行订单爬虫")
    print("=" * 60)

    responses = run_scraper(days=7)
    print(f"抓取了 {len(responses)} 天的数据")


# ==================== 完整的函数列表 ====================

def show_all_functions():
    """显示所有可用函数及其参数"""
    print("\n" + "=" * 60)
    print("所有可用函数列表（22个）")
    print("=" * 60)

    functions = {
        "搜索类函数 (7个)": [
            "search_dxm_product(search_value, shop_code, variant, debug=False)",
            "search_dxm_product_all(search_value, shop_code, variant, debug=False)",
            "search_package(content)",
            "search_package_ids(content)",
            "search_package2(content)",
            "get_package_numbers(content)",
            "get_dianxiaomi_order_id(content)",
        ],
        "商品管理类函数 (3个)": [
            "add_product_to_dianxiaomi(name, name_en, price, url, custom_zn, custom_en, sb_weight, sb_price, supplier, main_supplier, img_url, id, pid_pair, vid_pair, shop_id_pair, sku)",
            "add_product_sg_dxm(name, name_en, sku_code, sku, price, source_url, img_url, is_used, product_type, product_status, name_cn_bg, name_en_bg, weight_bg, price_bg, danger_des_bg, warehouse_id_list, supplier_id, is_main)",
            "add_product_to_warehouse(sku)",
        ],
        "订单操作类函数 (5个)": [
            "set_dianxiaomi_comment(package_ids)",
            "batch_commit_platform_packages(package_ids)",
            "batch_set_voided(package_ids)",
            "update_dianxiaomi_warehouse(package_ids, storage_id)",
            "update_dianxiaomi_provider_batch(package_ids, auth_id)",
        ],
        "信息查询类函数 (5个)": [
            "get_supplier_ids(supplier_name)",
            "get_shop_dict_with_cookie()",
            "request_dianxiaomi_provider_auth()",
            "get_ail_link(product_url)",
            "fetch_sku_code()",
        ],
        "文件上传类函数 (1个)": [
            "upload_excel_to_dianxiaomi(file_path)",
        ],
        "数据抓取类函数 (1个)": [
            "run_scraper(days)",
        ],
    }

    for category, funcs in functions.items():
        print(f"\n【{category}】")
        for func in funcs:
            print(f"  - {func}")


if __name__ == "__main__":
    print("=" * 60)
    print("API Service 函数式接口使用示例")
    print("=" * 60)

    # 显示所有可用函数
    show_all_functions()

    print("\n\n" + "=" * 60)
    print("使用提示")
    print("=" * 60)
    print("""
✅ Cookie 自动管理 - 无需手动传入路径！

1. 所有函数都会自动从 URL 下载并缓存 Cookie
2. Cookie 缓存 30 分钟，过期后自动刷新
3. 你只需要传入业务参数，不需要关心 Cookie 路径
4. 函数名保持 xbot_robot 原始定义

示例代码：
    from api_service import search_dxm_product, get_shop_dict_with_cookie

    # 搜索商品 - Cookie 自动处理
    result = search_dxm_product("iPhone", "SH001", "黑色")

    # 获取店铺字典 - Cookie 自动处理
    shops = get_shop_dict_with_cookie()

    # 获取包裹号 - Cookie 自动处理
    numbers = get_package_numbers("LYS-SP00001-15fe2a-c9-2156-A")
    """)

    print("\n运行以下示例函数来测试（取消注释）：")
    print("  # example_1_search_product()")
    print("  # example_2_get_shop_dict()")
    print("  # example_3_search_package()")
    print("  # example_4_batch_commit()")
    print("  # example_5_add_product()")
    print("  # example_6_update_warehouse()")
    print("  # example_7_get_supplier_ids()")
    print("  # example_8_upload_excel()")
    print("  # example_9_run_scraper()")

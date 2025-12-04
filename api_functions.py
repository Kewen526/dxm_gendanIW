"""
API函数封装 - 提供所有店小秘API功能的直接调用方式

使用方式1（推荐）：
    from api_functions import search_product, get_package_numbers

    result = search_product("iPhone", "SH001", "黑色")
    packages = get_package_numbers("LPP-SP00001-xxx")

使用方式2：
    import api_functions

    result = api_functions.search_product("iPhone", "SH001", "黑色")
    packages = api_functions.get_package_numbers("LPP-SP00001-xxx")
"""

from api_service import DianxiaomiService

# 创建全局服务实例
_service = DianxiaomiService()

# ==================== 搜索类函数 ====================

def search_product(search_value, shop_code, variant, debug=False):
    """
    搜索店小秘商品（返回第一个匹配结果）

    Args:
        search_value (str): 搜索关键词
        shop_code (str): 店铺编码
        variant (str): 变体信息
        debug (bool): 是否显示调试信息

    Returns:
        str: SKU名称，未找到返回None
    """
    return _service.search_product(search_value, shop_code, variant, debug)


def search_product_all(search_value, shop_code, variant, debug=False):
    """
    搜索店小秘商品（返回所有匹配结果）

    Args:
        search_value (str): 搜索关键词
        shop_code (str): 店铺编码
        variant (str): 变体信息
        debug (bool): 是否显示调试信息

    Returns:
        list: 所有匹配的SKU列表
    """
    return _service.search_product_all(search_value, shop_code, variant, debug)


def search_package(content):
    """
    搜索包裹信息并提取运单号

    Args:
        content (str): 搜索内容（订单号）

    Returns:
        str: 运单号，未找到返回None
    """
    return _service.search_package(content)


def search_package_ids(content):
    """
    搜索包裹ID列表

    Args:
        content (str): 搜索内容

    Returns:
        list: 包裹ID列表
    """
    return _service.search_package_ids(content)


def search_package2(content):
    """
    搜索包裹（方法2）

    Args:
        content (str): 搜索内容

    Returns:
        str: 包裹号
    """
    return _service.search_package2(content)


def get_package_numbers(content):
    """
    获取包裹号列表

    Args:
        content (str): 搜索内容

    Returns:
        list: 包裹号列表
    """
    return _service.get_package_numbers(content)


def get_dianxiaomi_order_id(content):
    """
    获取店小秘订单ID

    Args:
        content (str): 搜索内容

    Returns:
        str: 订单ID
    """
    return _service.get_dianxiaomi_order_id(content)


# ==================== 商品管理类函数 ====================

def add_product(product_data):
    """
    添加商品到店小秘

    Args:
        product_data (dict): 商品信息字典，包含以下字段：
            - name: 商品中文名称
            - name_en: 商品英文名称
            - price: 商品价格
            - url: 商品来源链接
            - custom_zn: 中文报关信息
            - custom_en: 英文报关信息
            - sb_weight: 预估重量
            - sb_price: 申报价值
            - supplier: 供应商ID列表
            - main_supplier: 主要供应商ID
            - img_url: 商品图片URL
            - id: 店小秘系统内商品ID
            - pid_pair: 平台商品ID
            - vid_pair: 变体ID
            - shop_id_pair: 店铺ID
            - sku: 商品SKU编码

    Returns:
        str: API响应结果
    """
    return _service.add_product(product_data)


def add_product_sg(product_data):
    """
    添加SG商品到店小秘

    Args:
        product_data (dict): 商品信息字典（字段同add_product）

    Returns:
        dict: API响应结果
    """
    return _service.add_product_sg(product_data)


def add_product_to_warehouse(sku):
    """
    添加商品到仓库

    Args:
        sku (str): 商品SKU编码

    Returns:
        dict: API响应结果
    """
    return _service.add_product_to_warehouse(sku)


# ==================== 订单操作类函数 ====================

def set_comment(package_ids):
    """
    设置订单备注

    Args:
        package_ids (str): 包裹ID，多个用逗号分隔

    Returns:
        dict: API响应结果
    """
    return _service.set_comment(package_ids)


def batch_commit(package_ids):
    """
    批量提交包裹到平台

    Args:
        package_ids (list or str): 包裹ID列表或逗号分隔的字符串

    Returns:
        dict: API响应结果
    """
    return _service.batch_commit(package_ids)


def batch_void(package_ids):
    """
    批量设置包裹为作废

    Args:
        package_ids (list or str): 包裹ID列表或逗号分隔的字符串

    Returns:
        dict: API响应结果
    """
    return _service.batch_void(package_ids)


def update_warehouse(package_ids, storage_id):
    """
    更新包裹仓库

    Args:
        package_ids (list or str): 包裹ID列表
        storage_id (str): 仓库ID

    Returns:
        dict: API响应结果
    """
    return _service.update_warehouse(package_ids, storage_id)


def update_provider(package_ids, auth_id):
    """
    批量更新物流服务商

    Args:
        package_ids (list or str): 包裹ID列表
        auth_id (str): 物流授权ID

    Returns:
        dict: API响应结果
    """
    return _service.update_provider(package_ids, auth_id)


# ==================== 信息查询类函数 ====================

def get_supplier_ids(supplier_name):
    """
    获取供应商ID

    Args:
        supplier_name (str): 供应商名称

    Returns:
        list: 供应商ID列表
    """
    return _service.get_supplier_ids(supplier_name)


def get_shop_dict():
    """
    获取店铺字典

    Returns:
        dict: 店铺信息字典
    """
    return _service.get_shop_dict()


def get_provider_list():
    """
    获取物流服务商列表

    Returns:
        dict: 物流服务商字典
    """
    return _service.get_provider_list()


def get_ali_link(product_url):
    """
    获取阿里巴巴链接

    Args:
        product_url (str): 商品URL

    Returns:
        str: 阿里巴巴链接
    """
    return _service.get_ali_link(product_url)


def fetch_sku_code():
    """
    获取SKU代码

    Returns:
        dict: SKU代码数据
    """
    return _service.fetch_sku_code()


# ==================== 文件上传类函数 ====================

def upload_excel(file_path):
    """
    上传Excel文件到店小秘

    Args:
        file_path (str): Excel文件路径

    Returns:
        str: UUID
    """
    return _service.upload_excel(file_path)


# ==================== 数据抓取类函数 ====================

def run_scraper(days):
    """
    运行订单爬虫

    Args:
        days (int): 抓取天数

    Returns:
        list: 响应列表
    """
    return _service.run_scraper(days)


# ==================== 导出所有函数 ====================

__all__ = [
    # 搜索类
    'search_product',
    'search_product_all',
    'search_package',
    'search_package_ids',
    'search_package2',
    'get_package_numbers',
    'get_dianxiaomi_order_id',

    # 商品管理
    'add_product',
    'add_product_sg',
    'add_product_to_warehouse',

    # 订单操作
    'set_comment',
    'batch_commit',
    'batch_void',
    'update_warehouse',
    'update_provider',

    # 信息查询
    'get_supplier_ids',
    'get_shop_dict',
    'get_provider_list',
    'get_ali_link',
    'fetch_sku_code',

    # 文件上传
    'upload_excel',

    # 数据抓取
    'run_scraper',
]


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("API函数封装测试")
    print("=" * 60)

    # 测试导入
    print("\n可用函数列表:")
    for i, func_name in enumerate(__all__, 1):
        print(f"  {i:2d}. {func_name}")

    print(f"\n共 {len(__all__)} 个函数可用")
    print("=" * 60)

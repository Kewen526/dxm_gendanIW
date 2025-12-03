"""
API服务层 - 封装所有xbot_robot函数，统一参数处理
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from cookie_manager import get_cookie_path

# 导入xbot_robot的各个模块
from xbot_robot import (
    search_dxm_product,
    add_product_to_dianxiaomi,
    add_product_sg_dxm,
    add_product_to_warehouse,
    get_dxm_info,
    get_ali_link,
    batch_commit_platform_packages,
    batch_set_voided,
    search_package,
    search_package_ids,
    search_package2,
    get_package_numbers,
    upload_excel_to_dianxiaomi,
    update_dianxiaomi_warehouse,
    update_dianxiaomi_provider_batch,
    set_dianxiaomi_comment,
    get_shop_dict,
    get_supplier_ids,
    request_dianxiaomi_provider_auth,
    search_dianxiaomi_package,
    fetch_sku_code,
)


class DianxiaomiService:
    """店小秘API服务类 - 封装所有功能"""

    def __init__(self):
        """初始化服务"""
        self.cookie_path = None
        self._refresh_cookie()

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

    # ==================== 搜索类函数 ====================

    def search_product(self, search_value, shop_code, variant, debug=False):
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
        cookie_path = self._ensure_cookie()
        return search_dxm_product.search_dxm_product(
            search_value, shop_code, variant, cookie_path, debug
        )

    def search_product_all(self, search_value, shop_code, variant, debug=False):
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
        cookie_path = self._ensure_cookie()
        return search_dxm_product.search_dxm_product_all(
            search_value, shop_code, variant, cookie_path, debug
        )

    def search_package(self, content):
        """
        搜索包裹信息并提取运单号

        Args:
            content (str): 搜索内容（订单号）

        Returns:
            str: 运单号，未找到返回None
        """
        cookie_path = self._ensure_cookie()
        return search_package.search_package(cookie_path, content)

    def search_package_ids(self, content):
        """
        搜索包裹ID列表

        Args:
            content (str): 搜索内容

        Returns:
            list: 包裹ID列表
        """
        cookie_path = self._ensure_cookie()
        return search_package_ids.search_package(cookie_path, content)

    def search_package2(self, content):
        """
        搜索包裹（方法2）

        Args:
            content (str): 搜索内容

        Returns:
            str: 包裹号
        """
        cookie_path = self._ensure_cookie()
        return search_package2.search_package(content, cookie_path)

    def get_package_numbers(self, content):
        """
        获取包裹号列表

        Args:
            content (str): 搜索内容

        Returns:
            list: 包裹号列表
        """
        cookie_path = self._ensure_cookie()
        return get_package_numbers.get_package_numbers(content, cookie_path)

    def get_dianxiaomi_order_id(self, content):
        """
        获取店小秘订单ID

        Args:
            content (str): 搜索内容

        Returns:
            str: 订单ID
        """
        cookie_path = self._ensure_cookie()
        return search_dianxiaomi_package.get_dianxiaomi_order_id(cookie_path, content)

    # ==================== 商品管理类函数 ====================

    def add_product(self, product_data):
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
        cookie_path = self._ensure_cookie()
        return add_product_to_dianxiaomi.add_product_to_dianxiaomi(
            cookie_path,
            product_data.get('name'),
            product_data.get('name_en'),
            product_data.get('price'),
            product_data.get('url'),
            product_data.get('custom_zn'),
            product_data.get('custom_en'),
            product_data.get('sb_weight'),
            product_data.get('sb_price'),
            product_data.get('supplier'),
            product_data.get('main_supplier'),
            product_data.get('img_url'),
            product_data.get('id'),
            product_data.get('pid_pair'),
            product_data.get('vid_pair'),
            product_data.get('shop_id_pair'),
            product_data.get('sku')
        )

    def add_product_sg(self, product_data):
        """
        添加SG商品到店小秘

        Args:
            product_data (dict): 商品信息字典（字段同add_product）

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return add_product_sg_dxm.add_product_sg_dxm(
            cookie_path,
            product_data.get('name'),
            product_data.get('name_en'),
            product_data.get('price'),
            product_data.get('url'),
            product_data.get('custom_zn'),
            product_data.get('custom_en'),
            product_data.get('sb_weight'),
            product_data.get('sb_price'),
            product_data.get('supplier'),
            product_data.get('main_supplier'),
            product_data.get('img_url'),
            product_data.get('sku'),
            product_data.get('pid_pair'),
            product_data.get('vid_pair'),
            product_data.get('shop_id_pair')
        )

    def add_product_to_warehouse(self, sku):
        """
        添加商品到仓库

        Args:
            sku (str): 商品SKU编码

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return add_product_to_warehouse.add_product_to_warehouse(cookie_path, sku)

    # ==================== 订单操作类函数 ====================

    def set_comment(self, package_ids):
        """
        设置订单备注

        Args:
            package_ids (str): 包裹ID，多个用逗号分隔

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return set_dianxiaomi_comment.set_dianxiaomi_comment(cookie_path, package_ids)

    def batch_commit(self, package_ids):
        """
        批量提交包裹到平台

        Args:
            package_ids (list or str): 包裹ID列表或逗号分隔的字符串

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return batch_commit_platform_packages.batch_commit_platform_packages(
            cookie_path, package_ids
        )

    def batch_void(self, package_ids):
        """
        批量设置包裹为作废

        Args:
            package_ids (list or str): 包裹ID列表或逗号分隔的字符串

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return batch_set_voided.batch_set_voided(cookie_path, package_ids)

    def update_warehouse(self, package_ids, storage_id):
        """
        更新包裹仓库

        Args:
            package_ids (list or str): 包裹ID列表
            storage_id (str): 仓库ID

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return update_dianxiaomi_warehouse.update_dianxiaomi_warehouse(
            cookie_path, package_ids, storage_id
        )

    def update_provider(self, package_ids, auth_id):
        """
        批量更新物流服务商

        Args:
            package_ids (list or str): 包裹ID列表
            auth_id (str): 物流授权ID

        Returns:
            dict: API响应结果
        """
        cookie_path = self._ensure_cookie()
        return update_dianxiaomi_provider_batch.update_dianxiaomi_provider_batch(
            cookie_path, package_ids, auth_id
        )

    # ==================== 信息查询类函数 ====================

    def get_supplier_ids(self, supplier_name):
        """
        获取供应商ID

        Args:
            supplier_name (str): 供应商名称

        Returns:
            list: 供应商ID列表
        """
        cookie_path = self._ensure_cookie()
        return get_supplier_ids.get_supplier_ids(cookie_path, supplier_name)

    def get_shop_dict(self):
        """
        获取店铺字典

        Returns:
            dict: 店铺信息字典
        """
        cookie_path = self._ensure_cookie()
        return get_shop_dict.get_shop_dict_with_cookie(cookie_path)

    def get_provider_list(self):
        """
        获取物流服务商列表

        Returns:
            dict: 物流服务商字典
        """
        cookie_path = self._ensure_cookie()
        return request_dianxiaomi_provider_auth.request_dianxiaomi_provider_auth(
            cookie_path
        )

    def get_ali_link(self, product_url):
        """
        获取阿里巴巴链接

        Args:
            product_url (str): 商品URL

        Returns:
            str: 阿里巴巴链接
        """
        cookie_path = self._ensure_cookie()
        return get_ali_link.get_ail_link(product_url, cookie_path)

    def fetch_sku_code(self):
        """
        获取SKU代码

        Returns:
            dict: SKU代码数据
        """
        cookie_path = self._ensure_cookie()
        return fetch_sku_code.fetch_sku_code(cookie_path)

    # ==================== 文件上传类函数 ====================

    def upload_excel(self, file_path):
        """
        上传Excel文件到店小秘

        Args:
            file_path (str): Excel文件路径

        Returns:
            str: UUID
        """
        cookie_path = self._ensure_cookie()
        return upload_excel_to_dianxiaomi.upload_excel_to_dianxiaomi(
            file_path, cookie_path
        )

    # ==================== 数据抓取类函数 ====================

    def run_scraper(self, days):
        """
        运行订单爬虫

        Args:
            days (int): 抓取天数

        Returns:
            list: 响应列表
        """
        cookie_path = self._ensure_cookie()
        return get_dxm_info.run_scraper(cookie_path, days)


# 创建全局服务实例
_service = None


def get_service():
    """获取服务实例的便捷函数"""
    global _service
    if _service is None:
        _service = DianxiaomiService()
    return _service


if __name__ == "__main__":
    # 测试服务
    print("=" * 60)
    print("测试API服务")
    print("=" * 60)

    try:
        service = DianxiaomiService()
        print("\n✓ 服务初始化成功")
        print(f"✓ Cookie路径: {service.cookie_path}")
    except Exception as e:
        print(f"\n✗ 服务初始化失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

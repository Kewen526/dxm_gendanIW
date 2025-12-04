"""
API服务层 - 封装所有xbot_robot函数，统一参数处理
所有功能集成在一个文件中，无需外部依赖
"""
import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))


# ==================== 配置常量（嵌入） ====================
# Cookie文件的远程URL
COOKIE_URL = "https://ceshi-1300392622.cos.ap-beijing.myqcloud.com/dxm_cookie.json"

# 本地Cookie缓存目录（使用临时目录，兼容RPA环境）
COOKIE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cookie_cache")

# 本地Cookie文件路径
LOCAL_COOKIE_PATH = os.path.join(COOKIE_CACHE_DIR, "dxm_cookie.json")

# Cookie缓存时间（分钟）
COOKIE_CACHE_MINUTES = 30

# HTTP配置
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 3
RETRY_DELAY = 2


# ==================== Cookie管理功能（嵌入） ====================
class _CookieManager:
    """内置Cookie管理器"""

    def __init__(self):
        self.cookie_url = COOKIE_URL
        self.local_path = LOCAL_COOKIE_PATH
        self.cache_dir = COOKIE_CACHE_DIR
        self.cache_minutes = COOKIE_CACHE_MINUTES
        self.timeout = DOWNLOAD_TIMEOUT
        self.retry_times = RETRY_TIMES
        self.retry_delay = RETRY_DELAY
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
                print(f"[CookieManager] 创建缓存目录: {self.cache_dir}")
            except Exception as e:
                print(f"[CookieManager] 创建缓存目录失败: {e}")

    def _is_cache_valid(self):
        """检查本地缓存是否有效"""
        if not os.path.exists(self.local_path):
            return False

        try:
            # 检查文件修改时间
            file_mtime = os.path.getmtime(self.local_path)
            file_time = datetime.fromtimestamp(file_mtime)
            now = datetime.now()

            # 判断是否过期
            if now - file_time > timedelta(minutes=self.cache_minutes):
                print(f"[CookieManager] Cookie缓存已过期 (超过{self.cache_minutes}分钟)")
                return False

            # 检查文件格式
            with open(self.local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'cookies' not in data or not data['cookies']:
                    print("[CookieManager] Cookie文件格式错误")
                    return False

            return True
        except Exception as e:
            print(f"[CookieManager] Cookie文件检查失败: {e}")
            return False

    def _download_cookie(self):
        """从URL下载Cookie文件"""
        print(f"[CookieManager] 正在从URL下载Cookie...")

        for attempt in range(self.retry_times):
            try:
                response = requests.get(self.cookie_url, timeout=self.timeout)
                response.raise_for_status()

                # 验证JSON格式
                cookie_data = response.json()
                if 'cookies' not in cookie_data:
                    raise ValueError("Cookie数据格式错误：缺少'cookies'字段")

                # 保存到本地
                with open(self.local_path, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, ensure_ascii=False, indent=2)

                print(f"[CookieManager] ✓ Cookie下载成功")
                print(f"[CookieManager] ✓ 包含 {len(cookie_data['cookies'])} 个cookies")
                return True

            except Exception as e:
                print(f"[CookieManager] ✗ 下载失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)

        print(f"[CookieManager] ✗ Cookie下载失败")
        return False

    def get_cookie_path(self, force_refresh=False):
        """获取可用的Cookie文件路径"""
        # 如果强制刷新或缓存无效，则下载
        if force_refresh or not self._is_cache_valid():
            if not self._download_cookie():
                # 如果下载失败，检查是否有旧的缓存可用
                if os.path.exists(self.local_path):
                    print("[CookieManager] ⚠️  使用旧的Cookie缓存")
                    return self.local_path
                else:
                    print("[CookieManager] ✗ 无法获取Cookie")
                    return None
        else:
            print(f"[CookieManager] ✓ 使用缓存的Cookie")

        return self.local_path


# 创建全局Cookie管理器实例
_cookie_manager = _CookieManager()


def get_cookie_path(force_refresh=False):
    """获取Cookie文件路径"""
    return _cookie_manager.get_cookie_path(force_refresh)


# ==================== 修复 xbot_robot 导入问题 ====================
# 创建 mock package 模块，避免相对导入错误
class _MockPackage:
    """Mock package 模块"""
    class variables:
        pass

# 将 mock package 添加到 sys.modules
sys.modules['xbot_robot.package'] = _MockPackage()
sys.modules['package'] = _MockPackage()

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


# ==================== 函数式接口 - 直接导出原始函数 ====================
# 以下函数使用 xbot_robot 的原始函数名和参数定义，可以直接调用

# 导入 xbot_robot 模块（避免命名冲突）
from xbot_robot import search_dxm_product as _search_dxm_product_module
from xbot_robot import add_product_to_dianxiaomi as _add_product_to_dianxiaomi_module
from xbot_robot import add_product_sg_dxm as _add_product_sg_dxm_module
from xbot_robot import add_product_to_warehouse as _add_product_to_warehouse_module
from xbot_robot import search_package as _search_package_module
from xbot_robot import search_package_ids as _search_package_ids_module
from xbot_robot import search_package2 as _search_package2_module
from xbot_robot import get_package_numbers as _get_package_numbers_module
from xbot_robot import search_dianxiaomi_package as _search_dianxiaomi_package_module
from xbot_robot import batch_commit_platform_packages as _batch_commit_platform_packages_module
from xbot_robot import batch_set_voided as _batch_set_voided_module
from xbot_robot import update_dianxiaomi_warehouse as _update_dianxiaomi_warehouse_module
from xbot_robot import update_dianxiaomi_provider_batch as _update_dianxiaomi_provider_batch_module
from xbot_robot import set_dianxiaomi_comment as _set_dianxiaomi_comment_module
from xbot_robot import get_shop_dict as _get_shop_dict_module
from xbot_robot import get_supplier_ids as _get_supplier_ids_module
from xbot_robot import request_dianxiaomi_provider_auth as _request_dianxiaomi_provider_auth_module
from xbot_robot import get_ali_link as _get_ali_link_module
from xbot_robot import fetch_sku_code as _fetch_sku_code_module
from xbot_robot import upload_excel_to_dianxiaomi as _upload_excel_to_dianxiaomi_module
from xbot_robot import get_dxm_info as _get_dxm_info_module

# 搜索类函数
def search_dxm_product(search_value, shop_code, variant, debug=False):
    """搜索店小秘商品（返回第一个匹配结果）"""
    cookie_path = get_cookie_path()
    return _search_dxm_product_module.search_dxm_product(
        search_value, shop_code, variant, cookie_path, debug
    )

def search_dxm_product_all(search_value, shop_code, variant, debug=False):
    """搜索店小秘商品（返回所有匹配结果）"""
    cookie_path = get_cookie_path()
    return _search_dxm_product_module.search_dxm_product_all(
        search_value, shop_code, variant, cookie_path, debug
    )

def search_package(content):
    """搜索包裹信息并提取运单号"""
    cookie_path = get_cookie_path()
    return _search_package_module.search_package(cookie_path, content)

def search_package_ids(content):
    """搜索包裹ID列表"""
    cookie_path = get_cookie_path()
    return _search_package_ids_module.search_package(cookie_path, content)

def search_package2(content):
    """搜索包裹（方法2）"""
    cookie_path = get_cookie_path()
    return _search_package2_module.search_package(content, cookie_path)

def get_package_numbers(content):
    """获取包裹号列表"""
    cookie_path = get_cookie_path()
    return _get_package_numbers_module.get_package_numbers(content, cookie_path)

def get_dianxiaomi_order_id(content):
    """获取店小秘订单ID"""
    cookie_path = get_cookie_path()
    return _search_dianxiaomi_package_module.get_dianxiaomi_order_id(cookie_path, content)

# 商品管理类函数
def add_product_to_dianxiaomi(
    name, name_en, price, url, custom_zn, custom_en,
    sb_weight, sb_price, supplier, main_supplier, img_url, id,
    pid_pair, vid_pair, shop_id_pair, sku
):
    """添加商品到店小秘"""
    cookie_path = get_cookie_path()
    return _add_product_to_dianxiaomi_module.add_product_to_dianxiaomi(
        cookie_path, name, name_en, price, url, custom_zn, custom_en,
        sb_weight, sb_price, supplier, main_supplier, img_url, id,
        pid_pair, vid_pair, shop_id_pair, sku
    )

def add_product_sg_dxm(
    name, name_en, sku_code, sku, price, source_url, img_url, is_used,
    product_type, product_status, name_cn_bg, name_en_bg, weight_bg,
    price_bg, danger_des_bg, warehouse_id_list, supplier_id, is_main
):
    """添加SG商品到店小秘"""
    cookie_path = get_cookie_path()
    return _add_product_sg_dxm_module.add_product_to_dianxiaomi(
        name, name_en, sku_code, sku, price, source_url, img_url, is_used,
        product_type, product_status, name_cn_bg, name_en_bg, weight_bg,
        price_bg, danger_des_bg, warehouse_id_list, supplier_id, is_main,
        cookie_path
    )

def add_product_to_warehouse(sku):
    """添加商品到仓库"""
    cookie_path = get_cookie_path()
    return _add_product_to_warehouse_module.add_product_to_warehouse(cookie_path, sku)

# 订单操作类函数
def set_dianxiaomi_comment(package_ids):
    """设置订单备注"""
    cookie_path = get_cookie_path()
    return _set_dianxiaomi_comment_module.set_dianxiaomi_comment(cookie_path, package_ids)

def batch_commit_platform_packages(package_ids):
    """批量提交包裹到平台"""
    cookie_path = get_cookie_path()
    return _batch_commit_platform_packages_module.batch_commit_platform_packages(
        cookie_path, package_ids
    )

def batch_set_voided(package_ids):
    """批量设置包裹为作废"""
    cookie_path = get_cookie_path()
    return _batch_set_voided_module.batch_set_voided(cookie_path, package_ids)

def update_dianxiaomi_warehouse(package_ids, storage_id):
    """更新包裹仓库"""
    cookie_path = get_cookie_path()
    return _update_dianxiaomi_warehouse_module.update_dianxiaomi_warehouse(
        cookie_path, package_ids, storage_id
    )

def update_dianxiaomi_provider_batch(package_ids, auth_id):
    """批量更新物流服务商"""
    cookie_path = get_cookie_path()
    return _update_dianxiaomi_provider_batch_module.update_dianxiaomi_provider_batch(
        cookie_path, package_ids, auth_id
    )

# 信息查询类函数
def get_supplier_ids(supplier_name):
    """获取供应商ID"""
    cookie_path = get_cookie_path()
    return _get_supplier_ids_module.get_supplier_ids(cookie_path, supplier_name)

def get_shop_dict_with_cookie():
    """获取店铺字典"""
    cookie_path = get_cookie_path()
    return _get_shop_dict_module.get_shop_dict_with_cookie(cookie_path)

def request_dianxiaomi_provider_auth():
    """获取物流服务商列表"""
    cookie_path = get_cookie_path()
    return _request_dianxiaomi_provider_auth_module.request_dianxiaomi_provider_auth(
        cookie_path
    )

def get_ail_link(product_url):
    """获取阿里巴巴链接"""
    cookie_path = get_cookie_path()
    return _get_ali_link_module.get_ail_link(product_url, cookie_path)

def fetch_sku_code():
    """获取SKU代码"""
    cookie_path = get_cookie_path()
    return _fetch_sku_code_module.fetch_sku_code(cookie_path)

# 文件上传类函数
def upload_excel_to_dianxiaomi(file_path):
    """上传Excel文件到店小秘"""
    cookie_path = get_cookie_path()
    return _upload_excel_to_dianxiaomi_module.upload_excel_to_dianxiaomi(
        file_path, cookie_path
    )

# 数据抓取类函数
def run_scraper(days):
    """运行订单爬虫"""
    cookie_path = get_cookie_path()
    return _get_dxm_info_module.run_scraper(cookie_path, days)


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

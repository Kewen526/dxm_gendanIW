"""
API服务层 - 直接向店小秘服务器发送HTTP请求
所有功能集成在一个文件中，无需外部依赖
"""
import os
import json
import time
import requests
import re
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# ==================== 配置常量 ====================
COOKIE_URL = "https://ceshi-1300392622.cos.ap-beijing.myqcloud.com/dxm_cookie.json"
COOKIE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cookie_cache")
LOCAL_COOKIE_PATH = os.path.join(COOKIE_CACHE_DIR, "dxm_cookie.json")
COOKIE_CACHE_MINUTES = 30
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 3
RETRY_DELAY = 2


# ==================== Cookie管理 ====================
class _CookieManager:
    """Cookie管理器 - 自动下载和缓存"""

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
            except:
                pass

    def _is_cache_valid(self):
        """检查缓存是否有效"""
        if not os.path.exists(self.local_path):
            return False

        try:
            file_mtime = os.path.getmtime(self.local_path)
            file_time = datetime.fromtimestamp(file_mtime)
            if datetime.now() - file_time > timedelta(minutes=self.cache_minutes):
                return False

            with open(self.local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return 'cookies' in data and data['cookies']
        except:
            return False

    def _download_cookie(self):
        """下载Cookie"""
        for attempt in range(self.retry_times):
            try:
                response = requests.get(self.cookie_url, timeout=self.timeout)
                response.raise_for_status()
                cookie_data = response.json()

                if 'cookies' not in cookie_data:
                    continue

                with open(self.local_path, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, ensure_ascii=False, indent=2)
                return True
            except:
                if attempt < self.retry_times - 1:
                    time.sleep(self.retry_delay)
        return False

    def get_cookies_dict(self):
        """获取Cookies字典"""
        # 如果缓存无效则下载
        if not self._is_cache_valid():
            if not self._download_cookie():
                if not os.path.exists(self.local_path):
                    return None

        # 读取并转换Cookie
        try:
            with open(self.local_path, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)

            cookies = {}
            if 'cookies' in cookie_data:
                for cookie in cookie_data['cookies']:
                    cookies[cookie['name']] = cookie['value']
                return cookies
        except:
            return None


# 创建全局Cookie管理器
_cookie_manager = _CookieManager()


def _get_cookies():
    """获取Cookies（内部使用）"""
    return _cookie_manager.get_cookies_dict()


# ==================== API函数 - 直接发送HTTP请求 ====================

# 搜索类函数 (7个)

def search_dxm_product(search_value: str, shop_code: str, variant: str, debug: bool = False) -> Optional[str]:
    """
    搜索店小秘商品并返回符合条件的SKU名称

    Args:
        search_value: 搜索关键词
        shop_code: 店铺编码
        variant: 变体信息
        debug: 是否显示调试信息

    Returns:
        找到的SKU名称，未找到返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    if not BeautifulSoup:
        return None

    url = "https://www.dianxiaomi.com/dxmCommodityProduct/pageList.htm"

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '50',
        'searchType': '6',
        'searchValue': search_value,
        'productPxId': '1',
        'productPxSxId': '0',
        'productMode': '-1',
        'saleMode': '-1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        sku_elements = soup.find_all('span', class_='inline-block no-new-line maxW240 goodsSKUName white-space')

        exact_results = []
        contains_results = []

        for sku_element in sku_elements:
            sku_name = sku_element.get_text(strip=True)

            if not (sku_name.startswith(shop_code) or shop_code in sku_name):
                continue

            current_element = sku_element
            for i in range(15):
                current_element = current_element.parent
                if current_element is None:
                    break

                title_elements = current_element.find_all(attrs={'title': True})
                for title_element in title_elements:
                    title_text = title_element.get('title', '')
                    if title_text and variant.lower() in title_text.lower():
                        if sku_name.startswith(shop_code):
                            exact_results.append(sku_name)
                        else:
                            contains_results.append(sku_name)
                        break
                if exact_results or contains_results:
                    break

        if exact_results:
            return exact_results[0]
        elif contains_results:
            return contains_results[0]
        return None
    except:
        return None


def search_dxm_product_all(search_value: str, shop_code: str, variant: str, debug: bool = False) -> List[Dict[str, str]]:
    """
    搜索店小秘商品并返回所有符合条件的SKU

    Args:
        search_value: 搜索关键词
        shop_code: 店铺编码
        variant: 变体信息
        debug: 是否显示调试信息

    Returns:
        所有匹配结果的列表
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return []

    url = "https://www.dianxiaomi.com/dxmCommodityProduct/pageList.htm"

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '50',
        'searchType': '6',
        'searchValue': search_value,
        'productPxId': '1',
        'productPxSxId': '0',
        'productMode': '-1',
        'saleMode': '-1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        sku_elements = soup.find_all('span', class_='inline-block no-new-line maxW240 goodsSKUName white-space')

        exact_results = []
        contains_results = []

        for sku_element in sku_elements:
            sku_name = sku_element.get_text(strip=True)

            if not (sku_name.startswith(shop_code) or shop_code in sku_name):
                continue

            current_element = sku_element
            for i in range(15):
                current_element = current_element.parent
                if current_element is None:
                    break

                title_elements = current_element.find_all(attrs={'title': True})
                for title_element in title_elements:
                    title_text = title_element.get('title', '')
                    if title_text and variant.lower() in title_text.lower():
                        result = {'sku_name': sku_name, 'title': title_text}
                        if sku_name.startswith(shop_code):
                            exact_results.append(result)
                        else:
                            contains_results.append(result)
                        break

        return exact_results if exact_results else contains_results
    except:
        return []


def search_package(content: str) -> Optional[str]:
    """
    搜索包裹并提取运单号

    Args:
        content: 搜索内容（订单号）

    Returns:
        运单号，未找到返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/package/searchPackage.htm'

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1',
        'isRemoved': '-1',
        'isSearch': '1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        tracking_matches = re.findall(r"doTrack\('([^']+)'", response.text)
        return tracking_matches[0] if tracking_matches else None
    except:
        return None


def search_package_ids(content: str) -> List[str]:
    """
    搜索包裹并提取包裹ID列表

    Args:
        content: 搜索内容（订单号）

    Returns:
        包裹ID列表
    """
    cookies = _get_cookies()
    if not cookies:
        return []

    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'

    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1'
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()

        if result.get('code') != 0:
            return []

        package_list = result.get('data', {}).get('page', {}).get('list', [])
        return [str(pkg.get('id')) for pkg in package_list if pkg.get('id')]
    except:
        return []


def search_package2(content: str) -> Optional[str]:
    """
    搜索包裹并提取包裹号

    Args:
        content: 搜索内容（订单号）

    Returns:
        包裹号，未找到返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/package/searchPackage.htm'

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        match = re.search(r'data-packageNumber="([^"]+)"', response.text)
        return match.group(1) if match else None
    except:
        return None


def get_package_numbers(content: str) -> Optional[List[str]]:
    """
    获取包裹号列表

    Args:
        content: 搜索内容（订单号）

    Returns:
        包裹号列表，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = "https://www.dianxiaomi.com/package/searchPackage.htm"

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        matches = re.findall(r'data-packageNumber="([^"]+)"', response.text)
        return matches if matches else []
    except:
        return None


def get_dianxiaomi_order_id(content: str) -> List[Optional[str]]:
    """
    搜索店小秘订单并获取订单ID和仓库ID

    Args:
        content: 搜索内容（订单号）

    Returns:
        [order_ids, storage_id] 列表，失败返回[None, None]
    """
    cookies = _get_cookies()
    if not cookies:
        return [None, None]

    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'

    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all?go=m1-1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'history': '',
        'searchType': 'orderId',
        'content': content,
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

    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()

        if result.get('code') != 0:
            return [None, None]

        order_ids = result.get('data', {}).get('orderIds')
        page_list = result.get('data', {}).get('page', {}).get('list', [])
        storage_id = page_list[0].get('storageId') if page_list else None

        return [order_ids, str(storage_id) if storage_id else None]
    except:
        return [None, None]


# 商品管理类函数 (3个)

def add_product_to_dianxiaomi(name: str, name_en: str, price: str, url: str, custom_zn: str,
                               custom_en: str, sb_weight: str, sb_price: str, supplier: str,
                               main_supplier: str, img_url: str, id: str, pid_pair: str,
                               vid_pair: str, shop_id_pair: str, sku: str) -> Optional[str]:
    """
    批量添加商品到店小秘

    Args:
        name: 中文名称
        name_en: 英文名称
        price: 价格
        url: 商品URL
        custom_zn: 海关中文名
        custom_en: 海关英文名
        sb_weight: 申报重量
        sb_price: 申报价格
        supplier: 供应商ID（JSON字符串）
        main_supplier: 主供应商ID
        img_url: 图片URL
        id: 商品ID
        pid_pair: 产品配对ID
        vid_pair: 变体配对ID
        shop_id_pair: 店铺配对ID
        sku: SKU编码

    Returns:
        响应文本，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url_endpoint = 'https://www.dianxiaomi.com/dxmCommodityProduct/addBatchProductInfo.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    product_info = {
        'name': name,
        'nameEn': name_en,
        'status': '1',
        'price': price,
        'url': url,
        'customZn': custom_zn,
        'customEn': custom_en,
        'sbWeight': sb_weight,
        'sbPrice': sb_price,
        'supplier': supplier,
        'mainSupplier': main_supplier,
        'imgUrl': img_url,
        'id': id,
        'pidPair': pid_pair,
        'vidPair': vid_pair,
        'shopIdPair': shop_id_pair,
        'ptPair': '',
        'sku': sku
    }

    data = {
        'productInfos': json.dumps([product_info])
    }

    try:
        response = requests.post(url_endpoint, headers=headers, cookies=cookies, data=data, timeout=30)
        return response.text
    except:
        return None


def add_product_sg_dxm(name: str, name_en: str, sku_code: str, sku: str, price: str,
                       source_url: str, img_url: str, is_used: str, product_type: str,
                       product_status: str, name_cn_bg: str, name_en_bg: str, weight_bg: str,
                       price_bg: str, danger_des_bg: str, warehouse_id_list: List[str],
                       supplier_id: str, is_main: str) -> Dict[str, Any]:
    """
    添加商品到店小秘（新加坡版本）

    Args:
        name: 商品名称
        name_en: 英文名称
        sku_code: SKU代码
        sku: SKU编码
        price: 价格
        source_url: 来源URL
        img_url: 图片URL
        is_used: 是否二手
        product_type: 商品类型
        product_status: 商品状态
        name_cn_bg: 报关中文名
        name_en_bg: 报关英文名
        weight_bg: 报关重量
        price_bg: 报关价格
        danger_des_bg: 危险品描述
        warehouse_id_list: 仓库ID列表
        supplier_id: 供应商ID
        is_main: 是否主供应商

    Returns:
        包含success和message的字典
    """
    cookies = _get_cookies()
    if not cookies:
        return {'success': False, 'message': '获取Cookie失败'}

    url = 'https://www.dianxiaomi.com/dxmCommodityProduct/addCommodityProduct.json'

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm?id=&type=0&editOrCopy=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    dxm_commodity_product = {
        'name': name,
        'nameEn': name_en,
        'skuCode': sku_code,
        'sku': sku,
        'price': price,
        'sourceUrl': source_url,
        'imgUrl': img_url,
        'isUsed': is_used,
        'type': product_type,
        'status': product_status
    }

    dxm_product_customs = {
        'nameCn': name_cn_bg,
        'nameEn': name_en_bg,
        'weight': weight_bg,
        'price': price_bg,
        'dangerDes': danger_des_bg
    }

    supplier_product_relation = [{
        'supplierId': supplier_id,
        'isMain': is_main
    }]

    payload = {
        'dxmCommodityProduct': json.dumps(dxm_commodity_product),
        'dxmProductCustoms': json.dumps(dxm_product_customs),
        'warehouseIdList': json.dumps(warehouse_id_list),
        'supplierProductRelationMapList': json.dumps(supplier_product_relation),
        'dxmProductPacks': json.dumps([]),
        'obj': json.dumps({
            'dxmCommodityProduct': dxm_commodity_product,
            'dxmProductCustoms': dxm_product_customs,
            'warehouseIdList': warehouse_id_list,
            'supplierProductRelationMapList': supplier_product_relation,
            'dxmProductPacks': []
        }),
        'pid': '',
        'vid': '',
        'orderStatus': '',
        'shopId': '',
        'pt': '',
        'orderId': '',
        'orderWarehoseId': '',
        'orderCount': ''
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=payload, timeout=30)
        result = response.json()
        return {'success': True, 'message': result}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def add_product_to_warehouse(sku: str) -> Optional[Dict[str, Any]]:
    """
    添加商品到仓库

    Args:
        sku: SKU编码

    Returns:
        API响应字典，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/dxmWarehoseProduct/batchAddWareHoseProductFromPair.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    objs = [{'sku': sku}]

    data = {
        'objs': json.dumps(objs),
        'warehoseIds': '54269603053732630,54269606228755206,54269608346849030,54269609676210950'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        result = response.json()
        return result if result.get('ret') == '1' else None
    except:
        return None


# 订单操作类函数 (5个)

def set_dianxiaomi_comment(package_ids: List[str]) -> Optional[Dict[str, Any]]:
    """
    设置店小秘订单备注（黄色标记）

    Args:
        package_ids: 包裹ID列表

    Returns:
        API响应字典，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/order/batchSetCustomComment.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    if isinstance(package_ids, list):
        package_ids_str = ','.join(package_ids)
    else:
        package_ids_str = package_ids

    data = {
        'isGreen': '0',
        'isYellow': '1',
        'isOrange': '0',
        'isRed': '0',
        'isViolet': '0',
        'isBlue': '0',
        'cornflowerBlue': '0',
        'pink': '0',
        'teal': '0',
        'turquoise': '0',
        'packageIds': package_ids_str,
        'history': ''
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        return response.json()
    except:
        return None


def batch_commit_platform_packages(package_ids: List[str]) -> Optional[requests.Response]:
    """
    批量提交包裹到平台

    Args:
        package_ids: 包裹ID列表

    Returns:
        响应对象，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/package/batchCommitPlatform.json'

    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m10201',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    if isinstance(package_ids, list):
        package_ids_str = ','.join(package_ids)
    else:
        package_ids_str = package_ids

    data = {
        'packageIds': package_ids_str
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        return response
    except:
        return None


def batch_set_voided(package_ids: List[str]) -> Optional[Dict[str, Any]]:
    """
    批量作废包裹

    Args:
        package_ids: 包裹ID列表

    Returns:
        API响应字典，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/package/batchSetVoided.json'

    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m10201',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    if isinstance(package_ids, list):
        package_ids_str = ','.join(package_ids)
    else:
        package_ids_str = package_ids

    data = {
        'packageIds': package_ids_str
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        result = response.json()

        # 检查登录页面
        if 'login' in response.text.lower():
            return None

        # 验证成功
        if (result.get('success') or
            result.get('code') == 200 or
            result.get('status') == 'success'):
            return result
        return None
    except:
        return None


def update_dianxiaomi_warehouse(package_ids: List[str], storage_id: str) -> Optional[Any]:
    """
    更新店小秘订单仓库

    Args:
        package_ids: 包裹ID列表
        storage_id: 仓库ID

    Returns:
        API响应（字典或文本），失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/package/batchUpdateUnProcessWarehouse.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    if isinstance(package_ids, list):
        package_ids_str = ','.join(package_ids)
    else:
        package_ids_str = package_ids

    data = {
        'packageIds': package_ids_str,
        'storageId': storage_id
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        try:
            return response.json()
        except:
            return response.text
    except:
        return None


def update_dianxiaomi_provider_batch(package_ids: List[str], auth_id: str) -> Optional[Dict[str, Any]]:
    """
    批量更新订单供应商

    Args:
        package_ids: 包裹ID列表
        auth_id: 授权供应商ID

    Returns:
        API响应字典，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/order/batchUpdateProvider.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    if isinstance(package_ids, list):
        package_ids_str = ','.join(package_ids)
    else:
        package_ids_str = package_ids

    data = {
        'packageIds': package_ids_str,
        'isAll': '0',
        'authId': auth_id,
        'orderState': 'approved',
        'saveType': '1'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        return response.json()
    except:
        return None


# 信息查询类函数 (5个)

def get_supplier_ids(supplier_name: str) -> List[str]:
    """
    获取供应商ID列表

    Args:
        supplier_name: 供应商名称

    Returns:
        供应商ID列表
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return []

    url = 'https://www.dianxiaomi.com/dxmSupplier/selectSupplierPageList.htm'

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'searchSelectType': '1',
        'searchSelectValue': supplier_name,
        'searchSelectSupplyType': '2'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        supplier_ids = []
        links = soup.find_all('a', onclick=True)

        for link in links:
            onclick_attr = link.get('onclick', '')
            if 'addSupplierSelectMethod' in onclick_attr:
                match = re.search(r"addSupplierSelectMethod\('(\d+)'", onclick_attr)
                if match:
                    supplier_ids.append(match.group(1))

        return supplier_ids
    except:
        return []


def get_shop_dict_with_cookie() -> Dict[str, str]:
    """
    获取店铺字典

    Returns:
        店铺字典 {shop_id: numeric_value, ...}
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return {}

    url = 'https://www.dianxiaomi.com/dxmTempWishPairProduct/listOrder.htm'

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'pageNo': '1',
        'pageSize': '100',
        'sku': '',
        'zt': 'order'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        shop_dict = {}
        links = soup.find_all('a', onclick=True)

        for link in links:
            onclick_attr = link.get('onclick', '')
            if 'selShopPair' in onclick_attr:
                shop_id = link.get_text(strip=True)
                match = re.search(r"selShopPair\('(\d+)'", onclick_attr)
                if match:
                    shop_dict[shop_id] = match.group(1)

        return shop_dict
    except:
        return {}


def request_dianxiaomi_provider_auth() -> Dict[str, str]:
    """
    请求店小秘供应商授权列表

    Returns:
        供应商字典 {provider_name: provider_id, ...}
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return {}

    url = 'https://www.dianxiaomi.com/providerAuth/getList.htm'

    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'code': '0'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        provider_dict = {}
        options = soup.find_all('option')

        # 跳过第一个选项（通常是"请选择"）
        for option in options[1:]:
            provider_name = option.get_text(strip=True)
            provider_id = option.get('value', '')
            if provider_name and provider_id:
                provider_dict[provider_name] = provider_id

        return provider_dict
    except:
        return {}


def get_ail_link(product_url: str) -> Optional[str]:
    """
    获取阿里巴巴商品链接信息

    Args:
        product_url: 阿里巴巴商品URL

    Returns:
        商品名称，失败返回None
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return None

    url = 'https://www.dianxiaomi.com/alibabaProduct/getProductByUrl.htm'

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'url': product_url,
        'fromWhere': 'pairProduct'
    }

    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        name_element = soup.find('td', class_='nameBox')
        if name_element:
            return name_element.get_text(strip=True)
        return None
    except:
        return None


def fetch_sku_code() -> Optional[str]:
    """
    获取SKU代码

    Returns:
        SKU代码，失败返回None
    """
    cookies = _get_cookies()
    if not cookies or not BeautifulSoup:
        return None

    url = 'https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm?id=&type=0&editOrCopy=0'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')

        sku_element = soup.find('span', id='skuCode')
        if sku_element:
            return sku_element.get_text(strip=True)
        return None
    except:
        return None


# 文件上传类函数 (1个)

def upload_excel_to_dianxiaomi(file_path: str) -> Optional[str]:
    """
    上传Excel文件到店小秘

    Args:
        file_path: Excel文件路径

    Returns:
        上传成功返回UUID，失败返回None
    """
    cookies = _get_cookies()
    if not cookies:
        return None

    url = 'https://www.dianxiaomi.com/excel/userImport.json'

    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/package/toAdd.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # Excel列映射配置
    excel_config = {
        "name": "用户导入订单",
        "order": "1",
        "type": "1",
        "excelTransformList": [
            {"key": "platformOrderId", "userKey": "平台订单号", "index": 0},
            {"key": "shopId", "userKey": "店铺", "index": 1},
            {"key": "country", "userKey": "国家", "index": 2},
            {"key": "province", "userKey": "省", "index": 3},
            {"key": "city", "userKey": "市", "index": 4},
            {"key": "address1", "userKey": "地址1", "index": 5},
            {"key": "address2", "userKey": "地址2", "index": 6},
            {"key": "zipCode", "userKey": "邮编", "index": 7},
            {"key": "name", "userKey": "收件人", "index": 8},
            {"key": "phone", "userKey": "电话", "index": 9},
            {"key": "sku", "userKey": "SKU", "index": 10},
            {"key": "quantity", "userKey": "数量", "index": 11}
        ]
    }

    try:
        with open(file_path, 'rb') as f:
            files = {
                'FileData': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'excelTransformConfig': json.dumps(excel_config)
            }

            response = requests.post(url, headers=headers, cookies=cookies, files=files, data=data, timeout=60)
            result = response.json()

            if result.get('code') == 0 and result.get('msg') == 'Successful':
                return result.get('data', {}).get('uuid')
            return None
    except:
        return None


# 数据抓取类函数 (1个)

def run_scraper(days: int) -> List[Dict[str, Any]]:
    """
    运行订单数据爬虫

    Args:
        days: 抓取最近几天的数据

    Returns:
        订单数据列表
    """
    cookies = _get_cookies()
    if not cookies:
        return []

    url = 'https://www.dianxiaomi.com/api/package/list.json'

    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

    headers = {
        'authority': 'www.dianxiaomi.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all?go=m1-1',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    responses = []
    current_time = datetime.now()

    for day_offset in range(days):
        target_date = current_time - timedelta(days=day_offset)
        start_time = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)

        data = {
            'pageNo': '1',
            'pageSize': '300',
            'shopId': '-1',
            'state': '',
            'platform': '',
            'isSearch': '1',
            'searchType': 'orderId',
            'authId': '-1',
            'startTime': str(start_timestamp),
            'endTime': str(end_timestamp),
            'country': '',
            'orderField': 'order_create_time',
            'isVoided': '-1',
            'isRemoved': '-1',
            'ruleId': '-1',
            'sysRule': '',
            'applyType': '',
            'applyStatus': '',
            'printJh': '-1',
            'printMd': '-1',
            'commitPlatform': '',
            'productStatus': '',
            'jhComment': '-1',
            'storageId': '0',
            'isOversea': '-1',
            'isFree': '-1',
            'isBatch': '-1',
            'history': '',
            'custom': '-1',
            'timeOut': '0',
            'refundStatus': '0',
            'buyerAccount': '',
            'forbiddenStatus': '-1',
            'forbiddenReason': '0',
            'behindTrack': '-1',
            'orderId': '',
            'axios_cancelToken': 'true'
        }

        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            result = response.json()

            if result.get('code') == 0:
                order_list = result.get('data', {}).get('page', {}).get('list', [])
                # 过滤在时间范围内的订单
                filtered_orders = [
                    order for order in order_list
                    if start_timestamp <= order.get('orderCreateTime', 0) <= end_timestamp
                ]
                if filtered_orders:
                    responses.append({
                        'date': target_date.strftime('%Y-%m-%d'),
                        'orders': filtered_orders,
                        'count': len(filtered_orders)
                    })
        except:
            continue

    return responses


# ==================== 服务类包装器 ====================
class DianxiaomiService:
    """店小秘服务类 - 提供面向对象的接口"""

    def search_product(self, search_value, shop_code, variant, debug=False):
        """搜索商品（单个结果）"""
        return search_dxm_product(search_value, shop_code, variant, debug)

    def search_product_all(self, search_value, shop_code, variant, debug=False):
        """搜索商品（所有结果）"""
        return search_dxm_product_all(search_value, shop_code, variant, debug)

    def search_package(self, content):
        """搜索包裹"""
        return search_package(content)

    def search_package_ids(self, content):
        """搜索包裹IDs"""
        return search_package_ids(content)

    def search_package2(self, content):
        """搜索包裹方法2"""
        return search_package2(content)

    def get_package_numbers(self, content):
        """获取包裹号"""
        return get_package_numbers(content)

    def get_dianxiaomi_order_id(self, content):
        """获取店小秘订单ID"""
        return get_dianxiaomi_order_id(content)

    def add_product(self, data):
        """添加商品"""
        return add_product_to_dianxiaomi(
            data['name'], data['name_en'], data['price'],
            data['url'], data['custom_zn'], data['custom_en']
        )

    def add_product_sg(self, data):
        """添加新加坡商品"""
        return add_product_sg_dxm(
            data['name'], data['name_en'], data['sku_code'],
            data['sku'], data['price'], data['url']
        )

    def add_product_to_warehouse(self, sku):
        """添加商品到仓库"""
        return add_product_to_warehouse(sku)

    def set_comment(self, package_ids):
        """设置备注"""
        return set_dianxiaomi_comment(package_ids)

    def batch_commit(self, package_ids):
        """批量提交"""
        return batch_commit_platform_packages(package_ids)

    def batch_void(self, package_ids):
        """批量作废"""
        return batch_set_voided(package_ids)

    def update_warehouse(self, package_ids, storage_id):
        """更新仓库"""
        return update_dianxiaomi_warehouse(package_ids, storage_id)

    def update_provider(self, package_ids, auth_id):
        """更新供应商"""
        return update_dianxiaomi_provider_batch(package_ids, auth_id)

    def get_supplier_ids(self, supplier_name):
        """获取供应商IDs"""
        return get_supplier_ids(supplier_name)

    def get_shop_dict(self):
        """获取店铺字典"""
        return get_shop_dict_with_cookie()

    def get_provider_list(self):
        """获取供应商列表"""
        return request_dianxiaomi_provider_auth()

    def get_ali_link(self, product_url):
        """获取阿里链接"""
        return get_ail_link(product_url)

    def fetch_sku_code(self):
        """获取SKU代码"""
        return fetch_sku_code()

    def upload_excel(self, file_path):
        """上传Excel文件"""
        return upload_excel_to_dianxiaomi(file_path)

    def run_scraper(self, days):
        """运行爬虫"""
        return run_scraper(days)


# 全局服务实例
_service = None


def get_service():
    """获取服务实例的便捷函数"""
    global _service
    if _service is None:
        _service = DianxiaomiService()
    return _service


if __name__ == "__main__":
    # 测试
    result = get_package_numbers("LYS-SP00001-15fe2a-c9-2156-A")
    print(f"结果: {result}")

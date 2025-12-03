# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

def main(args):
    pass
import requests
import json
import os

def load_cookies_from_file(file_path):
    """
    从JSON文件加载Cookie并转换为requests库所需的格式
    
    Args:
        file_path (str): Cookie JSON文件路径
    
    Returns:
        dict: 处理后的Cookie字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # 转换为requests库需要的格式
        cookies_dict = {}
        if "cookies" in cookie_data and isinstance(cookie_data["cookies"], list):
            for cookie in cookie_data["cookies"]:
                if "name" in cookie and "value" in cookie:
                    cookies_dict[cookie["name"]] = cookie["value"]
        
        print(f"已从 {file_path} 加载 {len(cookies_dict)} 个Cookie")
        return cookies_dict
    except Exception as e:
        print(f"加载Cookie文件出错: {str(e)}")
        return None

def add_product_to_dianxiaomi(
    name, 
    name_en, 
    sku_code, 
    sku, 
    price, 
    source_url, 
    img_url, 
    is_used, 
    product_type, 
    product_status,
    
    name_cn_bg, 
    name_en_bg, 
    weight_bg, 
    price_bg, 
    danger_des_bg,
    
    warehouse_id_list, 
    supplier_id, 
    is_main,
    
    cookie_file_path
):
    """
    向点小秘系统添加商品
    
    Args:
        name (str): 商品中文名称
        name_en (str): 商品英文名称
        sku_code (str): 商品编码
        sku (str): 系统SKU
        price (str): 商品销售价格
        source_url (str): 商品来源链接
        img_url (str): 商品主图URL
        is_used (int): 是否启用(1=启用,0=禁用)
        product_type (str): 商品类型代码
        product_status (str): 商品状态(1=上架,0=下架)
        name_cn_bg (str): 中文报关名称
        name_en_bg (str): 英文报关名称
        weight_bg (str): 报关重量(克)
        price_bg (str): 报关价格
        danger_des_bg (str): 危险品描述(0=非危险品)
        warehouse_id_list (str): 逗号分隔的仓库ID列表
        supplier_id (str): 供应商ID
        is_main (int): 是否主要供应商(1=是,0=否)
        cookie_file_path (str): Cookie JSON文件路径
        
    Returns:
        dict: 响应结果，包含成功状态和系统返回信息
    """
    # 请求URL - 点小秘添加商品的API端点
    url = 'https://www.dianxiaomi.com/dxmCommodityProduct/addCommodityProduct.json'

    # 请求头
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm?id=&type=0&editOrCopy=0',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # 加载Cookie
    cookies = load_cookies_from_file(cookie_file_path)
    if cookies is None:
        return {"success": False, "message": f"无法加载Cookie文件: {cookie_file_path}"}

    # 构建商品数据结构
    product_data = {
        # 商品基本信息对象
        "dxmCommodityProduct": json.dumps({
            "productId": "",
            "name": name,
            "nameEn": name_en,
            "skuCode": sku_code,
            "sku": sku,
            "productVariationStr": "",
            "sbmId": "",
            "agentId": "0",
            "developmentId": "0",
            "salesId": "0",
            "weight": "",
            "allowWeightError": "",
            "price": price,
            "sourceUrl": source_url,
            "imgUrl": img_url,
            "isUsed": is_used,
            "fullCid": "",
            "productType": product_type,
            "length": 0,
            "width": 0,
            "height": 0,
            "qcType": 0,
            "productStatus": product_status,
            "childIds": "",
            "childNums": "",
            "processFee": 0,
            "qcContent": "",
            "qcImgStr": "",
            "qcImgNum": 0,
            "groupState": "0"
        }),
        
        # 商品海关申报信息
        "dxmProductCustoms": json.dumps({
            "nameCnBg": name_cn_bg,
            "nameEnBg": name_en_bg,
            "weightBg": weight_bg,
            "priceBg": price_bg,
            "materialBg": "",
            "purposeBg": "",
            "hgbmBg": "",
            "dangerDesBg": danger_des_bg
        }),
        
        # 仓库ID列表
        "warehouseIdList": warehouse_id_list,
        
        # 供应商关系列表
        "supplierProductRelationMapList": json.dumps([
            {
                "supplierId": supplier_id,
                "isMain": is_main
            }
        ]),
        
        # 商品包装信息
        "dxmProductPacks": "[]"
    }

    # 构建完整请求数据
    data = {
        "obj": json.dumps(product_data),
        "pid": "",
        "vid": "",
        "orderStatus": "",
        "shopId": "-1",
        "pt": "-1",
        "orderId": "",
        "orderWarehoseId": "-1",
        "orderCount": "0"
    }
    
    # 打印请求信息摘要
    print(f"准备添加商品: {name} (SKU: {sku_code})")
    print(f"价格: {price}, 报关价格: {price_bg}")
    
    try:
        # 发送POST请求
        response = requests.post(
            url=url,
            headers=headers,
            cookies=cookies,
            data=data
        )
        
        # 检查请求是否成功
        if response.status_code == 200:
            print("请求成功，状态码:", response.status_code)
            return response.json()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return {"success": False, "message": f"请求失败，状态码: {response.status_code}"}
            
    except Exception as e:
        print(f"发送请求时出错: {str(e)}")
        return {"success": False, "message": f"发送请求时出错: {str(e)}"}


def save_cookies_to_file(cookies, file_path):
    """
    将Cookie保存到本地JSON文件
    
    Args:
        cookies (dict): Cookie字典
        file_path (str): 保存路径
    
    Returns:
        bool: 是否保存成功
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=2, ensure_ascii=False)
        print(f"Cookie已保存到: {file_path}")
        return True
    except Exception as e:
        print(f"保存Cookie失败: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    # 必须提供所有参数的示例
    result = add_product_to_dianxiaomi(
        # 商品基本信息
        name="女士休闲鞋",
        name_en="Women's Casual Shoes",
        sku_code="WCS12345",
        sku="custom-sku-wcs12345",
        price="25.99",
        source_url="https://detail.1688.com/offer/123456789.html",
        img_url="https://example.com/image.jpg",
        is_used=1,
        product_type="100",
        product_status="1",
        
        # 海关申报信息
        name_cn_bg="女式休闲平底鞋",
        name_en_bg="Women's Casual Flat Shoes",
        weight_bg="350",
        price_bg="10",
        danger_des_bg="0",
        
        # 仓库和供应商信息
        warehouse_id_list="4618738,4659184,6623995",
        supplier_id="54280071574247736",
        is_main=1,
        
        # Cookie文件路径
        cookie_file_path="cookie.json"
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
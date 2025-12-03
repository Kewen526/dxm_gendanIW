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
import json
import requests
import os

def load_cookies_from_file(file_path):
    """从本地文件加载cookies"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 将cookies转换为requests库需要的格式（字典形式）
        cookies_dict = {}
        for cookie in data['cookies']:
            cookies_dict[cookie['name']] = cookie['value']
        
        return cookies_dict
    except FileNotFoundError:
        print(f"错误: 找不到cookie文件 '{file_path}'")
        exit(1)
    except json.JSONDecodeError:
        print(f"错误: cookie文件 '{file_path}' 不是有效的JSON格式")
        exit(1)
    except Exception as e:
        print(f"错误: 读取cookie文件时出现问题: {str(e)}")
        exit(1)

def add_product_to_dianxiaomi(
    cookies_file,      
    name,               
    name_en,            
    price,              
    url,                
    custom_zn,        
    custom_en,         
    sb_weight,         
    sb_price,           
    supplier,           
    main_supplier,      
    img_url,            
    id,                
    pid_pair,           
    vid_pair,           
    shop_id_pair,
    sku        
):
    """向店小秘添加商品信息"""
    # 从文件加载cookies
    cookies = load_cookies_from_file(cookies_file)
    
    url_api = 'https://www.dianxiaomi.com/dxmCommodityProduct/addBatchProductInfo.json'
    
    # 请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 构建商品信息
    product_data = {
        "name": name,               # 商品中文名称
        "nameEn": name_en,          # 商品英文名称
        "status": "1",              # 商品状态(1表示启用)
        "sbm": "",                  # 商品识别码(为空)
        "weight": "0",              # 商品重量
        "price": price,             # 商品价格
        "length": "0.00",           # 商品长度
        "width": "0.00",            # 商品宽度
        "height": "0.00",           # 商品高度
        "url": url,                 # 商品来源链接
        "remark": "",               # 商品备注
        "customZn": custom_zn,      # 中文报关信息
        "customEn": custom_en,      # 英文报关信息
        "sbWeight": sb_weight,      # 预估重量
        "sbPrice": sb_price,        # 申报价值
        "customMaterial": "",       # 材质信息
        "customPurpose": "",        # 用途信息
        "customCode": "",           # 海关编码
        "dangerous": "0",           # 是否危险品(0表示否)
        "explain": 0,               # 说明字段
        "supplier": supplier,       # 供应商ID列表
        "mainSupplier": main_supplier,  # 主要供应商ID
        "develop": "0",             # 开发状态
        "procure": "0",             # 采购状态
        "sales": "0",               # 销售状态
        "dxmProductPacks": "",      # 商品包装信息
        "sku": sku,       # 商品SKU编码
        "imgUrl": img_url,          # 商品图片URL
        "id": id,                   # 店小秘系统内商品ID
        "pidPair": pid_pair,        # 平台商品ID
        "vidPair": vid_pair,        # 变体ID
        "shopIdPair": shop_id_pair, # 店铺ID
        "ptPair": "shopify",        # 平台类型(此处为Shopify)
        "sfOrder": "order"          # 排序方式
    }
    
    # 将商品数据转为JSON字符串并包装在数组中
    product_json = json.dumps([product_data], ensure_ascii=False)
    
    # 构建完整的请求数据
    data = {
        'productInfos': product_json
    }
    
    # 发送POST请求
    response = requests.post(
        url=url_api,
        headers=headers,
        cookies=cookies,
        data=data
    )
    print("\n状态码:", response.status_code)
    print("响应内容:")
    print(response.text)
    return response.text

if __name__ == "__main__":
    # 获取cookie文件路径
    cookies_file = input("请输入cookie文件路径(例如: C:\\path\\to\\cookie.json): ")
    
    # 验证文件是否存在
    if not os.path.exists(cookies_file):
        print(f"错误: 文件 '{cookies_file}' 不存在")
        exit(1)
    
    # 获取用户输入的商品信息
    name = input("请输入商品中文名称: ") or "商品名称"
    name_en = input("请输入商品英文名称: ") or "name"
    price = input("请输入商品价格: ") or "1"
    url = input("请输入商品来源链接: ") or ""
    custom_zn = input("请输入中文报关信息: ") or "中文报关"
    custom_en = input("请输入英文报关信息: ") or "Customs Declaration in English"
    sb_weight = input("请输入预估重量: ") or "3"
    sb_price = input("请输入申报价值: ") or "4"
    supplier = input("请输入供应商ID列表(格式如[\"12345\"]): ") or "[\"54280071577953030\"]"
    main_supplier = input("请输入主要供应商ID: ") or "54280071577953030"
    img_url = input("请输入商品图片URL: ") or ""
    id = input("请输入店小秘系统内商品ID: ") or ""
    pid_pair = input("请输入平台商品ID: ") or ""
    vid_pair = input("请输入变体ID: ") or ""
    shop_id_pair = input("请输入店铺ID: ") or ""
    
    # 发送请求
    response = add_product_to_dianxiaomi(
        cookies_file,
        name,
        name_en,
        price,
        url,
        custom_zn,
        custom_en,
        sb_weight,
        sb_price,
        supplier,
        main_supplier,
        img_url,
        id,
        pid_pair,
        vid_pair,
        shop_id_pair
    )
    
    # 打印响应结果
    print("\n状态码:", response.status_code)
    print("响应内容:")
    print(response.text)
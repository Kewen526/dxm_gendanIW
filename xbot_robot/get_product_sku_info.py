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
from urllib import parse
import json
 
def safe_json_loads(json_str, default=None):
    """安全地解析JSON字符串，处理None或空字符串的情况"""
    if json_str is None or json_str == '':
        return default if default is not None else []
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return default if default is not None else []

def get_order_details(order_id):
    request_url = 'http://47.95.157.46:8520/api/order_skuinfo'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id
    }
    data = parse.urlencode(form_data, True)
   
    response = requests.post(request_url, headers=headers, data=data)
   
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
        if response_json.get('success') and response_json.get('data'):
            result = {}
            order_data = response_json['data'][0]
           
            # 解析customer_english_title
            customer_english_title = safe_json_loads(order_data.get('customer_english_title'))
            result['customer_english_title'] = customer_english_title
           
            # 处理product_sku_info - 如果为None或空字符串，创建与customer_english_title长度相同的空列表
            product_sku_info = safe_json_loads(order_data.get('product_sku_info'))
            if not product_sku_info:  # 如果为空列表
                product_sku_info = ['' for _ in range(len(customer_english_title))]
            result['product_sku_info'] = product_sku_info
           
            # 处理status - 确保其长度与product_sku_info相同
            parsed_status = safe_json_loads(order_data.get('status'))
            # 如果status是[""]且product_sku_info长度不同，调整status
            if (len(parsed_status) == 1 and parsed_status[0] == '') and len(parsed_status) != len(result['product_sku_info']):
                result['status'] = ['' for _ in range(len(result['product_sku_info']))]
            else:
                result['status'] = parsed_status
           
            # 提取其余参数
            result['stop_product_variant'] = safe_json_loads(order_data.get('stop_product_variant'))
            result['ali_link'] = safe_json_loads(order_data.get('ali_link'))
            result['shop_num'] = order_data.get('shop_num', '')
            result['product_img'] = safe_json_loads(order_data.get('product_img'))
           
            return result
   
    return None
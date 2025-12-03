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

def load_cookies(cookies_file_path):
    """从JSON文件加载cookies"""
    try:
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 检查文件是否有预期的结构
        if 'cookies' in data:
            return {cookie['name']: cookie['value'] for cookie in data['cookies']}
        else:
            # 尝试直接格式(假设文件是cookies的列表或字典)
            return data
    except Exception as e:
        print(f"加载cookies时出错: {e}")
        return {}

def get_alibaba_product(cookies_file, urls, sku_ids_alibaba):
    """
    向dianxiaomi.com发送请求以获取产品信息
    
    参数:
        cookies_file: 包含cookies的JSON文件路径
        urls: 来自1688.com的产品URL
        sku_ids_alibaba: 以逗号分隔的SKU ID列表
    
    返回:
        API的响应
    """
    # 加载cookies
    cookies = load_cookies(cookies_file)
    
    # 定义请求URL
    url = 'https://www.dianxiaomi.com/alibabaProduct/getProductByUrls.json'
    
    # 定义请求头
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
    
    # 准备请求数据
    data = {
        'urls': urls,
        'singleOrBatch': '1',
        'skuIdsAlibaba': sku_ids_alibaba
    }
    
    # 发送请求
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    
    return response
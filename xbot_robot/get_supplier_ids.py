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
from bs4 import BeautifulSoup
import re

def get_supplier_ids(cookies_file_path, supplier_name):
    """
    从点小秘网站获取供应商ID
    
    参数:
        cookies_file_path (str): 包含cookies的JSON文件路径
        supplier_name (str): 供应商名称，例如 '广州世美如诗服饰商贸有限公司'
        
    返回:
        list: 供应商ID列表
    """
    try:
        # 加载cookies
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        # 将cookies转换为字典格式
        cookies = {}
        for cookie in cookies_data.get('cookies', []):
            if 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
        
        # 设置请求头
        headers = {
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # 设置请求数据
        data = {
            'searchSelectType': '1',
            'searchSelectValue': supplier_name,
            'searchSelectSupplyType': '2'
        }
        
        # 发送POST请求
        url = 'https://www.dianxiaomi.com/dxmSupplier/selectSupplierPageList.htm'
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}")
        
        # 解析HTML响应
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有包含addSupplierSelectMethod的链接
        supplier_ids = []
        links = soup.find_all('a', attrs={'onclick': re.compile(r'addSupplierSelectMethod\(')})
        
        for link in links:
            onclick_attr = link.get('onclick', '')
            # 提取addSupplierSelectMethod中的ID
            match = re.search(r"addSupplierSelectMethod\('(\d+)'", onclick_attr)
            if match:
                supplier_id = match.group(1)
                supplier_ids.append(supplier_id)
        
        return supplier_ids
    
    except Exception as e:
        import traceback
        error_msg = f"处理过程中出错: {e}\n{traceback.format_exc()}"
        raise Exception(error_msg)
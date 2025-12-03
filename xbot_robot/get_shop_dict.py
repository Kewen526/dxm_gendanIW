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
import re
from bs4 import BeautifulSoup

def get_shop_dict_with_cookie(cookie_file_path):
    """
    使用本地cookie文件发送请求，并返回店铺ID与数字值的字典
    
    参数:
    cookie_file_path (str): JSON格式cookie文件的路径
    
    返回:
    dict: 包含店铺ID(键)和对应值的字典
    """
    # 1. 读取JSON格式的cookie文件
    with open(cookie_file_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    # 从文件中提取cookie信息
    cookies = cookie_data.get('cookies', [])
    
    # 将cookie列表转换为字典格式
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']
    
    # 2. 设置请求头
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 请求数据
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'sku': '',
        'zt': 'order'
    }
    
    # 3. 发送POST请求
    url = 'https://www.dianxiaomi.com/dxmTempWishPairProduct/listOrder.htm'
    response = requests.post(url, headers=headers, cookies=cookie_dict, data=data)
    
    # 检查响应状态
    if response.status_code != 200:
        raise Exception(f"请求失败，状态码: {response.status_code}")
    
    # 4. 解析响应内容
    html_content = response.text
    
    # 创建BeautifulSoup对象解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 找到所有带有onclick="selShopPair"的链接
    links = soup.find_all('a', attrs={'onclick': re.compile(r'selShopPair\(')})
    
    # 创建字典存储结果
    shop_dict = {}
    
    # 遍历链接提取信息
    for link in links:
        # 获取店铺ID (链接文本)
        shop_id = link.text.strip()
        
        # 提取onclick属性中的数字参数
        onclick_attr = link['onclick']
        match = re.search(r"selShopPair\('(\d+)'", onclick_attr)
        if match:
            value = match.group(1)
            # 将店铺ID作为键名，数字作为键值
            shop_dict[shop_id] = value
    
    return shop_dict
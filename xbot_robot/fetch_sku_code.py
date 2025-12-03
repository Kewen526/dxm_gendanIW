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
from bs4 import BeautifulSoup

def fetch_sku_code(cookie_file_path):
    # 从JSON文件加载cookies
    with open(cookie_file_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    # 提取URL和cookies
    url = "https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm?id=&type=0&editOrCopy=0"
    
    # 将cookie列表转换为requests可以使用的字典格式
    cookies_dict = {}
    for cookie in cookie_data['cookies']:
        cookies_dict[cookie['name']] = cookie['value']
    
    # 设置请求头
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }
    
    # 发送请求
    try:
        response = requests.get(url, headers=headers, cookies=cookies_dict)
        response.raise_for_status()  # 检查请求是否成功
    except requests.exceptions.RequestException as e:
        return f"请求错误: {str(e)}"
    
    # 解析HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # 查找skuCode元素
    sku_code_span = soup.find('span', id='skuCode')
    
    # 提取并返回值
    if sku_code_span:
        return sku_code_span.text
    else:
        return "错误: 在响应中未找到skuCode"

if __name__ == "__main__":
    # 使用示例
    cookie_file_path = "cookie.json"  # 你的JSON cookie文件路径
    sku_code = fetch_sku_code(cookie_file_path)
    print(sku_code)  # 应该输出 79275964
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
from bs4 import BeautifulSoup

def search_product(cookie, search_value):
    # Base URL for the primary request
    url = 'https://www.dianxiaomi.com/alibabaPairProduct/pageList.htm'

    # Headers for the request
    headers = {
        'authority': 'www.dianxiaomi.com',
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,et;q=0.7,zh-TW;q=0.6',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'sec-ch-ua': '"Chromium";v="106"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    # Data payload for the POST request
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'searchType': '3',
        'searchValue': search_value,
        'status': '-1',
        'searchMode': '0',
    }

    # Making the POST request
    response = requests.post(url, headers=headers, data=data)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)
    # Find the first element with class "f-left supplier"
    supplier_element = soup.find('td', class_='f-left supplier')
    
    # Return just the company name if found
    if supplier_element:
        return supplier_element.text.strip()
    else:
        return "Company not found"
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

def get_product_info(cookie, urls, singleOrBatch='1'):
    """
    Function to fetch product information from Dianxiaomi.
    
    Parameters:
    - cookie: str, the authentication cookie required for the request
    - urls: str, the URL of the product you want to fetch information about
    - singleOrBatch: str, indicates if the request is for a single product ('1') or batch ('0'), default is '1'

    Returns:
    - JSON response from the server with the product details
    """
    url = 'https://www.dianxiaomi.com/alibabaProduct/getProductByUrls.json'

    headers = {
        'authority': 'www.dianxiaomi.com',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
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
        'x-requested-with': 'XMLHttpRequest'
    }

    data = {
        'urls': urls,
        'singleOrBatch': singleOrBatch,
    }

    response = requests.post(url, headers=headers, data=data)

    # Return the response in JSON format if possible, otherwise return the text response
    try:
        return response.json()
    except ValueError:
        return response.text
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
import re

def search_package(content, cookie_file_path):
    """
    Search for a package on dianxiaomi.com and extract just the package number.

    Args:
        content: The search content value
        cookie_file_path: Path to the JSON file containing cookies

    Returns:
        The package number if found, otherwise None
    """
    try:
        # Load cookies from JSON file
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)

        # Extract cookies
        cookies = {}
        for cookie in cookie_data.get('cookies', []):
            cookies[cookie['name']] = cookie['value']

        # 构建cookie字符串
        cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])

        # Set up headers
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.11',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': cookie_string,
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/web/order/all',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="137", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }

        # Set up data with defaults and provided content
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

        # Make the POST request to new API
        url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()

        # 解析JSON响应
        result = response.json()

        # 检查响应状态
        if result.get('code') != 0:
            print(f"API返回错误: {result.get('msg', '未知错误')}")
            return None

        # 提取包裹列表
        package_list = result.get('data', {}).get('page', {}).get('list', [])

        if package_list:
            # 返回第一个包裹的包裹号
            first_package = package_list[0]
            package_number = first_package.get('packageNumber')
            if package_number:
                return package_number
            else:
                print("Package number not found in response")
                return None
        else:
            print("No packages found in response")
            return None

    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    content_value = input("Enter content value (e.g., order ID): ")
    cookie_file = input("Enter path to cookie JSON file: ")
    
    package_number = search_package(content_value, cookie_file)
    
    if package_number:
        print(package_number)
    else:
        print("Failed to retrieve package number")
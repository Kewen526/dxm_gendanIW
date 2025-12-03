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
        
        # Set up headers
        headers = {
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
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
            'orderSearchType': '1'
        }
        
        # Make the POST request
        url = 'https://www.dianxiaomi.com/package/searchPackage.htm'
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Method 1: Find by data-packageNumber attribute
        element = soup.find(attrs={"data-packageNumber": True})
        if element:
            return element['data-packageNumber']
        
        # Method 2: If not found, try using regex to find the pattern
        package_match = re.search(r'data-packageNumber="([^"]+)"', response.text)
        if package_match:
            return package_match.group(1)
            
        # Method 3: If still not found, look for a specific pattern
        if 'data-packageNumber' in response.text:
            lines = response.text.split('\n')
            for line in lines:
                if 'data-packageNumber' in line:
                    match = re.search(r'data-packageNumber="([^"]+)"', line)
                    if match:
                        return match.group(1)
        
        print("Package number not found in response")
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
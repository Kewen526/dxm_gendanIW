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
def request_dianxiaomi_provider_auth(cookie_file_path):
    """
    Make a request to dianxiaomi.com using cookies from a local JSON file
    and parse the response to extract logistics providers as a dictionary
    
    Args:
        cookie_file_path (str): Path to the JSON file containing cookies
        
    Returns:
        dict: Dictionary with provider names as keys and provider IDs as values
        or None if an error occurs
    """
    import json
    import requests
    from bs4 import BeautifulSoup
    
    # Load the cookie file
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
    except Exception as e:
        print(f"Error loading cookie file: {e}")
        return None
    
    # Extract cookies and create a cookie dictionary
    cookies = {}
    for cookie in cookie_data['cookies']:
        cookies[cookie['name']] = cookie['value']
    
    # Set up headers
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # Define the URL and data
    url = 'https://www.dianxiaomi.com/providerAuth/getList.htm'
    data = {'code': '0'}
    
    # Make the request
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all option tags (except the first one which is just a placeholder)
        options = soup.find_all('option')[1:]
        
        # Create a dictionary with provider names as keys and provider IDs as values
        providers_dict = {}
        for option in options:
            provider_name = option.text.strip()
            provider_id = option.get('value')
            if provider_id:  # Make sure value is not empty
                providers_dict[provider_name] = provider_id
        
        return providers_dict
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None

# Usage example:
# providers = request_dianxiaomi_provider_auth('path/to/cookie.json')
# if providers:
#     print(providers)
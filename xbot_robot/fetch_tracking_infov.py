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
from typing import Dict, Union

def fetch_tracking_info(cookie_file_path: str, content: str, save_response: bool = False) -> Dict[str, Union[str, None]]:
    """
    Get tracking information from dianxiaomi.com using provided cookie file and content.
    
    Args:
        cookie_file_path: Path to the JSON file containing cookies in Chrome extension format
        content: The order ID to search for
        save_response: Whether to save the raw response to a file
        
    Returns:
        A dictionary containing:
        - 'tracking_number': The tracking number if found, None otherwise
        - 'error_message': Any error message found in the response, None if no error
        - 'status': 'success', 'error', or 'not_found'
    """
    # Initialize result dictionary
    result = {
        'tracking_number': None,
        'error_message': None,
        'status': 'not_found'
    }
    
    # Load cookies from JSON file
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # Extract cookies from the JSON structure
        cookies_dict = {}
        if "cookies" in cookie_data and isinstance(cookie_data["cookies"], list):
            for cookie in cookie_data["cookies"]:
                if "name" in cookie and "value" in cookie:
                    cookies_dict[cookie["name"]] = cookie["value"]
        elif isinstance(cookie_data, list):
            for cookie in cookie_data:
                if isinstance(cookie, dict) and "name" in cookie and "value" in cookie:
                    cookies_dict[cookie["name"]] = cookie["value"]
        elif isinstance(cookie_data, dict) and "cookies" not in cookie_data:
            cookies_dict = cookie_data
        else:
            print("Error: Cookie file does not contain expected format")
            result['error_message'] = "Cookie file format error"
            result['status'] = 'error'
            return result
    except Exception as e:
        print(f"Error loading cookie file: {e}")
        result['error_message'] = f"Error loading cookie file: {e}"
        result['status'] = 'error'
        return result
    
    # 构建cookie字符串
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
    
    # 新版API URL
    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'
    
    # 新版请求头
    headers = {
        'authority': 'www.dianxiaomi.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    
    # 请求数据（按照新curl参数）
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
    
    # Make the request
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # Print the raw response data
        print("\n--- RAW RESPONSE DATA ---")
        print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        print("--- END OF RAW RESPONSE PREVIEW ---\n")
        
        # Optionally save the response to a file
        if save_response:
            with open(f"response_{content.replace('-', '_')}.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Response saved to response_{content.replace('-', '_')}.json")
            
    except Exception as e:
        print(f"Error making request: {e}")
        result['error_message'] = f"Error making request: {e}"
        result['status'] = 'error'
        return result
    
    # 解析JSON响应
    try:
        json_result = response.json()
        
        # 检查全局响应状态
        if json_result.get('code') != 0:
            result['error_message'] = json_result.get('msg', '未知错误')
            result['status'] = 'error'
            return result
        
        # 提取包裹列表
        package_list = json_result.get('data', {}).get('page', {}).get('list', [])
        
        if not package_list:
            print("No packages found in response")
            return result
        
        # 获取第一个包裹
        first_package = package_list[0]
        
        # 检查单个包裹的错误信息
        error_msg = first_package.get('errorMsg', '')
        if error_msg:
            result['error_message'] = error_msg
            result['status'] = 'error'
            return result
        
        # 获取物流单号
        tracking_number = first_package.get('trackingNumber')
        
        if tracking_number:
            result['tracking_number'] = tracking_number
            result['status'] = 'success'
            return result
        else:
            print("No tracking number found in the package")
            return result
            
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        result['error_message'] = f"JSON parse error: {e}"
        result['status'] = 'error'
        return result


if __name__ == "__main__":
    # Example usage
    cookie_file = "cookie.json"  # Path to your JSON cookie file
    order_id = "4785806-68791"  # Order ID to search
    
    result = fetch_tracking_info(cookie_file, order_id, save_response=True)
    
    if result['status'] == 'success':
        print(f"Tracking number: {result['tracking_number']}")
    elif result['status'] == 'error':
        print(f"Error: {result['error_message']}")
    else:
        print("No tracking information found")
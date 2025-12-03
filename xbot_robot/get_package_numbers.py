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
import re
from typing import List, Optional

def get_package_numbers(content: str, cookie_file_path: str) -> Optional[List[str]]:
    """
    搜索包裹并提取packageNumber
    
    Args:
        content: 搜索内容 (例如: "6385553-1124")
        cookie_file_path: cookie JSON文件路径 (例如: "1.json")
    
    Returns:
        提取到的packageNumber列表，失败时返回None
    """
    
    # 加载cookies并转换格式
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # 转换cookie格式为requests可用的字典
        cookies = {}
        if 'cookies' in cookie_data:
            for cookie in cookie_data['cookies']:
                cookies[cookie['name']] = cookie['value']
        else:
            # 如果是简单的键值对格式，直接使用
            cookies = cookie_data
            
    except Exception as e:
        print(f"加载cookie文件失败: {e}")
        return None
    
    # 请求URL和配置
    url = "https://www.dianxiaomi.com/package/searchPackage.htm"
    
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m1-1',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
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
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        response.raise_for_status()
        
        # 提取packageNumber
        pattern = r'data-packageNumber="([^"]+)"'
        matches = re.findall(pattern, response.text)
        
        return matches if matches else []
        
    except Exception as e:
        print(f"请求失败: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    # 调用函数
    result = get_package_numbers("6385553-1124", "1.json")
    
    if result is not None:
        if result:
            print(f"找到 {len(result)} 个packageNumber: {result}")
        else:
            print("未找到packageNumber")
    else:
        print("请求失败")
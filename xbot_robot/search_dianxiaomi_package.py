# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能,如获取元素、访问全局变量、获取资源文件等功能
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

def get_dianxiaomi_order_id(cookie_file_path, content):
    """
    从本地JSON文件读取cookie并搜索包裹信息，返回orderIds和storageId的值
    
    参数:
        cookie_file_path (str): 包含cookie的JSON文件路径
        content (str): 搜索内容，如订单ID
        
    返回:
        list: 包含orderIds和storageId的列表，失败时返回[None, None]
    """
    # 从JSON文件读取cookie数据
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # 检查cookie格式并提取值
        cookies = {}
        
        # 新格式：包含"cookies"数组的对象
        if "cookies" in cookie_data and isinstance(cookie_data["cookies"], list):
            for cookie in cookie_data["cookies"]:
                if "name" in cookie and "value" in cookie:
                    cookies[cookie["name"]] = cookie["value"]
        
        # 旧格式：直接是cookie字符串
        elif isinstance(cookie_data, str):
            cookie_items = cookie_data.split('; ')
            for item in cookie_items:
                if '=' in item:
                    name, value = item.split('=', 1)
                    cookies[name] = value
        
        # 旧格式：直接是cookie字典
        elif isinstance(cookie_data, dict) and "cookies" not in cookie_data:
            cookies = cookie_data
        
        # 检查是否成功解析到cookie
        if not cookies:
            print("无法从文件中提取cookie信息")
            return [None, None]
            
    except Exception as e:
        print(f"读取cookie文件出错: {e}")
        return [None, None]
    
    # 新版API URL
    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'
    
    # 设置请求头
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all?go=m1-1',
        'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    
    # 设置请求数据 - 使用新版API参数
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',  # 改为空
        'shopId': '-1',
        'history': '',
        'searchType': 'orderId',
        'content': content,
        'isVoided': '-1',  # 改为-1
        'isRemoved': '-1',  # 改为-1
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
        'isSearch': '1',  # 改为1
        'isFree': '-1',  # 改为-1
        'isBatch': '-1',  # 改为-1
        'isOversea': '-1',
        'forbiddenStatus': '-1',
        'forbiddenReason': '0',
        'orderField': 'order_create_time',  # 改为create_time
        'behindTrack': '-1',
        'storageId': '0',
        'timeOut': '0',
        'orderSearchType': '1',
        'axios_cancelToken': 'true'  # 新增参数
    }
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        
        # 检查响应状态
        response.raise_for_status()
        
        # 解析JSON响应
        result = response.json()
        
        # 检查响应状态码
        if result.get('code') != 0:
            print(f"API返回错误: {result.get('msg', '未知错误')}")
            return [None, None]
        
        # 提取orderIds和storageId
        order_ids = None
        storage_id = None
        
        data_obj = result.get('data', {})
        
        # 获取orderIds
        order_ids = data_obj.get('orderIds')
        
        # 获取storageId - 从第一个订单中获取
        page_obj = data_obj.get('page', {})
        order_list = page_obj.get('list', [])
        
        if order_list and len(order_list) > 0:
            first_order = order_list[0]
            storage_id = first_order.get('storageId')
        
        # 如果找到了orderIds但没找到storageId，尝试从其他订单中获取
        if order_ids and not storage_id:
            for order in order_list:
                if order.get('storageId'):
                    storage_id = order.get('storageId')
                    break
        
        if order_ids:
            print(f"成功获取订单信息:")
            print(f"orderIds: {order_ids}")
            print(f"storageId: {storage_id}")
        else:
            print("未找到匹配的订单")
        
        return [str(order_ids) if order_ids else None, str(storage_id) if storage_id else None]
        
    except requests.exceptions.RequestException as e:
        print(f"请求发送失败: {e}")
        return [None, None]
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return [None, None]
    except Exception as e:
        print(f"处理过程出错: {e}")
        return [None, None]

# 示例用法
if __name__ == "__main__":
    # 调用示例
    cookie_file = "cookie.json"  # 替换为您的cookie文件路径
    search_content = "DMM-SP00002-easr6n-jq-1485-A"  # 替换为您要搜索的内容
    
    result = get_dianxiaomi_order_id(cookie_file, search_content)
    
    if result[0]:
        print(f"\n最终结果:")
        print(f"orderIds: {result[0]}")
        print(f"storageId: {result[1]}")
    else:
        print("\n获取结果失败")
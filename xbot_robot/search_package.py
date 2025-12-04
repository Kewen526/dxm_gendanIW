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

def search_package(cookie_json_path, content):
    """
    搜索店小秘包裹信息，并提取运单号

    参数:
        cookie_json_path (str): 本地cookie的JSON文件路径
        content (str): 搜索内容（订单号）

    返回:
        str: 运单号，如果找不到则返回None
    """
    # 读取cookie文件
    try:
        with open(cookie_json_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)

        # 从cookie数据中提取cookies数组，并转换为requests所需的字典格式
        cookies_dict = {}
        if 'cookies' in cookie_data and isinstance(cookie_data['cookies'], list):
            for cookie in cookie_data['cookies']:
                if 'name' in cookie and 'value' in cookie:
                    cookies_dict[cookie['name']] = cookie['value']
        else:
            print("Cookie文件格式不正确，未找到cookies数组")
            return None
    except Exception as e:
        print(f"读取cookie文件时出错: {e}")
        return None

    # 新的API URL
    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'

    # 构建cookie字符串
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

    # 请求头
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/web/order/all',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }

    # 请求数据
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'history': '',
        'searchType': 'orderId',
        'content': content,  # 使用传入的内容
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

    # 发送请求
    try:
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
            # 返回第一个包裹的运单号 (expressNumber字段)
            first_package = package_list[0]
            tracking_number = first_package.get('expressNumber') or first_package.get('trackingNumber')
            if tracking_number:
                return tracking_number
            else:
                print("未找到运单号")
                return None
        else:
            print("未找到包裹")
            return None

    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

# 使用示例
# tracking_number = search_package('cookie.json', '6432921-2878')
# if tracking_number:
#     print(f"运单号: {tracking_number}")
# else:
#     print("未能获取运单号")
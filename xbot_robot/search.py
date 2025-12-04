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

def search_dianxiaomi_package(cookies_file_path, content_value):
    """
    使用指定的cookies文件和content值在店小秘网站上搜索包裹信息并返回结果

    参数:
        cookies_file_path (str): 本地cookies JSON文件的路径
        content_value (str): 要搜索的内容值(如订单号)

    返回:
        dict: 搜索结果的JSON数据，如果出错则返回None
    """
    # 从JSON文件加载cookies
    try:
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取cookies数组中的name和value对
        cookies_dict = {}
        if "cookies" in data and isinstance(data["cookies"], list):
            for cookie in data["cookies"]:
                if "name" in cookie and "value" in cookie:
                    cookies_dict[cookie["name"]] = cookie["value"]
        else:
            # 尝试直接使用文件内容作为cookies字典
            cookies_dict = data

    except Exception as e:
        print(f"加载cookies文件时出错: {e}")
        return None

    # 新的API URL
    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'

    # 构建cookie字符串
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])

    # 请求头
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.5.11',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'cookie': cookie_string,
        'Origin': 'https://www.dianxiaomi.com',
        'Referer': 'https://www.dianxiaomi.com/web/order/all',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    # 表单数据
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'state': '',
        'shopId': '-1',
        'history': '',
        'searchType': 'orderId',
        'content': content_value,
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

    # 打印cookie信息进行调试
    print(f"使用的cookies数量: {len(cookies_dict)}")

    # 发送POST请求
    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=data
        )

        # 检查请求是否成功
        response.raise_for_status()

        # 解析JSON响应
        result = response.json()

        # 返回JSON数据
        return result
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"发送请求时出错: {e}")
        return None

# 使用示例:
# result = search_dianxiaomi_package("cookies.json", "6360846-1410")
# if result:
#     print(result)
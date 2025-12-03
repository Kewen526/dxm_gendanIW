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

def search_package(cookie_file_path, content):
    """
    搜索包裹并提取包裹ID
    
    参数:
    cookie_file_path: cookie JSON文件路径
    content: 搜索内容（订单号）
    
    返回:
    包裹ID列表
    """
    
    # 读取cookie文件
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
    except Exception as e:
        print(f"读取cookie文件失败: {e}")
        return []
    
    # 处理cookie格式
    cookies = {}
    
    # 如果数据包含"cookies"键
    if 'cookies' in cookie_data:
        cookies_list = cookie_data['cookies']
        for cookie in cookies_list:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
    # 如果直接是cookies数组
    elif isinstance(cookie_data, list):
        for cookie in cookie_data:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
    # 如果是键值对格式
    elif isinstance(cookie_data, dict) and 'cookies' not in cookie_data:
        cookies = cookie_data
    
    # 打印提取的cookie（用于调试）
    print(f"成功提取 {len(cookies)} 个cookie")
    print("提取的cookie名称:", list(cookies.keys()))
    
    # 构建cookie字符串
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])
    
    # 新的API URL
    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'
    
    # 请求头
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
    
    # 请求数据
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
    
    # 创建session来保持cookie
    session = requests.Session()
    
    try:
        # 发送POST请求
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # 打印响应状态（用于调试）
        print(f"响应状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 解析JSON响应
        result = response.json()
        
        # 检查响应状态
        if result.get('code') != 0:
            print(f"API返回错误: {result.get('msg', '未知错误')}")
            return []
        
        # 提取包裹列表
        package_list = result.get('data', {}).get('page', {}).get('list', [])
        
        # 提取所有包裹ID
        package_ids = [str(pkg.get('id')) for pkg in package_list if pkg.get('id')]
        
        return package_ids
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        # 保存响应内容用于调试
        with open('response_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("响应内容已保存到 response_debug.html 用于调试")
        return []
    except Exception as e:
        print(f"发生错误: {e}")
        return []
    finally:
        session.close()


# 使用示例
if __name__ == "__main__":
    # 指定cookie文件路径和搜索内容
    cookie_path = "cookie.json"
    search_content = "LYN-SP00001-62e3fd-22346-A"
    
    # 调用函数
    package_ids = search_package(cookie_path, search_content)
    
    # 打印结果
    if package_ids:
        print(f"\n成功！找到 {len(package_ids)} 个包裹ID:")
        for package_id in package_ids:
            print(f"  - {package_id}")
    else:
        print("\n未找到包裹ID")
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

def set_dianxiaomi_comment(cookie_file_path, package_ids):
    """
    从本地JSON文件读取cookie并发送请求设置自定义评论
    
    参数:
        cookie_file_path (str): 包含cookie的JSON文件路径
        package_ids (str): 包裹ID，多个ID用逗号分隔
        
    返回:
        dict: API响应结果，请求成功时返回响应JSON，失败时返回None
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
            return None
            
    except Exception as e:
        print(f"读取cookie文件出错: {e}")
        return None
    
    # 请求URL
    url = 'https://www.dianxiaomi.com/order/batchSetCustomComment.json'
    
    # 设置请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
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
    
    # 设置请求数据
    data = {
        'isGreen': '0',
        'isYellow': '1',
        'isOrange': '0',
        'isRed': '0',
        'isViolet': '0',
        'isBlue': '0',
        'cornflowerBlue': '0',
        'pink': '0',
        'teal': '0',
        'turquoise': '0',
        'packageIds': package_ids,
        'history': ''
    }
    
    # 发送请求
    try:
        # 使用cookies参数自动处理cookie
        response = requests.post(url, headers=headers, data=data, cookies=cookies)
        
        # 检查响应状态
        response.raise_for_status()
        
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求发送失败: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"解析响应JSON失败: {e}")
        print(f"响应内容: {response.text}")
        return None

# 示例用法
if __name__ == "__main__":
    # 调用示例
    cookie_file = "cookie.json"  # 替换为您的cookie文件路径
    package_ids = "54280086909130128"  # 替换为您的包裹ID
    
    result = set_dianxiaomi_comment(cookie_file, package_ids)
    
    if result:
        print("请求成功，响应结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("请求失败")
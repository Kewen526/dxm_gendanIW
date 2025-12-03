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

def batch_commit_platform_packages(cookie_file_path, package_ids):
    """
    批量提交平台包裹
    
    参数:
        cookie_file_path: cookie JSON文件的路径
        package_ids: 包裹ID，可以是单个ID字符串或多个ID的列表
    
    返回:
        响应对象
    """
    
    # 读取cookie文件
    with open(cookie_file_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    # 提取并格式化cookies
    cookies_dict = {}
    for cookie in cookie_data['cookies']:
        cookies_dict[cookie['name']] = cookie['value']
    
    # 构建cookie字符串（按照curl命令中的格式）
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies_dict.items()])
    
    # 设置请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m10201',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 处理packageIds参数，支持单个ID或多个ID
    if isinstance(package_ids, list):
        package_ids_str = ','.join(str(id) for id in package_ids)
    else:
        package_ids_str = str(package_ids)
    
    # 构建请求数据
    data = {
        'packageIds': package_ids_str
    }
    
    # 发送POST请求
    url = 'https://www.dianxiaomi.com/package/batchCommitPlatform.json'
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # 检查HTTP错误
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

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
import argparse
import json
import os


def parse_json_cookies_file(cookie_file_path):
    """从 JSON 文件中解析 cookies"""
    if not os.path.exists(cookie_file_path):
        raise FileNotFoundError(f"Cookie 文件 '{cookie_file_path}' 不存在")
    
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
        
        # 提取 cookies 列表并转换为 requests 可用的字典格式
        cookies = {}
        if 'cookies' in cookie_data and isinstance(cookie_data['cookies'], list):
            for cookie in cookie_data['cookies']:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
        
        return cookies
    
    except json.JSONDecodeError:
        raise ValueError(f"Cookie 文件 '{cookie_file_path}' 不是有效的 JSON 格式")
    except Exception as e:
        raise Exception(f"解析 cookie 文件时出错: {str(e)}")


def check_process(cookie_file_path, uuid):
    """发送请求检查处理状态"""
    url = 'https://www.dianxiaomi.com/checkProcess.json'
    
    # 设置 headers
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/package/toAdd.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 解析并使用 cookies
    cookies = parse_json_cookies_file(cookie_file_path)
    
    # 设置请求数据
    data = {
        'uuid': uuid
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        response.raise_for_status()
        
        # 返回 JSON 数据
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {"error": f"请求错误: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "响应不是有效的 JSON 格式", "response_text": response.text}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='检查店小秘处理状态')
    parser.add_argument('--cookie', required=True, help='Cookie JSON 文件路径')
    parser.add_argument('--uuid', required=True, help='UUID 参数')
    
    args = parser.parse_args()
    
    try:
        result = check_process(args.cookie, args.uuid)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"错误: {str(e)}")
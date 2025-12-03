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
from urllib import parse

def send_post_request():
    """
    发送POST请求到指定API
    """
    requestUrl = 'http://47.95.157.46:8520/api/post_task_dispatch'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {
        # 如果需要添加参数，在这里添加
    }
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None
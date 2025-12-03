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

def json_to_cookie_string(file_path):
    # Read the JSON file
    with open(file_path, 'r', encoding='utf-8') as file:
        cookie_json = json.load(file)

    # Extract and format the cookies without extra spaces or line breaks
    cookies = cookie_json['cookies']
    cookie_string = ';'.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    return cookie_string
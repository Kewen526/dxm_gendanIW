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

def get_shop_type(shop_id):
    request_url = 'http://47.95.157.46:8520/api/shop_id'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "id": shop_id
    }
    data = parse.urlencode(form_data, True)

    response = requests.post(request_url, headers=headers, data=data)
    if response.status_code == 200:
        try:
            result = response.json()
            shop_type = result["data"][0]["shop_type"]
            return shop_type
        except (KeyError, IndexError, ValueError):
            return "无法解析 shop_type"
    else:
        return f"请求失败，状态码：{response.status_code}"
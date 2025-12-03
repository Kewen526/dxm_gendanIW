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

def get_conductor_id(task_id):
    request_url = 'http://47.95.157.46:8520/api/conductor_id'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "id": str(task_id)
    }
    data = parse.urlencode(form_data, True)

    try:
        response = requests.post(request_url, headers=headers, data=data)
        response.raise_for_status()  # 抛出异常用于非200响应
        json_data = response.json()

        if json_data.get("success") and json_data.get("data"):
            return json_data["data"][0]["id"]
        else:
            print("请求成功但数据为空或格式不符")
            return None
    except Exception as e:
        print(f"请求失败：{e}")
        return None
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

def get_conductor_name(conductor_value):
    request_url = 'http://47.95.157.46:8520/api/get_conductor_name'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "conductor": conductor_value
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    
    if response.status_code == 200:
        response_json = response.json()
        if response_json['success'] and response_json['data']:
            return response_json['data'][0]['acct']
        else:
            return "No data found or request unsuccessful"
    else:
        return f"Request failed with status code: {response.status_code}"

# 示例用法
if __name__ == "__main__":
    conductor_value = input("请输入conductor值: ")
    result = get_conductor_name(conductor_value)
    print(result)
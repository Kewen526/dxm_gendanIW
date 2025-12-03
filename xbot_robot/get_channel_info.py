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
import json

def get_channel_info(order_id):
    request_url = 'http://47.95.157.46:8520/api/order_id_channel'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    
    if response.status_code == 200:
        result = json.loads(response.text)
        if result.get('success') and result.get('data'):
            # Return the first item in the data array
            return result['data'][0]
        else:
            return {"error": "No data found or request unsuccessful"}
    else:
        return {"error": f"Request failed with status code: {response.status_code}"}

# Example usage
if __name__ == "__main__":
    test_order_id = "QXL-B-26de1b-17275-A-1"
    channel_info = get_channel_info(test_order_id)
    print(channel_info)
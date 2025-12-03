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

def get_waybill_num(order_id):
    request_url = 'http://47.95.157.46:8520/api/order_ydh'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    response_json = response.json()
    
    if response_json['success']:
        waybill_num = response_json['data'][0]['waybill_num']
        return waybill_num
    else:
        return f"Error: {response_json['msg']}"

# Example usage
if __name__ == "__main__":
    order_id = input("请输入订单号(order_id): ")
    result = get_waybill_num(order_id)
    print(f"运单号(waybill_num): {result}")
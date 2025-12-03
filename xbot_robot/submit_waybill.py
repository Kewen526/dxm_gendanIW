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

def submit_waybill(order_id, waybill_number):
    """
    提交运单号的函数
    
    参数:
        order_id (str): 订单ID
        waybill_number (str): 运单号
        
    返回:
        dict: 包含status_code和response_text的字典
    """
    request_url = 'http://47.95.157.46:8520/api/waybill_number'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id,
        "waybill_number": waybill_number
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    
    return {
        "status_code": response.status_code,
        "response_text": response.text
    }

# 使用示例
if __name__ == "__main__":
    result = submit_waybill("QXL-8sqzmt-mu-1001-A", "4665")
    print(f"状态码: {result['status_code']}")
    print(f"响应内容: {result['response_text']}")
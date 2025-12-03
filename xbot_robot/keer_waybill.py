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

def submit_waybill(order_id, waybill_num):
    """
    提交订单ID和运单号到API
    
    参数:
        order_id (str): 订单ID
        waybill_num (str): 运单号
    
    返回:
        dict: 包含状态码和响应内容的字典
    """
    # 请求URL
    request_url = 'http://47.95.157.46:8520/api/waybill_num'
    
    # 请求头
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # 表单数据
    form_data = {
        "order_id": order_id,
        "waybill_num": waybill_num
    }
    
    # URL编码表单数据
    data = parse.urlencode(form_data, True)
    
    # 发送POST请求
    try:
        response = requests.post(request_url, headers=headers, data=data)
        return {
            "status_code": response.status_code,
            "text": response.text
        }
    except Exception as e:
        return {
            "status_code": None,
            "text": f"请求失败: {str(e)}"
        }

# 使用示例
# result = submit_waybill("123456", "YT2513421272203726")
# print(f"状态码: {result['status_code']}")
# print(f"响应内容: {result['text']}")
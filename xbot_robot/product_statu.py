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

def check_product_status(order_id, status_list):
    url = 'http://47.95.157.46:8520/api/product_status'
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # 将状态列表转换为字符串格式
    status_str = str(status_list).replace("'", "\"")
    
    form_data = {
        "order_id": order_id,
        "status": status_str
    }
    
    response = requests.post(url, headers=headers, data=form_data)
    
    return {
        "status_code": response.status_code,
        "response_text": response.text
    }

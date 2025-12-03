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

def check_task_status(invoice_id, task_status):
    request_url = 'http://47.95.157.46:8520/api/task_status'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "invoice_id": invoice_id,
        "task_status": task_status
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    return response

# 使用示例
invoice_id = "INV-001"  # 替换为您的发票ID
task_status = "completed"  # 替换为您需要的任务状态
check_task_status(invoice_id, task_status)
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
 
def send_task_request(invoice_id="", order_id="", intention_code="",
                     conductor="", queue_entry_time="", task_status="", conductor_name=""):
    """
    发送任务请求到API端点
   
    参数:
        invoice_id (str): 发票ID
        order_id (str): 订单ID
        intention_code (str): 意图代码
        conductor (str): 操作人
        queue_entry_time (str): 队列进入时间
        task_status (str): 任务状态
        conductor_name (str): 操作人名称
       
    返回:
        tuple: (状态码, 响应文本)
    """
    request_url = 'http://47.95.157.46:8520/api/up_task'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
   
    form_data = {
        "invoice_id": invoice_id,
        "order_id": order_id,
        "intention_code": intention_code,
        "conductor": conductor,
        "queue_entry_time": queue_entry_time,
        "task_status": task_status,
        "conductor_name": conductor_name
    }
   
    data = parse.urlencode(form_data, True)
    response = requests.post(request_url, headers=headers, data=data)
   
    return response.status_code, response.text
 
# 使用示例:
if __name__ == "__main__":
    status_code, response_text = send_task_request(
        invoice_id="12345",
        order_id="OR789",
        intention_code="INT001",
        conductor="张三",
        queue_entry_time="2023-11-01 12:00:00",
        task_status="active",
        conductor_name="张三"
    )
    print(status_code)
    print(response_text)
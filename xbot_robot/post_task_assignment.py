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
import json

def submit_task_assignment(order_list, invoice_id, shop_type, task_status, assignment_round):
    """
    发送任务分配请求
    
    Args:
        order_list (list): 订单列表
        invoice_id (str): 发票ID
        shop_type (str): 店铺类型
        task_status (str): 任务状态
        assignment_round (str): 分配轮次
    
    Returns:
        requests.Response: API响应对象
    """
    url = "http://47.95.157.46:8520/api/post_task_assignment"
    
    # 构建请求数据
    data = {
        "orderList": order_list,
        "invoice_id": invoice_id,
        "shop_type": shop_type,
        "task_status": task_status,
        "assignment_round": assignment_round
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        return response
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 调用函数
    result = submit_task_assignment(
        order_list=["123", "465", "789"],
        invoice_id="23190",
        shop_type="自营",
        task_status="测试",
        assignment_round="二次"
    )
    
    if result:
        print(f"状态码: {result.status_code}")
        print(f"响应内容: {result.text}")
    else:
        print("请求失败")
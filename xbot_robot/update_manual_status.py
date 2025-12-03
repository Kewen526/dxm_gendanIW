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

def update_manual_status(order_id, manual_status):
    """
    更新订单的手动状态
    
    Args:
        order_id (str): 订单ID
        manual_status (str): 手动状态值
    
    Returns:
        dict: 包含状态码和响应内容的字典
    """
    requestUrl = 'http://47.95.157.46:8520/api/manual_status'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {
        "order_id": order_id,
        "manual_status": manual_status
    }
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data)
        return {
            'status_code': response.status_code,
            'response_text': response.text,
            'success': response.status_code == 200
        }
    except requests.exceptions.RequestException as e:
        return {
            'status_code': None,
            'response_text': str(e),
            'success': False
        }

# 使用示例
if __name__ == "__main__":
    # 调用函数示例
    result = update_manual_status("12345", "completed")
    print(f"状态码: {result['status_code']}")
    print(f"响应内容: {result['response_text']}")
    print(f"请求成功: {result['success']}")
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

def send_shougongdan_request(title,shop_num,sku):
    """
    发送手工单备注请求
    
    参数:
        title (str): 要发送的标题内容
    
    返回:
        tuple: (状态码, 响应文本)
    """
    # 请求的URL地址
    requestUrl = 'http://47.95.157.46:8520/api/shougongdan_beizhu'
    
    # 设置请求头，指定内容类型为表单格式
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # 构建表单数据
    formData = {
        "title": title,
        "shop_num":shop_num,
        "sku":sku
    }
    
    # 将表单数据编码为URL编码格式
    data = parse.urlencode(formData, True)
    
    try:
        # 发送POST请求
        response = requests.post(requestUrl, headers=headers, data=data)
        
        # 打印状态码和响应内容
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 返回状态码和响应文本
        return response.status_code, response.text
        
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")
        return None, None

# 使用示例
if __name__ == "__main__":
    # 调用函数，传入title值
    title_value = "这是一个测试标题"
    send_shougongdan_request(title_value)
    
    # 或者接收返回值
    status, content = send_shougongdan_request("另一个标题")
    if status:
        print(f"请求成功，状态码: {status}")
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
from typing import Optional, Dict, Any

def send_package_order_request(package_id: str, order_id: str) -> Optional[Dict[str, Any]]:
    """
    发送包裹ID和订单ID到API
    
    Args:
        package_id: 包裹ID
        order_id: 订单ID
    
    Returns:
        API响应的字典，失败时返回None
    """
    
    requestUrl = 'http://47.95.157.46:8520/api/package_id_order_id'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    formData = {
        "package_id": package_id,
        "order_id": order_id
    }
    
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data)
        response.raise_for_status()  # 如果状态码不是200会抛出异常
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        # 尝试解析JSON响应
        try:
            return response.json()
        except:
            # 如果不是JSON格式，返回文本内容
            return {"text": response.text, "status_code": response.status_code}
            
    except Exception as e:
        print(f"请求失败: {e}")
        return None


# 使用示例
if __name__ == "__main__":
    # 调用函数
    result = send_package_order_request("XMR3BPM59098", "6385553-1124")
    
    if result:
        print(f"API响应: {result}")
    else:
        print("请求失败")
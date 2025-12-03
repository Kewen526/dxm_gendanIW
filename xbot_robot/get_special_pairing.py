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
import json

def get_special_pairing(product_id):
    """
    发送API请求获取特殊配对信息
    
    参数:
        product_id (str): 产品ID
        
    返回:
        str: 特殊配对值，如果请求失败返回None
    """
    request_url = 'http://47.95.157.46:8520/api/product_id_special_pairing'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "product_id": product_id
    }
    data = parse.urlencode(form_data, True)
    
    try:
        response = requests.post(request_url, headers=headers, data=data)
        
        # 检查响应状态
        if response.status_code == 200:
            # 解析JSON响应
            response_json = response.json()
            
            # 检查是否成功并且有数据
            if response_json.get('success') and response_json.get('data'):
                # 获取第一个结果中的special_pairing
                special_pairing = response_json['data'][0].get('special_pairing')
                return special_pairing
            else:
                print(f"API响应无效: {response_json}")
                return None
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求过程中出错: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    product_id = input("请输入product_id: ")
    result = get_special_pairing(product_id)
    
    if result is not None:
        print(f"special_pairing的值为: {result}")
    else:
        print("获取special_pairing失败")
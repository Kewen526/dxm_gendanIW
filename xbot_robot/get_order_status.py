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

def get_order_status(order_id):
    request_url = 'http://47.95.157.46:8520/api/order_status'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id
    }
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    
    if response.status_code == 200:
        try:
            response_json = response.json()
            if response_json.get('success') and response_json.get('data'):
                result = {}
                data_item = response_json['data'][0]  # 获取数据中的第一项
                
                # 处理 shipments_remark (JSON 字符串表示的列表)
                if 'shipments_remark' in data_item:
                    try:
                        result['shipments_remark'] = json.loads(data_item['shipments_remark'])
                    except:
                        result['shipments_remark'] = data_item['shipments_remark']
                
                # 处理 huo_remark (普通字符串)
                if 'huo_remark' in data_item:
                    result['huo_remark'] = data_item['huo_remark']
                
                # 处理 remark (JSON 字符串表示的列表)
                if 'remark' in data_item:
                    try:
                        result['remark'] = json.loads(data_item['remark'])
                    except:
                        result['remark'] = data_item['remark']
                
                return result
            else:
                return {"error": "没有返回数据或请求不成功"}
        except ValueError:
            return {"error": "无效的JSON响应"}
    else:
        return {"error": f"请求失败，状态码：{response.status_code}"}
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
from urllib.parse import urlencode

def get_shop_num(order_id):
    """
    传入 order_id，调用 API 并返回 shop_num 字符串
    """
    url = 'http://47.95.157.46:8520/api/order_shopnum'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    # 构造表单数据并 URL 编码
    form_data = {'order_id': order_id}
    encoded_data = urlencode(form_data)

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=encoded_data)
    # 如果返回状态不是 200，抛出异常
    response.raise_for_status()

    # 解析 JSON 响应
    result = response.json()
    if result.get('success') and result.get('data'):
        # 假设 data 是个列表，取第一个元素里的 shop_num
        shop_num = result['data'][0].get('shop_num')
        return shop_num
    else:
        # 请求失败或 data 为空时返回 None
        return None
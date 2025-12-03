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
def get_order_info(order_id, waybill_num):
    """
    获取订单信息通过订单ID和运单号
   
    Args:
        order_id (str): 订单ID
        waybill_num (str): 运单号
       
    Returns:
        requests.Response: 响应对象
    """
    import requests
    from urllib import parse
   
    # 检查 waybill_num 是否为字符串 "None"，如果是则转换为空字符串
    if waybill_num == "None":
        waybill_num = ""
   
    request_url = 'http://47.95.157.46:8520/api/order_info_waybill_num'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "order_id": order_id,
        "waybill_num": waybill_num
    }
    data = parse.urlencode(form_data, True)
   
    response = requests.post(request_url, headers=headers, data=data)
    return response
 
# 使用示例
if __name__ == "__main__":
    # 设置订单ID和运单号
    order_id = "123456789"
    waybill_num = "SF1234567890"  # 或者可能是 "None"
   
    # 调用函数获取响应
    response = get_order_info(order_id, waybill_num)
   
    # 打印状态码和响应内容
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
   
    # 如果响应是JSON格式，可以这样处理
    try:
        json_data = response.json()
        print(f"JSON数据: {json_data}")
    except:
        print("响应内容不是JSON格式")
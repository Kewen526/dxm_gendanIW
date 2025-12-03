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
import os

def upload_excel_to_dianxiaomi(file_path, cookie_file_path):
    """
    上传Excel文件到店小秘
    
    参数:
    file_path: 本地Excel文件的路径
    cookie_file_path: 包含cookie数据的JSON文件路径
    
    返回:
    成功时返回UUID，失败时返回None
    """
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 '{file_path}' 不存在!")
        return None
    
    # 检查cookie文件是否存在
    if not os.path.exists(cookie_file_path):
        print(f"错误: cookie文件 '{cookie_file_path}' 不存在!")
        return None
    
    # 请求URL
    url = 'https://www.dianxiaomi.com/excel/userImport.json'
    
    # 请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/package/toAdd.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 读取cookie文件
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
            
        # 将cookie数据转换为requests库所需的格式
        if 'cookies' in cookie_data and isinstance(cookie_data['cookies'], list):
            cookies = {item['name']: item['value'] for item in cookie_data['cookies']}
            print(f"成功从 '{cookie_file_path}' 加载cookie数据")
        else:
            print(f"错误: cookie文件格式不正确，无法获取cookies")
            return None
    except Exception as e:
        print(f"读取cookie文件时出错: {str(e)}")
        return None
    
    # Excel映射配置
    excel_transform_config = {
        "name": "模板2",
        "order": "0",
        "type": "order",
        "excelTransformList": [
            {"key": "noNeedTranFlag", "userKey": "运单号", "index": 1},
            {"key": "orderId", "userKey": "订单号", "index": 2},
            {"key": "noNeedTranFlag", "userKey": "包裹号", "index": 3},
            {"key": "noNeedTranFlag", "userKey": "客户英文标题", "index": 4},
            {"key": "noNeedTranFlag", "userKey": "客户产品变体", "index": 5},
            {"key": "number", "userKey": "数量", "index": 6},
            {"key": "country", "userKey": "国家", "index": 7},
            {"key": "noNeedTranFlag", "userKey": "1688链接", "index": 8},
            {"key": "noNeedTranFlag", "userKey": "物流渠道", "index": 9},
            {"key": "noNeedTranFlag", "userKey": "特殊备注", "index": 10},
            {"key": "noNeedTranFlag", "userKey": "1688买家留言", "index": 11},
            {"key": "noNeedTranFlag", "userKey": "采购单备注", "index": 12},
            {"key": "noNeedTranFlag", "userKey": "特殊配对", "index": 13},
            {"key": "noNeedTranFlag", "userKey": "产品拣货备注", "index": 14},
            {"key": "noNeedTranFlag", "userKey": "订单拣货备注", "index": 15},
            {"key": "email", "userKey": "邮箱", "index": 16},
            {"key": "buyerName", "userKey": "收件人姓名", "index": 17},
            {"key": "address1", "userKey": "地址", "index": 18},
            {"key": "city", "userKey": "城市", "index": 19},
            {"key": "zipCode", "userKey": "邮编", "index": 20},
            {"key": "province", "userKey": "省州", "index": 21},
            {"key": "phone", "userKey": "电话", "index": 22},
            {"key": "productStandard", "userKey": "属性", "index": 23},
            {"key": "sku", "userKey": "商品SKU", "index": 24},
            {"key": "shopName", "userKey": "店铺", "index": 25},
            {"key": "price", "userKey": "单价", "index": 26}
        ]
    }
    
    # 准备文件和表单数据
    files = {
        'FileData': (os.path.basename(file_path), open(file_path, 'rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    
    data = {
        'excelTransformConfig': json.dumps(excel_transform_config)
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, cookies=cookies, data=data, files=files)
        
        # 打印响应状态
        print(f"状态码: {response.status_code}")
        
        # 解析响应JSON
        uuid = None
        try:
            result = response.json()
            print(f"响应内容: {json.dumps(result)}")
            
            if result.get('code') == 0 and result.get('msg') == 'Successful' and 'data' in result and 'uuid' in result['data']:
                uuid = result['data']['uuid']
                print(f"上传成功! UUID: {uuid}")
            else:
                print(f"上传失败: {result.get('msg', '未知错误')}")
        except:
            print(f"无法解析响应JSON: {response.text}")
        
        return uuid
    
    except Exception as e:
        print(f"发生错误: {str(e)}")
        return None
    finally:
        # 确保文件关闭
        if 'FileData' in files and hasattr(files['FileData'][1], 'close'):
            files['FileData'][1].close()

# 使用示例
if __name__ == "__main__":
    file_path = input("请输入Excel文件路径: ")
    cookie_file_path = input("请输入cookie.json文件路径: ")
    
    uuid = upload_excel_to_dianxiaomi(file_path, cookie_file_path)
    if uuid:
        print(f"\n导入任务UUID: {uuid}")
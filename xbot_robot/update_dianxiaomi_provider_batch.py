import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

def main(args):
    pass

def update_dianxiaomi_provider_batch(cookie_file_path, package_ids, auth_id):
    """
    使用本地JSON文件中的cookies向dianxiaomi.com发送批量更新供应商的请求
    
    参数:
        cookie_file_path (str): 包含cookies的JSON文件路径
        package_ids (str): 订单包裹ID字符串参数
        auth_id (str): 授权ID参数
        
    返回:
        dict: 服务器响应的JSON数据
    """
    import json
    import requests
    
    # 加载cookie文件
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookie_data = json.load(f)
    except Exception as e:
        print(f"加载cookie文件错误: {e}")
        return None
    
    # 提取cookies并创建cookie字典
    cookies = {}
    for cookie in cookie_data['cookies']:
        cookies[cookie['name']] = cookie['value']
    
    # 设置请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m101',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 定义URL和请求数据
    url = 'https://www.dianxiaomi.com/order/batchUpdateProvider.json'
    data = {
        'packageIds': package_ids,
        'isAll': '0',
        'authId': auth_id,
        'orderState': 'approved',
        'saveType': '1'
    }
    
    # 发送请求
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        response.raise_for_status()
        
        # 返回JSON数据
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"请求发送错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应: {response.text}")
        return None

# 使用示例:
# result = update_dianxiaomi_provider_batch(
#     'path/to/cookie.json',
#     '54280086909130128',
#     '54280071572721456'
# )
# if result:
#     print(result)  # {'msg': '', 'code': 0, 'bor': {...}}
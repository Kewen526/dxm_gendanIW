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
import json
import requests

def add_product_to_warehouse(cookies_file_path, sku):
    """
    添加指定SKU的商品到仓库
    
    参数:
        cookies_file_path (str): 包含cookies的JSON文件路径
        sku (str): 需要添加的商品SKU，例如 '20250515'
    
    返回:
        dict: API响应内容
    """
    try:
        # 写死的仓库ID列表
        warehouse_ids = [4618738, 4659184, 6623995]
        
        # 加载cookies
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        # 将cookies转换为字典格式
        cookies = {}
        for cookie in cookies_data.get('cookies', []):
            if 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
        
        # 设置请求头
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/getDxmTempOrderPairProductIds.htm',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        # 准备请求参数 - 单个SKU的情况
        objs = [{"sku": sku}]
        
        # 构建请求数据
        data = {
            'objs': json.dumps(objs),
            'warehoseIds': ','.join(str(id) for id in warehouse_ids)
        }
        
        # 发送请求
        url = 'https://www.dianxiaomi.com/dxmWarehoseProduct/batchAddWareHoseProductFromPair.json'
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        
        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}")
        
        # 返回响应内容
        return response.json()
    
    except Exception as e:
        import traceback
        error_msg = f"处理过程中出错: {e}\n{traceback.format_exc()}"
        raise Exception(error_msg)

if __name__ == '__main__':
    # 示例调用
    cookies_file = 'cookie.json'  # 你的cookies JSON文件路径
    product_sku = '20250515'  # 需要添加的商品SKU
    
    try:
        result = add_product_to_warehouse(cookies_file, product_sku)
        print("API响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 检查响应状态
        if result.get('ret') == '1':
            print("添加商品到仓库成功!")
        else:
            print(f"添加失败: {result.get('msg', '未知错误')}")
    except Exception as err:
        print(f"错误: {err}")
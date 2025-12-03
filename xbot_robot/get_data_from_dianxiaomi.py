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

def get_data_from_dianxiaomi(cookie_file_path, search_value):
    """
    从点小秘网站获取数据并返回total值
    
    参数:
    cookie_file_path (str): 保存cookie的JSON文件路径
    search_value (str): 搜索值
    
    返回:
    int: 响应中的total值
    """
    # 从文件读取cookie信息
    with open(cookie_file_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    # 将cookie列表转换为字典格式
    cookies = {}
    for cookie in cookie_data.get('cookies', []):
        cookies[cookie['name']] = cookie['value']
    
    # 请求URL
    url = 'https://www.dianxiaomi.com/dxmCommodityProduct/getImgUrlExceptionStatData.json'
    
    # 设置headers
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 请求参数(使用默认值，只修改searchValue)
    data = {
        'pageNo': '1',
        'pageSize': '50',
        'searchType': '2',
        'searchValue': search_value,
        'productPxId': '1',
        'productPxSxId': '0',
        'fullCid': '',
        'productMode': '-1',
        'saleMode': '-1',
        'productSearchType': '1',
        'productGroupLxId': '1'
    }
    
    # 发送POST请求
    response = requests.post(url, headers=headers, cookies=cookies, data=data)
    
    # 确保请求成功
    response.raise_for_status()
    
    # 从JSON数据中提取total值
    result = response.json()
    return result.get('total', 0)  # 如果没有total键，默认返回0

def run_script():
    # 获取用户输入
    cookie_file_path = input("请输入cookie JSON文件路径: ")
    search_value = input("请输入searchValue值: ")
    
    try:
        # 获取total值
        total = get_data_from_dianxiaomi(cookie_file_path, search_value)
        
        # 只打印total值
        print(f"Total: {total}")
        
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    run_script()
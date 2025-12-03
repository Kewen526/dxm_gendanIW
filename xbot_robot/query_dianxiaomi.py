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
from bs4 import BeautifulSoup

def query_dianxiaomi(cookies_file_path, title, variant, shop_num):
    """
    从文件加载cookies并向店小秘发送产品查询请求
    
    参数:
        cookies_file_path: 包含cookies数据的JSON文件路径
        title: 商品标题
        variant: 商品变体
        shop_num: 店铺编号，用于匹配SKU
    
    返回:
        成功时返回包含[商品SKU, 是否已检查]的列表，失败时返回错误信息
    """
    print(f"\n=== 开始查询 ===")
    print(f"Title: {title}")
    print(f"Variant: {variant}")
    print(f"Shop_num: {shop_num}")
    
    # 从JSON文件加载cookies
    try:
        with open(cookies_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # 提取cookies并转换为字典格式
        cookies_dict = {}
        for cookie in data.get('cookies', []):
            cookies_dict[cookie['name']] = cookie['value']
        print(f"成功加载 {len(cookies_dict)} 个cookies")
    except Exception as e:
        return f"加载cookies文件时出错: {e}"
    
    # 构造search_value
    if variant == "UNI":
        search_value = title
    else:
        search_value = f"{title}-{variant}"  # 使用中文破折号
    
    print(f"\n第一次搜索值: {search_value}")
    
    # 发送请求到店小秘API的函数
    def send_search_request(search_val):
        url = 'https://www.dianxiaomi.com/dxmCommodityProduct/pageList.htm'
        
        headers = {
            'authority': 'www.dianxiaomi.com',
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
            'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        
        data = {
            'pageNo': '1',
            'pageSize': '50',
            'searchType': '6',
            'searchValue': search_val,
            'productPxId': '1',
            'productPxSxId': '0',
            'fullCid': '',
            'productMode': '-1',
            'saleMode': '-1',
            'productSearchType': '0',
            'productGroupLxId': '1'
        }
        
        print(f"发送POST请求到: {url}")
        print(f"请求数据: {data}")
        
        try:
            response = requests.post(url, headers=headers, cookies=cookies_dict, data=data)
            print(f"响应状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"响应长度: {len(response.text)} 字符")
                return response.text
            else:
                print(f"请求失败，响应内容: {response.text[:500]}...")  # 打印前500字符
                return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
    
    # 解析响应的函数 - 修改为返回结果、SKU总数和SKU列表
    def parse_response(html_text, search_shop_num):
        result = ["未找到商品SKU", "否"]
        
        soup = BeautifulSoup(html_text, 'html.parser')
        
        # 查找所有含有商品SKU的span标签
        sku_spans = soup.find_all('span', class_='goodsSKUName')
        total_sku_count = len(sku_spans)
        
        # 收集所有SKU到列表中
        sku_list = []
        for sku_span in sku_spans:
            sku_text = sku_span.text.strip()
            sku_list.append(sku_text)
        
        # 打印SKU列表
        print(f"找到 {total_sku_count} 个SKU")
        print("SKU列表:", sku_list)
        
        # 逐个打印SKU（保持原有格式）
        for i, sku_text in enumerate(sku_list):
            print(f"  SKU {i+1}: {sku_text}")
        
        # 查找包含search_shop_num的SKU
        for sku_span in sku_spans:
            sku_text = sku_span.text.strip()
            if search_shop_num in sku_text:
                print(f"\n✓ 找到匹配的SKU: {sku_text}")
                result[0] = sku_text
                
                # 查找对应的"已检查"标记
                parent_item = sku_span.find_parent('tr') or sku_span.find_parent('div', class_=lambda x: x and 'item' in x)
                if parent_item:
                    check_span = parent_item.find('span', attrs={"data-content": "已检查"})
                    if check_span and check_span.text.strip() == "备":
                        result[1] = "是"
                        print("  已检查状态: 是")
                    else:
                        print("  已检查状态: 否")
                break
        
        if result[0] == "未找到商品SKU":
            print(f"\n✗ 没有找到包含 '{search_shop_num}' 的SKU")
        
        return result, total_sku_count, sku_list
    
    # 执行匹配逻辑的函数（提取公共逻辑）
    def execute_matching_logic(response_text, debug_file_name):
        if not response_text:
            return ["未找到商品SKU", "否"]
        
        # 保存响应到文件（用于调试）
        with open(debug_file_name, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"已保存响应到 {debug_file_name}")
        
        # 首先使用完整的shop_num查找
        result, total_skus, sku_list = parse_response(response_text, shop_num)
        
        # 如果没找到匹配的SKU，尝试分割shop_num
        if result[0] == "未找到商品SKU" and '-' in shop_num:
            print(f"\n=== 尝试分割shop_num ===")
            # 使用中文破折号分割shop_num
            shop_num_parts = shop_num.split('-')
            print(f"分割结果: {shop_num_parts}")
            
            # 删除第一个元素
            if len(shop_num_parts) > 1:
                shop_num_parts = shop_num_parts[1:]
                partial_shop_num = '-'.join(shop_num_parts)
                print(f"删除第一个元素后: {partial_shop_num}")
                
                # 使用分割后的shop_num重新查找
                result, total_skus_after_split, _ = parse_response(response_text, partial_shop_num)
                
                # 如果分割后仍然没有找到任何SKU，重新用原始shop_num搜索
                if result[0] == "未找到商品SKU" and total_skus_after_split == 0:
                    print(f"\n=== 分割后未找到任何SKU，重新用原始shop_num搜索 ===")
                    result, _, _ = parse_response(response_text, shop_num)
        
        return result

    try:
        # 第一次搜索
        response_text = send_search_request(search_value)
        result = execute_matching_logic(response_text, 'debug_response_1.html')
        
        # 如果还是没找到匹配的SKU，且variant不是UNI，尝试使用空格-空格格式
        if result[0] == "未找到商品SKU" and variant != "UNI":
            search_value = f"{title} - {variant}"  # 使用空格-空格
            print(f"\n第二次搜索值: {search_value}")
            
            response_text = send_search_request(search_value)
            result = execute_matching_logic(response_text, 'debug_response_2.html')
        
        # 新增功能：如果以上所有搜索都没有找到匹配的SKU，直接使用title搜索
        if result[0] == "未找到商品SKU":
            print(f"\n=== 第三次搜索：直接使用title ===")
            search_value = title
            print(f"第三次搜索值: {search_value}")
            
            response_text = send_search_request(search_value)
            result = execute_matching_logic(response_text, 'debug_response_3.html')
        
        print(f"\n=== 查询结束 ===")
        print(f"最终结果: {result}")
        return result
    
    except Exception as e:
        print(f"\n发生异常: {e}")
        import traceback
        traceback.print_exc()
        return f"发送请求或解析响应时出错: {e}"
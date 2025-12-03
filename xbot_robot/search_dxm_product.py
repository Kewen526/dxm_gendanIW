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
from bs4 import BeautifulSoup
import sys
import os

def load_cookies_from_file(cookie_file_path):
    """从JSON文件加载cookies"""
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        
        cookies = {}
        
        # 处理cookie文件格式
        if isinstance(cookies_data, dict) and 'cookies' in cookies_data:
            # 从cookies数组中提取name和value
            for cookie in cookies_data['cookies']:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
        # 如果是简单的cookies数组格式
        elif isinstance(cookies_data, list):
            for cookie in cookies_data:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
        # 如果是字典格式的cookies
        elif isinstance(cookies_data, dict):
            cookies = cookies_data
        else:
            print("不支持的cookie格式")
            return {}
            
        return cookies
            
    except FileNotFoundError:
        print(f"Cookie文件不存在: {cookie_file_path}")
        return {}
    except json.JSONDecodeError:
        print("Cookie文件格式错误，请确保是有效的JSON格式")
        return {}
    except Exception as e:
        print(f"加载cookie文件时出错: {e}")
        return {}

def search_dxm_product(search_value, shop_code, variant, cookie_file_path="1.json", debug=False):
    """
    搜索店小秘商品并返回符合条件的SKU名称
    
    Args:
        search_value (str): 搜索关键词
        shop_code (str): 店铺编码，优先查找SKU名称以此开头的商品，如果没有则查找包含此编码的商品
        variant (str): 变体信息，title中必须包含此内容
        cookie_file_path (str): cookie文件路径，默认为"1.json"
        debug (bool): 是否显示调试信息，默认False
    
    Returns:
        str: 找到的SKU名称，如果找到多个会返回第一个，未找到返回None
    """
    
    # 检查参数
    if not all([search_value, shop_code, variant]):
        if debug:
            print("❌ 搜索值、店铺编码和变体都不能为空！")
        return None
    
    # 检查cookie文件是否存在
    if not os.path.exists(cookie_file_path):
        if debug:
            print(f"❌ Cookie文件不存在: {cookie_file_path}")
        return None
    
    # 加载cookies
    cookies = load_cookies_from_file(cookie_file_path)
    if not cookies:
        if debug:
            print("❌ 无法加载cookies")
        return None
    
    if debug:
        print(f"✅ 成功加载 {len(cookies)} 个cookies")
    
    # 请求URL和headers
    url = "https://www.dianxiaomi.com/dxmCommodityProduct/pageList.htm"
    
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 请求数据
    data = {
        'pageNo': '1',
        'pageSize': '50',
        'searchType': '6',
        'searchValue': search_value,
        'productPxId': '1',
        'productPxSxId': '0',
        'fullCid': '',
        'productMode': '-1',
        'saleMode': '-1',
        'productSearchType': '0',
        'productGroupLxId': '1'
    }
    
    try:
        if debug:
            print(f"🔍 正在搜索: {search_value}")
            print(f"🏪 店铺编码: {shop_code}")
            print(f"🔖 变体: {variant}")
        
        # 发送POST请求
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        response.raise_for_status()
        
        # 解析HTML响应
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有符合条件的商品
        exact_results = []  # 存储SKU名称以shop_code开头的结果
        contains_results = []  # 存储SKU名称包含shop_code的结果
        
        # 查找所有goodsSKUName元素
        sku_elements = soup.find_all('span', class_='inline-block no-new-line maxW240 goodsSKUName white-space')
        
        if debug:
            print(f"📦 找到 {len(sku_elements)} 个SKU元素")
        
        for sku_element in sku_elements:
            sku_name = sku_element.get_text(strip=True)
            
            if debug:
                print(f"  检查SKU: {sku_name}")
            
            # 检查SKU名称是否以店铺编码开头或包含店铺编码
            is_starts_with = sku_name.startswith(shop_code)
            is_contains = shop_code in sku_name
            
            if is_starts_with or is_contains:
                if debug:
                    if is_starts_with:
                        print(f"    ✅ SKU以 '{shop_code}' 开头")
                    else:
                        print(f"    ✅ SKU包含 '{shop_code}'")
                
                # 查找同一行的title元素
                current_element = sku_element
                found_variant = False
                
                # 在当前元素的父级中查找包含variant的title
                for i in range(15):
                    current_element = current_element.parent
                    if current_element is None:
                        break
                    
                    # 查找当前元素及其子元素中是否有包含variant的title
                    title_elements = current_element.find_all(attrs={'title': True})
                    for title_element in title_elements:
                        title_text = title_element.get('title', '')
                        if title_text and variant.lower() in title_text.lower():
                            if debug:
                                print(f"    ✅ 找到匹配的变体: {title_text}")
                            found_variant = True
                            result = {
                                'sku_name': sku_name,
                                'title': title_text
                            }
                            # 根据SKU是以shop_code开头还是包含shop_code，分别添加到不同的结果列表
                            if is_starts_with:
                                exact_results.append(result)
                            else:
                                contains_results.append(result)
                            break
                    
                    if found_variant:
                        break
                
                if not found_variant and debug:
                    print(f"    ❌ 未找到包含 '{variant}' 的变体")
            elif debug:
                print(f"    ❌ SKU不包含 '{shop_code}'")
        
        # 优先返回以shop_code开头的结果，如果没有再返回包含shop_code的结果
        if exact_results:
            if debug:
                print(f"✅ 找到 {len(exact_results)} 个以'{shop_code}'开头的商品:")
                for i, result in enumerate(exact_results, 1):
                    print(f"  {i}. {result['sku_name']} - {result['title']}")
            return exact_results[0]['sku_name']
        elif contains_results:
            if debug:
                print(f"✅ 找到 {len(contains_results)} 个包含'{shop_code}'的商品:")
                for i, result in enumerate(contains_results, 1):
                    print(f"  {i}. {result['sku_name']} - {result['title']}")
            return contains_results[0]['sku_name']
        else:
            if debug:
                print("❌ 未找到符合条件的商品")
            return None
        
    except requests.exceptions.RequestException as e:
        if debug:
            print(f"❌ 请求失败: {e}")
        return None
    except Exception as e:
        if debug:
            print(f"❌ 处理响应时出错: {e}")
        return None

def search_dxm_product_all(search_value, shop_code, variant, cookie_file_path="1.json", debug=False):
    """
    搜索店小秘商品并返回所有符合条件的SKU名称列表
    
    Args:
        search_value (str): 搜索关键词
        shop_code (str): 店铺编码，优先查找SKU名称以此开头的商品，如果没有则查找包含此编码的商品
        variant (str): 变体信息，title中必须包含此内容
        cookie_file_path (str): cookie文件路径，默认为"1.json"
        debug (bool): 是否显示调试信息，默认False
    
    Returns:
        list: 所有匹配的结果列表，每个元素包含sku_name和title
    """
    
    # 检查参数
    if not all([search_value, shop_code, variant]):
        if debug:
            print("❌ 搜索值、店铺编码和变体都不能为空！")
        return []
    
    # 检查cookie文件是否存在
    if not os.path.exists(cookie_file_path):
        if debug:
            print(f"❌ Cookie文件不存在: {cookie_file_path}")
        return []
    
    # 加载cookies
    cookies = load_cookies_from_file(cookie_file_path)
    if not cookies:
        if debug:
            print("❌ 无法加载cookies")
        return []
    
    if debug:
        print(f"✅ 成功加载 {len(cookies)} 个cookies")
    
    # 请求URL和headers
    url = "https://www.dianxiaomi.com/dxmCommodityProduct/pageList.htm"
    
    headers = {
        'accept': 'text/html, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/dxmCommodityProduct/index.htm',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 请求数据
    data = {
        'pageNo': '1',
        'pageSize': '50',
        'searchType': '6',
        'searchValue': search_value,
        'productPxId': '1',
        'productPxSxId': '0',
        'fullCid': '',
        'productMode': '-1',
        'saleMode': '-1',
        'productSearchType': '0',
        'productGroupLxId': '1'
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=30)
        response.raise_for_status()
        
        # 解析HTML响应
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找所有符合条件的商品
        exact_results = []  # 存储SKU名称以shop_code开头的结果
        contains_results = []  # 存储SKU名称包含shop_code的结果
        
        # 查找所有goodsSKUName元素
        sku_elements = soup.find_all('span', class_='inline-block no-new-line maxW240 goodsSKUName white-space')
        
        if debug:
            print(f"📦 找到 {len(sku_elements)} 个SKU元素")
        
        for sku_element in sku_elements:
            sku_name = sku_element.get_text(strip=True)
            
            if debug:
                print(f"  检查SKU: {sku_name}")
            
            # 检查SKU名称是否以店铺编码开头或包含店铺编码
            is_starts_with = sku_name.startswith(shop_code)
            is_contains = shop_code in sku_name
            
            if is_starts_with or is_contains:
                if debug:
                    if is_starts_with:
                        print(f"    ✅ SKU以 '{shop_code}' 开头")
                    else:
                        print(f"    ✅ SKU包含 '{shop_code}'")
                
                # 查找同一行的title元素
                current_element = sku_element
                found_variant = False
                
                # 在当前元素的父级中查找包含variant的title
                for i in range(15):
                    current_element = current_element.parent
                    if current_element is None:
                        break
                    
                    # 查找当前元素及其子元素中是否有包含variant的title
                    title_elements = current_element.find_all(attrs={'title': True})
                    for title_element in title_elements:
                        title_text = title_element.get('title', '')
                        if title_text and variant.lower() in title_text.lower():
                            if debug:
                                print(f"    ✅ 找到匹配的变体: {title_text}")
                            found_variant = True
                            result = {
                                'sku_name': sku_name,
                                'title': title_text
                            }
                            # 根据SKU是以shop_code开头还是包含shop_code，分别添加到不同的结果列表
                            if is_starts_with:
                                exact_results.append(result)
                            else:
                                contains_results.append(result)
                            break
                    
                    if found_variant:
                        break
                
                if not found_variant and debug:
                    print(f"    ❌ 未找到包含 '{variant}' 的变体")
            elif debug:
                print(f"    ❌ SKU不包含 '{shop_code}'")
        
        # 优先返回以shop_code开头的结果，如果没有再返回包含shop_code的结果
        if exact_results:
            if debug:
                print(f"✅ 找到 {len(exact_results)} 个以'{shop_code}'开头的商品")
            return exact_results
        elif contains_results:
            if debug:
                print(f"✅ 找到 {len(contains_results)} 个包含'{shop_code}'的商品")
            return contains_results
        else:
            if debug:
                print("❌ 未找到符合条件的商品")
            return []
        
    except requests.exceptions.RequestException as e:
        if debug:
            print(f"❌ 请求失败: {e}")
        return []
    except Exception as e:
        if debug:
            print(f"❌ 处理响应时出错: {e}")
        return []

# 使用示例和测试函数
def test_dxm_search():
    """测试函数"""
    print("=== 店小秘商品搜索工具测试 ===")
    
    # 示例调用
    search_value = input("请输入搜索关键词: ").strip()
    shop_code = input("请输入店铺编码: ").strip()
    variant = input("请输入变体: ").strip()
    
    if not all([search_value, shop_code, variant]):
        print("❌ 所有参数都不能为空")
        return
    
    print("\n" + "="*50)
    print("开始搜索...")
    
    # 调用搜索函数（只返回第一个结果）
    result = search_dxm_product(search_value, shop_code, variant, debug=True)
    
    if result:
        print(f"\n🎯 找到的SKU: {result}")
    else:
        print("\n❌ 未找到符合条件的商品")
    
    print("\n" + "="*50)
    print("搜索所有结果...")
    
    # 调用搜索函数（返回所有结果）
    all_results = search_dxm_product_all(search_value, shop_code, variant, debug=True)
    
    if all_results:
        print(f"\n📋 找到 {len(all_results)} 个符合条件的商品:")
        for i, item in enumerate(all_results, 1):
            print(f"  {i}. {item['sku_name']}")
            print(f"     {item['title']}")
    else:
        print("\n❌ 未找到符合条件的商品")

if __name__ == "__main__":
    # 检查依赖库
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("请运行: pip install requests beautifulsoup4")
        sys.exit(1)
    
    # 运行测试
    test_dxm_search()
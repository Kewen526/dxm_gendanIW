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
import re

def get_dianxiaomi_product_ids(cookies_file_path, search_value):
    """
    从点小秘网站获取指定搜索值的产品ID列表、商品标题列表、图片URL列表、店铺名称列表和SKU列表
    
    参数:
        cookies_file_path (str): 包含cookies的JSON文件路径
        search_value (str): 搜索值，例如 '6682279-1470'
    
    返回:
        tuple: (
            list of str: 产品ID列表,
            list of str: 商品标题列表,
            list of str: 商品图片URL列表,
            list of str: 店铺名称列表,
            list of str: 商品SKU列表
        )
    """
    try:
        # 加载 cookies
        with open(cookies_file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        cookies = {}
        for cookie in cookies_data.get('cookies', []):
            if 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']

        # 请求头 & 表单数据
        headers = {
            'accept': 'text/html, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        data = {
            'searchType': '2',
            'searchValue': search_value,
            'status': '2',
            'shopId': '-1',
            'pt': 'all',
            'searchMode': '1',
            'pageNo': '1',
            'pageSize': '100'
        }

        # 发送请求
        url = 'https://www.dianxiaomi.com/dxmTempWishPairProduct/pageOrderList.htm'
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        if response.status_code != 200:
            raise Exception(f"请求失败，状态码: {response.status_code}")

        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取每行的 productBox 值、商品标题、图片URL、店铺名称和SKU
        raw_entries = []  # (id, title, img_url, shop_name, sku)
        rows = soup.find_all('tr', class_='content')
        for row in rows:
            checkbox = row.find('input', attrs={'name': 'productBox', 'type': 'checkbox'})
            if not checkbox or 'value' not in checkbox.attrs:
                continue
                
            prod_id = checkbox['value']
            cols = row.find_all('td', class_='f-left')
            
            # 获取店铺名称 (第3个td，索引为2)
            shop_name = cols[2].get_text(strip=True) if len(cols) > 2 else ''
            
            # 获取商品标题 (第4个td，索引为3)
            title = cols[3].get_text(strip=True) if len(cols) > 3 else ''
            
            # 获取图片URL
            img_tag = row.find('img', class_='img-css')
            img_url = img_tag['data-original'] if img_tag and img_tag.has_attr('data-original') else ''
            
            # 获取商品SKU信息 - 从commodity-con中找到第一个div的文本
            sku = ""
            commodity_div = row.find('div', class_='commodity-con')
            if commodity_div:
                first_div = commodity_div.find('div')
                if first_div:
                    sku_text = first_div.get_text(strip=True)
                    # 提取SKU部分，去掉" X 数字"部分
                    sku_match = re.match(r'(.+?)\s*X\s*\d+', sku_text)
                    if sku_match:
                        sku = sku_match.group(1).strip()
                    else:
                        sku = sku_text.strip()
            
            raw_entries.append((prod_id, title, img_url, shop_name, sku))

        # 去重并保持顺序
        seen = set()
        product_ids, titles, img_urls, shop_names, skus = [], [], [], [], []
        for pid, name, url, shop, sku in raw_entries:
            if pid not in seen:
                seen.add(pid)
                product_ids.append(pid)
                titles.append(name)
                img_urls.append(url)
                shop_names.append(shop)
                skus.append(sku)

        return product_ids, titles, img_urls, shop_names, skus

    except Exception as e:
        import traceback
        error_msg = f"处理过程中出错: {e}\n{traceback.format_exc()}"
        raise Exception(error_msg)
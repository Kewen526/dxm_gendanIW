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
import urllib.parse
from bs4 import BeautifulSoup

def get_ail_link(product_url, cookie_file_path):
    """
    从点小蜜网站获取阿里巴巴产品信息
    
    参数:
        product_url: 阿里巴巴产品链接
        cookie_file_path: 本地cookie JSON文件路径
    
    返回:
        产品名称字符串，如果获取失败返回None
    """
    
    # 读取本地cookie文件
    try:
        with open(cookie_file_path, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)
        print("成功读取cookie文件")
    except Exception as e:
        print(f"读取cookie文件失败: {e}")
        return None
    
    # 将cookie数据转换为requests可用的格式
    cookies = {}
    try:
        # 处理你提供的cookie文件格式
        if 'cookies' in cookies_data and isinstance(cookies_data['cookies'], list):
            for cookie in cookies_data['cookies']:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
        elif isinstance(cookies_data, list):
            # 如果直接是列表格式的cookies
            for cookie in cookies_data:
                if 'name' in cookie and 'value' in cookie:
                    cookies[cookie['name']] = cookie['value']
        elif isinstance(cookies_data, dict) and 'cookies' not in cookies_data:
            # 如果是直接的字典格式
            cookies = cookies_data
        
        print(f"成功解析 {len(cookies)} 个cookie")
    except Exception as e:
        print(f"解析cookie失败: {e}")
        return None
    
    # 请求的目标URL
    api_url = "https://www.dianxiaomi.com/alibabaProduct/getProductByUrl.htm"
    
    # 请求头设置
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/dxmTempWishPairProduct/index.htm',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    
    # 构造POST数据
    post_data = {
        'url': product_url,
        'fromWhere': 'pairProduct'
    }
    
    try:
        print("正在发送请求...")
        # 发送POST请求
        response = requests.post(
            api_url,
            headers=headers,
            cookies=cookies,
            data=post_data,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        # 检查响应状态
        response.raise_for_status()
        
        # 检查响应内容类型
        print(f"响应内容类型: {response.headers.get('content-type', 'unknown')}")
        print(f"响应内容长度: {len(response.text)}")
        
        # 打印响应内容的前500个字符用于调试
        print("响应内容预览:")
        print(response.text[:500])
        print("="*50)
        
        # 确保响应内容是字符串
        if not isinstance(response.text, str):
            print("响应内容不是字符串类型")
            return None
        
        # 检查响应是否为空
        if not response.text.strip():
            print("响应内容为空")
            return None
        
        # 解析HTML响应
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找产品名称 (在class="nameBox"的td标签中)
        name_box = soup.find('td', class_='nameBox')
        
        if name_box:
            product_name = name_box.get_text(strip=True)
            print(f"成功获取产品名称: {product_name}")
            return product_name
        else:
            print("未找到class='nameBox'的td标签")
            # 尝试其他可能的选择器
            name_elements = soup.find_all('td', string=lambda text: text and len(text.strip()) > 10)
            if name_elements:
                print("找到可能的产品名称元素:")
                for i, elem in enumerate(name_elements):
                    text = elem.get_text(strip=True)
                    print(f"  {i+1}: {text}")
                    # 如果文本长度合理且包含中文，可能是产品名称
                    if 10 < len(text) < 200 and any('\u4e00' <= char <= '\u9fff' for char in text):
                        print(f"选择最可能的产品名称: {text}")
                        return text
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None
    except Exception as e:
        print(f"解析响应失败: {e}")
        print(f"错误类型: {type(e).__name__}")
        # 打印更详细的错误信息
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return None

# 使用示例
if __name__ == "__main__":
    # 产品URL
    product_url = "https://detail.1688.com/offer/798222535275.html"
    
    # cookie文件路径
    cookie_file = "1.json"
    
    # 调用函数获取产品信息
    result = get_ail_link(product_url, cookie_file)
    
    if result:
        print(f"\n最终结果 - 产品名称: {result}")
    else:
        print("\n获取产品信息失败")
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

def batch_set_voided(cookie_file_path, package_ids):
    """
    批量设置包裹作废
    
    参数:
    cookie_file_path: cookie JSON文件路径
    package_ids: 包裹ID，可以是单个ID字符串或ID列表
    
    返回:
    操作结果（字典格式）
    """
    
    # 读取cookie文件
    with open(cookie_file_path, 'r', encoding='utf-8') as f:
        cookie_data = json.load(f)
    
    # 处理cookie格式
    cookies = {}
    
    # 如果数据包含"cookies"键
    if 'cookies' in cookie_data:
        cookies_list = cookie_data['cookies']
        for cookie in cookies_list:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
    
    # 如果直接是cookies数组
    elif isinstance(cookie_data, list):
        for cookie in cookie_data:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                cookies[cookie['name']] = cookie['value']
    
    # 如果是键值对格式
    elif isinstance(cookie_data, dict) and 'cookies' not in cookie_data:
        cookies = cookie_data
    
    # 处理package_ids参数
    if isinstance(package_ids, list):
        # 如果是列表，用逗号连接
        package_ids_str = ','.join(str(pid) for pid in package_ids)
    else:
        # 如果是单个ID，直接转换为字符串
        package_ids_str = str(package_ids)
    
    print(f"准备作废的包裹ID: {package_ids_str}")
    print(f"成功提取 {len(cookies)} 个cookie")
    
    # 构建cookie字符串
    cookie_string = '; '.join([f"{k}={v}" for k, v in cookies.items()])
    
    # 请求URL
    url = 'https://www.dianxiaomi.com/package/batchSetVoided.json'
    
    # 请求头
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': cookie_string,
        'origin': 'https://www.dianxiaomi.com',
        'priority': 'u=1, i',
        'referer': 'https://www.dianxiaomi.com/order/index.htm?go=m10201',
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
        'packageIds': package_ids_str
    }
    
    # 创建session
    session = requests.Session()
    
    try:
        # 发送POST请求
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # 打印响应状态
        print(f"响应状态码: {response.status_code}")
        
        # 尝试解析JSON响应
        try:
            result = response.json()
            print(f"操作结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查操作是否成功
            if isinstance(result, dict):
                if result.get('success') or result.get('code') == 200 or result.get('status') == 'success':
                    print("✓ 操作成功")
                else:
                    print("✗ 操作可能失败，请检查返回信息")
            
            return result
            
        except json.JSONDecodeError:
            print("响应不是有效的JSON格式")
            print(f"响应内容: {response.text[:500]}...")  # 只显示前500个字符
            
            # 检查是否返回了登录页面
            if '欢迎登录' in response.text or 'login' in response.text.lower():
                print("\n警告: 返回了登录页面，Cookie可能已失效")
                return {'error': '需要重新登录', 'response': response.text}
            
            return {'error': '响应格式错误', 'response': response.text}
        
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return {'error': str(e)}
    except Exception as e:
        print(f"发生错误: {e}")
        return {'error': str(e)}
    finally:
        session.close()

def batch_operation_example():
    """
    批量操作示例：先搜索包裹，然后批量作废
    """
    from search_package import search_package  # 导入之前的搜索函数
    
    # 配置
    cookie_path = "cookie.json"
    search_content = "QXL-wj3q7w-hf-1451-A"
    
    print("=== 步骤1: 搜索包裹 ===")
    package_ids = search_package(cookie_path, search_content)
    
    if package_ids:
        print(f"\n找到 {len(package_ids)} 个包裹")
        
        # 询问是否要作废这些包裹
        print("\n=== 步骤2: 批量作废 ===")
        confirm = input(f"是否要作废这 {len(package_ids)} 个包裹? (y/n): ")
        
        if confirm.lower() == 'y':
            result = batch_set_voided(cookie_path, package_ids)
            return result
        else:
            print("操作已取消")
            return None
    else:
        print("没有找到包裹，无法执行作废操作")
        return None

# 使用示例
if __name__ == "__main__":
    # 方式1: 直接指定包裹ID
    cookie_path = "cookie.json"
    
    # 单个包裹ID
    package_id = "54280086942075840"
    result = batch_set_voided(cookie_path, package_id)
    
    # 或者多个包裹ID
    # package_ids = ["54280086942075840", "54280086942075841", "54280086942075842"]
    # result = batch_set_voided(cookie_path, package_ids)
    
    # 方式2: 先搜索后批量操作（取消注释使用）
    # result = batch_operation_example()
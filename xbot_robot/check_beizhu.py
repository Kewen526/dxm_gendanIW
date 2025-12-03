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
from urllib import parse

def get_sku_result(title, shop_num):
    """
    发送请求获取sku_result值
    
    Args:
        title (str): 标题参数
        shop_num (str): 店铺编号参数
    
    Returns:
        str: sku_result的值，如果请求失败返回None
    """
    
    requestUrl = 'http://47.95.157.46:8520/api/if_shougongdan_beizhu'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {
        "title": title,
        "shop_num": shop_num
    }
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data)
        
        # 检查请求是否成功
        if response.status_code == 200:
            result = response.json()
            
            # 检查返回数据结构并提取sku_result
            if result.get('success') and result.get('data'):
                if len(result['data']) > 0 and 'sku_result' in result['data'][0]:
                    return result['data'][0]['sku_result']
                else:
                    print("未找到sku_result字段")
                    return None
            else:
                print(f"API返回错误: {result.get('msg', '未知错误')}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 调用函数示例
    sku_value = get_sku_result("12", "2")
    if sku_value:
        print(f"获取到的sku_result值: {sku_value}")
    else:
        print("获取sku_result失败")
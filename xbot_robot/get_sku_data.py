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
from urllib import parse
import json

def get_sku_data():
    requestUrl = 'http://47.95.157.46:8520/api/get_sku'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    formData = {
        # 添加你需要的表单数据
    }
    data = parse.urlencode(formData, True)
    
    try:
        response = requests.post(requestUrl, headers=headers, data=data)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应数据: {result}")
            
            # 检查响应是否成功
            if result.get('success'):
                data_list = result.get('data', [])
                
                # 检查 data[3] 是否为空列表
                if len(data_list) >= 4 and isinstance(data_list[3], list):
                    if not data_list[3]:  # 空列表的情况
                        print("返回 None (数据为空)")
                        return None
                    else:  # 有数据的情况
                        # 返回第一个字典对象
                        if len(data_list[3]) > 0 and isinstance(data_list[3][0], dict):
                            print("返回字典数据")
                            return data_list[3][0]
                        else:
                            print("数据格式异常")
                            return None
                else:
                    print("数据结构异常")
                    return None
            else:
                print(f"API 返回失败: {result.get('msg')}")
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")
        return None
    except Exception as e:
        print(f"其他错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    result = get_sku_data()
    
    if result is None:
        print("最终结果: None")
    else:
        print(f"最终结果: {result}")
        # 你可以访问字典中的具体字段
        print(f"任务状态: {result.get('task_status')}")
        print(f"店铺类型: {result.get('shop_type')}")
        print(f"发票ID: {result.get('invoice_id')}")
        print(f"订单ID: {result.get('order_id')}")
        print(f"分配轮次: {result.get('assignment_round')}")
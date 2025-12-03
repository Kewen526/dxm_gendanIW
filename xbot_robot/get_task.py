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
 
def get_task_info() -> list:
    """
    请求 Redis Ticker Info 接口并返回任务信息（列表格式）
 
    返回:
        list: 包含任务信息的列表，按顺序为 [id, order_id, intention_code, conductor]
    """
    url = "https://keepkeer.cn/api/external/get-redis-ticker-info"
    headers = {
        "Content-Type": "application/json"
    }
 
    try:
        response = requests.post(url, json={}, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(data)
        # 检查响应是否成功且包含所需数据
        if data.get('code') == 200 and 'data' in data:
            print(data)
            task_data = data['data']
            # 从数据中提取所需字段并以列表形式返回
            return [
                task_data.get('id'),
                task_data.get('order_id'),
                task_data.get('intention_code'),
                task_data.get('conductor')
            ]
        else:
            return [None, None, None, None]  # 返回空值列表表示无有效数据
    except requests.exceptions.RequestException as err:
        print(f"请求异常: {str(err)}")
        return [None, None, None, None]
    except ValueError:
        print("响应不是有效的 JSON 格式")
        return [None, None, None, None]
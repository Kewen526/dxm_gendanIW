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

def get_task_data():
    request_url = 'http://47.95.157.46:8520/api/task_reassigned_task'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {}
    data = parse.urlencode(form_data, True)
    
    response = requests.post(request_url, headers=headers, data=data)
    
    if response.status_code == 200:
        response_json = response.json()
        if response_json.get('success'):
            # Check the structure of the response
            data_array = response_json['data']
            
            # Find the task data list in the response
            task_data = None
            for item in data_array:
                if isinstance(item, list) and len(item) > 0 and isinstance(item[0], dict):
                    task_data = item[0]
                    break
            
            if task_data:
                return task_data
            else:
                print("Could not find task data in the response")
                return None
        else:
            print("Request was not successful. Message:", response_json.get('msg'))
            return None
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return None

# Example usage
if __name__ == "__main__":
    result = get_task_data()
    print(result)
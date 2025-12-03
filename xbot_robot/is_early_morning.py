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
from datetime import datetime

def is_early_morning():
    current_time = datetime.now()
    current_hour = current_time.hour
    
    # 检查小时是否在0(午夜)到2(包含)之间
    # 这覆盖了00:00到02:59:59
    if 0 <= current_hour < 3:
        return True
    else:
        return False

# 使用示例
if __name__ == "__main__":
    result = is_early_morning()
    print(result)
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
def is_one_dimensional(lst):
    # 如果列表中没有任何元素，认为是一维列表
    if not lst:
        return True
    # 如果列表中任何一个元素是列表，就认为是二维列表
    return not any(isinstance(i, list) for i in lst)
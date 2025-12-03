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
def find_first_match(channel_dict, keyword):
    # 按渠道名称进行模糊搜索
    matches = [(name, cid) for name, cid in channel_dict.items() if keyword in name]
    
    if matches:
        # 返回第一个匹配项
        return matches[0]
    else:
        return None

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

def parse_variant_string(variant_string):
    """
    传入字符串形式的 SKU JSON 列表，返回 Python 列表对象。
    """
    try:
        result = json.loads(variant_string)
        if not isinstance(result, list):
            raise ValueError("解析结果不是列表")
        return result
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON解析失败: {e}")

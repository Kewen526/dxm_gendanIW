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

def convert_to_list(data: str):
    try:
        # 第一次解析（把外层字符串解析成 list[str]）
        first = json.loads(data)
    except Exception:
        try:
            first = eval(data)
        except Exception as e:
            raise ValueError(f"第一次解析失败: {e}")

    # 如果解析后还是 list 且里面第一个是字符串，再解析一次
    if isinstance(first, list) and len(first) == 1 and isinstance(first[0], str):
        try:
            second = json.loads(first[0])
        except Exception:
            try:
                second = eval(first[0])
            except Exception as e:
                raise ValueError(f"第二次解析失败: {e}")
        return second

    if not isinstance(first, list):
        raise TypeError("转换结果不是列表")
    return first

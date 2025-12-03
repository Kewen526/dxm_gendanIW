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
def is_all_empty(data_dict):
    """
    检查字典中的 shipments_remark、remark 列表和 huo_remark 是否都“为空”
    如果都为空，返回 True，否则返回 False

    空的定义:
    - 对于列表、字符串：所有元素或字符串 本身
        - 为空字符串或只包含空格
        - 或者等于 "--"
    """
    def is_empty_value(val):
        """
        判断单个值是否为空：
        - val.strip() 结果为空
        - 或 val.strip() 等于 "--"
        """
        text = str(val).strip()
        return text == "" or text == "--"

    # 检查 shipments_remark 列表
    for item in data_dict.get('shipments_remark', []):
        if not is_empty_value(item):
            return False

    # 检查 remark 列表
    for item in data_dict.get('remark', []):
        if not is_empty_value(item):
            return False

    # 检查 huo_remark 字符串
    if not is_empty_value(data_dict.get('huo_remark', "")):
        return False

    # 全部都是“空”值
    return True

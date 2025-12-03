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
import re
from bs4 import BeautifulSoup

def extract_variants(html):
    """
    从HTML中提取所有出现在"Variants："后面的值
    
    参数:
        html (str): 需要解析的HTML内容
    
    返回:
        list: 包含所有提取出的变体值的列表
    """
    # 创建列表用于存储提取的变体信息
    variants = []
    
    # 方法一：使用正则表达式查找所有匹配项
    # 正则表达式：查找在"Variants："后面且在"</span>"前面的所有文本
    pattern = r'Variants：([^<]+)</span>'
    matches = re.findall(pattern, html)
    
    # 将匹配结果添加到变体列表中，并去除前后空格
    variants = [match.strip() for match in matches]
    
    # 方法二(备选方案)：使用BeautifulSoup解析HTML
    # 如果需要使用此方法，请取消下面代码的注释
    """
    # 创建BeautifulSoup对象解析HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有包含class="isOverLengThHide"的span标签
    spans = soup.find_all('span', class_='isOverLengThHide')
    
    # 遍历所有span标签
    for span in spans:
        text = span.text
        # 检查span中是否包含"Variants："
        if 'Variants：' in text:
            # 提取"Variants："后面的文本
            variant = text.split('Variants：')[1].strip()
            variants.append(variant)
    """
    
    return variants
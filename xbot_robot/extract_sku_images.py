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

def extract_sku_images(data_str):
    try:
        # Parse the data string into a Python dictionary
        if isinstance(data_str, str):
            data = json.loads(data_str)
        else:
            data = data_str
        
        # Get the variants list
        variants = data.get('alibabaProduct', {}).get('dxmTempAlibabaVariantList', [])
        
        # Extract unique image URLs (removing trailing pipe characters)
        image_urls = set()
        for variant in variants:
            if 'mainImg' in variant and variant['mainImg']:
                img_url = variant['mainImg'].rstrip('|')
                image_urls.add(img_url)
        
        return list(image_urls)
    except Exception as e:
        return f"Error processing data: {str(e)}"
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
def extract_skuids(data_str):
    """
    Extract all SKU IDs from the provided data and return as comma-separated string
    
    Args:
        data_str (str): Data containing Alibaba product information
    
    Returns:
        str: Comma-separated string of SKU IDs
    """
    try:
        # Try to handle the data in different formats
        if isinstance(data_str, str):
            # Check if it's a JSON string
            try:
                import json
                data_dict = json.loads(data_str)
            except json.JSONDecodeError:
                # If it's not valid JSON, try to treat it as a Python dict literal
                import ast
                try:
                    data_dict = ast.literal_eval(data_str)
                except:
                    return "Error: Unable to parse the data string"
        else:
            # Already a dictionary
            data_dict = data_str
        
        # Extract SKU IDs
        sku_ids = []
        
        # Check if the expected structure exists
        if 'alibabaProduct' in data_dict and 'dxmTempAlibabaVariantList' in data_dict['alibabaProduct']:
            for variant in data_dict['alibabaProduct']['dxmTempAlibabaVariantList']:
                if 'skuId' in variant:
                    sku_ids.append(variant['skuId'])
        
        # Join the SKU IDs with commas
        result = ','.join(sku_ids)
        return result
    
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
# result = extract_skuids(your_data_string)
# print(result)
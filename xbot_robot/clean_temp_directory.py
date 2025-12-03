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
import os
import shutil
import tempfile
import time

def clean_temp_directory():
    """
    清空Windows临时目录中的文件和文件夹
    跳过无法删除的文件（如被占用的文件）
    """
    # 获取系统临时目录路径
    temp_dir = tempfile.gettempdir()
    print(f"正在清理临时目录: {temp_dir}")
    
    # 统计变量
    total_files = 0
    total_dirs = 0
    deleted_files = 0
    deleted_dirs = 0
    skipped_items = 0
    
    # 遍历临时目录中的所有文件和文件夹
    for item in os.listdir(temp_dir):
        item_path = os.path.join(temp_dir, item)
        
        try:
            if os.path.isfile(item_path):
                total_files += 1
                os.remove(item_path)
                deleted_files += 1
                print(f"已删除文件: {item}")
            elif os.path.isdir(item_path):
                total_dirs += 1
                shutil.rmtree(item_path, ignore_errors=False)
                deleted_dirs += 1
                print(f"已删除文件夹: {item}")
        except (PermissionError, OSError) as e:
            skipped_items += 1
            print(f"无法删除 {item}: {e}")
            continue
    
    # 打印统计结果
    print("\n清理完成!")
    print(f"扫描文件总数: {total_files}")
    print(f"扫描文件夹总数: {total_dirs}")
    print(f"成功删除文件数: {deleted_files}")
    print(f"成功删除文件夹数: {deleted_dirs}")
    print(f"跳过的项目数: {skipped_items}")
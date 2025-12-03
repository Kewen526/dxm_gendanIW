# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from . import package
from .package import variables as glv

def main(args):
    pass

import pymysql
from datetime import datetime
import logging

def check_and_clear_tables():
    """
    检查当前时间是否为凌晨12点（00点），如果是则清空指定的数据库表格
    返回: (bool, str) - (是否执行了清空操作, 状态消息)
    """
   
    # 数据库连接配置
    db_config = {
        'host': '47.95.157.46',
        'user': 'root',
        'password': 'root@kunkun',
        'port': 3306,
        'database': 'order_tracking_iw',
        'charset': 'utf8mb4'
    }
   
    # 要清空的表格列表
    tables_to_clear = ['task', 'order_details', 'task_dispatch', 'kpi_report_info', 'kpi_report']
   
    try:
        # 检查当前时间是否为凌晨12点（00点这个小时）
        current_time = datetime.now()
        if current_time.hour != 0:
            return False, f"当前时间为 {current_time.strftime('%H:%M:%S')}，不是凌晨12点，无需清空表格"
       
        # 连接数据库
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
       
        # 清空表格
        cleared_tables = []
        for table in tables_to_clear:
            try:
                # 使用TRUNCATE快速清空表格（保留表结构）
                cursor.execute(f"TRUNCATE TABLE `{table}`")
                cleared_tables.append(table)
                print(f"成功清空表格: {table}")
            except Exception as e:
                print(f"清空表格 {table} 时出错: {str(e)}")
                # 如果TRUNCATE失败，尝试使用DELETE
                try:
                    cursor.execute(f"DELETE FROM `{table}`")
                    cleared_tables.append(table)
                    print(f"使用DELETE成功清空表格: {table}")
                except Exception as e2:
                    print(f"DELETE清空表格 {table} 也失败: {str(e2)}")
       
        # 提交事务
        connection.commit()
       
        # 关闭连接
        cursor.close()
        connection.close()
       
        if cleared_tables:
            return True, f"凌晨12点检测成功，已清空表格: {', '.join(cleared_tables)}"
        else:
            return False, "虽然是凌晨12点，但没有成功清空任何表格"
           
    except pymysql.Error as e:
        return False, f"数据库连接或操作错误: {str(e)}"
    except Exception as e:
        return False, f"发生未知错误: {str(e)}"

# 使用示例
if __name__ == "__main__":
    success, message = check_and_clear_tables()
    print(message)
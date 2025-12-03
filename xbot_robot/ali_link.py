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
import pymysql

# 数据库配置
# 修改为使用 pymysql 连接，不使用 mysql-connector-python
db_config = {
    "user": "gocrm",
    "password": "4ijmvv7U",
    "host": "rm-j6ce98dcz1z47ee42so.mysql.rds.aliyuncs.com",
    "port": 3306,
    "database": "gocrm",
    "connect_timeout": 10
}


def get_ali_link(shop_name, product_title):
    """
    根据店铺名称和商品标题查找ali_link
    
    参数:
        shop_name (str): 店铺名称，对应 product 表中的 shop_num 列
        product_title (str): 商品标题
    
    返回:
        str: 找到匹配的 ali_link 或空字符串
    """
    print(f"\n开始查询 - 店铺: '{shop_name}', 标题: '{product_title}'")

    try:
        # 建立数据库连接
        conn = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            port=db_config["port"],
            connect_timeout=db_config["connect_timeout"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()

        # 查询逻辑与原代码一致
        query = """
        SELECT * FROM `gocrm`.`product`
        WHERE `shop_num` LIKE %s
        AND `customer_english_title` LIKE %s
        LIMIT 1000
        """
        shop_pattern = f"%{shop_name}%"
        title_pattern = f"%{product_title}%"
        print(f"执行SQL: SELECT * FROM `gocrm`.`product` WHERE `shop_num` LIKE '%{shop_name}%' AND `customer_english_title` LIKE '%{product_title}%' LIMIT 1000")

        cursor.execute(query, (shop_pattern, title_pattern))
        results = cursor.fetchall()
        print(f"查询返回 {len(results)} 条结果")

        # 输出前 5 条结果
        for i, item in enumerate(results[:5], start=1):
            print(f"结果 #{i}:")
            print(f"  shop_num: '{item['shop_num']}'")
            print(f"  customer_english_title: '{item['customer_english_title']}'")
            if 'ali_link' in item:
                print(f"  ali_link: '{item['ali_link']}'")
            else:
                print("  警告: 结果中没有 ali_link 字段")

        # 返回第一个匹配项的 ali_link
        if results and 'ali_link' in results[0]:
            print(f"返回第一个结果的 ali_link: '{results[0]['ali_link']}'")
            return results[0]['ali_link']
        elif results:
            print("警告: 结果中没有 ali_link 字段")
            print(f"返回的字段有: {', '.join(results[0].keys())}")
            return ""
        else:
            print("没有找到匹配记录")
            # 验证单独查询行为
            verify_query = "SELECT COUNT(*) as count FROM `gocrm`.`product` WHERE `shop_num` LIKE %s"
            cursor.execute(verify_query, (shop_pattern,))
            shop_count = cursor.fetchone()['count']
            print(f"仅用 shop_num 查询找到 {shop_count} 条记录")

            title_query = "SELECT COUNT(*) as count FROM `gocrm`.`product` WHERE `customer_english_title` LIKE %s"
            cursor.execute(title_query, (title_pattern,))
            title_count = cursor.fetchone()['count']
            print(f"仅用 customer_english_title 查询找到 {title_count} 条记录")

            direct_query = f"""
            SELECT * FROM `gocrm`.`product`
            WHERE `shop_num` LIKE '%{shop_name}%'
            AND `customer_english_title` LIKE '%{product_title}%'
            LIMIT 5
            """
            print(f"尝试直接 SQL 查询: {direct_query}")
            try:
                cursor.execute(direct_query)
                direct_results = cursor.fetchall()
                print(f"直接 SQL 查询返回 {len(direct_results)} 条结果")
            except Exception as e:
                print(f"直接 SQL 查询出错: {e}")
            return ""

    except Exception as e:
        print(f"查询过程中发生错误: {e}")
        import traceback
        print(f"错误详情: {traceback.format_exc()}")
        return ""

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
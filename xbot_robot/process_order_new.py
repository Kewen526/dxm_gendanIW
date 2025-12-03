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
import requests
import pymysql
from urllib import parse
import json
import time

def get_order_data(order_id):
    """调用API获取订单数据"""
    print(f"开始获取订单数据，订单ID: {order_id}")
    
    try:
        request_url = 'http://47.95.157.46:8520/api/order'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        form_data = {"order_id": order_id}
        data = parse.urlencode(form_data, True)
        
        # 发送请求
        response = requests.post(request_url, headers=headers, data=data)
        
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 直接使用内容解析为JSON
            content = response.content.decode('utf-8')
            print(f"API原始响应: {content}")
            
            # 尝试解析JSON
            try:
                json_data = json.loads(content)
                print("JSON解析成功")
                return json_data
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                print("响应不是有效的JSON格式")
                return None
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"API请求发生异常: {e}")
        return None

def generate_ali_sku(stop_product_variant, special_pairing):
    """根据stop_product_variant和special_pairing生成ali_sku列表"""
    print(f"开始生成ali_sku，stop_product_variant: {stop_product_variant}")
    print(f"special_pairing: {special_pairing}")
    
    try:
        # 解析stop_product_variant为列表
        variant_list = []
        if stop_product_variant:
            try:
                parsed_variant = json.loads(stop_product_variant)
                if isinstance(parsed_variant, list):
                    variant_list = parsed_variant
                else:
                    variant_list = [str(parsed_variant)]
            except (json.JSONDecodeError, TypeError):
                variant_list = [str(stop_product_variant)]
        
        print(f"解析后的variant_list: {variant_list}")
        
        # 解析special_pairing获取映射关系
        pairing_dict = {}
        if special_pairing:
            try:
                pairing_data = json.loads(special_pairing)
                print(f"解析后的pairing_data: {pairing_data}")
                
                if isinstance(pairing_data, list) and len(pairing_data) > 0:
                    # 检查第一个元素是否是字符串（嵌套JSON）
                    if isinstance(pairing_data[0], str):
                        try:
                            inner_data = json.loads(pairing_data[0])
                            print(f"嵌套解析后的inner_data: {inner_data}")
                            if isinstance(inner_data, list):
                                for item in inner_data:
                                    if isinstance(item, dict) and 'customerVariant' in item and 'alibabaSku' in item:
                                        pairing_dict[item['customerVariant']] = item['alibabaSku']
                        except (json.JSONDecodeError, TypeError):
                            print("嵌套JSON解析失败")
                    else:
                        # 直接是字典列表
                        for item in pairing_data:
                            if isinstance(item, dict) and 'customerVariant' in item and 'alibabaSku' in item:
                                pairing_dict[item['customerVariant']] = item['alibabaSku']
                                
            except (json.JSONDecodeError, TypeError) as e:
                print(f"解析special_pairing失败: {e}")
        
        print(f"生成的pairing_dict: {pairing_dict}")
        
        # 生成ali_sku列表
        sku_list = []
        for variant in variant_list:
            if str(variant) in pairing_dict:
                sku_list.append(pairing_dict[str(variant)])
                print(f"找到匹配: {variant} -> {pairing_dict[str(variant)]}")
            else:
                sku_list.append("")
                print(f"未找到匹配: {variant} -> 空值")
        
        print(f"最终生成的sku_list: {sku_list}")
        return sku_list
        
    except Exception as e:
        print(f"生成ali_sku时发生错误: {e}")
        return []

def check_table_structure(connection):
    """检查表结构和主键信息"""
    try:
        with connection.cursor() as cursor:
            # 检查表结构
            cursor.execute("SHOW CREATE TABLE order_details")
            create_table = cursor.fetchone()
            print(f"表创建语句: {create_table}")
            
            # 检查主键信息
            cursor.execute("SHOW KEYS FROM order_details WHERE Key_name = 'PRIMARY'")
            primary_keys = cursor.fetchall()
            print("主键信息:")
            for key in primary_keys:
                print(f"  {key}")
                
    except Exception as e:
        print(f"检查表结构时发生错误: {e}")

def insert_into_database(order_id, intention_id, api_data):
    """将数据插入数据库"""
    print("开始插入数据到数据库...")
    connection = None
    
    try:
        # 验证API数据
        if not api_data or not isinstance(api_data, dict):
            print(f"API数据无效: {api_data}")
            return False
            
        if not api_data.get('success') or not api_data.get('data'):
            print(f"API返回无成功数据: {api_data}")
            return False
            
        # 获取订单信息
        order_info = api_data['data'][0]
        print(f"订单信息: {order_info}")
        
        # 检查waybill_num是否为空
        waybill_num = order_info.get('waybill_num', '')
        if waybill_num:
            print(f"运单号不为空，值为: {waybill_num}，跳过数据库写入")
            return False
        
        # 处理customer_english_title以生成status字段
        customer_english_title = order_info.get('customer_english_title', '')
        try:
            # 尝试将customer_english_title解析为列表
            title_list = json.loads(customer_english_title)
            # 获取列表长度
            list_length = len(title_list)
        except (json.JSONDecodeError, TypeError):
            # 解析失败时，默认长度为1，确保至少有一个空字符串
            print(f"无法解析customer_english_title为JSON: {customer_english_title}")
            list_length = 1
            
        # 确保list_length至少为1，保证status至少有一个空字符串元素
        list_length = max(1, list_length)
        
        # 创建相同长度的空列表并转换为JSON字符串，使用separators去除空格
        status_list = [""] * list_length
        status_json = json.dumps(status_list, separators=(',', ':'))
        print(f"生成的status值: {status_json}")
        
        # 生成ali_sku字段
        stop_product_variant = order_info.get('stop_product_variant', '')
        special_pairing = order_info.get('special_pairing', '')
        ali_sku_list = generate_ali_sku(stop_product_variant, special_pairing)
        ali_sku_json = json.dumps(ali_sku_list, separators=(',', ':'), ensure_ascii=False)
        print(f"生成的ali_sku值: {ali_sku_json}")
        
        # 连接数据库
        connection = pymysql.connect(
            host='47.95.157.46',
            user='root',
            password='root@kunkun',
            database='order_tracking_iw',
            port=3306,
            charset='utf8mb4'
        )
        
        # 检查表结构
        print("===检查表结构===")
        check_table_structure(connection)
        
        with connection.cursor() as cursor:
            # 查看实际的主键是什么
            print(f"尝试查找可能存在的记录...")
            cursor.execute("SELECT order_id, intention_id FROM order_details WHERE order_id = %s", [order_id])
            existing_records = cursor.fetchall()
            print(f"找到的同order_id记录: {existing_records}")
            
            # 构建数据字典
            data = {
                'order_id': order_id,
                'intention_id': intention_id,
                'shop_num': order_info.get('shop_num', ''),
                'waybill_num': waybill_num,
                'info': order_info.get('info', ''),
                'package_id': order_info.get('package_id', ''),
                'shipments_remark': order_info.get('shipments_remark', ''),
                'ali_buyer_word': order_info.get('ali_buyer_word', ''),
                'purchase_remark': order_info.get('purchase_remark', ''),
                'remark': order_info.get('remark', ''),
                'special_pairing': order_info.get('special_pairing', ''),
                'huo_remark': order_info.get('huo_remark', ''),
                'nation': order_info.get('nation', ''),
                'channel': order_info.get('channel', ''),
                'channel_remark': order_info.get('channel_remark', ''),
                'customer_english_title': order_info.get('customer_english_title', ''),
                'stop_product_variant': order_info.get('stop_product_variant', ''),
                'num': order_info.get('num', ''),
                'ali_link': order_info.get('ali_link', ''),
                'product_sku_info': order_info.get('product_sku_info', ''),
                'product_img': order_info.get('product_img', ''),
                'status': status_json,
                'ali_sku': ali_sku_json
            }
            
            # 尝试先用ON DUPLICATE KEY UPDATE的方式
            columns = list(data.keys())
            values = list(data.values())
            
            columns_str = ", ".join(f"`{col}`" for col in columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            # 构建ON DUPLICATE KEY UPDATE部分
            update_parts = [f"`{col}` = VALUES(`{col}`)" for col in columns if col not in ['order_id']]
            update_str = ", ".join(update_parts)
            
            sql = f"""
            INSERT INTO order_details ({columns_str}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_str}
            """
            
            print(f"执行INSERT ON DUPLICATE KEY UPDATE SQL")
            print(f"ali_sku值: {ali_sku_json}")
            
            cursor.execute(sql, values)
            affected_rows = cursor.rowcount
            print(f"操作影响行数: {affected_rows}")
            
            connection.commit()
            
            # 验证结果
            cursor.execute("SELECT ali_sku FROM order_details WHERE order_id = %s", [order_id])
            result = cursor.fetchone()
            print(f"最终ali_sku值: {result}")
            
            print("数据操作成功!")
            return True
            
    except Exception as e:
        print(f"数据库操作失败: {e}")
        if connection:
            connection.rollback()
        return False
        
    finally:
        if connection:
            connection.close()
            print("数据库连接已关闭")

def process_order(order_id, intention_id):
    """处理订单的主函数"""
    print("===开始处理订单===")
    start_time = time.time()
    
    try:
        # 1. 获取API响应
        api_data = get_order_data(order_id)
        if not api_data:
            print("无法获取API数据，处理终止")
            return False
            
        # 2. 插入数据库
        result = insert_into_database(order_id, intention_id, api_data)
        
        end_time = time.time()
        print(f"===处理完成，耗时: {end_time - start_time:.2f}秒, 结果: {'成功' if result else '失败'}===")
        return result
        
    except Exception as e:
        print(f"处理过程中发生错误: {e}")
        return False
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
        
        # 首先检查订单级别的字段 huo_remark
        huo_remark = order_info.get('huo_remark', '')
        if huo_remark:
            print(f"huo_remark不为空('{huo_remark}')，跳过整个订单")
            return False
        
        # 安全解析JSON数组字段，确保正确处理Unicode
        def safe_parse_json_array(json_str, default=None):
            if default is None:
                default = []
            try:
                if not json_str:
                    return default
                # 解析JSON字符串
                if isinstance(json_str, str):
                    parsed = json.loads(json_str)
                    # 打印解析后的内容以便调试
                    print(f"解析JSON: {json_str} -> {parsed}")
                    return parsed if isinstance(parsed, list) else default
                else:
                    print(f"非字符串输入: {json_str}")
                    return default
            except json.JSONDecodeError as e:
                print(f"无法解析JSON数组: {json_str}, 错误: {e}")
                return default

        # 解析各个数组字段
        remark_array = safe_parse_json_array(order_info.get('remark', '[]'))
        shipments_remark_array = safe_parse_json_array(order_info.get('shipments_remark', '[]'))
        num_array = safe_parse_json_array(order_info.get('num', '[]'))
        special_pairing_array = safe_parse_json_array(order_info.get('special_pairing', '[]'))
        ali_buyer_word_array = safe_parse_json_array(order_info.get('ali_buyer_word', '[]'))
        purchase_remark_array = safe_parse_json_array(order_info.get('purchase_remark', '[]'))
        customer_english_title_array = safe_parse_json_array(order_info.get('customer_english_title', '[]'))
        stop_product_variant_array = safe_parse_json_array(order_info.get('stop_product_variant', '[]'))
        ali_link_array = safe_parse_json_array(order_info.get('ali_link', '[]'))
        
        # 打印解析后的中文数据
        print(f"解析后的字段数组:")
        print(f"remark_array: {remark_array}")
        print(f"shipments_remark_array: {shipments_remark_array}")
        print(f"customer_english_title_array: {customer_english_title_array}")
        
        # 确定哪些商品满足条件（remark和shipments_remark都为空）
        valid_product_indices = []
        for i in range(max(len(remark_array), len(shipments_remark_array))):
            remark_value = remark_array[i] if i < len(remark_array) else ""
            shipments_remark_value = shipments_remark_array[i] if i < len(shipments_remark_array) else ""
            
            if not remark_value and not shipments_remark_value:
                valid_product_indices.append(i)
        
        print(f"符合条件的商品索引: {valid_product_indices}")
        
        if not valid_product_indices:
            print("没有符合条件的商品，跳过数据库插入")
            return False
        
        # 过滤数组字段的辅助函数
        def filter_array(array, indices):
            return [array[i] if i < len(array) else "" for i in indices]
        
        # 过滤数组字段，只保留符合条件的商品
        filtered_data = {
            'order_id': order_id,
            'intention_id': intention_id,
            'shop_num': order_info.get('shop_num', ''),
            'waybill_num': order_info.get('waybill_num', ''),
            'info': order_info.get('info', ''),
            'package_id': order_info.get('package_id', ''),
            'huo_remark': huo_remark,
            'nation': order_info.get('nation', ''),
            'channel': order_info.get('channel', ''),
            'channel_remark': order_info.get('channel_remark', ''),
            'product_sku_info': order_info.get('product_sku_info', ''),
            
            # 使用ensure_ascii=False确保中文字符不被转义为Unicode
            'remark': json.dumps(filter_array(remark_array, valid_product_indices), ensure_ascii=False),
            'shipments_remark': json.dumps(filter_array(shipments_remark_array, valid_product_indices), ensure_ascii=False),
            'num': json.dumps(filter_array(num_array, valid_product_indices), ensure_ascii=False) if num_array else '',
            'special_pairing': json.dumps(filter_array(special_pairing_array, valid_product_indices), ensure_ascii=False) if special_pairing_array else '',
            'ali_buyer_word': json.dumps(filter_array(ali_buyer_word_array, valid_product_indices), ensure_ascii=False) if ali_buyer_word_array else '',
            'purchase_remark': json.dumps(filter_array(purchase_remark_array, valid_product_indices), ensure_ascii=False) if purchase_remark_array else '',
            'customer_english_title': json.dumps(filter_array(customer_english_title_array, valid_product_indices), ensure_ascii=False) if customer_english_title_array else '',
            'stop_product_variant': json.dumps(filter_array(stop_product_variant_array, valid_product_indices), ensure_ascii=False) if stop_product_variant_array else '',
            'ali_link': json.dumps(filter_array(ali_link_array, valid_product_indices), ensure_ascii=False) if ali_link_array else ''
        }
        
        print(f"过滤后的数据: {filtered_data}")
        
        # 连接数据库
        connection = pymysql.connect(
            host='47.95.157.46',
            user='root',
            password='root@kunkun',
            database='order_tracking_iw',
            port=3306,
            charset='utf8mb4'  # 确保使用utf8mb4字符集以支持所有Unicode字符
        )
        
        with connection.cursor() as cursor:
            # 获取所有列名和值
            columns = list(filtered_data.keys())
            values = list(filtered_data.values())
            
            # 构建SQL插入语句
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            sql = f"INSERT INTO order_details ({columns_str}) VALUES ({placeholders})"
            
            print(f"执行SQL: {sql}")
            
            # 执行插入
            cursor.execute(sql, values)
            connection.commit()
            
            print("数据插入成功!")
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
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单数据批量导入脚本（优化版 - 修复None值问题）
支持批量新增和更新订单数据到MySQL数据库
优化：减少数据库交互次数，分批提交，降低数据库压力
修复：处理productList和attrList为None的情况
"""

import pymysql
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime


class OrderBatchImporter:
    """订单批量数据导入器"""
    
    def __init__(self, host='47.104.72.198', user='root', password='Kewen888@', 
                 database='dxm_info', port=3306, batch_size=100):
        """
        初始化数据库连接
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名
            port: 数据库端口
            batch_size: 批次大小，每次提交的订单数量（默认100）
        """
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        self.batch_size = batch_size
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def _safe_get_list(self, data: dict, key: str, default: list = None) -> list:
        """
        安全获取列表值，如果是None则返回空列表
        
        Args:
            data: 字典数据
            key: 键名
            default: 默认值
            
        Returns:
            list: 列表值，确保不会是None
        """
        if default is None:
            default = []
        value = data.get(key, default)
        # 如果值是None，返回空列表
        return value if value is not None else []
    
    def _prepare_order_params(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """准备订单参数"""
        return {
            'orderId': order.get('orderId'),
            'id': order.get('id'),
            'puid': order.get('puid'),
            'shopId': order.get('shopId'),
            'originId': order.get('originId'),
            'parentId': order.get('parentId'),
            'splitParentId': order.get('splitParentId'),
            'extendedOrderId': order.get('extendedOrderId'),
            'orderAmount': order.get('orderAmount'),
            'orderUnit': order.get('orderUnit'),
            'shipAmount': order.get('shipAmount', 0),
            'refundAmountUsd': order.get('refundAmountUsd', 0),
            'platform': order.get('platform'),
            'buyerName': order.get('buyerName'),
            'contactName': order.get('contactName'),
            'buyerAccount': order.get('buyerAccount'),
            'buyerCountry': order.get('buyerCountry'),
            'orderState': order.get('orderState'),
            'orderStatePlatform': order.get('orderStatePlatform'),
            'forbiddenState': order.get('forbiddenState', 0),
            'forbiddenReason': order.get('forbiddenReason', 0),
            'packageState': order.get('packageState'),
            'interceptState': order.get('interceptState', -1),
            'errorState': order.get('errorState'),
            'errorMsg': order.get('errorMsg'),
            'orderCreateTime': order.get('orderCreateTime'),
            'orderPayTime': order.get('orderPayTime'),
            'orderTimeoutTime': order.get('orderTimeoutTime'),
            'paidTime': order.get('paidTime'),
            'approvedTime': order.get('approvedTime'),
            'processedTime': order.get('processedTime'),
            'distributeTime': order.get('distributeTime'),
            'outStockTime': order.get('outStockTime'),
            'shippedTime': order.get('shippedTime'),
            'refunedTime': order.get('refunedTime'),
            'createTime': order.get('createTime'),
            'updateTime': order.get('updateTime'),
            'packageNumber': order.get('packageNumber'),
            'trackingNumber': order.get('trackingNumber'),
            'newTrackingNumber': order.get('newTrackingNumber'),
            'agentTrackNum': order.get('agentTrackNum'),
            'agentProviderName': order.get('agentProviderName', ''),
            'forwardOrderId': order.get('forwardOrderId'),
            'sku': order.get('sku'),
            'productSku': order.get('productSku'),
            'skuCount': order.get('skuCount', 0),
            'storageId': order.get('storageId'),
            'goodsShelfName': order.get('goodsShelfName', ''),
            'goodsShelfNum': order.get('goodsShelfNum', 0),
            'mergeId': order.get('mergeId'),
            'mergeKey': order.get('mergeKey'),
            'isMerge': int(order.get('isMerge', 0)),
            'isMergeable': int(order.get('isMergeable', 0)),
            'isOurShip': int(order.get('isOurShip', 0)),
            'isVoided': int(order.get('isVoided', 0)),
            'isRemoved': int(order.get('isRemoved', 0)),
            'isPrintPl': int(order.get('isPrintPl', 0)),
            'isPrintMd': int(order.get('isPrintMd', False)),
            'isBattery': int(order.get('isBattery', 0)),
            'isInsure': int(order.get('isInsure', False)),
            'isLiquid': int(order.get('isLiquid', False)),
            'isSendBack': int(order.get('isSendBack', False)),
            'isSplit': int(order.get('isSplit', False)),
            'isFree': int(order.get('isFree', False)),
            'isBatch': int(order.get('isBatch', False)),
            'hasGift': int(order.get('hasGift', False)),
            'secondPicking': int(order.get('secondPicking', False)),
            'secondPickFinish': int(order.get('secondPickFinish', False)),
            'isHasServiceComment': int(order.get('isHasServiceComment', False)),
            'isHasPickingComment': int(order.get('isHasPickingComment', False)),
            'isHasOrderComment': int(order.get('isHasOrderComment', False)),
            'isHasOrderMessage': int(order.get('isHasOrderMessage', False)),
            'ruleId': order.get('ruleId', '0'),
            'isRuleComment': int(order.get('isRuleComment', False)),
            'isRuleMessage': int(order.get('isRuleMessage', False)),
            'isRuleBuyerSelect': int(order.get('isRuleBuyerSelect', False)),
            'isRuleCustomsForm': int(order.get('isRuleCustomsForm', False)),
            'isRuleStockNum': int(order.get('isRuleStockNum', False)),
            'isRuleStockSku': int(order.get('isRuleStockSku', False)),
            'isRuleRussianName': int(order.get('isRuleRussianName', False)),
            'isRuleStockNoSku': int(order.get('isRuleStockNoSku', False)),
            'isRuleBlacklist': int(order.get('isRuleBlacklist', False)),
            'isGreen': int(order.get('isGreen', 0)),
            'isYellow': int(order.get('isYellow', 0)),
            'isOrange': int(order.get('isOrange', 0)),
            'isRed': int(order.get('isRed', 0)),
            'isViolet': int(order.get('isViolet', 0)),
            'isBlue': int(order.get('isBlue', 0)),
            'cornflowerBlue': int(order.get('cornflowerBlue', 0)),
            'pink': int(order.get('pink', 0)),
            'teal': int(order.get('teal', 0)),
            'turquoise': int(order.get('turquoise', 0)),
            'weight': order.get('weight', 0),
            'totalProductWeight': order.get('totalProductWeight'),
            'packageIndex': order.get('packageIndex', 0),
            'packageProductStatus': order.get('packageProductStatus'),
            'newAgentId': order.get('newAgentId', 0),
            'authId': order.get('authId', '0'),
            'commitPlatformStatus': order.get('commitPlatformStatus'),
            'handleState': int(order.get('handleState', False)),
            'refundedReason': order.get('refundedReason'),
            'refundedBy': order.get('refundedBy')
        }
    
    def _prepare_product_params(self, order_id: str, product: Dict[str, Any]) -> Dict[str, Any]:
        """准备产品参数"""
        return {
            'id': product.get('id'),
            'orderId': order_id,
            'dxmOrderId': product.get('dxmOrderId'),
            'puid': product.get('puid'),
            'shopId': product.get('shopId', '0'),
            'productId': product.get('productId'),
            'childId': product.get('childId'),
            'productName': product.get('productName'),
            'productSku': product.get('productSku'),
            'productSubSku': product.get('productSubSku'),
            'productDisplaySku': product.get('productDisplaySku'),
            'stockProductId': product.get('stockProductId'),
            'newSubSku': product.get('newSubSku'),
            'productImg': product.get('productImg'),
            'oriProductImg': product.get('oriProductImg'),
            'productUrl': product.get('productUrl'),
            'sourceUrl': product.get('sourceUrl'),
            'sourceName': product.get('sourceName'),
            'productSnapUrl': product.get('productSnapUrl'),
            'quantity': product.get('quantity'),
            'oldQuantity': product.get('oldQuantity'),
            'splitNum': product.get('splitNum', 0),
            'productCount': product.get('productCount'),
            'relationCount': product.get('relationCount'),
            'cancelCount': product.get('cancelCount', 0),
            'surplusNum': product.get('surplusNum', 0),
            'lotNum': product.get('lotNum', 0),
            'price': product.get('price'),
            'currency': product.get('currency'),
            'priceUsd': product.get('priceUsd'),
            'priceBrl': product.get('priceBrl', 0),
            'totalPriceUsd': product.get('totalPriceUsd'),
            'totalPriceCny': product.get('totalPriceCny'),
            'deltaMoney': product.get('deltaMoney', 0),
            'commission': product.get('commission'),
            'totalCommission': product.get('totalCommission'),
            'productStandard': product.get('productStandard'),
            'productWeight': product.get('productWeight', 0),
            'weight': product.get('weight', 0),
            'tag': product.get('tag'),
            'addProduct': int(product.get('addProduct', False)),
            'addGift': int(product.get('addGift', False)),
            'cancelFlag': int(product.get('cancelFlag', False)),
            'onlineTime': product.get('onlineTime'),
            'createTime': product.get('createTime'),
            'updateTime': product.get('updateTime')
        }
    
    def _batch_insert_orders(self, order_params_list: List[Dict[str, Any]]):
        """批量插入订单主表"""
        if not order_params_list:
            return
            
        sql = """
        INSERT INTO orders (
            order_id, id, puid, shop_id, origin_id, parent_id, split_parent_id,
            extended_order_id, order_amount, order_unit, ship_amount, refund_amount_usd,
            platform, buyer_name, contact_name, buyer_account, buyer_country,
            order_state, order_state_platform, forbidden_state, forbidden_reason,
            package_state, intercept_state, error_state, error_msg,
            order_create_time, order_pay_time, order_timeout_time, paid_time,
            approved_time, processed_time, distribute_time, out_stock_time,
            shipped_time, refuned_time, create_time, update_time,
            package_number, tracking_number, new_tracking_number, agent_track_num,
            agent_provider_name, forward_order_id, sku, product_sku, sku_count,
            storage_id, goods_shelf_name, goods_shelf_num, merge_id, merge_key,
            is_merge, is_mergeable, is_our_ship, is_voided, is_removed,
            is_print_pl, is_print_md, is_battery, is_insure, is_liquid,
            is_send_back, is_split, is_free, is_batch, has_gift,
            second_picking, second_pick_finish, is_has_service_comment,
            is_has_picking_comment, is_has_order_comment, is_has_order_message,
            rule_id, is_rule_comment, is_rule_message, is_rule_buyer_select,
            is_rule_customs_form, is_rule_stock_num, is_rule_stock_sku,
            is_rule_russian_name, is_rule_stock_no_sku, is_rule_blacklist,
            is_green, is_yellow, is_orange, is_red, is_violet, is_blue,
            cornflower_blue, pink, teal, turquoise, weight, total_product_weight,
            package_index, package_product_status, new_agent_id, auth_id,
            commit_platform_status, handle_state, refunded_reason, refunded_by
        ) VALUES (
            %(orderId)s, %(id)s, %(puid)s, %(shopId)s, %(originId)s, %(parentId)s, %(splitParentId)s,
            %(extendedOrderId)s, %(orderAmount)s, %(orderUnit)s, %(shipAmount)s, %(refundAmountUsd)s,
            %(platform)s, %(buyerName)s, %(contactName)s, %(buyerAccount)s, %(buyerCountry)s,
            %(orderState)s, %(orderStatePlatform)s, %(forbiddenState)s, %(forbiddenReason)s,
            %(packageState)s, %(interceptState)s, %(errorState)s, %(errorMsg)s,
            %(orderCreateTime)s, %(orderPayTime)s, %(orderTimeoutTime)s, %(paidTime)s,
            %(approvedTime)s, %(processedTime)s, %(distributeTime)s, %(outStockTime)s,
            %(shippedTime)s, %(refunedTime)s, %(createTime)s, %(updateTime)s,
            %(packageNumber)s, %(trackingNumber)s, %(newTrackingNumber)s, %(agentTrackNum)s,
            %(agentProviderName)s, %(forwardOrderId)s, %(sku)s, %(productSku)s, %(skuCount)s,
            %(storageId)s, %(goodsShelfName)s, %(goodsShelfNum)s, %(mergeId)s, %(mergeKey)s,
            %(isMerge)s, %(isMergeable)s, %(isOurShip)s, %(isVoided)s, %(isRemoved)s,
            %(isPrintPl)s, %(isPrintMd)s, %(isBattery)s, %(isInsure)s, %(isLiquid)s,
            %(isSendBack)s, %(isSplit)s, %(isFree)s, %(isBatch)s, %(hasGift)s,
            %(secondPicking)s, %(secondPickFinish)s, %(isHasServiceComment)s,
            %(isHasPickingComment)s, %(isHasOrderComment)s, %(isHasOrderMessage)s,
            %(ruleId)s, %(isRuleComment)s, %(isRuleMessage)s, %(isRuleBuyerSelect)s,
            %(isRuleCustomsForm)s, %(isRuleStockNum)s, %(isRuleStockSku)s,
            %(isRuleRussianName)s, %(isRuleStockNoSku)s, %(isRuleBlacklist)s,
            %(isGreen)s, %(isYellow)s, %(isOrange)s, %(isRed)s, %(isViolet)s, %(isBlue)s,
            %(cornflowerBlue)s, %(pink)s, %(teal)s, %(turquoise)s, %(weight)s, %(totalProductWeight)s,
            %(packageIndex)s, %(packageProductStatus)s, %(newAgentId)s, %(authId)s,
            %(commitPlatformStatus)s, %(handleState)s, %(refundedReason)s, %(refundedBy)s
        )
        ON DUPLICATE KEY UPDATE
            id = VALUES(id),
            puid = VALUES(puid),
            shop_id = VALUES(shop_id),
            order_amount = VALUES(order_amount),
            order_unit = VALUES(order_unit),
            ship_amount = VALUES(ship_amount),
            platform = VALUES(platform),
            buyer_name = VALUES(buyer_name),
            contact_name = VALUES(contact_name),
            buyer_country = VALUES(buyer_country),
            order_state = VALUES(order_state),
            forbidden_state = VALUES(forbidden_state),
            package_number = VALUES(package_number),
            tracking_number = VALUES(tracking_number),
            order_create_time = VALUES(order_create_time),
            order_pay_time = VALUES(order_pay_time),
            paid_time = VALUES(paid_time),
            approved_time = VALUES(approved_time),
            shipped_time = VALUES(shipped_time),
            sku = VALUES(sku),
            product_sku = VALUES(product_sku),
            sku_count = VALUES(sku_count),
            storage_id = VALUES(storage_id),
            is_green = VALUES(is_green),
            is_yellow = VALUES(is_yellow),
            is_orange = VALUES(is_orange),
            is_red = VALUES(is_red),
            is_violet = VALUES(is_violet),
            is_blue = VALUES(is_blue),
            update_time = VALUES(update_time)
        """
        
        self.cursor.executemany(sql, order_params_list)
    
    def _batch_insert_products(self, product_params_list: List[Dict[str, Any]]):
        """批量插入产品明细"""
        if not product_params_list:
            return
            
        sql = """
        INSERT INTO order_products (
            id, order_id, dxm_order_id, puid, shop_id,
            product_id, child_id, product_name, product_sku, product_sub_sku,
            product_display_sku, stock_product_id, new_sub_sku,
            product_img, ori_product_img, product_url, source_url, source_name,
            product_snap_url, quantity, old_quantity, split_num, product_count,
            relation_count, cancel_count, surplus_num, lot_num,
            price, currency, price_usd, price_brl, total_price_usd, total_price_cny,
            delta_money, commission, total_commission, product_standard, product_weight,
            weight, tag, add_product, add_gift, cancel_flag, online_time,
            create_time, update_time
        ) VALUES (
            %(id)s, %(orderId)s, %(dxmOrderId)s, %(puid)s, %(shopId)s,
            %(productId)s, %(childId)s, %(productName)s, %(productSku)s, %(productSubSku)s,
            %(productDisplaySku)s, %(stockProductId)s, %(newSubSku)s,
            %(productImg)s, %(oriProductImg)s, %(productUrl)s, %(sourceUrl)s, %(sourceName)s,
            %(productSnapUrl)s, %(quantity)s, %(oldQuantity)s, %(splitNum)s, %(productCount)s,
            %(relationCount)s, %(cancelCount)s, %(surplusNum)s, %(lotNum)s,
            %(price)s, %(currency)s, %(priceUsd)s, %(priceBrl)s, %(totalPriceUsd)s, %(totalPriceCny)s,
            %(deltaMoney)s, %(commission)s, %(totalCommission)s, %(productStandard)s, %(productWeight)s,
            %(weight)s, %(tag)s, %(addProduct)s, %(addGift)s, %(cancelFlag)s, %(onlineTime)s,
            %(createTime)s, %(updateTime)s
        )
        ON DUPLICATE KEY UPDATE
            product_name = VALUES(product_name),
            quantity = VALUES(quantity),
            price = VALUES(price),
            price_usd = VALUES(price_usd),
            product_img = VALUES(product_img),
            product_url = VALUES(product_url),
            update_time = VALUES(update_time)
        """
        
        self.cursor.executemany(sql, product_params_list)
    
    def _batch_insert_attrs(self, attr_params_list: List[Tuple]):
        """批量插入产品属性"""
        if not attr_params_list:
            return
            
        # 先批量删除旧的属性
        product_ids = list(set([params[0] for params in attr_params_list]))
        if product_ids:
            delete_sql = "DELETE FROM order_product_attrs WHERE order_product_id IN (%s)" % ','.join(['%s'] * len(product_ids))
            self.cursor.execute(delete_sql, product_ids)
        
        # 批量插入新属性
        insert_sql = """
        INSERT INTO order_product_attrs (order_product_id, order_id, attr_name, attr_value)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.executemany(insert_sql, attr_params_list)
    
    def import_orders_batch(self, order_list: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        批量导入订单数据
        
        Args:
            order_list: 订单列表
            
        Returns:
            tuple: (成功数量, 失败数量)
        """
        total = len(order_list)
        print(f"开始批量导入 {total} 个订单...")
        print(f"批次大小: {self.batch_size}，预计分 {(total + self.batch_size - 1) // self.batch_size} 批次处理")
        
        success_count = 0
        fail_count = 0
        
        # 分批处理
        for batch_start in range(0, total, self.batch_size):
            batch_end = min(batch_start + self.batch_size, total)
            batch_orders = order_list[batch_start:batch_end]
            
            try:
                # 准备批量数据
                order_params_list = []
                product_params_list = []
                attr_params_list = []
                
                for order in batch_orders:
                    # 准备订单参数
                    order_params = self._prepare_order_params(order)
                    order_params_list.append(order_params)
                    
                    # 【关键修复】安全获取产品列表，确保不会是None
                    product_list = self._safe_get_list(order, 'productList')
                    
                    for product in product_list:
                        product_params = self._prepare_product_params(order['orderId'], product)
                        product_params_list.append(product_params)
                        
                        # 【关键修复】安全获取属性列表，确保不会是None
                        attr_list = self._safe_get_list(product, 'attrList')
                        
                        for attr in attr_list:
                            attr_name = attr.get('pName', '')
                            attr_params_list.append((
                                product['id'],
                                order['orderId'],
                                attr_name,
                                attr_name
                            ))
                
                # 批量执行插入
                self._batch_insert_orders(order_params_list)
                self._batch_insert_products(product_params_list)
                self._batch_insert_attrs(attr_params_list)
                
                # 提交当前批次
                self.conn.commit()
                
                batch_success = len(batch_orders)
                success_count += batch_success
                print(f"✓ 批次 {batch_start // self.batch_size + 1} 完成: "
                      f"成功导入 {batch_success} 个订单 ({batch_start + 1}-{batch_end}/{total})")
                
            except Exception as e:
                self.conn.rollback()
                batch_fail = len(batch_orders)
                fail_count += batch_fail
                print(f"✗ 批次 {batch_start // self.batch_size + 1} 失败: {str(e)}")
                print(f"  失败订单范围: {batch_start + 1}-{batch_end}")
        
        print(f"\n=== 导入完成 ===")
        print(f"总计: {total} 个订单")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"成功率: {success_count / total * 100:.2f}%")
        
        return success_count, fail_count
    
    def import_from_json_file(self, json_file_path: str) -> Tuple[int, int]:
        """
        从JSON文件批量导入数据
        
        Args:
            json_file_path: JSON文件路径
            
        Returns:
            tuple: (成功数量, 失败数量)
        """
        print(f"正在读取文件: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        order_list = data.get('data', {}).get('page', {}).get('list', [])
        print(f"文件读取成功，共 {len(order_list)} 个订单\n")
        
        return self.import_orders_batch(order_list)
    
    def import_from_dict(self, data: Dict[str, Any]) -> Tuple[int, int]:
        """
        从字典数据批量导入
        
        Args:
            data: 订单数据字典
            
        Returns:
            tuple: (成功数量, 失败数量)
        """
        order_list = data.get('data', {}).get('page', {}).get('list', [])
        return self.import_orders_batch(order_list)


def run_import(json_file_path, batch_size=100):
    """
    运行批量导入函数
    
    Args:
        json_file_path: JSON文件路径
        batch_size: 批次大小（默认100）
    
    Returns:
        tuple: (成功数量, 失败数量)
    """
    with OrderBatchImporter(batch_size=batch_size) as importer:
        return importer.import_from_json_file(json_file_path)


def import_from_file(json_file_path, host='47.104.72.198', user='root', 
                     password='Kewen888@', database='dxm_info', port=3306, batch_size=100):
    """
    从文件批量导入订单数据（便捷函数）
    
    Args:
        json_file_path: JSON文件路径
        host: 数据库主机
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名
        port: 数据库端口
        batch_size: 批次大小（默认100）
    
    Returns:
        tuple: (成功数量, 失败数量)
    """
    with OrderBatchImporter(host, user, password, database, port, batch_size) as importer:
        return importer.import_from_json_file(json_file_path)


def import_from_data(data_dict, host='47.104.72.198', user='root',
                     password='Kewen888@', database='dxm_info', port=3306, batch_size=100):
    """
    从字典数据批量导入订单（便捷函数）
    
    Args:
        data_dict: 订单数据字典
        host: 数据库主机
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名
        port: 数据库端口
        batch_size: 批次大小（默认100）
    
    Returns:
        tuple: (成功数量, 失败数量)
    """
    with OrderBatchImporter(host, user, password, database, port, batch_size) as importer:
        return importer.import_from_dict(data_dict)


if __name__ == '__main__':
    # 示例调用
    # 方式1: 从文件导入，使用默认批次大小100
    # run_import('/path/to/your/orders.json')
    
    # 方式2: 从文件导入，自定义批次大小
    # run_import('/path/to/your/orders.json', batch_size=50)
    
    # 方式3: 使用便捷函数，完全自定义参数
    # import_from_file(
    #     '/path/to/your/orders.json',
    #     host='47.104.72.198',
    #     user='root',
    #     password='Kewen888@',
    #     database='dxm_info',
    #     port=3306,
    #     batch_size=100
    # )
    
    pass
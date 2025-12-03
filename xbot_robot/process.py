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
import json
from typing import List, Tuple, Dict, Set
import logging
from collections import defaultdict
import time
from datetime import datetime
import requests
from urllib import parse
import psutil
import os

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================== 公共工具函数（增强版） ===========================

def acquire_global_lock(cursor, timeout: int = 0) -> bool:
    """获取统一的全局互斥锁"""
    lock_name = "global_kpi_process_lock"
    try:
        cursor.execute("SELECT GET_LOCK(%s,%s)", (lock_name, timeout))
        res = cursor.fetchone()
        if res and res[0] == 1:
            print(f"[LOCK] 成功获取全局互斥锁({lock_name})")
            return True
        print(f"[LOCK] 未获取到全局互斥锁({lock_name})，可能已有实例在运行")
        return False
    except Exception as e:
        print(f"[LOCK] 获取锁时出错: {e}")
        return False


def release_global_lock(cursor):
    """释放统一的全局互斥锁"""
    lock_name = "global_kpi_process_lock"
    try:
        cursor.execute("SELECT RELEASE_LOCK(%s)", (lock_name,))
        print(f"[LOCK] 已释放全局互斥锁({lock_name})")
    except Exception as e:
        print(f"[LOCK] 释放全局互斥锁失败({lock_name}): {e}")


def execute_with_retry(cursor, query, params=None, max_retries=3, retry_delay=1):
    """带重试机制的数据库执行"""
    for attempt in range(max_retries + 1):
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.rowcount
        except pymysql.err.OperationalError as e:
            if e.args[0] in [1205, 1213]:  # 锁等待超时或死锁
                if attempt < max_retries:
                    print(f"[RETRY] 数据库锁冲突(错误{e.args[0]})，重试第 {attempt + 1} 次...")
                    kill_blocking_sessions(cursor, 'kpi_report')
                    kill_blocking_sessions(cursor, 'kpi_report_info')
                    time.sleep(retry_delay * (attempt + 1))  # 递增延迟
                    continue
                else:
                    print(f"[ERROR] 重试{max_retries}次后仍然失败: {e}")
                    raise
            else:
                raise
        except Exception as e:
            if attempt < max_retries:
                print(f"[RETRY] 执行失败，重试第 {attempt + 1} 次: {e}")
                time.sleep(retry_delay)
                continue
            raise


def executemany_with_retry(cursor, query, param_list, max_retries=3, retry_delay=1):
    """带重试机制的批量数据库执行"""
    for attempt in range(max_retries + 1):
        try:
            cursor.executemany(query, param_list)
            return cursor.rowcount
        except pymysql.err.OperationalError as e:
            if e.args[0] in [1205, 1213]:  # 锁等待超时或死锁
                if attempt < max_retries:
                    print(f"[RETRY] 批量操作锁冲突(错误{e.args[0]})，重试第 {attempt + 1} 次...")
                    kill_blocking_sessions(cursor, 'kpi_report')
                    kill_blocking_sessions(cursor, 'kpi_report_info')
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    print(f"[ERROR] 批量操作重试{max_retries}次后仍然失败: {e}")
                    raise
            else:
                raise
        except Exception as e:
            if attempt < max_retries:
                print(f"[RETRY] 批量操作失败，重试第 {attempt + 1} 次: {e}")
                time.sleep(retry_delay)
                continue
            raise


def kill_blocking_sessions(cursor, table_name: str):
    """检测并杀死阻塞指定表的会话"""
    try:
        query = """
        SELECT DISTINCT bt.PROCESSLIST_ID
        FROM performance_schema.data_lock_waits w
        JOIN performance_schema.data_locks bl ON w.blocking_engine_lock_id = bl.engine_lock_id
        JOIN performance_schema.data_locks rl ON w.requesting_engine_lock_id = rl.engine_lock_id
        JOIN performance_schema.threads bt ON bl.engine_thread_id = bt.thread_id
        WHERE rl.OBJECT_NAME = %s
        """
        cursor.execute(query, (table_name,))
        rows = cursor.fetchall()
        if not rows:
            return
        for (pid,) in rows:
            try:
                print(f"[LOCK] 检测到阻塞会话 {pid}，执行KILL")
                cursor.execute(f"KILL {pid}")
            except Exception as e:
                print(f"[LOCK] KILL {pid} 失败: {e}")
    except Exception as e:
        print(f"[LOCK] 自动杀锁检测失败: {e}")


def check_process_running():
    """检查是否有其他相同进程在运行"""
    try:
        current_pid = os.getpid()
        current_name = psutil.Process(current_pid).name()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if (proc.info['pid'] != current_pid and 
                    proc.info['name'] == current_name and
                    proc.info['cmdline'] and
                    any('process_first_and_second_run' in str(cmd) for cmd in proc.info['cmdline'])):
                    print(f"[WARN] 发现其他相同进程在运行: PID {proc.info['pid']}")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return False
    except Exception as e:
        print(f"[WARN] 进程检查失败: {e}")
        return False


def create_safe_connection():
    """创建更安全的数据库连接"""
    db_config = {
        'host': '47.95.157.46',
        'user': 'root',
        'password': 'root@kunkun',
        'port': 3306,
        'database': 'order_tracking_iw',
        'charset': 'utf8mb4',
        'autocommit': False
    }
    
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    
    # 设置事务隔离级别为READ COMMITTED，减少锁冲突
    cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
    
    # 设置锁等待超时时间
    cursor.execute("SET SESSION innodb_lock_wait_timeout = 50")
    
    # 设置语句超时时间（5分钟）
    cursor.execute("SET SESSION max_execution_time = 300000")
    
    return connection, cursor


def get_conductor_id(task_id):
    """通过intention_id获取处理人id"""
    print(f"[API] 开始获取处理人ID，task_id: {task_id}")

    request_url = 'http://47.95.157.46:8520/api/conductor_id'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "id": str(task_id)
    }
    data = parse.urlencode(form_data, True)

    logger.info(f"API请求 - URL: {request_url}")
    logger.info(f"API请求 - Headers: {headers}")
    logger.info(f"API请求 - Data: {data}")
    logger.info(f"API请求 - intention_id: {task_id}")

    try:
        print(f"[API] 发送请求到: {request_url}")
        response = requests.post(request_url, headers=headers, data=data, timeout=10)
        print(f"[API] 响应状态码: {response.status_code}")

        logger.info(f"API响应 - Status Code: {response.status_code}")
        logger.info(f"API响应 - Response Text: {response.text}")

        response.raise_for_status()
        json_data = response.json()
        logger.info(f"API响应 - JSON Data: {json_data}")

        if json_data.get("success") and json_data.get("data"):
            conductor_id = json_data["data"][0]["id"]
            print(f"[API] 成功获取conductor_id: {conductor_id}")
            logger.info(f"API响应 - 获取到conductor_id: {conductor_id}")
            return conductor_id
        else:
            print(f"[API] 请求成功但数据为空或格式不符")
            logger.warning("请求成功但数据为空或格式不符")
            return None
    except Exception as e:
        print(f"[API] 请求失败：{e}")
        logger.error(f"请求失败：{e}")
        return None


def get_conductor_name(conductor_value):
    """通过处理人id获取处理人姓名"""
    print(f"[API] 开始获取处理人姓名，conductor_value: {conductor_value}")

    request_url = 'http://47.95.157.46:8520/api/get_conductor_name'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    form_data = {
        "conductor": conductor_value
    }
    data = parse.urlencode(form_data, True)

    logger.info(f"API请求 - URL: {request_url}")
    logger.info(f"API请求 - Headers: {headers}")
    logger.info(f"API请求 - Data: {data}")
    logger.info(f"API请求 - conductor_value: {conductor_value}")

    try:
        print(f"[API] 发送请求到: {request_url}")
        response = requests.post(request_url, headers=headers, data=data, timeout=10)
        print(f"[API] 响应状态码: {response.status_code}")

        logger.info(f"API响应 - Status Code: {response.status_code}")
        logger.info(f"API响应 - Response Text: {response.text}")

        if response.status_code == 200:
            response_json = response.json()
            logger.info(f"API响应 - JSON Data: {response_json}")

            if response_json['success'] and response_json['data']:
                conductor_name = response_json['data'][0]['acct']
                print(f"[API] 成功获取处理人姓名: {conductor_name}")
                logger.info(f"API响应 - 获取到conductor_name: {conductor_name}")
                return conductor_name
            else:
                print(f"[API] 请求成功但数据为空或格式不符")
                logger.warning("请求成功但数据为空或格式不符")
                return "No data found or request unsuccessful"
        else:
            print(f"[API] 请求失败，状态码: {response.status_code}")
            logger.error(f"Request failed with status code: {response.status_code}")
            return f"Request failed with status code: {response.status_code}"
    except Exception as e:
        print(f"[API] 获取处理人姓名失败: {e}")
        logger.error(f"获取处理人姓名失败: {e}")
        return "No data found or request unsuccessful"


def get_today_filter():
    today = datetime.now()
    result = f"{today.month}月{today.day}日"
    print(f"[DATE] 今天的筛选条件: {result}")
    return result


def get_today_int():
    today = datetime.now()
    result = int(today.strftime("%Y%m%d"))
    print(f"[DATE] 今天的整数格式: {result}")
    return result


def get_today_date_string():
    today = datetime.now()
    result = today.strftime("%Y-%m-%d")
    print(f"[DATE] 今天的日期字符串: {result}")
    return result


def is_valid_waybill_number(waybill_number):
    if not waybill_number:
        return False
    waybill_str = str(waybill_number)
    if len(waybill_str) <= 20:
        return False
    error_keywords = [
        '报错', '失败', '校验失败', '云途返回',
        '错误', 'error', 'Error', 'ERROR',
        '下单规则', '收件人姓名', '公司名'
    ]
    for keyword in error_keywords:
        if keyword in waybill_str:
            print(f"[WAYBILL] 发现报错信息，不算交运成功: {waybill_str[:50]}...")
            return False
    return True


def get_correct_conductor_name_from_task(cursor, intention_id, today_filter):
    try:
        query = """
       SELECT conductor_name 
       FROM task 
       WHERE invoice_id = %s 
       AND queue_entry_time LIKE %s
       LIMIT 1
       """
        cursor.execute(query, (intention_id, f'%{today_filter}%'))
        result = cursor.fetchone()
        if result and result[0]:
            conductor_name = result[0]
            print(f"[TASK] 从task表获取到intention_id {intention_id} 的处理人姓名: {conductor_name}")
            logger.info(f"从task表获取到intention_id {intention_id} 的处理人姓名: {conductor_name}")
            return conductor_name
        else:
            print(f"[TASK] 在task表中未找到intention_id {intention_id} 的处理人信息")
            logger.warning(f"在task表中未找到intention_id {intention_id} 的处理人信息")
            return None
    except Exception as e:
        print(f"[ERROR] 从task表获取处理人姓名失败: {e}")
        logger.error(f"从task表获取处理人姓名失败: {e}")
        return None


# =========================== 主流程（并发安全版） ===========================

def process_first_and_second_run():
    """并发安全的首次和二次运行处理函数"""
    print("=" * 60)
    print("开始执行 process_first_and_second_run 函数（并发安全版）")
    print("=" * 60)

    # 检查是否有其他相同进程在运行
    if check_process_running():
        print("[WARN] 检测到其他相同进程在运行，退出执行")
        return

    start_time = time.time()
    connection = None
    cursor = None
    lock_acquired = False

    try:
        print("[DB] 正在创建安全数据库连接...")
        connection, cursor = create_safe_connection()
        print("[DB] 数据库连接成功!")
        logger.info("数据库连接成功")

        # 使用统一的全局锁
        lock_acquired = acquire_global_lock(cursor, 0)
        if not lock_acquired:
            print("[LOCK] 未能获取全局锁，可能有其他实例在运行")
            return

        today_filter = get_today_filter()

        print("[QUERY] 查询今天的首次运行任务...")
        execute_with_retry(cursor, """
            SELECT conductor_name, invoice_id 
            FROM task 
            WHERE task_status = '运行结束-首次运行' 
              AND queue_entry_time LIKE %s
        """, (f'%{today_filter}%',))
        first_run_results = cursor.fetchall()
        print(f"[QUERY] 找到 {len(first_run_results)} 个今天的首次运行任务")
        logger.info(f"找到 {len(first_run_results)} 个今天的首次运行任务")

        print("[QUERY] 查询今天的所有任务...")
        execute_with_retry(cursor, """
            SELECT conductor_name, invoice_id 
            FROM task 
            WHERE queue_entry_time LIKE %s
        """, (f'%{today_filter}%',))
        all_today_results = cursor.fetchall()
        print(f"[QUERY] 找到 {len(all_today_results)} 个今天的所有任务")
        logger.info(f"找到 {len(all_today_results)} 个今天的所有任务")

        all_invoice_ids = list(set([invoice_id for _, invoice_id in all_today_results]))
        print(f"[PROCESS] 去重后共有 {len(all_invoice_ids)} 个不同的invoice_id")
        logger.info(f"去重后共有 {len(all_invoice_ids)} 个不同的invoice_id")

        if first_run_results:
            print("[PROCESS] 开始处理首次运行任务...")
            first_run_intention_ids = [invoice_id for _, invoice_id in first_run_results]
            existing_ids = batch_check_existing_ids(cursor, first_run_intention_ids)
            first_run_tasks = [(conductor_name, invoice_id)
                               for conductor_name, invoice_id in first_run_results
                               if invoice_id not in existing_ids]
            print(f"[PROCESS] 需要进行首次运行处理的任务: {len(first_run_tasks)} 个")
            logger.info(f"需要进行首次运行处理的任务: {len(first_run_tasks)} 个")
            if first_run_tasks:
                batch_process_first_run(cursor, connection, first_run_tasks)
        
        connection.commit()
        print("[DB] 首次运行事务提交成功")

        print("[STATS] 开始计算并更新用户订单统计...")
        update_user_order_statistics(cursor, connection, all_invoice_ids)
        print("[STATS] 用户订单统计更新完成")

        print("[SYNC] 开始同步数据到gocrm数据库...")
        sync_to_gocrm(cursor)
        print("[SYNC] 数据同步完成")

        elapsed_time = time.time() - start_time
        print(f"[COMPLETE] 首次运行处理完成，耗时: {elapsed_time:.2f} 秒")
        logger.info(f"首次运行处理完成，耗时: {elapsed_time:.2f} 秒")

        # 释放锁（此时游标仍然打开）
        if lock_acquired:
            release_global_lock(cursor)
            lock_acquired = False

        # 关闭连接后调用二次函数
        cursor.close()
        connection.close()
        cursor = None
        connection = None

        print("\n" + "=" * 60)
        print("首次计算完成，现在自动调用二次计算函数...")
        print("=" * 60 + "\n")
        process_only_second_run()

    except Exception as e:
        print(f"[ERROR] 处理过程中出错: {str(e)}")
        logger.error(f"处理过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        if connection:
            connection.rollback()
        raise
    finally:
        try:
            if lock_acquired and cursor:
                release_global_lock(cursor)
        except:
            pass
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if connection:
                connection.close()
        except:
            pass
        print("[DB] 确保数据库连接已关闭")
        logger.info("确保数据库连接已关闭")


def process_only_second_run():
    """并发安全的二次运行处理函数"""
    print("=" * 60)
    print("开始执行 process_only_second_run 函数（并发安全版）")
    print("=" * 60)
    
    # 检查是否有其他相同进程在运行
    if check_process_running():
        print("[WARN] 检测到其他相同进程在运行，退出执行")
        return
    
    start_time = time.time()
    connection = None
    cursor = None
    lock_acquired = False

    try:
        print("[DB] 正在创建安全数据库连接...")
        connection, cursor = create_safe_connection()
        print("[DB] 数据库连接成功!")

        # 使用统一的全局锁
        lock_acquired = acquire_global_lock(cursor, 0)
        if not lock_acquired:
            print("[LOCK] 未能获取全局锁，可能有其他实例在运行")
            return

        today_filter = get_today_filter()
        print("[QUERY] 从task表查询今天的所有invoice_id...")
        execute_with_retry(cursor, """
            SELECT DISTINCT invoice_id, conductor_name
            FROM task 
            WHERE queue_entry_time LIKE %s
        """, (f'%{today_filter}%',))
        task_results = cursor.fetchall()
        invoice_conductor_map = {invoice_id: conductor_name for invoice_id, conductor_name in task_results}
        today_invoice_ids = list(invoice_conductor_map.keys())
        print(f"[QUERY] 从task表找到 {len(today_invoice_ids)} 个今天的invoice_id")
        logger.info(f"从task表找到 {len(today_invoice_ids)} 个今天的invoice_id")

        if today_invoice_ids:
            existing_ids = batch_check_existing_ids(cursor, today_invoice_ids)
            ids_for_second_run = list(existing_ids)
            missing_ids = [i for i in today_invoice_ids if i not in existing_ids]

            if ids_for_second_run:
                batch_process_second_run(cursor, connection, ids_for_second_run)
            connection.commit()

            if missing_ids:
                missing_tasks = [(invoice_conductor_map.get(i, "未知用户"), i) for i in missing_ids]
                batch_process_first_run(cursor, connection, missing_tasks)
                batch_process_second_run(cursor, connection, missing_ids)
                connection.commit()

            print("[STATS] 开始更新用户订单统计...")
            update_user_order_statistics(cursor, connection, today_invoice_ids)
            print("[STATS] 用户订单统计更新完成")

            print("[SYNC] 开始同步数据到gocrm数据库...")
            sync_to_gocrm(cursor)
            print("[SYNC] 数据同步完成")

        elapsed_time = time.time() - start_time
        print(f"[COMPLETE] 二次报错处理完成，耗时: {elapsed_time:.2f} 秒")

    except Exception as e:
        print(f"[ERROR] 处理过程中出错: {str(e)}")
        logger.error(f"处理过程中出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        if connection:
            connection.rollback()
        raise
    finally:
        try:
            if lock_acquired and cursor:
                release_global_lock(cursor)
        except:
            pass
        try:
            if cursor:
                cursor.close()
        except:
            pass
        try:
            if connection:
                connection.close()
        except:
            pass
        print("[DB] 数据库连接已关闭")
        logger.info("数据库连接已关闭")


# =========================== 统计、KPI 等函数（并发安全版） ===========================

def safe_int(value):
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return 0
    return 0


def update_user_order_statistics(cursor, connection, invoice_ids: List[str]):
    print(f"[STATS] 开始更新用户订单统计，处理 {len(invoice_ids)} 个invoice_id")
    if not invoice_ids:
        print("[STATS] 没有需要统计的invoice_id")
        return
    try:
        today_int = get_today_int()
        today_filter = get_today_filter()
        today_date_string = get_today_date_string()
        print(f"[STATS] 处理日期: {today_int}")
        logger.info(f"开始处理用户订单统计，日期: {today_int}")

        print("[STATS] 从kpi_report表获取相关数据...")
        placeholders = ','.join(['%s'] * len(invoice_ids))
        query = f"""
        SELECT intention_id, first_run_fail_count, invoice_order_count, name,
               manual_error_num, delivery_error_num, sku_error_num
        FROM kpi_report 
        WHERE intention_id IN ({placeholders})
        AND DATE(create_time) = %s
        """
        execute_with_retry(cursor, query, invoice_ids + [today_date_string])
        kpi_data = cursor.fetchall()
        if not kpi_data:
            print("[STATS] 在kpi_report中没有找到相关数据")
            return
        print(f"[STATS] 从kpi_report获取到 {len(kpi_data)} 条数据")
        kpi_data = list(kpi_data)

        print("[STATS] 删除今天旧数据...")
        delete_sql = "DELETE FROM user_order_amount_statistics WHERE dateday = %s"
        execute_with_retry(cursor, delete_sql, (today_int,))
        print(f"[STATS] 删除完成，影响行数: {cursor.rowcount}")

        abnormal_names = ["No data found or request unsuccessful", "未知用户", "", None]
        records_to_update = []

        for i, row in enumerate(kpi_data):
            intention_id = row[0]
            name = row[3]
            if name in abnormal_names or (name and str(name).strip() == ""):
                correct_name = get_correct_conductor_name_from_task(cursor, intention_id, today_filter)
                if correct_name:
                    if len(correct_name) > 10:
                        correct_name = correct_name[:10]
                    records_to_update.append((correct_name, intention_id))
                    kpi_data[i] = (row[0], row[1], row[2], correct_name, row[4], row[5], row[6])
                else:
                    conductor_id = get_conductor_id(intention_id)
                    if conductor_id:
                        api_name = get_conductor_name(conductor_id)
                        if api_name != "No data found or request unsuccessful":
                            if len(api_name) > 10:
                                api_name = api_name[:10]
                            records_to_update.append((api_name, intention_id))
                            kpi_data[i] = (row[0], row[1], row[2], api_name, row[4], row[5], row[6])
                        else:
                            records_to_update.append(("系统用户", intention_id))
                            kpi_data[i] = (row[0], row[1], row[2], "系统用户", row[4], row[5], row[6])
                    else:
                        records_to_update.append(("系统用户", intention_id))
                        kpi_data[i] = (row[0], row[1], row[2], "系统用户", row[4], row[5], row[6])

        if records_to_update:
            executemany_with_retry(cursor,
                "UPDATE kpi_report SET name=%s WHERE intention_id=%s AND DATE(create_time)=%s",
                [(n, iid, today_date_string) for n, iid in records_to_update]
            )

        user_stats = defaultdict(lambda: {
            'first_run_fail_count': 0,
            'invoice_order_count': 0,
            'manual_error_num': 0,
            'delivery_error_num': 0,
            'sku_error_num': 0,
            'ticket_count': 0
        })
        for row in kpi_data:
            name = row[3]
            if not name:
                continue
            if len(name) > 10:
                name = name[:10]
            user_stats[name]['first_run_fail_count'] += safe_int(row[1])
            user_stats[name]['invoice_order_count'] += safe_int(row[2])
            user_stats[name]['manual_error_num'] += safe_int(row[4])
            user_stats[name]['delivery_error_num'] += safe_int(row[5])
            user_stats[name]['sku_error_num'] += safe_int(row[6])
            user_stats[name]['ticket_count'] += 1

        coefficients = {
            'ticket_num': 1,
            'order_num': 2,
            'first_run_num': 3,
            'sku_num': 1,
            'shipment_num': 1,
            'handmade_singular': 1
        }

        user_data_list = []
        for name, stats in user_stats.items():
            performance_amount = (
                stats['ticket_count'] * coefficients['ticket_num'] +
                stats['invoice_order_count'] * coefficients['order_num'] +
                stats['first_run_fail_count'] * coefficients['first_run_num'] +
                stats['sku_error_num'] * coefficients['sku_num'] +
                stats['delivery_error_num'] * coefficients['shipment_num'] +
                stats['manual_error_num'] * coefficients['handmade_singular']
            )
            user_data_list.append((
                today_int, name, stats['ticket_count'], stats['invoice_order_count'],
                stats['first_run_fail_count'], stats['sku_error_num'],
                stats['delivery_error_num'], stats['manual_error_num'],
                performance_amount, 0, performance_amount
            ))

        if user_data_list:
            executemany_with_retry(cursor, """
            INSERT INTO user_order_amount_statistics
            (dateday, name, ticket_num, order_num, first_run_num,
             sku_num, shipment_num, handmade_singular, performance_amount,
             rank_amount, performance_bonus)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, user_data_list)
            print(f"[STATS] 成功插入 {len(user_data_list)} 个用户统计数据")

        calculate_rank_and_bonus(cursor, connection, today_int)
        print("[STATS] 用户订单统计更新完成")
        connection.commit()
    except Exception as e:
        print(f"[ERROR] 更新用户订单统计时出错: {e}")
        logger.error(f"更新用户订单统计时出错: {e}")
        raise


def calculate_rank_and_bonus(cursor, connection, dateday: int):
    print(f"[RANK] 开始计算排名奖金，日期: {dateday}")
    execute_with_retry(cursor, """
    SELECT name, order_num, performance_amount
    FROM user_order_amount_statistics
    WHERE dateday=%s
    ORDER BY order_num DESC
    """, (dateday,))
    rows = cursor.fetchall()
    if not rows:
        return
    rank_amounts = [500, 300, 100]
    updates = []
    for i, (name, order_num, performance_amount) in enumerate(rows):
        rank_amount = rank_amounts[i] if i < len(rank_amounts) else 0
        perf_bonus = safe_int(performance_amount) + rank_amount
        updates.append((rank_amount, perf_bonus, dateday, name))
    if updates:
        executemany_with_retry(cursor, """
        UPDATE user_order_amount_statistics
        SET rank_amount=%s, performance_bonus=%s
        WHERE dateday=%s AND name=%s
        """, updates)
    execute_with_retry(cursor, """
    SELECT name, performance_amount, rank_amount, performance_bonus,
           (performance_amount + rank_amount) AS calc_bonus
    FROM user_order_amount_statistics
    WHERE dateday=%s
    """, (dateday,))
    wrong = [r for r in cursor.fetchall() if safe_int(r[3]) != safe_int(r[4])]
    if wrong:
        execute_with_retry(cursor, """
        UPDATE user_order_amount_statistics
        SET performance_bonus = performance_amount + rank_amount
        WHERE dateday=%s
        """, (dateday,))
    print("[RANK] 排名奖金计算完成")


def sync_to_gocrm(source_cursor):
    print("[SYNC] 开始同步数据到gocrm数据库...")
    gocrm_config = {
        'host': 'rm-j6ce98dcz1z47ee42so.mysql.rds.aliyuncs.com',
        'user': 'gocrm',
        'password': '4ijmvv7U',
        'database': 'gocrm',
        'port': 3306,
        'charset': 'utf8mb4'
    }
    gocrm_conn = None
    gocrm_cursor = None
    try:
        today_int = get_today_int()
        execute_with_retry(source_cursor, """
        SELECT dateday, name, ticket_num, order_num, first_run_num,
               sku_num, shipment_num, handmade_singular, rank_amount,
               performance_amount, performance_bonus
        FROM user_order_amount_statistics
        WHERE dateday=%s
        """, (today_int,))
        rows = source_cursor.fetchall()
        if not rows:
            print("[SYNC] 没有今天的数据需要同步")
            return
        gocrm_conn = pymysql.connect(**gocrm_config)
        gocrm_cursor = gocrm_conn.cursor()
        gocrm_conn.begin()
        execute_with_retry(gocrm_cursor, "DELETE FROM user_order_amount_statistics WHERE dateday=%s", (today_int,))
        executemany_with_retry(gocrm_cursor, """
        INSERT INTO user_order_amount_statistics
        (dateday,name,ticket_num,order_num,first_run_num,
         sku_num,shipment_num,handmade_singular,rank_amount,
         performance_amount,performance_bonus)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, rows)
        gocrm_conn.commit()
        print("[SYNC] 数据同步成功完成")
    except Exception as e:
        if gocrm_conn:
            gocrm_conn.rollback()
        print(f"[SYNC] 同步失败: {e}")
        logger.error(f"同步失败: {e}")
    finally:
        try:
            if gocrm_cursor:
                gocrm_cursor.close()
        except:
            pass
        try:
            if gocrm_conn:
                gocrm_conn.close()
        except:
            pass
        print("[SYNC] gocrm数据库连接已关闭")


def batch_check_existing_ids(cursor, intention_ids: List[str]) -> Set[str]:
    print(f"[BATCH] 批量检查 {len(intention_ids)} 个intention_id是否存在...")
    if not intention_ids:
        return set()
    today_date_string = get_today_date_string()
    placeholders = ','.join(['%s'] * len(intention_ids))
    query = f"""
    SELECT intention_id 
    FROM kpi_report 
    WHERE intention_id IN ({placeholders})
    AND DATE(create_time)=%s
    """
    execute_with_retry(cursor, query, intention_ids + [today_date_string])
    existing_ids = {str(r[0]) for r in cursor.fetchall()}
    print(f"[BATCH] 找到 {len(existing_ids)} 个已存在的intention_id（今天创建）")
    return existing_ids


def batch_process_first_run(cursor, connection, tasks: List[Tuple[str, str]]):
    print(f"[BATCH] 开始批量处理首次运行，共 {len(tasks)} 个任务")
    try:
        intention_ids = [t[1] for t in tasks]
        existing_info_records = batch_get_existing_kpi_info(cursor, intention_ids)

        print("[BATCH] 插入kpi_report记录...")
        # 使用INSERT IGNORE避免重复插入错误
        insert_data = []
        for conductor_name, intention_id in tasks:
            try:
                if conductor_name == "No data found or request unsuccessful":
                    conductor_id = get_conductor_id(intention_id)
                    if conductor_id:
                        tmp_name = get_conductor_name(conductor_id)
                        if tmp_name != "No data found or request unsuccessful":
                            if len(tmp_name) > 10:
                                tmp_name = tmp_name[:10]
                            conductor_name = tmp_name
                        else:
                            conductor_name = "系统用户"
                    else:
                        conductor_name = "系统用户"
                insert_data.append((intention_id, conductor_name))
            except Exception as e:
                print(f"[ERROR] 处理conductor_name时出错: {e}")
                insert_data.append((intention_id, "系统用户"))
        
        if insert_data:
            # 使用INSERT IGNORE避免重复插入
            executemany_with_retry(cursor,
                "INSERT IGNORE INTO kpi_report (intention_id, name) VALUES (%s,%s)",
                insert_data
            )
        connection.commit()

        all_order_data = batch_get_order_details_new(cursor, intention_ids)
        kpi_updates = []
        kpi_info_inserts = []
        for conductor_name, intention_id in tasks:
            if intention_id not in all_order_data:
                continue
            order_results = all_order_data[intention_id]
            existing_set = existing_info_records.get(intention_id, set())
            first_run_fail_count = delivery_count = manual_count = sku_count = 0
            invoice_order_count = len(order_results)
            for od in order_results:
                order_id = od['order_id']
                waybill_num = od['waybill_num']
                waybill_number = od['waybill_number']
                manual_status = od['manual_status']
                status = od['status']
                customer_english_title = od['customer_english_title']
                stop_product_variant = od['stop_product_variant']

                if waybill_num is None or waybill_num == '':
                    if status:
                        for status_item in parse_string_list(status):
                            if status_item and '三项备注' in str(status_item):
                                key = (f"{order_id}+首次运行失败", intention_id, '首次运行失败')
                                if key not in existing_set:
                                    kpi_info_inserts.append(key)
                                    first_run_fail_count += 1
                                break

                if status:
                    status_list = parse_string_list(status)
                    customer_titles = parse_string_list(customer_english_title)
                    variants = parse_string_list(stop_product_variant)
                    max_len = max(len(status_list), len(customer_titles), len(variants))
                    for i in range(max_len):
                        status_item = status_list[i] if i < len(status_list) else ""
                        cust_title = customer_titles[i] if i < len(customer_titles) else ""
                        variant = variants[i] if i < len(variants) else ""
                        # 修改后的SKU判断条件：增加了"未搜到未识别订单"的过滤
                        if (status_item and str(status_item).strip() != '' and
                                '三项备注' not in str(status_item) and '成功' not in str(status_item) and
                                '未搜到未识别订单' not in str(status_item)):
                            key = (f"{order_id}+{status_item}+{cust_title}+{variant}", intention_id, 'SKU')
                            if key not in existing_set:
                                kpi_info_inserts.append(key)
                                sku_count += 1

                if is_valid_waybill_number(waybill_number):
                    key = (order_id, intention_id, '交运')
                    if key not in existing_set:
                        kpi_info_inserts.append(key)
                        delivery_count += 1
                if manual_status and str(manual_status).startswith('https:'):
                    key = (order_id, intention_id, '手工')
                    if key not in existing_set:
                        kpi_info_inserts.append(key)
                        manual_count += 1

            kpi_updates.append((first_run_fail_count, invoice_order_count,
                                manual_count, delivery_count, sku_count, intention_id))

        if kpi_updates:
            executemany_with_retry(cursor, """
            UPDATE kpi_report
            SET first_run_fail_count=%s,
                invoice_order_count=%s,
                manual_error_num=%s,
                delivery_error_num=%s,
                sku_error_num=%s
            WHERE intention_id=%s AND DATE(create_time)=%s
            """, [u + (get_today_date_string(),) for u in kpi_updates])

        if kpi_info_inserts:
            batch_insert_kpi_info_with_dedup(cursor, kpi_info_inserts)
            remove_duplicates_from_kpi_info(cursor, connection)

        connection.commit()
        print("[BATCH] 首次运行批量处理完成")
    except Exception as e:
        print(f"[ERROR] 批量处理首次运行时出错: {e}")
        logger.error(f"批量处理首次运行时出错: {e}")
        raise


def batch_process_second_run(cursor, connection, intention_ids: List[str]):
    print(f"[BATCH] 开始批量处理二次运行，共 {len(intention_ids)} 个intention_id")
    try:
        all_order_data = batch_get_order_details_new(cursor, intention_ids)
        existing_info_records = batch_get_existing_kpi_info(cursor, intention_ids)
        kpi_info_inserts = []
        for intention_id in intention_ids:
            if intention_id not in all_order_data:
                continue
            order_results = all_order_data[intention_id]
            existing_set = existing_info_records.get(intention_id, set())
            for od in order_results:
                order_id = od['order_id']
                manual_status = od['manual_status']
                waybill_number = od['waybill_number']
                waybill_num = od['waybill_num']
                status = od['status']
                customer_english_title = od['customer_english_title']
                stop_product_variant = od['stop_product_variant']

                if waybill_num is None or waybill_num == '':
                    if status:
                        for status_item in parse_string_list(status):
                            if status_item and '三项备注' in str(status_item):
                                key = (f"{order_id}+首次运行失败", intention_id, '首次运行失败')
                                if key not in existing_set:
                                    kpi_info_inserts.append(key)
                                break

                if status:
                    status_list = parse_string_list(status)
                    customer_titles = parse_string_list(customer_english_title)
                    variants = parse_string_list(stop_product_variant)
                    max_len = max(len(status_list), len(customer_titles), len(variants))
                    for i in range(max_len):
                        status_item = status_list[i] if i < len(status_list) else ""
                        cust_title = customer_titles[i] if i < len(customer_titles) else ""
                        variant = variants[i] if i < len(variants) else ""
                        # 修改后的SKU判断条件：增加了"未搜到未识别订单"的过滤
                        if (status_item and str(status_item).strip() != '' and
                                '三项备注' not in str(status_item) and '成功' not in str(status_item) and
                                '未搜到未识别订单' not in str(status_item)):
                            key = (f"{order_id}+{status_item}+{cust_title}+{variant}", intention_id, 'SKU')
                            if key not in existing_set:
                                kpi_info_inserts.append(key)

                if manual_status and str(manual_status).startswith('https:'):
                    key = (order_id, intention_id, '手工')
                    if key not in existing_set:
                        kpi_info_inserts.append(key)
                if is_valid_waybill_number(waybill_number):
                    key = (order_id, intention_id, '交运')
                    if key not in existing_set:
                        kpi_info_inserts.append(key)

        if kpi_info_inserts:
            batch_insert_kpi_info_with_dedup(cursor, kpi_info_inserts)
            remove_duplicates_from_kpi_info(cursor, connection)

        today_date_string = get_today_date_string()
        update_data = []
        for intention_id in intention_ids:
            execute_with_retry(cursor, """
            SELECT type, COUNT(*)
            FROM kpi_report_info
            WHERE intention_id=%s AND DATE(create_time)=%s
            GROUP BY type
            """, (intention_id, today_date_string))
            type_counts = dict(cursor.fetchall())
            update_data.append((
                type_counts.get('首次运行失败', 0),
                type_counts.get('交运', 0),
                type_counts.get('SKU', 0),
                type_counts.get('手工', 0),
                intention_id,
                today_date_string
            ))
        if update_data:
            executemany_with_retry(cursor, """
            UPDATE kpi_report
            SET first_run_fail_count=%s,
                delivery_error_num=%s,
                sku_error_num=%s,
                manual_error_num=%s
            WHERE intention_id=%s AND DATE(create_time)=%s
            """, update_data)
        connection.commit()
        print(f"[BATCH] 二次运行批量处理完成，处理了 {len(intention_ids)} 个intention_id")
    except Exception as e:
        print(f"[ERROR] 批量处理二次运行时出错: {e}")
        logger.error(f"批量处理二次运行时出错: {e}")
        raise


def batch_get_order_details_new(cursor, intention_ids: List[str]) -> Dict[str, List[Dict]]:
    print(f"[BATCH] 批量获取 {len(intention_ids)} 个intention_id的order_details数据...")
    if not intention_ids:
        return {}
    placeholders = ','.join(['%s'] * len(intention_ids))
    query = f"""
    SELECT intention_id, order_id, waybill_num, waybill_number,
           manual_status, status, customer_english_title, stop_product_variant
    FROM order_details
    WHERE intention_id IN ({placeholders})
    """
    execute_with_retry(cursor, query, intention_ids)
    result = defaultdict(list)
    for row in cursor.fetchall():
        result[str(row[0])].append({
            'order_id': row[1],
            'waybill_num': row[2],
            'waybill_number': row[3],
            'manual_status': row[4],
            'status': row[5],
            'customer_english_title': row[6],
            'stop_product_variant': row[7]
        })
    print(f"[BATCH] 获取到 {len(result)} 个intention_id的order_details数据")
    return dict(result)


def batch_get_existing_kpi_info(cursor, intention_ids: List[str]) -> Dict[str, Set[Tuple]]:
    print(f"[BATCH] 批量获取 {len(intention_ids)} 个intention_id的已存在kpi_report_info记录...")
    if not intention_ids:
        return {}
    today_date_string = get_today_date_string()
    placeholders = ','.join(['%s'] * len(intention_ids))
    query = f"""
    SELECT intention_id, order_product_info, type
    FROM kpi_report_info
    WHERE intention_id IN ({placeholders})
    AND DATE(create_time)=%s
    """
    execute_with_retry(cursor, query, intention_ids + [today_date_string])
    result = defaultdict(set)
    for row in cursor.fetchall():
        result[str(row[0])].add((row[1], str(row[0]), row[2]))
    print(f"[BATCH] 获取到 {len(result)} 个intention_id的已存在kpi_report_info记录（今天创建）")
    return dict(result)


def batch_insert_kpi_info_with_dedup(cursor, data: List[Tuple]):
    print(f"[BATCH] 批量插入kpi_report_info（带去重检查），原始数据量: {len(data)}")
    if not data:
        return
    unique_data = list(set(data))
    first_run_fail_records = [r for r in unique_data if r[2] == "首次运行失败"]
    other_records = [r for r in unique_data if r[2] != "首次运行失败"]
    today_date_string = get_today_date_string()

    def filter_existing(records):
        if not records:
            return []
        check_conditions = []
        params = []
        for opi, iid, tp in records:
            check_conditions.append("(order_product_info=%s AND intention_id=%s AND type=%s)")
            params.extend([opi, iid, tp])
        query = f"""
        SELECT order_product_info, intention_id, type
        FROM kpi_report_info
        WHERE ({' OR '.join(check_conditions)}) AND DATE(create_time)=%s
        """
        params.append(today_date_string)
        execute_with_retry(cursor, query, params)
        existing = set(cursor.fetchall())
        return [r for r in records if r not in existing]

    first_to_insert = filter_existing(first_run_fail_records)
    other_to_insert = filter_existing(other_records)
    to_insert = first_to_insert + other_to_insert
    if not to_insert:
        print("[BATCH] 无需插入（全部已存在）")
        return

    # 使用INSERT IGNORE避免重复插入错误
    insert_query = """
    INSERT IGNORE INTO kpi_report_info(order_product_info, intention_id, type)
    VALUES (%s,%s,%s)
    """
    batch_size = 1000
    inserted = 0
    for i in range(0, len(to_insert), batch_size):
        batch = to_insert[i:i + batch_size]
        try:
            executemany_with_retry(cursor, insert_query, batch)
            inserted += cursor.rowcount
        except Exception as e:
            print(f"[ERROR] 批量插入失败，尝试单条插入: {e}")
            for rec in batch:
                try:
                    execute_with_retry(cursor, insert_query, rec)
                    inserted += cursor.rowcount
                except pymysql.err.IntegrityError:
                    pass  # 重复键，忽略
                except Exception as single_error:
                    print(f"[ERROR] 单条插入失败: {single_error}")
    print(f"[BATCH] kpi_report_info批量插入完成，实际插入 {inserted} 条记录")


def remove_duplicates_from_kpi_info(cursor, connection):
    print("[DEDUP] 去除kpi_report_info表中type为'首次运行失败'的重复数据(全表)...")
    try:
        delete_sql = """
        DELETE t1 FROM kpi_report_info t1
        JOIN kpi_report_info t2
          ON t1.order_product_info = t2.order_product_info
         AND t1.intention_id = t2.intention_id
         AND t1.type = t2.type
         AND t1.create_time < t2.create_time
        WHERE t1.type='首次运行失败'
        """
        execute_with_retry(cursor, delete_sql)
        deleted = cursor.rowcount
        print(f"[DEDUP] 删除了 {deleted} 条旧的重复记录")
        connection.commit()
    except Exception as e:
        print(f"[ERROR] 去重过程中出错: {e}")
        logger.error(f"去重过程中出错: {e}")
        raise


def parse_string_list(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except:
        try:
            return eval(value)
        except:
            return []


if __name__ == "__main__":
    process_first_and_second_run()
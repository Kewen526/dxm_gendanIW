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
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time
import random
import os


class DianxiaomiScraper:
    def __init__(self, cookie_json_path: str, debug: bool = True):
        self.cookie_json_path = cookie_json_path
        self.debug = debug
        self.session = requests.Session()
        self.base_url = "https://www.dianxiaomi.com/api/package/list.json"
        self._load_cookies()
        
    def _debug_print(self, message: str):
        if self.debug:
            print(message)
        
    def _load_cookies(self):
        try:
            print(f"[INFO] 正在读取cookie文件: {self.cookie_json_path}")
            
            with open(self.cookie_json_path, 'r', encoding='utf-8') as f:
                cookie_data = json.load(f)
            
            self._debug_print(f"[DEBUG] Cookie文件键: {list(cookie_data.keys())}")
            
            cookies_list = cookie_data.get('cookies', [])
            
            if not cookies_list:
                print("⚠️ 警告: cookie文件中没有cookies字段或为空")
            
            print(f"[INFO] 找到 {len(cookies_list)} 个cookies")
            
            for i, cookie in enumerate(cookies_list):
                cookie_name = cookie.get('name', 'unknown')
                cookie_domain = cookie.get('domain', '')
                cookie_value = cookie.get('value', '')
                
                self._debug_print(f"[DEBUG] Cookie {i+1}: {cookie_name} (domain: {cookie_domain}, value长度: {len(cookie_value)})")
                
                self.session.cookies.set(
                    name=cookie.get('name'),
                    value=cookie.get('value'),
                    domain=cookie.get('domain', ''),
                    path=cookie.get('path', '/')
                )
            
            print(f"✓ 成功加载 {len(cookies_list)} 个cookies")
            self._debug_print(f"[DEBUG] Session中的cookies数量: {len(self.session.cookies)}")
            
        except FileNotFoundError:
            print(f"✗ 错误: 找不到文件 {self.cookie_json_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"✗ 错误: JSON文件格式错误")
            self._debug_print(f"[DEBUG] 错误详情: {str(e)}")
            raise
        except Exception as e:
            print(f"✗ 加载cookie时发生未知错误: {type(e).__name__} - {str(e)}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'authority': 'www.dianxiaomi.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.5.11',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.dianxiaomi.com',
            'referer': 'https://www.dianxiaomi.com/web/order/all?go=m1-1',
            'sec-ch-ua': '"Chromium";v="109", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
    
    def _build_post_data(self, page_no: int = 1, page_size: int = 300) -> Dict[str, str]:
        return {
            'pageNo': str(page_no),
            'pageSize': str(page_size),
            'shopId': '-1',
            'state': '',
            'platform': '',
            'isSearch': '1',
            'searchType': 'orderId',
            'authId': '-1',
            'startTime': '',
            'endTime': '',
            'country': '',
            'orderField': 'order_create_time',
            'isVoided': '-1',
            'isRemoved': '-1',
            'ruleId': '-1',
            'sysRule': '',
            'applyType': '',
            'applyStatus': '',
            'printJh': '-1',
            'printMd': '-1',
            'commitPlatform': '',
            'productStatus': '',
            'jhComment': '-1',
            'storageId': '0',
            'isOversea': '-1',
            'isFree': '-1',
            'isBatch': '-1',
            'history': '',
            'custom': '-1',
            'timeOut': '0',
            'refundStatus': '0',
            'buyerAccount': '',
            'forbiddenStatus': '-1',
            'forbiddenReason': '0',
            'behindTrack': '-1',
            'orderId': '',
            'axios_cancelToken': 'true'
        }
    
    def fetch_one_page(self, page_no: int) -> Dict:
        try:
            data = self._build_post_data(page_no=page_no, page_size=300)
            
            self._debug_print(f"    [DEBUG] 请求参数: pageNo={page_no}, pageSize=300")
            
            response = self.session.post(
                self.base_url,
                headers=self._get_headers(),
                data=data,
                timeout=30
            )
            
            self._debug_print(f"    [DEBUG] HTTP状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"    ✗ HTTP错误: 状态码 {response.status_code}")
                self._debug_print(f"    [DEBUG] 响应内容: {response.text[:500]}")
                return None
            
            try:
                result = response.json()
            except json.JSONDecodeError as e:
                print(f"    ✗ JSON解析失败: {str(e)}")
                self._debug_print(f"    [DEBUG] 响应内容前500字符: {response.text[:500]}")
                return None
            
            self._debug_print(f"    [DEBUG] 响应键: {list(result.keys())}")
            
            # 检查code字段而不是success字段
            if result.get('code') != 0:
                print(f"    ✗ API返回失败!")
                self._debug_print(f"    [DEBUG] code字段: {result.get('code')}")
                self._debug_print(f"    [DEBUG] msg字段: {result.get('msg', '无')}")
                return None
            
            # 检查data字段
            if 'data' not in result:
                print(f"    ✗ 响应中缺少data字段")
                return None
            
            data_obj = result.get('data', {})
            
            # 数据在 data.page.list 中
            page_obj = data_obj.get('page', {})
            orders = page_obj.get('list', [])
            
            self._debug_print(f"    [DEBUG] 订单数量: {len(orders)}")
            
            return result
            
        except requests.exceptions.Timeout as e:
            print(f"    ✗ 请求超时: {str(e)}")
            return None
        except requests.exceptions.ConnectionError as e:
            print(f"    ✗ 连接错误: {str(e)}")
            return None
        except Exception as e:
            print(f"    ✗ 未知错误: {type(e).__name__} - {str(e)}")
            return None


def run_scraper(cookie_json_path: str, days: int) -> List[Dict]:
    all_responses = []
    
    print(f"\n[INFO] 初始化爬虫...")
    print(f"[INFO] Cookie文件: {cookie_json_path}")
    print(f"[INFO] 抓取天数: {days}")
    
    try:
        scraper = DianxiaomiScraper(cookie_json_path)
    except Exception as e:
        print(f"\n✗ 初始化失败: {str(e)}")
        return []
    
    today = datetime.now()
    cutoff_date = today - timedelta(days=days)
    
    print(f"\n开始翻页抓取订单数据...")
    print(f"当前日期: {today.strftime('%Y-%m-%d')}")
    print(f"截止日期: {cutoff_date.strftime('%Y-%m-%d')} (不包含)")
    print("=" * 60)
    
    page_no = 1
    total_orders = 0
    in_range_orders = 0
    
    while True:
        print(f"\n  → 第 {page_no} 页...")
        
        result = scraper.fetch_one_page(page_no)
        
        if not result:
            print(f"    ⚠️ 第 {page_no} 页请求失败，停止抓取")
            break
        
        all_responses.append(result)
        
        # 从 data.page.list 获取订单
        data = result.get('data', {})
        page_obj = data.get('page', {})
        orders = page_obj.get('list', [])
        
        if not orders:
            print(f"    ✓ 无更多数据")
            break
        
        page_in_range = 0
        page_out_range = 0
        earliest_date = None
        latest_date = None
        
        for order in orders:
            # 使用orderCreateTime字段（时间戳，毫秒）
            order_time_ms = order.get('orderCreateTime', 0)
            if order_time_ms:
                try:
                    order_time = datetime.fromtimestamp(order_time_ms / 1000.0)
                    
                    if earliest_date is None or order_time < earliest_date:
                        earliest_date = order_time
                    if latest_date is None or order_time > latest_date:
                        latest_date = order_time
                    
                    if order_time >= cutoff_date:
                        page_in_range += 1
                    else:
                        page_out_range += 1
                        
                except Exception as e:
                    print(f"    ⚠️ 日期解析失败: {order_time_ms}")
        
        total_orders += len(orders)
        in_range_orders += page_in_range
        
        date_range_str = ""
        if earliest_date and latest_date:
            if earliest_date.date() == latest_date.date():
                date_range_str = f" | 日期: {earliest_date.strftime('%Y-%m-%d')}"
            else:
                date_range_str = f" | 日期: {latest_date.strftime('%Y-%m-%d')} ~ {earliest_date.strftime('%Y-%m-%d')}"
        
        print(f"    ✓ 获取 {len(orders)} 条订单 (范围内: {page_in_range}, 范围外: {page_out_range}){date_range_str}")
        print(f"    [累计] 总订单: {total_orders}, 范围内: {in_range_orders}, 响应页数: {len(all_responses)}")
        
        if page_out_range > 0 and page_in_range == 0:
            print(f"    ✓ 已超出日期范围，停止翻页")
            break
        
        page_no += 1
        
        delay = random.uniform(3, 5)
        print(f"  ⏱️  等待 {delay:.1f} 秒...", end=" ")
        time.sleep(delay)
        print("继续")
    
    print("\n" + "=" * 60)
    print(f"🎉 抓取完成!")
    print(f"  - 共请求: {len(all_responses)} 页")
    print(f"  - 总订单: {total_orders} 条")
    print(f"  - 范围内: {in_range_orders} 条")
    
    return all_responses


if __name__ == "__main__":
    responses = run_scraper(
        cookie_json_path="cookie.json",
        days=3
    )
    
    print(f"\n返回的响应列表长度: {len(responses)}")
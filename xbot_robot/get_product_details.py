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
import time
import hmac
import hashlib
import json

def get_product_details(offer_id):
    # 基本信息
    app_key = '2019459'
    secret = 'XgepZVNu5iz'
    access_token = '1c87e807-03ff-4d1e-a08f-72746cb06c64'
    api_url = 'https://gw.open.1688.com/openapi/param2/1/com.alibaba.fenxiao.crossborder/product.search.queryProductDetail/2019459'
    url_path = 'param2/1/com.alibaba.fenxiao.crossborder/product.search.queryProductDetail/2019459'  # 注意这里不带前面的斜杠
    
    # 添加重试逻辑
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 请求参数
            offer_detail_param = {
                'offerId': offer_id,
                'country': 'en'
            }
            params = {
                'offerDetailParam': json.dumps(offer_detail_param),  # 使用 JSON 格式化 offerDetailParam 参数
                'access_token': access_token,
                '_aop_timestamp': str(int(time.time() * 1000)),  # 使用当前时间戳
            }
            # 拼装参数
            sorted_params = sorted(params.items())
            query_string = ''.join(f"{k}{v}" for k, v in sorted_params)
            # 合并签名因子和拼装参数
            sign_string = url_path + query_string
            # 对合并后的签名因子执行hmac_sha1算法
            signature = hmac.new(secret.encode('utf-8'), sign_string.encode('utf-8'), hashlib.sha1).hexdigest().upper()
            params['_aop_signature'] = signature
            # 发送请求
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
            response = requests.post(api_url, data=params, headers=headers)
            result = response.json()
            
            # 检查响应是否包含错误
            if 'error' not in result:
                return result
            
            # 如果有错误，增加重试次数
            retry_count += 1
            print(f"API返回错误，正在进行第{retry_count}次重试...")
            time.sleep(1)  # 等待1秒后重试
        
        except Exception as e:
            retry_count += 1
            print(f"请求异常: {e}，正在进行第{retry_count}次重试...")
            time.sleep(1)
    
    # 如果所有重试都失败，返回最后一次的结果
    return result
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
import json
import hashlib
import time
import random
from abc import ABC, abstractmethod

class TranslatorBase(ABC):
    """翻译器基类"""
    
    @abstractmethod
    def translate(self, text, source='zh', target='en'):
        pass

class YoudaoTranslator(TranslatorBase):
    """改进的有道翻译"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://fanyi.youdao.com/',
            'Cookie': 'OUTFOX_SEARCH_USER_ID=124042336@10.169.0.83;'
        }
    
    def translate(self, text, source='zh-CHS', target='en'):
        url = 'https://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
        
        # 生成时间戳和盐值
        salt = str(int(time.time() * 1000) + random.randint(1, 10))
        
        data = {
            'i': text,
            'from': source,
            'to': target,
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10)
            # 调试信息
            print(f"Status Code: {response.status_code}")
            print(f"Response Text (first 200 chars): {response.text[:200]}")
            
            # 检查响应内容
            if response.status_code != 200:
                return {
                    'original': text,
                    'error': f'HTTP Error: {response.status_code}',
                    'success': False
                }
            
            # 尝试解析JSON
            try:
                result = response.json()
            except json.JSONDecodeError:
                return {
                    'original': text,
                    'error': 'Invalid JSON response',
                    'success': False
                }
            
            if 'translateResult' in result:
                translated = result['translateResult'][0][0]['tgt']
                return {
                    'original': text,
                    'translated': translated,
                    'success': True
                }
            else:
                return {
                    'original': text,
                    'error': f'Unexpected response format: {result}',
                    'success': False
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'original': text,
                'error': f'Request failed: {str(e)}',
                'success': False
            }
        except Exception as e:
            return {
                'original': text,
                'error': f'Unexpected error: {str(e)}',
                'success': False
            }

class GoogleTranslateSimple(TranslatorBase):
    """简单的Google翻译（使用translate.googleapis.com）"""
    
    def translate(self, text, source='zh-CN', target='en'):
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': source,
            'tl': target,
            'dt': 't',
            'q': text
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Google Translate返回的是嵌套数组
                result = response.json()
                translated = ''.join([item[0] for item in result[0] if item[0]])
                
                return {
                    'original': text,
                    'translated': translated,
                    'success': True
                }
            else:
                return {
                    'original': text,
                    'error': f'HTTP Error: {response.status_code}',
                    'success': False
                }
                
        except Exception as e:
            return {
                'original': text,
                'error': str(e),
                'success': False
            }

class BingTranslator(TranslatorBase):
    """使用Bing翻译"""
    
    def translate(self, text, source='zh-Hans', target='en'):
        # 注意：这是一个示例，实际使用需要API密钥
        # 这里提供一个使用requests-html的替代方案
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Bing翻译的URL格式
        url = f'https://www.bing.com/ttranslatev3'
        
        data = {
            'fromLang': source,
            'to': target,
            'text': text
        }
        
        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    translated = result[0].get('translations', [{}])[0].get('text', '')
                    if translated:
                        return {
                            'original': text,
                            'translated': translated,
                            'success': True
                        }
            
            return {
                'original': text,
                'error': 'Translation failed',
                'success': False
            }
                
        except Exception as e:
            return {
                'original': text,
                'error': str(e),
                'success': False
            }

class TranslatorManager:
    """翻译管理器，支持多种翻译服务"""
    
    def __init__(self):
        self.translators = {
            'youdao': YoudaoTranslator(),
            'google': GoogleTranslateSimple(),
            'bing': BingTranslator(),
        }
    
    def translate(self, text, service='google', **kwargs):
        """使用指定服务翻译"""
        if service in self.translators:
            return self.translators[service].translate(text, **kwargs)
        else:
            return {
                'original': text,
                'error': f'Service {service} not found',
                'success': False
            }
    
    def translate_with_fallback(self, text, services=['google', 'youdao', 'bing'], **kwargs):
        """使用多个服务，失败时自动切换"""
        for service in services:
            print(f"尝试使用 {service} 翻译...")
            result = self.translate(text, service, **kwargs)
            if result['success']:
                result['service'] = service
                return result
            else:
                print(f"{service} 失败: {result.get('error', 'Unknown error')}")
        
        return {
            'original': text,
            'error': 'All translation services failed',
            'success': False
        }

# 带缓存的翻译器
class CachedTranslator:
    def __init__(self, translator_manager):
        self.translator_manager = translator_manager
        self.cache = {}
    
    def translate(self, text, service='google', **kwargs):
        cache_key = f"{text}_{service}_{kwargs}"
        
        if cache_key in self.cache:
            print(f"从缓存获取: {text}")
            return self.cache[cache_key]
        
        result = self.translator_manager.translate(text, service, **kwargs)
        if result['success']:
            self.cache[cache_key] = result
        
        return result
    
    def translate_with_fallback(self, text, **kwargs):
        cache_key = f"{text}_fallback_{kwargs}"
        
        if cache_key in self.cache:
            print(f"从缓存获取: {text}")
            return self.cache[cache_key]
        
        result = self.translator_manager.translate_with_fallback(text, **kwargs)
        if result['success']:
            self.cache[cache_key] = result
        
        return result
    
    def clear_cache(self):
        self.cache.clear()

def test_translation():
    """测试翻译功能"""
    manager = TranslatorManager()
    
    # 测试单个服务
    print("=== 测试Google翻译 ===")
    result = manager.translate("计算机视觉是人工智能的重要领域", service='google')
    if result['success']:
        print(f"原文: {result['original']}")
        print(f"译文: {result['translated']}")
    else:
        print(f"翻译失败: {result.get('error', 'Unknown error')}")
    
    print("\n=== 测试带回退的翻译 ===")
    result = manager.translate_with_fallback("机器学习是人工智能的一个分支")
    if result['success']:
        print(f"使用服务: {result.get('service', 'Unknown')}")
        print(f"原文: {result['original']}")
        print(f"译文: {result['translated']}")
    else:
        print(f"所有服务都失败了")
    
    print("\n=== 测试缓存翻译 ===")
    cached_translator = CachedTranslator(manager)
    
    texts = [
        "深度学习",
        "神经网络",
        "深度学习",  # 重复，会从缓存获取
    ]
    
    for text in texts:
        result = cached_translator.translate_with_fallback(text)
        if result['success']:
            print(f"{result['original']} -> {result['translated']} (服务: {result.get('service', 'cached')})")

def translate_text(text, service='google'):
    """翻译单个文本的便捷函数"""
    manager = TranslatorManager()
    # 如果单个服务失败，自动尝试其他服务
    result = manager.translate(text, service)
    if not result['success']:
        print(f"{service} 翻译失败，尝试其他服务...")
        result = manager.translate_with_fallback(text)
    
    if result['success']:
        return result['translated']
    else:
        return f"翻译失败: {result.get('error', 'Unknown error')}"
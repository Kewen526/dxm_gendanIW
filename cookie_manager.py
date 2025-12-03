"""
Cookie管理器 - 自动下载、缓存和刷新Cookie
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta
import config


class CookieManager:
    """Cookie管理器类"""

    def __init__(self):
        self.cookie_url = config.COOKIE_URL
        self.local_path = config.LOCAL_COOKIE_PATH
        self.cache_dir = config.COOKIE_CACHE_DIR
        self.cache_minutes = config.COOKIE_CACHE_MINUTES
        self.timeout = config.DOWNLOAD_TIMEOUT
        self.retry_times = config.RETRY_TIMES
        self.retry_delay = config.RETRY_DELAY

        # 确保缓存目录存在
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"[CookieManager] 创建缓存目录: {self.cache_dir}")

    def _is_cache_valid(self):
        """检查本地缓存是否有效"""
        if not os.path.exists(self.local_path):
            return False

        # 检查文件修改时间
        file_mtime = os.path.getmtime(self.local_path)
        file_time = datetime.fromtimestamp(file_mtime)
        now = datetime.now()

        # 判断是否过期
        if now - file_time > timedelta(minutes=self.cache_minutes):
            print(f"[CookieManager] Cookie缓存已过期 (超过{self.cache_minutes}分钟)")
            return False

        # 检查文件是否为空或格式错误
        try:
            with open(self.local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'cookies' not in data or not data['cookies']:
                    print("[CookieManager] Cookie文件格式错误")
                    return False
        except Exception as e:
            print(f"[CookieManager] Cookie文件读取失败: {e}")
            return False

        return True

    def _download_cookie(self):
        """从URL下载Cookie文件"""
        print(f"[CookieManager] 正在从URL下载Cookie...")
        print(f"[CookieManager] URL: {self.cookie_url}")

        for attempt in range(self.retry_times):
            try:
                response = requests.get(self.cookie_url, timeout=self.timeout)
                response.raise_for_status()

                # 验证JSON格式
                cookie_data = response.json()
                if 'cookies' not in cookie_data:
                    raise ValueError("Cookie数据格式错误：缺少'cookies'字段")

                # 保存到本地
                with open(self.local_path, 'w', encoding='utf-8') as f:
                    json.dump(cookie_data, f, ensure_ascii=False, indent=2)

                print(f"[CookieManager] ✓ Cookie下载成功，已保存到: {self.local_path}")
                print(f"[CookieManager] ✓ 包含 {len(cookie_data['cookies'])} 个cookies")
                return True

            except requests.exceptions.RequestException as e:
                print(f"[CookieManager] ✗ 下载失败 (尝试 {attempt + 1}/{self.retry_times}): {e}")
                if attempt < self.retry_times - 1:
                    print(f"[CookieManager] 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
            except Exception as e:
                print(f"[CookieManager] ✗ 下载失败: {e}")
                return False

        print(f"[CookieManager] ✗ Cookie下载失败，已重试 {self.retry_times} 次")
        return False

    def get_cookie_path(self, force_refresh=False):
        """
        获取可用的Cookie文件路径

        Args:
            force_refresh (bool): 是否强制刷新Cookie

        Returns:
            str: 本地Cookie文件路径，如果获取失败返回None
        """
        # 如果强制刷新或缓存无效，则下载
        if force_refresh or not self._is_cache_valid():
            if not self._download_cookie():
                # 如果下载失败，检查是否有旧的缓存可用
                if os.path.exists(self.local_path):
                    print("[CookieManager] ⚠️  使用旧的Cookie缓存")
                    return self.local_path
                else:
                    print("[CookieManager] ✗ 无法获取Cookie")
                    return None
        else:
            print(f"[CookieManager] ✓ 使用缓存的Cookie: {self.local_path}")

        return self.local_path

    def refresh_cookie(self):
        """手动刷新Cookie"""
        return self.get_cookie_path(force_refresh=True)


# 创建全局实例
_cookie_manager = CookieManager()


def get_cookie_path(force_refresh=False):
    """
    获取Cookie文件路径的便捷函数

    Args:
        force_refresh (bool): 是否强制刷新

    Returns:
        str: Cookie文件路径
    """
    return _cookie_manager.get_cookie_path(force_refresh)


def refresh_cookie():
    """刷新Cookie的便捷函数"""
    return _cookie_manager.refresh_cookie()


if __name__ == "__main__":
    # 测试Cookie管理器
    print("=" * 60)
    print("测试Cookie管理器")
    print("=" * 60)

    # 测试获取Cookie
    cookie_path = get_cookie_path()
    if cookie_path:
        print(f"\n✓ 成功获取Cookie路径: {cookie_path}")

        # 读取并显示Cookie信息
        with open(cookie_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✓ Cookie数量: {len(data['cookies'])}")
    else:
        print("\n✗ 获取Cookie失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

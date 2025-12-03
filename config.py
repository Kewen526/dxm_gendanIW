"""
配置文件 - 管理所有配置项
"""
import os

# ==================== Cookie配置 ====================
# Cookie文件的远程URL（固定）
COOKIE_URL = "https://ceshi-1300392622.cos.ap-beijing.myqcloud.com/dxm_cookie.json"

# 本地Cookie缓存目录
COOKIE_CACHE_DIR = os.path.join(os.path.dirname(__file__), "cookie_cache")

# 本地Cookie文件路径
LOCAL_COOKIE_PATH = os.path.join(COOKIE_CACHE_DIR, "dxm_cookie.json")

# Cookie缓存时间（分钟），超过这个时间会重新下载
COOKIE_CACHE_MINUTES = 30

# ==================== HTTP配置 ====================
# 下载超时时间（秒）
DOWNLOAD_TIMEOUT = 30

# 请求重试次数
RETRY_TIMES = 3

# 重试延迟（秒）
RETRY_DELAY = 2

# ==================== API服务器配置 ====================
# API服务器地址
API_HOST = "0.0.0.0"

# API服务器端口
API_PORT = 5000

# 是否开启调试模式
DEBUG = True

# ==================== 日志配置 ====================
# 日志目录
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

# 日志文件名
LOG_FILE = os.path.join(LOG_DIR, "api_service.log")

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = "INFO"

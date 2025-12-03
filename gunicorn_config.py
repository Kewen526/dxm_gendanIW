# Gunicorn配置文件
import multiprocessing

# 绑定地址和端口
bind = "0.0.0.0:5000"

# 工作进程数（建议: CPU核心数 * 2 + 1）
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式（sync, gevent, eventlet等）
worker_class = "sync"

# 每个worker的线程数
threads = 2

# 超时时间（秒）
timeout = 120

# 保持连接时间（秒）
keepalive = 5

# 日志级别
loglevel = "info"

# 访问日志
accesslog = "/home/user/dxm_gendanIW/logs/access.log"

# 错误日志
errorlog = "/home/user/dxm_gendanIW/logs/error.log"

# 进程名称
proc_name = "dxm_api"

# 后台运行
daemon = False

# 最大请求数（防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 优雅重启超时
graceful_timeout = 30

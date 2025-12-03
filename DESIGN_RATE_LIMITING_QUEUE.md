# 店小秘API限流队列服务器 - 详细设计方案

## 📋 目录
1. [系统架构](#1-系统架构)
2. [核心组件设计](#2-核心组件设计)
3. [API接口规范](#3-api接口规范)
4. [限流算法实现](#4-限流算法实现)
5. [客户端改造方案](#5-客户端改造方案)
6. [部署方案](#6-部署方案)
7. [监控与日志](#7-监控与日志)

---

## 1. 系统架构

### 1.1 整体架构图
```
┌─────────────────┐
│  客户端代码 1   │────┐
└─────────────────┘    │
                       │
┌─────────────────┐    │    ┌──────────────────────┐
│  客户端代码 2   │────┼───→│  限流队列服务器      │
└─────────────────┘    │    │  (FastAPI)           │
                       │    │  - HTTP接口层        │
┌─────────────────┐    │    │  - 请求队列          │
│  客户端代码 N   │────┘    │  - 限流控制 (8次/s) │
└─────────────────┘         │  - Cookie管理        │
                            │  - 重试机制          │
                            └──────────┬───────────┘
                                       │
                                       ↓
                            ┌──────────────────────┐
                            │  店小秘API服务器     │
                            │  (限制: 10次/s)     │
                            └──────────────────────┘
```

### 1.2 设计原则
- **单一职责**: 服务器只负责限流和转发
- **可靠性**: 支持失败重试和错误处理
- **可扩展性**: 易于添加新的API端点
- **可监控性**: 完整的日志和统计信息

---

## 2. 核心组件设计

### 2.1 请求队列管理器
```python
class RequestQueueManager:
    """
    管理所有待处理的API请求
    - 使用asyncio.Queue实现异步队列
    - FIFO (先进先出) 策略
    - 支持优先级 (可选扩展)
    """
```

### 2.2 限流控制器
```python
class RateLimiter:
    """
    实现令牌桶算法
    - 速率: 8 requests/second
    - 容量: 8 tokens (允许短时间突发)
    - 补充速率: 每125ms补充1个token
    """
```

### 2.3 Cookie管理器
```python
class CookieManager:
    """
    管理cookie文件的加载和缓存
    - 文件缓存机制
    - 自动重载检测
    - 支持多账号切换 (可选)
    """
```

### 2.4 请求执行器
```python
class RequestExecutor:
    """
    执行实际的HTTP请求
    - 失败重试 (最多3次)
    - 超时控制 (30秒)
    - 错误分类和处理
    """
```

---

## 3. API接口规范

### 3.1 统一请求接口

**端点**: `POST /api/proxy`

**请求格式**:
```json
{
  "url": "https://www.dianxiaomi.com/api/package/searchPackage.json",
  "method": "POST",
  "headers": {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
  },
  "data": {
    "pageNo": "1",
    "pageSize": "100",
    "content": "order-123"
  },
  "cookie_file": "cookie.json",
  "timeout": 30,
  "retry": 3,
  "priority": 0
}
```

**参数说明**:
- `url` (必填): 店小秘API的完整URL
- `method` (可选): HTTP方法，默认POST
- `headers` (可选): 额外的HTTP头
- `data` (可选): 请求数据
- `cookie_file` (必填): cookie文件路径
- `timeout` (可选): 超时时间(秒)，默认30
- `retry` (可选): 重试次数，默认3
- `priority` (可选): 优先级，0最高，默认0

**响应格式**:
```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "code": 0,
    "msg": "success",
    "data": {...}
  },
  "queue_info": {
    "queue_size": 5,
    "position": 3,
    "wait_time": 0.375
  },
  "meta": {
    "request_id": "uuid-xxx",
    "timestamp": 1234567890,
    "retry_count": 0
  }
}
```

### 3.2 服务器状态接口

**端点**: `GET /api/status`

**响应**:
```json
{
  "server_status": "running",
  "queue_size": 12,
  "rate_limit": {
    "current_rate": "8/s",
    "tokens_available": 5,
    "next_token_time": 0.05
  },
  "statistics": {
    "total_requests": 1523,
    "successful_requests": 1498,
    "failed_requests": 25,
    "avg_response_time": 0.856,
    "uptime": 86400
  }
}
```

### 3.3 健康检查接口

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "timestamp": 1234567890
}
```

---

## 4. 限流算法实现

### 4.1 令牌桶算法
```python
import time
import asyncio
from typing import Optional

class TokenBucket:
    def __init__(self, rate: float = 8.0, capacity: int = 8):
        """
        Args:
            rate: 每秒生成的令牌数 (8次/s)
            capacity: 桶的最大容量 (允许突发8个请求)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> float:
        """
        获取一个令牌，如果没有则等待
        Returns:
            等待时间(秒)
        """
        async with self._lock:
            now = time.time()
            # 补充令牌
            elapsed = now - self.last_update
            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.rate
            )
            self.last_update = now

            # 如果有令牌，立即返回
            if self.tokens >= 1:
                self.tokens -= 1
                return 0.0

            # 否则计算等待时间
            wait_time = (1 - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
            self.tokens = 0
            self.last_update = time.time()
            return wait_time
```

### 4.2 滑动窗口算法 (备选方案)
```python
from collections import deque
import time

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 8, window_size: float = 1.0):
        """
        Args:
            max_requests: 窗口内最大请求数
            window_size: 窗口大小(秒)
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = deque()

    async def acquire(self) -> float:
        """获取许可"""
        now = time.time()

        # 移除窗口外的请求
        while self.requests and now - self.requests[0] > self.window_size:
            self.requests.popleft()

        # 检查是否超限
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return 0.0

        # 计算等待时间
        oldest = self.requests[0]
        wait_time = self.window_size - (now - oldest) + 0.001
        await asyncio.sleep(wait_time)
        self.requests.append(time.time())
        return wait_time
```

---

## 5. 客户端改造方案

### 5.1 通用客户端包装器

创建一个统一的客户端库，包装所有店小秘API调用：

**文件**: `dxm_client.py`
```python
import requests
import json
from typing import Dict, Any, Optional

class DianxiaomiClient:
    def __init__(self,
                 server_url: str = "http://localhost:8000",
                 cookie_file: str = "cookie.json",
                 timeout: int = 60):
        """
        Args:
            server_url: 限流服务器地址
            cookie_file: cookie文件路径
            timeout: 请求超时时间
        """
        self.server_url = server_url
        self.cookie_file = cookie_file
        self.timeout = timeout

    def request(self,
                url: str,
                method: str = "POST",
                headers: Optional[Dict] = None,
                data: Optional[Dict] = None,
                **kwargs) -> Dict[str, Any]:
        """
        发送请求到限流服务器

        Args:
            url: 店小秘API的URL
            method: HTTP方法
            headers: 请求头
            data: 请求数据
            **kwargs: 其他参数

        Returns:
            店小秘API的响应
        """
        proxy_url = f"{self.server_url}/api/proxy"

        payload = {
            "url": url,
            "method": method,
            "headers": headers or {},
            "data": data or {},
            "cookie_file": self.cookie_file,
            **kwargs
        }

        response = requests.post(
            proxy_url,
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()

        result = response.json()

        if not result.get("success"):
            raise Exception(f"Request failed: {result.get('error')}")

        return result.get("data")
```

### 5.2 改造现有函数

**改造前** (`search_dianxiaomi_package.py`):
```python
def get_dianxiaomi_order_id(cookie_file_path, content):
    # 直接调用店小秘API
    response = requests.post(url, headers=headers, data=data, cookies=cookies)
    return response.json()
```

**改造后**:
```python
from dxm_client import DianxiaomiClient

def get_dianxiaomi_order_id(cookie_file_path, content):
    # 通过限流服务器调用
    client = DianxiaomiClient(cookie_file=cookie_file_path)

    url = 'https://www.dianxiaomi.com/api/package/searchPackage.json'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/x-www-form-urlencoded',
        # ...其他headers
    }
    data = {
        'pageNo': '1',
        'pageSize': '100',
        'content': content,
        # ...其他参数
    }

    result = client.request(url, method="POST", headers=headers, data=data)
    return result
```

### 5.3 批量改造脚本

**文件**: `migrate_to_rate_limiter.py`
```python
"""
自动改造现有代码，将直接调用改为通过限流服务器调用
"""
import os
import re

def migrate_file(file_path: str):
    """改造单个Python文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 添加import
    if 'from dxm_client import DianxiaomiClient' not in content:
        content = 'from dxm_client import DianxiaomiClient\n' + content

    # 查找并替换requests.post调用
    # 这里需要根据实际情况编写正则表达式
    # ...

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 需要改造的文件列表
files_to_migrate = [
    "xbot_robot/search_dianxiaomi_package.py",
    "xbot_robot/add_product_to_dianxiaomi.py",
    "xbot_robot/batch_commit_platform_packages.py",
    # ...其他27个文件
]

for file_path in files_to_migrate:
    migrate_file(file_path)
```

---

## 6. 部署方案

### 6.1 项目结构
```
rate_limiter_server/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── rate_limiter.py      # 限流器实现
│   ├── queue_manager.py     # 队列管理器
│   ├── cookie_manager.py    # Cookie管理器
│   ├── request_executor.py  # 请求执行器
│   └── models.py            # 数据模型
├── tests/
│   ├── test_rate_limiter.py
│   └── test_queue.py
├── config/
│   └── settings.py          # 配置文件
├── logs/                    # 日志目录
├── requirements.txt
├── Dockerfile              # Docker镜像
├── docker-compose.yml      # Docker编排
└── README.md
```

### 6.2 配置文件

**文件**: `config/settings.py`
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 限流配置
    RATE_LIMIT: float = 8.0  # 每秒请求数
    RATE_CAPACITY: int = 8   # 令牌桶容量

    # 队列配置
    MAX_QUEUE_SIZE: int = 1000
    QUEUE_TIMEOUT: int = 300  # 队列等待超时(秒)

    # 请求配置
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # 重试延迟(秒)

    # Cookie配置
    COOKIE_CACHE_TTL: int = 3600  # Cookie缓存时间(秒)

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/server.log"

    class Config:
        env_file = ".env"

settings = Settings()
```

### 6.3 Docker部署

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY app/ ./app/
COPY config/ ./config/

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 8000

# 启动服务
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  rate_limiter:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
      - ./cookie.json:/app/cookie.json
    environment:
      - RATE_LIMIT=8.0
      - MAX_QUEUE_SIZE=1000
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 6.4 systemd服务 (Linux)

**文件**: `/etc/systemd/system/dxm-rate-limiter.service`
```ini
[Unit]
Description=Dianxiaomi Rate Limiter Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/rate_limiter_server
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动命令:
```bash
sudo systemctl enable dxm-rate-limiter
sudo systemctl start dxm-rate-limiter
sudo systemctl status dxm-rate-limiter
```

---

## 7. 监控与日志

### 7.1 日志记录

**日志级别**:
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息(请求/响应)
- `WARNING`: 警告信息(重试、慢请求)
- `ERROR`: 错误信息(失败的请求)

**日志格式**:
```
2025-12-03 10:23:45.123 | INFO | request_id=abc123 | url=/api/package/searchPackage.json | status=200 | duration=0.856s | queue_wait=0.125s
```

### 7.2 性能指标

**统计指标**:
- 总请求数
- 成功/失败请求数
- 平均响应时间
- P50/P95/P99延迟
- 队列长度
- 令牌使用率
- 错误率

**Prometheus监控** (可选):
```python
from prometheus_client import Counter, Histogram, Gauge

# 定义指标
request_counter = Counter('dxm_requests_total', 'Total requests')
request_duration = Histogram('dxm_request_duration_seconds', 'Request duration')
queue_size = Gauge('dxm_queue_size', 'Current queue size')
error_counter = Counter('dxm_errors_total', 'Total errors')
```

### 7.3 告警规则

**告警条件**:
1. 队列长度 > 500: 警告
2. 队列长度 > 800: 严重
3. 错误率 > 5%: 警告
4. 错误率 > 10%: 严重
5. 平均响应时间 > 5s: 警告
6. 服务不可用: 严重

---

## 8. 测试方案

### 8.1 单元测试
```python
import pytest
from app.rate_limiter import TokenBucket

@pytest.mark.asyncio
async def test_token_bucket():
    limiter = TokenBucket(rate=8.0, capacity=8)

    # 测试突发请求
    for i in range(8):
        wait_time = await limiter.acquire()
        assert wait_time == 0.0

    # 第9个请求应该等待
    wait_time = await limiter.acquire()
    assert wait_time > 0
```

### 8.2 压力测试
```python
import asyncio
import aiohttp

async def stress_test(num_requests: int = 100):
    """
    发送大量并发请求测试限流效果
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            task = session.post(
                "http://localhost:8000/api/proxy",
                json={"url": "...", "data": {...}}
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # 验证限流效果
        # 预期: 100个请求应该在 100/8 = 12.5秒内完成
```

### 8.3 集成测试
```bash
# 启动服务器
python -m uvicorn app.main:app --reload

# 运行测试
pytest tests/ -v

# 压力测试
locust -f tests/locustfile.py --host=http://localhost:8000
```

---

## 9. 实施计划

### 阶段1: 核心开发 (1-2周)
- [ ] 实现TokenBucket限流器
- [ ] 实现请求队列管理器
- [ ] 实现Cookie管理器
- [ ] 实现请求执行器
- [ ] 开发FastAPI服务器

### 阶段2: 客户端改造 (1周)
- [ ] 开发DianxiaomiClient包装器
- [ ] 改造27个接口函数
- [ ] 编写单元测试

### 阶段3: 测试验证 (3-5天)
- [ ] 单元测试
- [ ] 集成测试
- [ ] 压力测试
- [ ] 功能验证

### 阶段4: 部署上线 (2-3天)
- [ ] 配置生产环境
- [ ] 部署服务器
- [ ] 灰度测试
- [ ] 全量上线

### 阶段5: 监控优化 (持续)
- [ ] 监控运行状态
- [ ] 收集性能数据
- [ ] 优化参数配置
- [ ] 问题修复

---

## 10. 风险与应对

### 10.1 风险识别

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 服务器单点故障 | 高 | 中 | 部署高可用集群 |
| Cookie失效 | 中 | 高 | 自动检测和告警 |
| 队列积压 | 中 | 中 | 限制最大队列长度 |
| 网络问题 | 中 | 低 | 重试机制 |
| 代码Bug | 低 | 中 | 完善测试 |

### 10.2 回滚方案

如果限流服务器出现问题，可以快速回滚到直接调用模式：
```python
# 在DianxiaomiClient中添加降级逻辑
class DianxiaomiClient:
    def __init__(self, fallback_mode: bool = False):
        self.fallback_mode = fallback_mode

    def request(self, url, **kwargs):
        if self.fallback_mode:
            # 直接调用店小秘API (旧方式)
            return self._direct_request(url, **kwargs)
        else:
            # 通过限流服务器 (新方式)
            return self._proxy_request(url, **kwargs)
```

---

## 11. 总结

这个方案提供了一个完整的店小秘API限流队列系统：

### 优势
- ✅ 全局统一限流，确保不超过10次/s
- ✅ 8次/s的保守设置，留有安全余量
- ✅ 支持多客户端并发访问
- ✅ 完善的错误处理和重试机制
- ✅ 易于监控和维护
- ✅ 代码改造成本可控

### 技术栈
- **后端**: Python 3.10+ / FastAPI
- **限流算法**: 令牌桶 / 滑动窗口
- **异步框架**: asyncio / aiohttp
- **部署**: Docker / systemd
- **监控**: 日志 / Prometheus (可选)

### 下一步
请告诉我您是否需要：
1. 立即开始实现这个方案
2. 对某些部分进行调整
3. 添加其他功能

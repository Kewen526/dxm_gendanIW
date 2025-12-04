# 通用HTTP API代理服务 - 使用文档

## 📋 目录

- [概述](#概述)
- [架构设计](#架构设计)
- [快速开始](#快速开始)
- [客户端API](#客户端api)
- [服务器API](#服务器api)
- [使用示例](#使用示例)
- [错误处理](#错误处理)
- [最佳实践](#最佳实践)
- [FAQ](#faq)

---

## 概述

### 什么是通用HTTP API代理服务？

这是一个**统一的HTTP代理服务**，可以代理执行任意HTTP请求，并自动处理Cookie注入和速率限制。

### 核心特点

✅ **单一Endpoint** - 只需要一个API接口
✅ **自动Cookie注入** - 服务器自动管理Cookie，客户端无需关心
✅ **速率限制** - 8次/秒，防止被目标服务器封禁
✅ **支持POST和GET** - 覆盖所有常见HTTP请求
✅ **自动重试** - 遇到速率限制自动重试
✅ **完全自包含** - 客户端代码无需外部依赖

### 服务器地址

```
http://47.104.72.198:5000
```

---

## 架构设计

### 数据流

```
┌─────────────────┐
│   用户代码       │
│  api_call(...)  │
└────────┬────────┘
         │ POST请求
         │ {url, headers, data, method}
         ▼
┌─────────────────────────────────┐
│  代理服务器 (47.104.72.198:5000) │
│  POST /api/execute               │
│                                  │
│  1. 接收参数                     │
│  2. 速率限制检查 (8次/秒)         │
│  3. Cookie自动注入               │
│  4. 执行HTTP请求                 │
│  5. 返回原始响应                 │
└────────┬────────────────────────┘
         │ 返回结果
         │ {success, response, ...}
         ▼
┌─────────────────┐
│   用户代码       │
│  处理响应        │
└─────────────────┘
```

### 核心组件

**后端服务器 (server.py)**
- 单一endpoint: `/api/execute`
- 集成速率限制器（8次/秒）
- 自动Cookie管理
- 错误处理

**通用API服务 (generic_api_service.py)**
- HTTP请求执行器
- Cookie注入器
- 速率限制器

**客户端代码 (client_api.py)**
- 自包含的调用函数
- 自动重试机制
- 完整的错误处理

---

## 快速开始

### 1. 安装依赖

客户端只需要 `requests` 库：

```bash
pip install requests
```

### 2. 下载客户端代码

将 `client_api.py` 复制到你的项目目录。

### 3. 开始使用

```python
from client_api import api_call

# 发送POST请求
result = api_call(
    url="https://www.dianxiaomi.com/api/package/searchPackage.json",
    headers={
        'accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded'
    },
    data={
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': 'ORDER123'
    },
    method='POST'
)

if result['success']:
    print(result['response'])
else:
    print(f"错误: {result['error']}")
```

---

## 客户端API

### 主函数: `api_call()`

```python
def api_call(url, headers=None, data=None, method='POST', params=None, timeout=30, verbose=False):
    """
    统一的API调用函数

    参数:
        url (str): 目标API的完整URL（必填）
        headers (dict): 请求头，不含cookie（可选）
        data (dict): POST请求的表单数据（可选）
        method (str): HTTP方法，'POST'或'GET'（可选，默认'POST'）
        params (dict): GET请求的URL参数（可选）
        timeout (int): 请求超时时间（秒）（可选，默认30）
        verbose (bool): 是否显示详细日志（可选，默认False）

    返回:
        dict: {
            'success': bool,      # 请求是否成功
            'response': any,      # 响应数据（成功时）
            'response_type': str, # 'json'或'text'
            'status_code': int,   # HTTP状态码
            'error': str,         # 错误信息（失败时）
            'retries': int        # 实际重试次数
        }
    """
```

### 便捷函数

#### `post()` - POST请求

```python
from client_api import post

result = post(
    url="https://api.example.com/endpoint",
    headers={'Content-Type': 'application/json'},
    data={'key': 'value'}
)
```

#### `get()` - GET请求

```python
from client_api import get

result = get(
    url="https://api.example.com/endpoint",
    headers={'Accept': 'application/json'},
    params={'id': '123'}
)
```

---

## 服务器API

### Endpoint: `POST /api/execute`

**请求格式:**

```json
{
  "url": "https://www.dianxiaomi.com/api/package/searchPackage.json",
  "headers": {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded"
  },
  "data": {
    "pageNo": "1",
    "pageSize": "100",
    "searchType": "orderId",
    "content": "ORDER123"
  },
  "method": "POST"
}
```

**响应格式（成功）:**

```json
{
  "success": true,
  "status_code": 200,
  "response": {
    "code": 0,
    "data": {...}
  },
  "response_type": "json",
  "headers": {...},
  "request_info": {...}
}
```

**响应格式（失败）:**

```json
{
  "success": false,
  "error": "请求超时",
  "status_code": 500,
  "request_info": {...}
}
```

### 其他Endpoints

#### `GET /` - API文档

返回完整的API文档。

#### `GET /health` - 健康检查

检查服务器状态：

```json
{
  "status": "healthy",
  "service": "generic-api",
  "version": "2.0.0",
  "cookie_available": true
}
```

---

## 使用示例

### 示例1: 搜索包裹（POST请求）

```python
from client_api import api_call

result = api_call(
    url="https://www.dianxiaomi.com/api/package/searchPackage.json",
    headers={
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/x-www-form-urlencoded'
    },
    data={
        'pageNo': '1',
        'pageSize': '100',
        'searchType': 'orderId',
        'content': 'LYS-SP00001-15fe2a-c9-2156-A',
        'isVoided': '-1'
    },
    method='POST'
)

if result['success']:
    response_data = result['response']
    if response_data.get('code') == 0:
        packages = response_data.get('data', {}).get('page', {}).get('list', [])
        print(f"找到 {len(packages)} 个包裹")
        for pkg in packages:
            print(f"  - 包裹号: {pkg.get('packageNumber')}")
    else:
        print(f"API返回错误: {response_data.get('msg')}")
else:
    print(f"请求失败: {result['error']}")
```

### 示例2: 获取SKU代码（GET请求）

```python
from client_api import get

result = get(
    url="https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm",
    headers={
        'accept': 'text/html,application/xhtml+xml',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    },
    params={
        'id': '',
        'type': '0',
        'editOrCopy': '0'
    }
)

if result['success']:
    html = result['response']
    # 解析HTML获取SKU代码
    import re
    match = re.search(r'<span id="skuCode">([^<]+)</span>', html)
    if match:
        sku_code = match.group(1)
        print(f"SKU代码: {sku_code}")
else:
    print(f"请求失败: {result['error']}")
```

### 示例3: 批量设置订单备注

```python
from client_api import post

# 批量设置订单为黄色标记
result = post(
    url="https://www.dianxiaomi.com/order/batchSetCustomComment.json",
    headers={
        'accept': 'application/json, text/javascript, */*',
        'content-type': 'application/x-www-form-urlencoded'
    },
    data={
        'isGreen': '0',
        'isYellow': '1',  # 黄色标记
        'isOrange': '0',
        'isRed': '0',
        'packageIds': '123456,789012',  # 包裹ID列表
        'history': ''
    }
)

if result['success']:
    print("设置成功")
else:
    print(f"设置失败: {result['error']}")
```

### 示例4: 使用verbose模式调试

```python
from client_api import api_call

# 启用详细日志
result = api_call(
    url="https://www.dianxiaomi.com/api/package/searchPackage.json",
    headers={'accept': 'application/json'},
    data={'pageNo': '1'},
    method='POST',
    verbose=True  # 显示详细日志
)

# 输出:
# [Client] 尝试 1/4: POST https://www.dianxiaomi.com/api/package/searchPackage.json
# [Client] ✓ 请求成功: 200
```

---

## 错误处理

### 错误类型

#### 1. 参数错误

```python
result = api_call(url="", method="POST")
# result = {'success': False, 'error': '参数错误: url 不能为空'}
```

#### 2. 不支持的HTTP方法

```python
result = api_call(url="https://api.example.com", method="DELETE")
# result = {'success': False, 'error': '参数错误: 不支持的HTTP方法 DELETE'}
```

#### 3. 请求超时

```python
result = api_call(url="https://slow-api.com", timeout=5)
# result = {'success': False, 'error': '请求超时（超过5秒）', 'retries': 3}
```

#### 4. 连接错误

```python
result = api_call(url="https://invalid-domain.com")
# result = {'success': False, 'error': '连接错误: 无法连接到服务器', 'retries': 3}
```

#### 5. 速率限制

客户端会自动重试，无需手动处理：

```python
result = api_call(url="https://api.example.com")
# 如果遇到速率限制，会自动等待2秒、4秒、8秒后重试
# result['retries'] 会显示实际重试次数
```

### 错误处理最佳实践

```python
from client_api import api_call

def safe_api_call(url, **kwargs):
    """安全的API调用，带完整错误处理"""
    try:
        result = api_call(url=url, **kwargs)

        if result['success']:
            return result['response']
        else:
            # 记录错误日志
            print(f"API调用失败: {result['error']}")
            print(f"重试次数: {result.get('retries', 0)}")

            # 根据不同错误类型采取不同措施
            if '超时' in result['error']:
                print("建议: 增加timeout参数")
            elif '连接错误' in result['error']:
                print("建议: 检查网络连接")

            return None

    except Exception as e:
        print(f"未预期的错误: {e}")
        return None

# 使用
data = safe_api_call(
    url="https://www.dianxiaomi.com/api/endpoint",
    headers={'accept': 'application/json'},
    data={'key': 'value'},
    method='POST'
)

if data:
    print("成功:", data)
else:
    print("失败，请查看上方错误信息")
```

---

## 最佳实践

### 1. 始终检查 success 字段

```python
result = api_call(url="...")
if result['success']:
    # 处理成功情况
    data = result['response']
else:
    # 处理失败情况
    print(result['error'])
```

### 2. 使用 verbose 模式调试

开发时启用详细日志：

```python
result = api_call(url="...", verbose=True)
```

### 3. 合理设置 timeout

根据API响应时间设置合理的超时：

```python
# 快速API
result = api_call(url="...", timeout=10)

# 慢速API
result = api_call(url="...", timeout=60)
```

### 4. 检查响应类型

```python
if result['success']:
    if result['response_type'] == 'json':
        data = result['response']  # 已经是字典
    else:
        text = result['response']  # 是字符串
```

### 5. 批量请求时注意速率限制

```python
import time

urls = [...]  # 100个URL
results = []

for i, url in enumerate(urls):
    result = api_call(url=url, ...)
    results.append(result)

    # 每10个请求打印一次进度
    if (i + 1) % 10 == 0:
        print(f"已完成 {i + 1}/{len(urls)}")

    # 服务器会自动限制为8次/秒，无需手动sleep
```

### 6. 保存完整的请求和响应用于调试

```python
import json

result = api_call(url="...", verbose=True)

# 保存到文件
with open('debug.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
```

---

## FAQ

### Q1: 我需要自己管理Cookie吗？

**不需要。** 服务器会自动注入Cookie，你只需要提供目标URL、headers和data即可。

### Q2: 速率限制是多少？

**8次/秒。** 服务器端会自动控制，超过限制会自动等待。客户端遇到429状态码也会自动重试。

### Q3: 支持哪些HTTP方法？

目前支持 **POST** 和 **GET**。这两种方法覆盖了现有代码中的所有22个函数。

### Q4: 如果请求失败会自动重试吗？

**会。** 客户端会自动重试3次，每次等待2秒、4秒、8秒（指数退避）。

### Q5: 可以发送文件上传请求吗？

目前的实现主要支持表单数据（`application/x-www-form-urlencoded`）和JSON数据。文件上传（`multipart/form-data`）需要单独处理。

### Q6: 响应数据格式是什么？

服务器会尝试解析JSON。如果成功，`response` 字段是字典，`response_type` 是 `'json'`。否则，`response` 是原始文本，`response_type` 是 `'text'`。

### Q7: 如何调试请求问题？

1. 启用 `verbose=True` 查看详细日志
2. 检查 `result['request_info']` 查看请求详情
3. 检查 `result['retries']` 了解重试次数
4. 访问 `http://47.104.72.198:5000/health` 检查服务器状态

### Q8: 服务器在哪里运行？

服务器部署在 `http://47.104.72.198:5000`。

### Q9: 需要认证吗？

**不需要。** 服务器不需要任何认证。

### Q10: 可以并发请求吗？

可以，但请注意：
- 服务器有8次/秒的速率限制
- 建议使用线程池控制并发数量
- 每个请求都会受到速率限制保护

```python
from concurrent.futures import ThreadPoolExecutor
from client_api import api_call

def make_request(url):
    return api_call(url=url, ...)

urls = [...]  # 多个URL

# 使用线程池，最多8个并发
with ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(make_request, urls))
```

---

## 技术支持

如有问题，请联系开发团队或查看：
- 服务器文档: `http://47.104.72.198:5000/`
- 健康检查: `http://47.104.72.198:5000/health`
- 测试脚本: `python test_api.py`

---

## 更新日志

### v2.0.0 (当前版本)
- 完全重构为通用API代理服务
- 删除所有22个特定endpoints
- 创建单一 `/api/execute` endpoint
- 实现8次/秒速率限制
- 自动Cookie注入
- 支持POST和GET方法
- 客户端自动重试机制

### v1.0.0 (旧版本)
- 提供22个特定的API endpoints
- 手动Cookie管理

---

## 许可证

内部使用，保留所有权利。

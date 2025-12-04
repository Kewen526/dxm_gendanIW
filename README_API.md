# DXM API 通用服务

## 📦 文件说明

### 核心文件
- **`generic_api_service.py`** - 通用API服务（后端）
  - 自动Cookie管理
  - 速率限制：8次/秒
  - 支持POST/GET请求

- **`dxm_client.py`** - API客户端（前端调用）
  - 简单易用的调用接口
  - 自动注入Cookie
  - 自动限流

- **`cookie_manager.py`** - Cookie管理器
  - 自动下载Cookie
  - 30分钟缓存
  - 自动刷新

- **`config.py`** - 配置文件
  - Cookie URL配置
  - 缓存路径配置

### 测试文件
- **`test_generic_service.py`** - 完整测试示例

## 🚀 快速开始

### 方法1：使用客户端（推荐）

```python
from dxm_client import call_api

# 准备请求参数
url = "https://www.dianxiaomi.com/api/package/searchPackage.json"

headers = {
    'accept': 'application/json, text/plain, */*',
    'bx-v': '2.5.11',
    'content-type': 'application/x-www-form-urlencoded',
}

data = {
    'pageNo': '1',
    'pageSize': '100',
    'searchType': 'orderId',
    'content': 'LPP-SP00001-4c54be-96812-A',
    'axios_cancelToken': 'true'
}

# 调用API（自动注入Cookie，自动限流）
result = call_api(url, headers, data, method='POST')

# 处理结果
if result['success']:
    print("成功:", result['response'])
else:
    print("失败:", result['error'])
```

### 方法2：使用便捷函数

```python
from dxm_client import call_api, extract_package_ids, extract_package_numbers

# 调用API
result = call_api(url, headers, data)

# 提取包裹ID
package_ids = extract_package_ids(result)
print("包裹ID:", package_ids)

# 提取包裹号
package_numbers = extract_package_numbers(result)
print("包裹号:", package_numbers)
```

### 方法3：直接使用服务

```python
from generic_api_service import GenericAPIService

service = GenericAPIService()

result = service.execute_request(
    url="https://www.dianxiaomi.com/api/package/searchPackage.json",
    headers={...},
    data={...},
    method='POST'
)
```

## 📋 返回值格式

```python
{
    'success': True,                    # 是否成功
    'status_code': 200,                 # HTTP状态码
    'headers': {...},                   # 响应头
    'response': {...},                  # 响应数据
    'response_type': 'json',            # 响应类型
    'request_info': {                   # 请求信息
        'url': '...',
        'method': '...',
        'headers': {...},
        'data': {...},
        'timestamp': 1234567890.123
    },
    'error': None                       # 错误信息（如果有）
}
```

## ⚙️ 特性

✅ **自动Cookie管理** - 服务器自动下载、缓存、注入Cookie
✅ **速率限制** - 8次/秒，队列管理
✅ **灵活参数** - 任意URL、headers、data
✅ **支持POST/GET** - 覆盖所有HTTP方法
✅ **完整返回值** - 包含所有请求和响应信息
✅ **错误处理** - 完善的异常捕获和错误信息

## 🔧 部署到服务器

1. 复制文件到服务器：
```bash
scp generic_api_service.py cookie_manager.py config.py dxm_client.py root@your-server:/data/projects/dxm_gendanIW/
```

2. 在服务器上测试：
```bash
cd /data/projects/dxm_gendanIW
python3 dxm_client.py
```

3. 在你的代码中导入使用：
```python
from dxm_client import call_api
```

## 📝 注意事项

1. **不需要传Cookie** - headers中不需要包含cookie字段，服务器会自动注入
2. **速率限制** - 自动限流8次/秒，无需手动控制
3. **本地调整** - 可以在本地调整所有参数，无需修改服务器代码
4. **完整数据** - 返回值包含所有请求和响应信息，方便调试

## 🎯 示例：搜索包裹

```python
from dxm_client import call_api, extract_package_ids

result = call_api(
    url="https://www.dianxiaomi.com/api/package/searchPackage.json",
    headers={'accept': 'application/json', 'bx-v': '2.5.11'},
    data={'content': 'ORDER-123', 'searchType': 'orderId', 'axios_cancelToken': 'true'}
)

if result['success']:
    package_ids = extract_package_ids(result)
    print(f"找到 {len(package_ids)} 个包裹")
```

## ❓ 常见问题

**Q: Cookie会过期吗？**
A: 不会。服务器每30分钟自动刷新Cookie。

**Q: 可以调用其他API吗？**
A: 可以！只需要改变url、headers、data参数即可。

**Q: 支持GET请求吗？**
A: 支持。设置 `method='GET'` 并使用 `params` 参数。

**Q: 如何查看完整的请求信息？**
A: 查看返回值中的 `request_info` 字段。

# 店小秘API服务

统一管理和调用店小秘各种API功能的服务层，自动处理Cookie管理。

## 📁 文件结构

```
dxm_gendanIW/
├── config.py              # 配置文件
├── cookie_manager.py      # Cookie自动下载和管理
├── api_service.py         # API服务层（封装所有xbot_robot函数）
├── server.py              # HTTP API服务器
├── cli.py                 # 交互式命令行工具（重点）
├── xbot_robot/            # 原有的业务代码（不修改）
├── cookie_cache/          # Cookie缓存目录（自动创建）
└── README.md              # 本文档
```

## 🚀 快速开始

### 方式1：使用交互式命令行工具（推荐⭐）

这是最简单的使用方式，只需要运行一个命令：

```bash
python cli.py
```

然后：
1. 系统会显示所有可用的函数列表（按分类展示）
2. 输入要调用的函数编号
3. 根据提示输入参数
4. 查看执行结果
5. 选择是否继续执行其他函数

**示例：**
```
======================================================================
可用函数列表
======================================================================

【搜索类】
  1. search_product                   - 搜索商品（单个结果）
  2. search_product_all               - 搜索商品（所有结果）
  3. search_package                   - 搜索包裹
  ...

【商品管理】
  8. add_product                      - 添加商品
  9. add_product_sg                   - 添加SG商品
  ...

  0. 退出程序
======================================================================

请选择要执行的函数编号: 1

执行函数: 搜索商品（单个结果）
说明: 搜索店小秘商品，返回第一个匹配的SKU

请输入参数：
  search_value: iPhone
  shop_code: SH001
  variant: 黑色
  debug (是否调试模式，输入yes/no) (可选，直接回车跳过):

执行中...

✓ 执行成功！
结果:
SH001-iPhone-黑色
```

### 方式2：启动HTTP API服务器

如果需要通过HTTP调用API：

```bash
python server.py
```

服务器会运行在 `http://localhost:5000`

访问 `http://localhost:5000/` 查看所有可用接口。

### 方式3：在Python代码中直接调用

```python
from api_service import DianxiaomiService

# 创建服务实例
service = DianxiaomiService()

# 调用各种功能（不需要传cookie路径）
result = service.search_product(
    search_value='iPhone',
    shop_code='SH001',
    variant='黑色'
)
print(result)
```

## 📦 安装依赖

```bash
pip install flask flask-cors requests
```

## ⚙️ 配置说明

在 `config.py` 中可以修改以下配置：

```python
# Cookie URL（默认已配置，一般不需要修改）
COOKIE_URL = "https://ceshi-1300392622.cos.ap-beijing.myqcloud.com/dxm_cookie.json"

# Cookie缓存时间（分钟）
COOKIE_CACHE_MINUTES = 30

# API服务器端口
API_PORT = 5000
```

## 📚 可用函数列表

### 搜索类
- `search_product` - 搜索商品（单个结果）
- `search_product_all` - 搜索商品（所有结果）
- `search_package` - 搜索包裹
- `search_package_ids` - 搜索包裹ID列表
- `search_package2` - 搜索包裹（方法2）
- `get_package_numbers` - 获取包裹号列表
- `get_dianxiaomi_order_id` - 获取订单ID

### 商品管理
- `add_product` - 添加商品
- `add_product_sg` - 添加SG商品
- `add_product_to_warehouse` - 添加商品到仓库

### 订单操作
- `set_comment` - 设置订单备注
- `batch_commit` - 批量提交订单
- `batch_void` - 批量作废订单
- `update_warehouse` - 更新仓库
- `update_provider` - 更新物流商

### 信息查询
- `get_supplier_ids` - 获取供应商ID
- `get_shop_dict` - 获取店铺字典
- `get_provider_list` - 获取物流商列表
- `get_ali_link` - 获取阿里链接
- `fetch_sku_code` - 获取SKU代码

### 文件上传
- `upload_excel` - 上传Excel文件

### 数据抓取
- `run_scraper` - 运行订单爬虫

## 🔧 HTTP API调用示例

### 搜索商品
```bash
curl -X POST http://localhost:5000/api/search/product \
  -H "Content-Type: application/json" \
  -d '{
    "search_value": "iPhone",
    "shop_code": "SH001",
    "variant": "黑色",
    "debug": false
  }'
```

### 添加商品
```bash
curl -X POST http://localhost:5000/api/product/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "苹果手机",
    "name_en": "iPhone",
    "price": "999",
    "url": "https://example.com/product",
    "custom_zn": "手机",
    "custom_en": "Mobile Phone",
    "sb_weight": "200",
    "sb_price": "100",
    "supplier": "[\"54280071577953030\"]",
    "main_supplier": "54280071577953030",
    "img_url": "https://example.com/image.jpg",
    "sku": "SKU-001",
    "id": "",
    "pid_pair": "123456",
    "vid_pair": "789",
    "shop_id_pair": "001"
  }'
```

### 设置订单备注
```bash
curl -X POST http://localhost:5000/api/order/set_comment \
  -H "Content-Type: application/json" \
  -d '{
    "package_ids": "54280086909130128,54280086909130129"
  }'
```

## 🔑 核心特性

### 1. 自动Cookie管理
- ✅ 自动从URL下载Cookie
- ✅ 本地缓存（30分钟有效期）
- ✅ 过期自动刷新
- ✅ 下载失败自动重试
- ✅ 调用时无需关心Cookie路径

### 2. 统一的参数处理
- ✅ 隐藏复杂的cookie_file_path参数
- ✅ 统一的函数命名
- ✅ 简化的参数传递

### 3. 统一的返回格式
成功响应：
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

失败响应：
```json
{
  "success": false,
  "error": "ERROR_TYPE",
  "message": "错误详情"
}
```

## 🎯 使用场景

### 场景1：日常运维（推荐用cli.py）
```bash
# 直接运行交互式工具
python cli.py

# 选择要执行的功能
# 输入参数
# 查看结果
```

### 场景2：定时任务
```python
from api_service import DianxiaomiService

service = DianxiaomiService()

# 每天抓取订单数据
responses = service.run_scraper(days=1)

# 处理数据
for response in responses:
    # 处理逻辑
    pass
```

### 场景3：Web应用集成
```python
# 在你的Flask/Django应用中
from api_service import get_service

service = get_service()
result = service.search_product(keyword, shop, variant)
```

### 场景4：外部系统调用
```javascript
// 从其他系统通过HTTP调用
fetch('http://your-server:5000/api/search/product', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    search_value: 'iPhone',
    shop_code: 'SH001',
    variant: '黑色'
  })
})
```

## 🐛 故障排查

### Cookie下载失败
检查：
1. 网络连接是否正常
2. Cookie URL是否可访问
3. 查看错误日志

### 函数执行失败
检查：
1. 参数是否正确
2. xbot_robot模块是否正常
3. 查看详细错误信息

### API服务器无法启动
检查：
1. 端口5000是否被占用
2. 依赖是否安装完整
3. Python版本是否兼容

## 📝 开发说明

### 添加新功能
1. 在 `xbot_robot/` 下添加新模块
2. 在 `api_service.py` 的 `DianxiaomiService` 类中添加封装方法
3. 在 `server.py` 添加对应的HTTP接口
4. 在 `cli.py` 的 `functions` 字典中注册新函数

### 修改配置
编辑 `config.py` 文件即可

## 📞 技术支持

如有问题，请检查：
1. README文档
2. config.py配置
3. 错误日志

## 🎉 完成！

现在您可以：
- ✅ 运行 `python cli.py` 使用交互式工具
- ✅ 运行 `python server.py` 启动HTTP服务
- ✅ 在代码中 `from api_service import DianxiaomiService` 直接调用

所有Cookie管理都是自动的，您只需要关注业务逻辑！
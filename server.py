"""
通用HTTP API服务器 - 提供统一的API代理服务
使用Flask框架

特点：
- 单一endpoint: /api/execute
- 自动注入Cookie
- 速率限制: 8次/秒
- 支持POST和GET方法
- 返回目标API的原始响应

启动方式：
    python server.py

部署地址：
    http://47.104.72.198:5000
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import config
from generic_api_service import get_service

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取通用API服务实例
api_service = None


def get_generic_api_service():
    """获取通用API服务实例"""
    global api_service
    if api_service is None:
        api_service = get_service()
    return api_service


@app.route('/', methods=['GET'])
def index():
    """API文档首页"""
    docs = {
        "服务名称": "通用HTTP API代理服务",
        "版本": "2.0.0",
        "服务器地址": "http://47.104.72.198:5000",
        "特点": [
            "单一endpoint - 简化API调用",
            "自动Cookie注入 - 无需手动管理",
            "速率限制 - 8次/秒",
            "支持POST和GET方法",
            "返回目标API的原始响应"
        ],
        "endpoint": {
            "路径": "POST /api/execute",
            "说明": "执行任意HTTP请求",
            "参数": {
                "url": "目标API的完整URL（必填）",
                "headers": "请求头字典，不含cookie（可选）",
                "data": "POST请求的表单数据（可选）",
                "method": "HTTP方法，'POST'或'GET'，默认'POST'（可选）",
                "params": "GET请求的URL参数（可选）"
            },
            "返回格式": {
                "success": "布尔值，表示请求是否成功",
                "status_code": "HTTP状态码",
                "response": "目标API的原始响应数据",
                "response_type": "'json'或'text'",
                "headers": "响应头字典",
                "error": "错误信息（失败时）"
            }
        },
        "使用示例": {
            "POST请求": {
                "url": "https://www.dianxiaomi.com/api/package/searchPackage.json",
                "headers": {
                    "accept": "application/json, text/plain, */*",
                    "content-type": "application/x-www-form-urlencoded"
                },
                "data": {
                    "pageNo": "1",
                    "pageSize": "100",
                    "searchType": "orderId",
                    "content": "ORDER123"
                },
                "method": "POST"
            },
            "GET请求": {
                "url": "https://www.dianxiaomi.com/dxmCommodityProduct/openAddModal.htm",
                "headers": {
                    "accept": "text/html"
                },
                "method": "GET"
            }
        },
        "客户端代码": "使用 client_api.py 中的 api_call() 函数",
        "注意事项": [
            "请求头中不要包含cookie，服务器会自动注入",
            "速率限制为8次/秒，超过会自动等待",
            "客户端遇到429状态码应自动重试"
        ]
    }
    return jsonify(docs)


@app.route('/api/execute', methods=['POST'])
def execute_request():
    """
    通用HTTP请求执行器

    接收参数：
        - url: 目标API的完整URL
        - headers: 请求头（不含cookie）
        - data: POST请求数据
        - method: HTTP方法（'POST'或'GET'）
        - params: GET请求参数

    返回：
        目标API的原始响应
    """
    try:
        # 获取请求参数
        request_data = request.json

        if not request_data:
            return jsonify({
                "success": False,
                "error": "请求体不能为空",
                "message": "请提供JSON格式的请求参数"
            }), 400

        # 提取参数
        url = request_data.get('url')
        headers = request_data.get('headers', {})
        data = request_data.get('data')
        method = request_data.get('method', 'POST')
        params = request_data.get('params')

        # 验证必填参数
        if not url:
            return jsonify({
                "success": False,
                "error": "缺少必填参数: url",
                "message": "请提供目标API的URL"
            }), 400

        # 验证HTTP方法
        if method.upper() not in ['POST', 'GET']:
            return jsonify({
                "success": False,
                "error": f"不支持的HTTP方法: {method}",
                "message": "仅支持POST和GET方法"
            }), 400

        # 执行请求
        service = get_generic_api_service()
        result = service.execute_request(
            url=url,
            headers=headers,
            data=data,
            method=method,
            params=params
        )

        # 返回结果
        if result.get('success'):
            return jsonify(result), 200
        else:
            # 请求失败，返回错误信息
            status_code = result.get('status_code', 500)
            return jsonify(result), status_code

    except Exception as e:
        # 捕获所有异常
        error_trace = traceback.format_exc()
        print(f"[Server] 错误: {error_trace}")

        return jsonify({
            "success": False,
            "error": str(e),
            "message": "服务器内部错误",
            "traceback": error_trace
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查endpoint"""
    try:
        service = get_generic_api_service()
        return jsonify({
            "status": "healthy",
            "service": "generic-api",
            "version": "2.0.0",
            "cookie_available": service.cookie_path is not None
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "error": "NOT_FOUND",
        "message": "接口不存在，请使用 POST /api/execute"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "error": "INTERNAL_ERROR",
        "message": "服务器内部错误"
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("通用HTTP API代理服务器")
    print("=" * 60)
    print(f"服务器地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"调试模式: {config.DEBUG}")
    print(f"速率限制: 8次/秒")
    print(f"主要endpoint: POST /api/execute")
    print("=" * 60)
    print("\n启动服务器...")

    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )

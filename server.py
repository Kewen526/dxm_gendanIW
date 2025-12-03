"""
HTTP API服务器 - 提供RESTful API接口
使用Flask框架

启动方式：
    python server.py

API文档：
    访问 http://localhost:5000/ 查看所有可用接口
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import config
from api_service import get_service

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 获取服务实例
service = None


def get_api_service():
    """获取API服务实例"""
    global service
    if service is None:
        service = get_service()
    return service


def success_response(data, message="操作成功"):
    """成功响应格式"""
    return jsonify({
        "success": True,
        "data": data,
        "message": message
    })


def error_response(error, message="操作失败"):
    """错误响应格式"""
    return jsonify({
        "success": False,
        "error": str(error),
        "message": message
    }), 400


@app.route('/', methods=['GET'])
def index():
    """API文档首页"""
    apis = {
        "API服务器": "店小秘API服务",
        "版本": "1.0.0",
        "可用接口": {
            "搜索类": {
                "POST /api/search/product": "搜索商品（单个结果）",
                "POST /api/search/product_all": "搜索商品（所有结果）",
                "POST /api/search/package": "搜索包裹",
                "POST /api/search/package_ids": "搜索包裹ID列表",
                "POST /api/search/package2": "搜索包裹（方法2）",
                "POST /api/search/package_numbers": "获取包裹号列表",
                "POST /api/search/order_id": "获取订单ID"
            },
            "商品管理类": {
                "POST /api/product/add": "添加商品",
                "POST /api/product/add_sg": "添加SG商品",
                "POST /api/product/add_to_warehouse": "添加商品到仓库"
            },
            "订单操作类": {
                "POST /api/order/set_comment": "设置订单备注",
                "POST /api/order/batch_commit": "批量提交订单",
                "POST /api/order/batch_void": "批量作废订单",
                "POST /api/order/update_warehouse": "更新仓库",
                "POST /api/order/update_provider": "更新物流商"
            },
            "信息查询类": {
                "POST /api/info/get_supplier_ids": "获取供应商ID",
                "GET /api/info/get_shop_dict": "获取店铺字典",
                "GET /api/info/get_provider_list": "获取物流商列表",
                "POST /api/info/get_ali_link": "获取阿里链接",
                "GET /api/info/fetch_sku_code": "获取SKU代码"
            },
            "文件上传类": {
                "POST /api/upload/excel": "上传Excel文件"
            },
            "数据抓取类": {
                "POST /api/scraper/run": "运行订单爬虫"
            }
        }
    }
    return jsonify(apis)


# ==================== 搜索类接口 ====================

@app.route('/api/search/product', methods=['POST'])
def search_product():
    """搜索商品（单个结果）"""
    try:
        data = request.json
        result = get_api_service().search_product(
            data['search_value'],
            data['shop_code'],
            data['variant'],
            data.get('debug', False)
        )
        return success_response(result)
    except Exception as e:
        return error_response(e, f"搜索商品失败: {str(e)}")


@app.route('/api/search/product_all', methods=['POST'])
def search_product_all():
    """搜索商品（所有结果）"""
    try:
        data = request.json
        result = get_api_service().search_product_all(
            data['search_value'],
            data['shop_code'],
            data['variant'],
            data.get('debug', False)
        )
        return success_response(result)
    except Exception as e:
        return error_response(e, f"搜索商品失败: {str(e)}")


@app.route('/api/search/package', methods=['POST'])
def search_package():
    """搜索包裹"""
    try:
        data = request.json
        result = get_api_service().search_package(data['content'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"搜索包裹失败: {str(e)}")


@app.route('/api/search/package_ids', methods=['POST'])
def search_package_ids():
    """搜索包裹ID列表"""
    try:
        data = request.json
        result = get_api_service().search_package_ids(data['content'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"搜索包裹ID失败: {str(e)}")


@app.route('/api/search/package2', methods=['POST'])
def search_package2():
    """搜索包裹（方法2）"""
    try:
        data = request.json
        result = get_api_service().search_package2(data['content'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"搜索包裹失败: {str(e)}")


@app.route('/api/search/package_numbers', methods=['POST'])
def search_package_numbers():
    """获取包裹号列表"""
    try:
        data = request.json
        result = get_api_service().get_package_numbers(data['content'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取包裹号失败: {str(e)}")


@app.route('/api/search/order_id', methods=['POST'])
def get_order_id():
    """获取订单ID"""
    try:
        data = request.json
        result = get_api_service().get_dianxiaomi_order_id(data['content'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取订单ID失败: {str(e)}")


# ==================== 商品管理类接口 ====================

@app.route('/api/product/add', methods=['POST'])
def add_product():
    """添加商品"""
    try:
        data = request.json
        result = get_api_service().add_product(data)
        return success_response(result)
    except Exception as e:
        return error_response(e, f"添加商品失败: {str(e)}")


@app.route('/api/product/add_sg', methods=['POST'])
def add_product_sg():
    """添加SG商品"""
    try:
        data = request.json
        result = get_api_service().add_product_sg(data)
        return success_response(result)
    except Exception as e:
        return error_response(e, f"添加SG商品失败: {str(e)}")


@app.route('/api/product/add_to_warehouse', methods=['POST'])
def add_product_to_warehouse():
    """添加商品到仓库"""
    try:
        data = request.json
        result = get_api_service().add_product_to_warehouse(data['sku'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"添加商品到仓库失败: {str(e)}")


# ==================== 订单操作类接口 ====================

@app.route('/api/order/set_comment', methods=['POST'])
def set_comment():
    """设置订单备注"""
    try:
        data = request.json
        result = get_api_service().set_comment(data['package_ids'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"设置备注失败: {str(e)}")


@app.route('/api/order/batch_commit', methods=['POST'])
def batch_commit():
    """批量提交订单"""
    try:
        data = request.json
        result = get_api_service().batch_commit(data['package_ids'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"批量提交失败: {str(e)}")


@app.route('/api/order/batch_void', methods=['POST'])
def batch_void():
    """批量作废订单"""
    try:
        data = request.json
        result = get_api_service().batch_void(data['package_ids'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"批量作废失败: {str(e)}")


@app.route('/api/order/update_warehouse', methods=['POST'])
def update_warehouse():
    """更新仓库"""
    try:
        data = request.json
        result = get_api_service().update_warehouse(
            data['package_ids'],
            data['storage_id']
        )
        return success_response(result)
    except Exception as e:
        return error_response(e, f"更新仓库失败: {str(e)}")


@app.route('/api/order/update_provider', methods=['POST'])
def update_provider():
    """更新物流商"""
    try:
        data = request.json
        result = get_api_service().update_provider(
            data['package_ids'],
            data['auth_id']
        )
        return success_response(result)
    except Exception as e:
        return error_response(e, f"更新物流商失败: {str(e)}")


# ==================== 信息查询类接口 ====================

@app.route('/api/info/get_supplier_ids', methods=['POST'])
def get_supplier_ids():
    """获取供应商ID"""
    try:
        data = request.json
        result = get_api_service().get_supplier_ids(data['supplier_name'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取供应商ID失败: {str(e)}")


@app.route('/api/info/get_shop_dict', methods=['GET'])
def get_shop_dict():
    """获取店铺字典"""
    try:
        result = get_api_service().get_shop_dict()
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取店铺字典失败: {str(e)}")


@app.route('/api/info/get_provider_list', methods=['GET'])
def get_provider_list():
    """获取物流商列表"""
    try:
        result = get_api_service().get_provider_list()
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取物流商列表失败: {str(e)}")


@app.route('/api/info/get_ali_link', methods=['POST'])
def get_ali_link():
    """获取阿里链接"""
    try:
        data = request.json
        result = get_api_service().get_ali_link(data['product_url'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取阿里链接失败: {str(e)}")


@app.route('/api/info/fetch_sku_code', methods=['GET'])
def fetch_sku_code():
    """获取SKU代码"""
    try:
        result = get_api_service().fetch_sku_code()
        return success_response(result)
    except Exception as e:
        return error_response(e, f"获取SKU代码失败: {str(e)}")


# ==================== 文件上传类接口 ====================

@app.route('/api/upload/excel', methods=['POST'])
def upload_excel():
    """上传Excel文件"""
    try:
        data = request.json
        result = get_api_service().upload_excel(data['file_path'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"上传Excel失败: {str(e)}")


# ==================== 数据抓取类接口 ====================

@app.route('/api/scraper/run', methods=['POST'])
def run_scraper():
    """运行订单爬虫"""
    try:
        data = request.json
        result = get_api_service().run_scraper(data['days'])
        return success_response(result)
    except Exception as e:
        return error_response(e, f"运行爬虫失败: {str(e)}")


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return error_response("NOT_FOUND", "接口不存在"), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return error_response("INTERNAL_ERROR", "服务器内部错误"), 500


if __name__ == '__main__':
    print("=" * 60)
    print("店小秘API服务器")
    print("=" * 60)
    print(f"服务器地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"调试模式: {config.DEBUG}")
    print("=" * 60)
    print("\n启动服务器...")

    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG
    )

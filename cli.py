"""
交互式命令行工具 - 让用户通过选择函数名来调用不同功能

使用方式：
    python cli.py

功能：
    - 显示所有可用函数列表
    - 用户选择要调用的函数
    - 根据函数要求输入参数
    - 执行函数并显示结果
"""
import json
from api_service import DianxiaomiService


class CLI:
    """命令行交互界面"""

    def __init__(self):
        """初始化CLI"""
        print("=" * 70)
        print("店小秘API命令行工具")
        print("=" * 70)
        print("正在初始化...")

        try:
            self.service = DianxiaomiService()
            print("✓ 初始化成功")
            print(f"✓ Cookie路径: {self.service.cookie_path}")
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            exit(1)

        # 定义所有可用的函数及其参数
        self.functions = {
            # 搜索类
            "search_product": {
                "name": "搜索商品（单个结果）",
                "params": ["search_value", "shop_code", "variant", "debug"],
                "description": "搜索店小秘商品，返回第一个匹配的SKU"
            },
            "search_product_all": {
                "name": "搜索商品（所有结果）",
                "params": ["search_value", "shop_code", "variant", "debug"],
                "description": "搜索店小秘商品，返回所有匹配的SKU列表"
            },
            "search_package": {
                "name": "搜索包裹",
                "params": ["content"],
                "description": "搜索包裹信息并提取运单号"
            },
            "search_package_ids": {
                "name": "搜索包裹ID列表",
                "params": ["content"],
                "description": "搜索包裹ID列表"
            },
            "search_package2": {
                "name": "搜索包裹（方法2）",
                "params": ["content"],
                "description": "搜索包裹（备用方法）"
            },
            "get_package_numbers": {
                "name": "获取包裹号列表",
                "params": ["content"],
                "description": "获取包裹号列表"
            },
            "get_dianxiaomi_order_id": {
                "name": "获取订单ID",
                "params": ["content"],
                "description": "获取店小秘订单ID"
            },

            # 商品管理类
            "add_product": {
                "name": "添加商品",
                "params": ["product_data"],
                "description": "添加商品到店小秘（需要完整的商品信息字典）"
            },
            "add_product_sg": {
                "name": "添加SG商品",
                "params": ["product_data"],
                "description": "添加SG商品到店小秘"
            },
            "add_product_to_warehouse": {
                "name": "添加商品到仓库",
                "params": ["sku"],
                "description": "将商品添加到仓库"
            },

            # 订单操作类
            "set_comment": {
                "name": "设置订单备注",
                "params": ["package_ids"],
                "description": "设置订单备注（package_ids用逗号分隔）"
            },
            "batch_commit": {
                "name": "批量提交订单",
                "params": ["package_ids"],
                "description": "批量提交包裹到平台"
            },
            "batch_void": {
                "name": "批量作废订单",
                "params": ["package_ids"],
                "description": "批量设置包裹为作废"
            },
            "update_warehouse": {
                "name": "更新仓库",
                "params": ["package_ids", "storage_id"],
                "description": "更新包裹仓库信息"
            },
            "update_provider": {
                "name": "更新物流商",
                "params": ["package_ids", "auth_id"],
                "description": "批量更新物流服务商"
            },

            # 信息查询类
            "get_supplier_ids": {
                "name": "获取供应商ID",
                "params": ["supplier_name"],
                "description": "根据供应商名称获取ID"
            },
            "get_shop_dict": {
                "name": "获取店铺字典",
                "params": [],
                "description": "获取所有店铺信息"
            },
            "get_provider_list": {
                "name": "获取物流商列表",
                "params": [],
                "description": "获取所有物流服务商信息"
            },
            "get_ali_link": {
                "name": "获取阿里链接",
                "params": ["product_url"],
                "description": "获取阿里巴巴商品链接"
            },
            "fetch_sku_code": {
                "name": "获取SKU代码",
                "params": [],
                "description": "获取SKU代码数据"
            },

            # 文件上传类
            "upload_excel": {
                "name": "上传Excel文件",
                "params": ["file_path"],
                "description": "上传Excel文件到店小秘"
            },

            # 数据抓取类
            "run_scraper": {
                "name": "运行订单爬虫",
                "params": ["days"],
                "description": "抓取指定天数的订单数据"
            },
        }

    def show_menu(self):
        """显示函数菜单"""
        print("\n" + "=" * 70)
        print("可用函数列表")
        print("=" * 70)

        categories = {
            "搜索类": ["search_product", "search_product_all", "search_package",
                      "search_package_ids", "search_package2", "get_package_numbers",
                      "get_dianxiaomi_order_id"],
            "商品管理": ["add_product", "add_product_sg", "add_product_to_warehouse"],
            "订单操作": ["set_comment", "batch_commit", "batch_void",
                        "update_warehouse", "update_provider"],
            "信息查询": ["get_supplier_ids", "get_shop_dict", "get_provider_list",
                        "get_ali_link", "fetch_sku_code"],
            "文件上传": ["upload_excel"],
            "数据抓取": ["run_scraper"],
        }

        idx = 1
        func_index = {}

        for category, funcs in categories.items():
            print(f"\n【{category}】")
            for func_name in funcs:
                if func_name in self.functions:
                    func_info = self.functions[func_name]
                    print(f"  {idx}. {func_name:30s} - {func_info['name']}")
                    func_index[idx] = func_name
                    idx += 1

        print(f"\n  0. 退出程序")
        print("=" * 70)

        return func_index

    def get_input(self, prompt, param_type="str", optional=False):
        """获取用户输入"""
        if optional:
            prompt += " (可选，直接回车跳过)"

        user_input = input(f"{prompt}: ").strip()

        if optional and not user_input:
            return None

        if param_type == "int":
            try:
                return int(user_input)
            except ValueError:
                print("⚠️  输入格式错误，请输入数字")
                return self.get_input(prompt, param_type, optional)
        elif param_type == "bool":
            return user_input.lower() in ['true', 'yes', 'y', '1']
        elif param_type == "json":
            try:
                return json.loads(user_input)
            except json.JSONDecodeError:
                print("⚠️  JSON格式错误，请重新输入")
                return self.get_input(prompt, param_type, optional)
        else:
            return user_input

    def execute_function(self, func_name):
        """执行选择的函数"""
        func_info = self.functions[func_name]
        params = func_info["params"]

        print(f"\n{'=' * 70}")
        print(f"执行函数: {func_info['name']}")
        print(f"说明: {func_info['description']}")
        print(f"{'=' * 70}")

        # 获取参数
        kwargs = {}

        if not params or (len(params) == 1 and params[0] == ""):
            # 无参数函数
            pass
        else:
            print("\n请输入参数：")
            for param in params:
                if param == "debug":
                    kwargs[param] = self.get_input(
                        f"  {param} (是否调试模式，输入yes/no)",
                        param_type="bool",
                        optional=True
                    ) or False
                elif param == "days":
                    kwargs[param] = self.get_input(
                        f"  {param} (天数)",
                        param_type="int"
                    )
                elif param == "product_data":
                    print(f"  {param} (商品信息JSON，示例如下)")
                    print('    {"name": "商品名", "name_en": "Product Name", "price": "100", ...}')
                    kwargs[param] = self.get_input(
                        f"  请输入完整的JSON",
                        param_type="json"
                    )
                else:
                    kwargs[param] = self.get_input(f"  {param}")

        # 执行函数
        print(f"\n执行中...")
        try:
            method = getattr(self.service, func_name)
            result = method(**kwargs)

            print(f"\n{'=' * 70}")
            print("✓ 执行成功！")
            print(f"{'=' * 70}")
            print("\n结果:")
            if isinstance(result, (dict, list)):
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(result)
            print(f"\n{'=' * 70}")

        except Exception as e:
            print(f"\n{'=' * 70}")
            print("✗ 执行失败！")
            print(f"{'=' * 70}")
            print(f"错误信息: {e}")
            print(f"{'=' * 70}")

    def run(self):
        """运行CLI主循环"""
        while True:
            func_index = self.show_menu()

            try:
                choice = int(input("\n请选择要执行的函数编号: "))

                if choice == 0:
                    print("\n感谢使用，再见！")
                    break

                if choice in func_index:
                    func_name = func_index[choice]
                    self.execute_function(func_name)

                    # 询问是否继续
                    continue_input = input("\n是否继续执行其他函数？(y/n): ").strip().lower()
                    if continue_input not in ['y', 'yes']:
                        print("\n感谢使用，再见！")
                        break
                else:
                    print("\n⚠️  无效的选择，请重新输入")

            except ValueError:
                print("\n⚠️  请输入数字")
            except KeyboardInterrupt:
                print("\n\n程序已中断，再见！")
                break


def main():
    """主函数"""
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()

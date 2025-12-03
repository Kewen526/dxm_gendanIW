# 使用提醒:
# 1. xbot包提供软件自动化、数据表格、Excel、日志、AI等功能
# 2. package包提供访问当前应用数据的功能，如获取元素、访问全局变量、获取资源文件等功能
# 3. 当此模块作为流程独立运行时执行main函数
# 4. 可视化流程中可以通过"调用模块"的指令使用此模块

import xbot
from xbot import print, sleep
from .import package
from .package import variables as glv

def main(args):
    pass
from qcloud_cos import CosConfig, CosS3Client

def upload_to_cos(path, filename):
    """
    上传文件到腾讯云COS（支持代理环境）

    参数：
        path (str): 本地文件路径
        filename (str): 文件名（上传到COS后的名称）

    返回：
        str: 上传后的文件URL
    """
    # 配置腾讯云 COS 凭证
    secret_id = 'AKIDrYz93g26vUmpb6KHxMULvFI4aonVw60d'
    secret_key = 'OVMwFH1astc4FApEMCm47tOcaGfnfFXZ'
    region = 'ap-beijing'
    bucket = 'ceshi-1300392622'

    # 代理设置（请根据实际代理信息填写）
    proxy = {
        'http': None,
        'https': None
    }

    try:
        # 配置CosConfig，包含代理信息
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=None, Proxies=proxy)
        client = CosS3Client(config)

        # 上传文件
        response = client.put_object_from_local_file(
            Bucket=bucket,
            LocalFilePath=path,
            Key=filename
        )

        # 获取上传后的文件URL
        url = f"https://{bucket}.cos.{region}.myqcloud.com/{filename}"
        return url

    except Exception as e:
        print(f"文件上传失败: {e}")
        return None

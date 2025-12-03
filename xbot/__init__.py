"""
Mock xbot包 - 用于在非影刀环境中运行代码
"""
import time

# Mock基本函数
print = print  # 使用Python内置print
sleep = time.sleep

__all__ = ['print', 'sleep']

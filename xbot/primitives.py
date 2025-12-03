"""
Mock primitives模块
"""

class VariableDict(dict):
    """Mock VariableDict类"""
    pass

class ResourceReader:
    """Mock ResourceReader类"""
    def __init__(self, loader, path):
        self.loader = loader
        self.path = path

    def get_text(self, name):
        return ""

    def get_bytes(self, name):
        return b""

# Mock _sdmodules字典
_sdmodules = {}

"""
Mock selector模块
"""

class SelectorStore:
    """Mock SelectorStore类"""
    def __init__(self, path):
        self.path = path

    def __call__(self, name):
        return None

class ImageSelectorStore:
    """Mock ImageSelectorStore类"""
    def __init__(self, path):
        self.path = path

    def __call__(self, name):
        return None

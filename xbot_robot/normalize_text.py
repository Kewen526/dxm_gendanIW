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
import unicodedata
import re

def normalize_text(text):
    """
    移除文本中的所有变音符号和特殊字符，将字符转换为基本形式
    例如: lévêque -> leveque, й -> и, ñ -> n, ü -> u, æ -> ae, ø -> o, ™ -> TM 等
    """
    # 特殊字符映射表
    special_char_map = {
        # 连字符（Ligatures）
        'æ': 'ae', 'Æ': 'AE',
        'œ': 'oe', 'Œ': 'OE',
        'ĳ': 'ij', 'Ĳ': 'IJ',
        'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
        'ﬅ': 'st', 'ﬆ': 'st',
        
        # 带斜线或横线的字母
        'ø': 'o', 'Ø': 'O',
        'đ': 'd', 'Đ': 'D',
        'ł': 'l', 'Ł': 'L',
        'ħ': 'h', 'Ħ': 'H',
        'ŧ': 't', 'Ŧ': 'T',
        'ƀ': 'b', 'Ƀ': 'B',
        'ɨ': 'i', 'Ɨ': 'I',
        
        # 特殊符号
        '™': 'TM', '®': 'R', '©': 'C',
        '℠': 'SM', '℗': 'P',
        
        # 数学和技术符号
        '°': 'deg', '℃': 'C', '℉': 'F',
        '№': 'No', '℮': 'e',
        
        # 货币符号（可选）
        '€': 'EUR', '£': 'GBP', '¥': 'JPY', '₹': 'INR',
        '¢': 'c', '¤': 'currency',
        
        # 其他特殊拉丁字母
        'ð': 'd', 'Ð': 'D',  # eth
        'þ': 'th', 'Þ': 'TH',  # thorn
        'ß': 'ss', 'ẞ': 'SS',  # 德语 sharp s
        
        # 带特殊记号的字母
        'å': 'a', 'Å': 'A',
        'ą': 'a', 'Ą': 'A',
        'ę': 'e', 'Ę': 'E',
        'į': 'i', 'Į': 'I',
        'ų': 'u', 'Ų': 'U',
        
        # 其他常见特殊字符
        'ə': 'e',  # schwa
        'ɐ': 'a',  # turned a
        'ɔ': 'o',  # open o
        'ɛ': 'e',  # open e
        'ʃ': 'sh', # esh
        'ʒ': 'zh', # ezh
        'ŋ': 'ng', # eng
        'ɲ': 'ny', # enye
        'ʔ': "'",  # glottal stop
        
        # 标点和引号
        ''': "'", ''': "'", '"': '"', '"': '"',
        '«': '"', '»': '"', '‹': "'", '›': "'",
        '—': '-', '–': '-', '…': '...',
        '•': '*', '·': '.', '‚': ',', '„': '"',
    }
    
    # 首先应用特殊字符映射
    for char, replacement in special_char_map.items():
        text = text.replace(char, replacement)
    
    # 然后进行 NFD 规范化处理变音符号
    normalized = unicodedata.normalize('NFD', text)
    
    # 过滤掉所有变音符号和组合标记
    result = ''.join(c for c in normalized if not unicodedata.combining(c))
    
    # 可选：移除其他非ASCII字符（取消注释以启用）
    # result = ''.join(c if ord(c) < 128 else ' ' for c in result)
    
    # 可选：处理其他未映射的特殊字符
    # 通过字符名称来识别和处理
    final_result = []
    for char in result:
        if ord(char) > 127:  # 非ASCII字符
            try:
                char_name = unicodedata.name(char, '').upper()
                # 处理某些类型的字符
                if 'LETTER' in char_name and 'WITH' in char_name:
                    # 尝试获取基本字符（这会捕获一些遗漏的变音字符）
                    base_char = char_name.split(' WITH')[0].split()[-1].lower()
                    if len(base_char) == 1:
                        final_result.append(base_char)
                        continue
                elif 'LIGATURE' in char_name:
                    # 处理其他连字
                    parts = char_name.replace('LATIN ', '').replace('LIGATURE ', '').lower()
                    final_result.append(parts)
                    continue
            except:
                pass
            final_result.append(char)
        else:
            final_result.append(char)
    
    return ''.join(final_result)


# 测试函数
if __name__ == "__main__":
    test_texts = [
        "lévêque™ with æther and øre",
        "Café® with Œuvre and Łódź",
        "Temperature: 25℃ or 77℉",
        "Copyright© 2024™ - All rights reserved®",
        "naïve résumé piñata über",
        "Åse's Ørsted ægg",
        "№1 best™ café",
        "𝕳𝖊𝖑𝖑𝖔 𝖂𝖔𝖗𝖑𝖉",  # 特殊字体
        "Москва Zürich København",
    ]
    
    print("原始文本 -> 规范化文本")
    print("-" * 50)
    for text in test_texts:
        normalized = normalize_text(text)
        print(f"{text} -> {normalized}")

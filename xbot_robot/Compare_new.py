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
import requests
import os
import time
import concurrent.futures
from PIL import Image
import io
import base64
import re
from zhipuai import ZhipuAI

def download_image(url, save_path, max_retries=3):
    """
    Downloads an image from a URL and saves it to the specified path.
    Includes retry logic and proper headers to mimic a browser.
    
    Args:
        url: The URL of the image to download
        save_path: The path where the image should be saved
        max_retries: Maximum number of retry attempts (default: 3)
        
    Returns:
        True if successful, False otherwise
    """
    # Define headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.alibaba.com/',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    for attempt in range(max_retries):
        try:
            # Add delay to avoid rate limiting (increase delay with each retry)
            if attempt > 0:
                time.sleep(2 * attempt)  # Exponential backoff
                
            print(f"Downloading image: {url} (attempt {attempt+1}/{max_retries})")
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            
            if response.status_code == 200:
                # Convert to PNG if needed
                with Image.open(io.BytesIO(response.content)) as img:
                    img.save(save_path, format="PNG")
                print(f"Successfully downloaded image to {save_path}")
                return True
            elif response.status_code == 420 or response.status_code == 429:
                # Rate limited, wait longer before retrying
                wait_time = 5 * (attempt + 1)
                print(f"Rate limited (status code: {response.status_code}). Waiting {wait_time} seconds before retry.")
                time.sleep(wait_time)
            else:
                print(f"Failed to download image: status code {response.status_code}")
                # If it's the last attempt, try one more approach
                if attempt == max_retries - 1:
                    print("Trying alternative download method...")
                    try:
                        # Alternative method using urllib
                        import urllib.request
                        opener = urllib.request.build_opener()
                        opener.addheaders = [(k, v) for k, v in headers.items()]
                        urllib.request.install_opener(opener)
                        urllib.request.urlretrieve(url, save_path)
                        
                        # Verify the image can be opened
                        with Image.open(save_path) as img:
                            img.verify()
                        print(f"Successfully downloaded image using alternative method")
                        return True
                    except Exception as alt_e:
                        print(f"Alternative download method failed: {str(alt_e)}")
                        
        except Exception as e:
            print(f"Error downloading image (attempt {attempt+1}/{max_retries}): {str(e)}")
            
            # If it's the last attempt, try one more approach
            if attempt == max_retries - 1:
                try:
                    print("Trying with a session...")
                    session = requests.Session()
                    response = session.get(url, headers=headers, timeout=30)
                    if response.status_code == 200:
                        with Image.open(io.BytesIO(response.content)) as img:
                            img.save(save_path, format="PNG")
                        print(f"Successfully downloaded image using session")
                        return True
                except Exception as session_e:
                    print(f"Session download failed: {str(session_e)}")
    
    print(f"All download attempts failed for: {url}")
    return False

def analyze_two_images(image1_path, image2_path, prompt_text):
    """
    使用GLM-4V模型分析两张本地图片
    
    参数:
        image1_path (str): 第一张图片的本地路径
        image2_path (str): 第二张图片的本地路径
        prompt_text (str): 提示词，用于指导模型如何分析图片
        
    返回:
        str: 模型的分析结果
    """
    # 初始化客户端
    client = ZhipuAI(api_key="791f0a2f02094652b97f3ca8450b43db.MIIBVAIBADANBgkqhkiG9w0BAQEFAASCAT4wggE6AgEAAkEAwhjLLplenn3Zj+jmoHF5rDzIkbBuhPIUc4fRzowUV0Bejt0fmjAxSNJuwZ5ZAMVIDuFX7YyVPkoo65IvGNaErwIDAQABAkAQRjHrE1L6qQSv61BDDaCtD1+lz4xEu2N5mF7AGcCu3AJqKdvPYcducCGZVZPpjuRAGhqw67WhzvGYfZXhcIjxAiEA5vrDa4rm9a4p/Ox9Qu9f+GReXThamM6RFlig7TakxwcCIQDXHz7Vxy/xwJnQei5989JV6LyGYHreyE5eHoLTs8YDGQIhAIdni7X4qKpvnheyP0BE+bqwhA0b4yhfN/iknjpRZUlzAiBnV2g9FEoQ7cA2aWuKMCYcBQkD2LdN7JXRGwEoKBV4iQIgDfNrJ979kAVtcqs54VzHn2GRPgz6k/WfSR/lOSRSR30=")
    
    # 读取并编码第一张图片
    with open(image1_path, 'rb') as img_file:
        image1_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    # 读取并编码第二张图片
    with open(image2_path, 'rb') as img_file:
        image2_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    # 添加请求重试逻辑
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 发送请求
            response = client.chat.completions.create(
                model="GLM-4V-Flash",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image1_base64
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image2_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ]
            )
            
            # 返回模型响应
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"API请求失败(尝试 {attempt+1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"等待{wait_time}秒后重试...")
                time.sleep(wait_time)
            else:
                print("所有尝试均失败")
                raise
    
    return "图片分析失败：无法连接到API服务"

def analyze_image_with_fallback(image_paths, prompt, detail="high"):
    """
    使用ZhipuAI分析两张图片
    
    Args:
        image_paths: 图片路径列表，预期有两张图片
        prompt: 分析提示
        detail: 不使用但保留参数以保持接口一致性
        
    Returns:
        分析结果文本
    """
    if len(image_paths) < 2:
        return "错误：需要至少两张图片进行比较"
    
    try:
        # 使用analyze_two_images函数分析前两张图片
        result = analyze_two_images(image_paths[0], image_paths[1], prompt)
        return result
    except Exception as e:
        print(f"图片分析失败: {str(e)}")
        return f"图片分析失败: {str(e)}"

def process_variant(variant_key, image_url, ref_image_path, product_name, temp_dir="./temp_images"):
    """
    Process a single product variant by:
    1. Downloading the variant image
    2. Comparing it with the reference image using AI
    3. Determining if they are the same product
    
    Args:
        variant_key: The name/key of the variant
        image_url: The URL of the variant image
        ref_image_path: Path to the reference image
        product_name: Name of the product
        temp_dir: Directory to store downloaded images
        
    Returns:
        Tuple of (variant_key, is_same)
    """
    # Create a unique filename for the downloaded image
    variant_filename = os.path.join(temp_dir, f"{variant_key}_{int(time.time())}.png")
    
    # Download the image
    if not download_image(image_url, variant_filename):
        return variant_key, False
    
    # Create the image paths list with reference image first
    image_paths = [ref_image_path, variant_filename]
    
    # Create the prompt - 修改提示词，确保输出格式一致
    prompt = f"""
你是一个专业的电商运营专家
我传给你这个本地图片list，第二张图片是我想要的商品样式
请你判断第一张图片中的商品是否和第二张一样

这个是第一张图片的标题+变体，作为辅助判断
{product_name}
这个是第二张图片的变体，作为辅助判断
{variant_key}
任务描述  
系统会收到两张图片：第一张是我的目标商品图（商品可能来自任意品类，如服装、手表、文具、玩具、数码产品、家居用品、运动器材、美妆产品、食品包装等无限品类），第二张是1688找到的商品图。请基于以下条件严格比对这两张图片中的商品是否完全一致。回答需详细、全面地描述各项比对的结果，并确保任何微小的差异都不被忽略。对比过程需针对商品类型灵活关注其特有的结构、设计元素、功能组件和材质特点（如服装的领口设计、手表的表盘与表带、文具的笔尖与笔帽、玩具的关节与拼接方式、数码产品的接口与按键、家居用品的把手与收纳结构、运动器材的外形和功能件、美妆产品的瓶口设计和包装细节、食品包装的印刷图案和密封结构等），避免因仅有局部相似而误判为同一商品。

比对条件

1. 商品类别识别  
   - 必须确认两张图片中的商品类别完全一致，包括大类和子类。  
     例如：  
     - 服装类：确认是否同为"长款风衣"或"运动夹克"  
     - 手表类：确认是否同为"机械表"或"智能腕表"  
     - 文具类：确认是否同为"签字笔"或"自动铅笔"  
     - 玩具类：确认是否同为"拼装积木"或"遥控汽车"  
     - 数码类：确认是否同为"智能手机"或"平板电脑"  
     - 家居用品：确认是否同为"储物盒"或"陶瓷花瓶"  
     - 美妆产品：确认是否同为"口红"或"面霜罐"  
     - 食品包装：确认是否同为"饼干包装盒"或"饮料瓶"  
     - 运动器材：确认是否同为"网球拍"或"哑铃"  
   - 若类别有任何不一致，请详细说明分类差异并指出对商品识别的影响。

2. 颜色与色差比对（必须判定主色是否为同色系）
    2.1 提取色值  
    - 先对主体大面积区域、装饰/流苏、配件等关键部位分别采样，获取平均 HSL 或 RGB 色值，并给出对应的规范色名（参考 CSS / Pantone 基础色）。  
    - 如果拍摄环境存在灯光或滤镜，需做相对校正后再比对。
    2.2: 判定阈值  
    - 主色调：若两图色相差 ≥ 10°（或色名归属不同色系，例如 青绿色 vs 深海蓝），即判定为"主色不同"。  
    - 同色系深浅差：如色相差 < 10° 但亮度或饱和度差 > 8 百分点，归为"同色系但深浅/纯度不同"，需说明视觉影响程度（轻微 / 中等 / 明显）。
    2.3:细节色差  
    - 对边缘饰条、纽扣、流苏等附属组件再做一次独立比对；即便只出现轻微偏黄、偏绿、偏灰等，也要指出具体部位和差异方向。

3. 款式和设计一致性  
   - 对比商品整体形状、尺寸比例、结构特征和功能组件排布。  
     示例：  
     - 服装类：版型、领口和袖口设计、纽扣和拉链位置、口袋布局  
     - 手表类：表盘形状、刻度设计、表带材质与连接方式、表冠位置  
     - 文具类：笔身长度、笔尖形状、笔帽结构、笔夹设计  
     - 玩具类：主要组件形状、拼插方式、关节数量和位置、表面纹理  
     - 数码产品：按键布局、接口位置与数量、摄像头排列、边框形状  
     - 家居用品：外观轮廓、开合方式、把手或提手设计、内部格局  
     - 美妆产品：瓶身形状、瓶口设计、按压头或旋转盖形式、标签印刷布局  
     - 食品包装：包装盒/瓶的形状、开口方式、密封条设计、印刷图案位置  
     - 运动器材：器材形状、握柄、接触面材质与设计、功能部件分布  
   - 若有设计细微差异，请详细描述并说明其对整体观感的影响。

4. 角度和拍摄差异考虑  
   - 考虑拍摄角度、光线、摆放方式的影响，避免因角度或光影变化导致的误判。  
   - 若角度造成厚度、立体感或比例误差，请详细说明推断过程及理由。

5. 主要商品聚焦 
   - 仅对比两张图片中所显示的主要商品本体特征，不将商品包装、装饰盒、展示底座、说明书、吊牌或其他非商品本体的元素纳入比对。  
   - 在确认材质、颜色、花纹、工艺或结构时，务必先判断该特征是否属于商品本体。如果该特征在一张图中属于商品主体，另一张图中则仅为背景或包装，请勿因此误判。  
   - 若背景或光线影响对商品本体细节的辨识，应说明影响程度及对判断的影响，但不因背景或包装差异而视为商品差异。

6. 材质和质地识别  
   - 分析商品材质，包括表面光滑度、光泽度、纹理和触感特征：  
     - 服装：面料织纹与厚度  
     - 手表：表带材质、表盘玻璃通透度  
     - 文具：笔身材质（塑料、金属、木质）、表面处理工艺（磨砂、光滑）  
     - 玩具：塑料或金属的表面光泽与硬度  
     - 数码产品：机身材质（金属、塑料、玻璃）、表面处理（镜面、磨砂）  
     - 家居用品：材质（陶瓷、木质、金属、塑料）、表面涂层  
     - 美妆产品：包装材质（玻璃、塑料、金属）、表面光泽与印刷工艺  
     - 食品包装：纸质、塑料膜或金属箔材质，光泽度和印刷质感  
     - 运动器材：材质（木、碳纤、橡胶、金属）、表面防滑纹理  
   - 若材质质感存在差异请详细描述。

7. 花纹及装饰元素一致性  
   - 对比商品上的图案、品牌Logo、印刷文字、标志性花纹、雕刻或刻印、贴纸和任何装饰元素（如手表表盘刻度、笔杆印刷商标、玩具表面贴纸、数码产品品牌Logo、家居用品花纹图案、美妆包装上的品牌标志、食品包装上的商标与配料说明、运动器材上的品牌标志）。  
   - 确保花纹、标识、图案位置与比例完全一致，任一微小差异需记录。

8. 工艺与结构细节  
   - 对比商品的制作工艺，如接缝、螺丝布局、粘合方式、部件拼接紧密度、表面处理工艺、按键与开关手感、封条、密封件。  
   - 根据品类特征检查特定细节：  
     - 服装：缝线密度、纽扣固定方式、拉链质量  
     - 手表：表冠、表扣、指针形状、刻度立体感  
     - 文具：笔尖处理、内部弹簧结构、笔芯接口  
     - 玩具：关节紧实度、衔接方式、螺丝或铆钉位置  
     - 数码产品：按键回弹、接口开孔精度、摄像头凸起程度  
     - 家居用品：盖子、抽屉、合页、把手处的安装方式  
     - 美妆产品：旋转、按压机制、密封垫圈、标签贴合程度  
     - 食品包装：封口方式、易拉环、拉链条、密封胶带  
     - 运动器材：接合部强度、握柄防滑处理、运动配件固定方式  
   - 若工艺细节存在差异请详细描述并评估对最终识别的影响。

信息提取要求  
请根据以上条件，逐项提取以下八项信息（确保每项仅包含一个类别判断）：  
1. 商品类别  
2. 颜色和色差  
3. 款式和设计一致性  
4. 角度和拍摄差异考虑  
5. 主要商品聚焦  
6. 材质和质地识别  
7. 花纹及装饰元素一致性  
8. 工艺与结构细节

比对标准  
上述八项信息中只要有一项存在差异即视为不同商品。若全部一致，则判定为同一商品。请严格对每一项进行细致比对，不忽略任何微小差异。

结果格式  
识别结果：一样 or 不一样  
解释：逐项详细描述每个比对项的结果，包括：  
1. 商品类别：确认商品类别及子类是否匹配。  
2. 颜色和色差：描述各部分颜色及光泽度差异。  
3. 款式和设计一致性：罗列核心结构与设计点，对比差异。  
4. 角度和拍摄差异考虑：说明是否受角度影响。  
5. 主要商品聚焦：说明背景和光线对识别的影响。  
6. 材质和质地识别：描述材质光滑度、纹理、厚度等差异。  
7. 花纹及装饰元素一致性：对比图案、Logo、标志性元素。  
8. 工艺与结构细节：描述缝合、拼接、螺丝、按键、密封等差异。

在解释中，请明确指出任何差异对最终判断的影响，以确保识别结果的严谨与精确。

注意：你的回答必须以"识别结果："开头，并且必须清晰表明"一样"或"不一样"，这对于自动化处理非常重要。
"""
    
    # Call the AI image analysis
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            result = analyze_image_with_fallback(image_paths, prompt)
            print(f"变体 {variant_key} 的分析结果:")
            print(result)
            
            # 改进结果解析逻辑，处理多种可能的回答格式
            # 检查关键词，而不是严格依赖特定格式
            if result:
                # 如果包含"一样"但不包含"不一样"，则认为商品匹配
                if "一样" in result and "不一样" not in result:
                    # 清理临时文件
                    try:
                        os.remove(variant_filename)
                    except:
                        pass
                    return variant_key, True
                break
        except Exception as e:
            print(f"分析变体 {variant_key} 时出错(尝试 {attempt+1}/{max_attempts}): {str(e)}")
            if attempt < max_attempts - 1:
                print(f"正在重试...")
                time.sleep(3)  # 在重试前添加短暂延迟
            else:
                print(f"分析变体 {variant_key} 失败，已达到最大尝试次数")
    
    # 清理临时文件
    try:
        os.remove(variant_filename)
    except:
        pass
    
    return variant_key, False

def find_matching_variants(product_dict, reference_image_path, product_name):
    """
    Find all product variants that match the reference image.
    
    Args:
        product_dict: Dictionary of variant names (keys) and image URLs (values)
        reference_image_path: Path to the reference image
        product_name: Name of the product
        
    Returns:
        List of variant names that match the reference image
    """
    # 创建临时目录
    temp_dir = "./temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    # 存储匹配的变体
    matching_variants = []
    
    # 限制并发数量，提高稳定性
    max_workers = min(len(product_dict), 5)  # 最多5个并发
    print(f"以{max_workers}个并发线程处理{len(product_dict)}个变体")
    
    # 使用线程池处理变体
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交任务
        future_to_variant = {
            executor.submit(
                process_variant, 
                variant_key, 
                image_url, 
                reference_image_path, 
                product_name, 
                temp_dir
            ): variant_key 
            for variant_key, image_url in product_dict.items()
        }
        
        # 处理结果
        for future in concurrent.futures.as_completed(future_to_variant):
            variant_key = future_to_variant[future]
            try:
                result_key, is_same = future.result()
                if is_same:
                    matching_variants.append(result_key)
                    print(f"找到匹配的变体: {result_key}")
            except Exception as e:
                print(f"处理变体 {variant_key} 时发生错误: {str(e)}")
    
    # 清理临时目录
    try:
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        if not os.listdir(temp_dir):  # 确保目录为空
            os.rmdir(temp_dir)
    except Exception as e:
        print(f"清理临时目录时出错: {str(e)}")
    
    return matching_variants

def compare_product_variants(product_dict, img_file, product_name):
    """
    Compare product variants with a reference image and return matching variants.
    
    Args:
        product_dict: Dictionary of variant names (keys) and image URLs (values)
        img_file: Path to the reference image
        product_name: Name of the product
        
    Returns:
        List of variant names that match the reference image
    """
    try:
        # 检查参考图片是否存在
        if not os.path.exists(img_file):
            print(f"错误: 参考图片 {img_file} 不存在")
            return []
            
        # 检查product_dict是否为空或无效
        if not product_dict or not isinstance(product_dict, dict):
            print(f"错误: 产品变体字典为空或无效")
            return []
            
        # 找到匹配的变体
        matching_variants = find_matching_variants(product_dict, img_file, product_name)
        
        print(f"分析完成. 找到 {len(matching_variants)} 个匹配的变体: {matching_variants}")
        return matching_variants
        
    except Exception as e:
        print(f"比较产品变体时发生错误: {str(e)}")
        return []

# 示例用法
if __name__ == "__main__":
    # 测试数据
    test_product_dict = {
        "蓝色 M": "https://example.com/blue_m.jpg",
        "红色 L": "https://example.com/red_l.jpg"
    }
    test_img_file = "./reference.png"  # 参考图片路径
    test_product_name = "测试产品名称"
    
    # 执行比较
    results = compare_product_variants(test_product_dict, test_img_file, test_product_name)
    print(f"匹配的变体: {results}")
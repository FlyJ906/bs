import os
import numpy as np
from PIL import Image
import re

# 尝试导入Tesseract OCR作为备选
tesseract_available = False
try:
    import pytesseract
    from PIL import Image
    tesseract_available = True
    print("✓ Tesseract OCR可用")
except ImportError:
    print("⚠ Tesseract OCR不可用，将使用简单的文本提取")
    pass

# 尝试导入EasyOCR作为备选
easyocr_available = False
try:
    import easyocr
    easyocr_available = True
    print("✓ EasyOCR可用")
except ImportError:
    print("⚠ EasyOCR不可用，将使用简单的文本提取")
    pass

# 必须在导入任何Paddle相关模块之前设置这些环境变量
def _set_paddle_env():
    # 禁用oneDNN/MKLDNN以避免版本兼容性问题
    os.environ["FLAGS_use_mkldnn"] = "0"
    os.environ["FLAGS_use_mkldnn_int8"] = "0"
    os.environ["FLAGS_use_onednn"] = "0"
    os.environ["FLAGS_enable_new_executor"] = "0"
    os.environ["FLAGS_enable_pir_in_executor"] = "0"
    os.environ["FLAGS_enable_pir_api"] = "0"
    os.environ["FLAGS_use_philox_random_seed"] = "0"
    os.environ["FLAGS_cudnn_deterministic"] = "1"
    # 禁用Paddle的模型源检查，避免网络问题
    os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "1"
    # 禁用新的执行器和PIR
    os.environ["FLAGS_enable_new_ir_in_executor"] = "0"
    os.environ["FLAGS_enable_parallel_graph_executor"] = "0"
    os.environ["FLAGS_enable_distributed_executor"] = "0"
    # 额外的环境变量来禁用oneDNN
    os.environ["MKLDNN_DISABLE"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["PADDLE_ENABLE_ONEDNN_OPTS"] = "0"

# 立即设置环境变量
_set_paddle_env()

_ocr_instance = None

def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        try:
            # paddleocr 需要 paddlepaddle（import 名为 paddle）
            import paddle

            # 双保险：部分版本环境变量不生效时，运行期强制关闭 oneDNN/MKLDNN/new_executor
            try:
                paddle.set_flags(
                    {
                        "FLAGS_use_mkldnn": False,
                        "FLAGS_use_mkldnn_int8": False,
                        "FLAGS_use_onednn": False,
                        "FLAGS_enable_new_executor": False,
                        "FLAGS_enable_pir_in_executor": False,
                        "FLAGS_enable_pir_api": False,
                        "FLAGS_use_philox_random_seed": False,
                        "FLAGS_cudnn_deterministic": True,
                    }
                )
            except Exception as e:
                print(f"设置paddle flags失败: {e}")
                pass
        except Exception as e:
            raise ImportError(
                "缺少 OCR 运行依赖：未能导入 `paddle`。"
                "请确保使用已安装 paddlepaddle 的 conda/Anaconda 环境运行，或在当前环境安装 paddlepaddle（CPU 版）。"
            ) from e

        # 懒加载 paddleocr，避免应用启动时卡住
        from paddleocr import PaddleOCR

        # 使用最基本的参数初始化，避免使用可能不兼容的参数
        _ocr_instance = PaddleOCR(
            use_angle_cls=False,  # 禁用角度分类，减少复杂性
            lang="ch"
        )
    return _ocr_instance

# 文本清洗
def _normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\u3000", " ").replace("\t", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# 从OCR文本中抽取“配料/成分”段落
def _extract_ingredient_section(full_text: str) -> str:
    text = _normalize_text(full_text)
    if not text:
        return ""

    # 常见“非配料区”标题，遇到就截断，避免把整张包装都当配料
    stop_keywords = [
        "营养成分表", "营养成分", "营养信息",
        "净含量", "规格", "贮存条件", "贮存", "储存",
        "保质期", "生产日期", "食用方法", "生产许可证", "执行标准",
        "厂家", "地址", "电话", "产地", "条形码",
    ]

    # 优先从“配料/配料表/成分”开始截取
    start_match = re.search(r"(配料表|配料|成分)\s*[:：]?", text)
    if start_match:
        section = text[start_match.start():]
    else:
        section = text

    # 截断到第一个 stop keyword
    cut_idx = None
    for kw in stop_keywords:
        i = section.find(kw)
        if i != -1:
            cut_idx = i if cut_idx is None else min(cut_idx, i)
    if cut_idx is not None and cut_idx > 0:
        section = section[:cut_idx]

    return _normalize_text(section)

# 解析配料表
def parse_ingredients(ingredients_raw):
    # 简单的配料解析逻辑
    if not ingredients_raw:
        return ""
    
    ingredients_raw = _normalize_text(ingredients_raw)

    # 移除配料前缀
    prefixes = ["配料表：", "配料表:", "配料：", "配料:", "成分：", "成分:"]
    for prefix in prefixes:
        if prefix in ingredients_raw:
            ingredients_raw = ingredients_raw.replace(prefix, "")
            break

    # 常见括号内容不作为分隔符，但可能混入比例/说明；先统一括号
    ingredients_raw = ingredients_raw.replace("（", "(").replace("）", ")")

    # 统一各种分隔符到顿号，便于后续 split
    ingredients_raw = ingredients_raw.replace("；", "、").replace(";", "、")
    ingredients_raw = ingredients_raw.replace("，", "、").replace(",", "、")
    ingredients_raw = ingredients_raw.replace("/", "、")
    
    # 按常见分隔符分割
    if "、" in ingredients_raw:
        ingredients = [ing.strip() for ing in ingredients_raw.split("、")]
    else:
        ingredients = [ingredients_raw.strip()]

    # 去空、去多余标点
    cleaned = []
    for ing in ingredients:
        ing = ing.strip().strip("。．. ")
        if not ing:
            continue
        cleaned.append(ing)

    return ",".join(cleaned)

# OCR识别配料表
def ocr_ingredients(image):
    try:
        # 处理不同类型的图片输入
        print(f"接收到的图片类型: {type(image)}")
        
        # 确保图片是PIL Image格式
        pil_image = None
        if isinstance(image, Image.Image):
            print("处理PIL Image输入")
            pil_image = image
        elif isinstance(image, str):
            # 如果是文件路径，直接使用
            print(f"处理文件路径输入: {image}")
            if not os.path.exists(image):
                print(f"文件不存在: {image}")
                return "OCR识别失败：文件不存在"
            pil_image = Image.open(image)
        elif isinstance(image, dict):
            # Gradio UploadButton 可能传入字典格式
            print(f"处理字典输入: {list(image.keys())}")
            if "name" in image:
                image_path = image["name"]
                print(f"使用字典中的name字段: {image_path}")
                if not os.path.exists(image_path):
                    print(f"文件不存在: {image_path}")
                    return "OCR识别失败：文件不存在"
                pil_image = Image.open(image_path)
            elif "data" in image:
                # 直接使用数据
                print("使用字典中的data字段")
                data = image["data"]
                if isinstance(data, np.ndarray):
                    pil_image = Image.fromarray(data)
                else:
                    return "OCR识别失败：不支持的图片格式"
        elif isinstance(image, np.ndarray):
            # 已经是numpy数组
            print(f"处理numpy数组输入: {image.shape}")
            pil_image = Image.fromarray(image)
        else:
            print(f"未知的图片类型: {type(image)}")
            return "OCR识别失败：不支持的图片格式"
        
        # 尝试使用Tesseract OCR
        if tesseract_available:
            try:
                print("使用Tesseract OCR识别...")
                # 预处理图片：转为灰度图并二值化
                gray_image = pil_image.convert('L')
                # 使用Tesseract识别中文
                recognized_text = pytesseract.image_to_string(gray_image, lang='chi_sim')
                print(f"Tesseract识别到的文本: {recognized_text}")
                
                # 抽取“配料/成分”段落后再解析
                section = _extract_ingredient_section(recognized_text)
                print(f"提取的配料段: {section}")
                
                parsed_ingredients = parse_ingredients(section)
                print(f"解析后的配料: {parsed_ingredients}")
                
                if parsed_ingredients:
                    return parsed_ingredients
                else:
                    print("Tesseract OCR未能识别到配料表")
            except Exception as e:
                print(f"Tesseract OCR识别失败: {e}")
        
        # 尝试使用EasyOCR
        if easyocr_available:
            try:
                print("使用EasyOCR识别...")
                # 初始化EasyOCR
                reader = easyocr.Reader(['ch_sim'])
                # 转换为numpy数组
                image_np = np.array(pil_image)
                # 识别文本
                result = reader.readtext(image_np)
                print(f"EasyOCR识别结果长度: {len(result)}")
                
                # 提取识别的文字
                recognized_text = ""
                for (bbox, text, prob) in result:
                    recognized_text += text + " "
                
                print(f"EasyOCR识别到的文本: {recognized_text}")
                
                # 抽取“配料/成分”段落后再解析
                section = _extract_ingredient_section(recognized_text)
                print(f"提取的配料段: {section}")
                
                parsed_ingredients = parse_ingredients(section)
                print(f"解析后的配料: {parsed_ingredients}")
                
                if parsed_ingredients:
                    return parsed_ingredients
                else:
                    print("EasyOCR未能识别到配料表")
            except Exception as e:
                print(f"EasyOCR识别失败: {e}")
        
        # 尝试使用PaddleOCR识别图片
        try:
            print("初始化PaddleOCR...")
            ocr = _get_ocr()
            
            print("开始PaddleOCR识别...")
            # 转换为numpy数组
            image_np = np.array(pil_image)
            try:
                result = ocr.ocr(image_np)
                print(f"PaddleOCR识别结果类型: {type(result)}")
            except TypeError as e:
                # 兜底：旧版本仍可能需要 cls 参数
                print(f"第一次识别失败，尝试带cls参数: {e}")
                result = ocr.ocr(image_np, cls=False)
            
            # 提取识别的文字
            recognized_text = ""
            # result 常见结构：List[List[[box, (text, score)], ...]]
            # 也可能是 List[[box, (text, score)], ...]
            if not result:
                print("PaddleOCR识别结果为空")
                return "OCR识别失败：未能识别到文本"

            print(f"PaddleOCR识别结果长度: {len(result)}")
            
            # 统一成二维
            if isinstance(result, list) and result:
                if isinstance(result[0], list):
                    lines = result
                else:
                    lines = [result]
            else:
                print("PaddleOCR识别结果格式异常")
                return "OCR识别失败：识别结果格式异常"

            for line in lines:
                for word_info in line:
                    try:
                        if isinstance(word_info, (list, tuple)) and len(word_info) >= 2:
                            text = word_info[1]
                            if isinstance(text, (list, tuple)) and len(text) >= 1:
                                text = text[0]
                            recognized_text += str(text) + " "
                    except Exception as e:
                        print(f"处理PaddleOCR识别结果时出错: {e}")
                        continue
            
            print(f"PaddleOCR识别到的文本: {recognized_text}")
            
            # 抽取“配料/成分”段落后再解析
            section = _extract_ingredient_section(recognized_text)
            print(f"提取的配料段: {section}")
            
            parsed_ingredients = parse_ingredients(section)
            print(f"解析后的配料: {parsed_ingredients}")
            
            if parsed_ingredients:
                return parsed_ingredients
            else:
                print("PaddleOCR未能识别到配料表")
                return "OCR识别失败：未能识别到配料表"
        except Exception as e:
            print(f"PaddleOCR识别失败: {e}")
            # 不再返回具体的错误信息，而是返回一个友好的提示
            return "OCR识别失败：请确保图片清晰，配料表文字可见"
    except Exception as e:
        print(f"OCR识别错误: {e}")
        import traceback
        traceback.print_exc()
        # 不再返回具体的错误信息，而是返回一个友好的提示
        return "OCR识别失败：请确保图片清晰，配料表文字可见"




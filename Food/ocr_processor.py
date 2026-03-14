import os
import numpy as np
from PIL import Image
import re

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_use_mkldnn_int8"] = "0"
os.environ["FLAGS_use_onednn"] = "0"
os.environ["FLAGS_enable_new_executor"] = "0"
os.environ["FLAGS_enable_pir_in_executor"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["FLAGS_enable_new_ir"] = "0"
os.environ["FLAGS_use_pir"] = "0"
os.environ["FLAGS_check_nan_inf"] = "0"
os.environ["GLOG_minloglevel"] = "2"
os.environ["GLOG_v"] = "0"

_ocr_instance = None

def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
            print("正在初始化 PaddleOCR 模型...")
            # 调整OCR参数，提高识别准确率
            _ocr_instance = PaddleOCR(
                use_angle_cls=True, 
                lang="ch", 
                show_log=False,
                det_algorithm='DB',
                det_db_thresh=0.3,
                det_db_box_thresh=0.6,
                det_db_unclip_ratio=1.5,
                rec_batch_num=1,
                max_text_length=100
            )
            print("PaddleOCR 初始化成功")
        except Exception as e:
            print(f"PaddleOCR 初始化失败: {e}")
            raise
    return _ocr_instance

def _extract_ingredients_section(text_list):
    """
    从OCR识别结果中提取配料表信息
    优先匹配"配料"关键字，如果没有则自动识别配料内容
    """
    ingredients_lines = []
    found_ingredients = False
    skip_next = False
    
    # 常见配料关键词（用于自动识别配料）
    common_ingredient_keywords = [
        "水", "糖", "浆", "汁", "浓缩", "果葡", "葡萄糖", "蔗糖", "果糖",
        "维生素", "柠檬酸", "苹果酸", "乳酸", "苯甲酸钠", "山梨酸钾",
        "香精", "色素", "胶", "酯", "钠", "钾", "钙", "蛋白质", "脂肪",
        "淀粉", "纤维素", "明胶", "卡拉胶", "黄原胶", "瓜尔胶",
        "椰子", "苹果", "橙", "柠檬", "草莓", "葡萄", "芒果", "番石榴",
        "芭乐", "桃", "梨", "香蕉", "菠萝", "西瓜", "哈密瓜",
        "三氯蔗糖", "二氧化碳", "柠檬酸", "柠檬酸钠", "苯甲酸", "山梨酸"
    ]
    
    # 配料表开始关键词
    start_keywords = [
        "配料", "配料表", "配料：", "配料表：", "配料:", "配料表:",
        "原料", "原料表", "原料：", "原料表：", "原料:", "原料表:",
        "成分", "成分表", "成分：", "成分表：", "成分:", "成分表:"
    ]
    
    # 配料表结束关键词
    stop_keywords = [
        "营养成分表", "营养成分", "营养信息",
        "净含量", "规格", "贮存条件", "贮存", "储存",
        "保质期", "生产日期", "食用方法", "生产许可证", "执行标准",
        "产品标准号", "厂家", "地址", "电话", "产地", "条形码",
        "生产商", "经销商", "服务热线", "如有", "产品类型", "产品名称"
    ]
    
    # 营养成分表特有的模式（用于检测和截断）
    nutrition_patterns = [
        r"项目\s*每100[gm]l?",  # "项目 每100ml" 或 "项目每100g"
        r"项目\s+N?R?V",  # "项目 NRV"
        r"每100[gm]l?\s*N?R?V",  # "每100ml NRV%"
        r"能量\s+\d+.*kJ",  # "能量 136kJ"
        r"\d+kJ\s+\d+%",  # "136kJ 2%"
    ]
    
    # 营养成分表包含的关键词（用于检测混入的内容）
    nutrition_content_keywords = [
        "NRV%", "每100ml", "每100g", "每100mL",
        "能量", "蛋白质", "脂肪", "碳水化合物",
        "膳食纤维", "钙", "铁", "锌"
    ]
    
    # 配料关键词（用于判断是否包含配料内容）
    ingredient_keywords = ["维生素", "柠檬酸", "柠檬酸钠", "香精", "糖", "浓缩", "浆", "汁", "三氯蔗糖", "苯甲酸钠", "二氧化碳", "果葡", "胶", "酸", "酯", "钾", "钠"]
    
    for i, text in enumerate(text_list):
        if skip_next:
            skip_next = False
            continue
            
        text = text.strip()
        if not text:
            continue
        
        if not found_ingredients:
            # 检查是否包含配料表开始关键词，优先匹配最长的关键词
            matched_kw = None
            max_length = 0
            for start_kw in start_keywords:
                if start_kw in text and len(start_kw) > max_length:
                    matched_kw = start_kw
                    max_length = len(start_kw)
            
            if matched_kw:
                found_ingredients = True
                # 提取配料内容
                idx = text.find(matched_kw)
                content = text[idx + len(matched_kw):].strip()
                # 移除可能的冒号和空格
                if content.startswith("：") or content.startswith(":"):
                    content = content[1:].strip()
                if content:
                    ingredients_lines.append(content)
            
            # 处理"配"和"料"分开的情况
            if not found_ingredients and "配" in text and i + 1 < len(text_list):
                # 找到"配"字的位置
                pei_pos = text.rfind("配")
                if pei_pos != -1:
                    next_text = text_list[i + 1].strip()
                    if next_text.startswith("料"):
                        found_ingredients = True
                        skip_next = True
                        # 提取配料内容
                        # 处理"料表"的情况
                        if next_text.startswith("料表"):
                            content = next_text[2:].strip()
                        else:
                            content = next_text[1:].strip()
                        # 移除可能的冒号
                        if content.startswith("：") or content.startswith(":"):
                            content = content[1:].strip()
                        if content:
                            ingredients_lines.append(content)
            
            # 自动识别配料：检查是否包含常见配料关键词
            if not found_ingredients:
                # 排除明显不是配料的行
                exclude_keywords = ["产品名称", "产品类型", "净含量", "保质期", "生产日期"]
                if any(exclude_kw in text for exclude_kw in exclude_keywords):
                    print(f"  排除非配料行: {text}")
                    continue
                
                keyword_count = sum(1 for kw in common_ingredient_keywords if kw in text)
                # 如果包含4个或更多配料关键词，可能是配料内容
                if keyword_count >= 4:
                    found_ingredients = True
                    ingredients_lines.append(text)
        else:
            should_stop = False
            clean_text = text
            
            # 检查是否包含"。"（配料表结束符）
            if "。" in text:
                idx = text.find("。")
                clean_text = text[:idx].strip()
                if clean_text:
                    ingredients_lines.append(clean_text)
                break  # 遇到句号，结束配料表提取
            
            # 检查是否包含停止关键字（完全停止）
            for kw in stop_keywords:
                if kw in text:
                    # 如果同时包含配料关键词，尝试提取配料部分
                    if any(ing in text for ing in ingredient_keywords):
                        idx = text.find(kw)
                        if idx > 0:
                            clean_text = text[:idx].strip()
                            if clean_text:
                                ingredients_lines.append(clean_text)
                    should_stop = True
                    break
            
            if not should_stop:
                # 检查是否包含营养成分表模式
                for pattern in nutrition_patterns:
                    match = re.search(pattern, text)
                    if match:
                        # 找到营养成分表开始位置，截断前面的配料内容
                        idx = text.find(match.group())
                        if idx > 0:
                            clean_text = text[:idx].strip()
                            if clean_text:
                                ingredients_lines.append(clean_text)
                        should_stop = True
                        break  # 跳出内层循环
                
                if not should_stop:
                    # 检查是否包含多个营养成分关键词（可能是营养成分表内容）
                    nutrition_keyword_count = sum(1 for kw in nutrition_content_keywords if kw in text)
                    if nutrition_keyword_count >= 2:
                        # 这行可能是营养成分表，检查是否同时有配料关键词
                        has_ingredient = any(keyword in text for keyword in ingredient_keywords)
                        if has_ingredient:
                            # 尝试找到营养成分关键词出现的位置，截断前面的配料
                            min_idx = len(text)
                            for kw in nutrition_content_keywords:
                                idx = text.find(kw)
                                if idx > 0 and idx < min_idx:
                                    min_idx = idx
                            if min_idx < len(text):
                                clean_text = text[:min_idx].strip()
                                if clean_text:
                                    ingredients_lines.append(clean_text)
                        should_stop = True
            
            if should_stop:
                break  # 跳出外层循环，停止提取配料
            
            # 移除可能的"营养成分表"错误识别前缀
            if "营养成分表" in clean_text:
                clean_text = clean_text.replace("营养成分表", "").strip()
            
            # 移除可能的其他无关前缀
            for stop_kw in stop_keywords:
                if clean_text.startswith(stop_kw):
                    clean_text = clean_text[len(stop_kw):].strip()
                    break
            
            if clean_text:
                ingredients_lines.append(clean_text)
    
    return ingredients_lines

def _parse_ingredients(ingredients_lines):
    """
    解析配料表，将多行配料合并并分割成独立成分
    """
    if not ingredients_lines:
        return ""
    
    full_text = " ".join(ingredients_lines)
    
    # 遇到"。"就结束（配料表结束符）
    if "。" in full_text:
        full_text = full_text.split("。")[0]
    
    full_text = full_text.replace("（", "(").replace("）", ")")
    full_text = full_text.replace("；", "、").replace(";", "、")
    full_text = full_text.replace("，", "、").replace(",", "、")
    full_text = full_text.replace("/", "、")
    
    if "、" in full_text:
        ingredients = [ing.strip() for ing in full_text.split("、")]
    else:
        ingredients = [full_text.strip()]
    
    cleaned = []
    for ing in ingredients:
        ing = ing.strip().strip("。．. ")
        if ing and len(ing) > 0:
            cleaned.append(ing)
    
    return ",".join(cleaned)

def parse_ingredients(ingredients_raw):
    """
    公开的配料解析函数，供其他模块调用
    """
    if not ingredients_raw:
        return ""
    lines = [ingredients_raw] if isinstance(ingredients_raw, str) else ingredients_raw
    return _parse_ingredients(lines)

def _preprocess_image(image):
    """
    图像预处理，提高OCR识别效果
    """
    # 暂时不进行预处理，直接返回原始图像
    return image

def ocr_ingredients(image):
    """
    OCR识别配料表
    返回格式：解析后的配料字符串
    """
    try:
        print(f"接收到的图片类型: {type(image)}")
        
        pil_image = None
        if isinstance(image, Image.Image):
            pil_image = image
        elif isinstance(image, str):
            if not os.path.exists(image):
                return "OCR识别失败：文件不存在"
            pil_image = Image.open(image)
        elif isinstance(image, dict):
            if "name" in image:
                image_path = image["name"]
                if not os.path.exists(image_path):
                    return "OCR识别失败：文件不存在"
                pil_image = Image.open(image_path)
            elif "data" in image:
                data = image["data"]
                if isinstance(data, np.ndarray):
                    pil_image = Image.fromarray(data)
                else:
                    return "OCR识别失败：不支持的图片格式"
        elif isinstance(image, np.ndarray):
            pil_image = Image.fromarray(image)
        else:
            return "OCR识别失败：不支持的图片格式"
        
        print("正在初始化PaddleOCR...")
        ocr = _get_ocr()
        
        print("开始图像预处理...")
        # 图像预处理
        processed_image = _preprocess_image(pil_image)
        
        print("开始PaddleOCR识别...")
        image_np = np.array(processed_image)
        print(f"图片数组形状: {image_np.shape}, dtype: {image_np.dtype}")
        
        # 如果是灰度图，转换为BGR格式
        if len(image_np.shape) == 2:
            # 灰度图转BGR
            image_np = np.stack([image_np, image_np, image_np], axis=2)
            print("已将灰度图转换为 BGR 格式")
        elif len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = image_np[:, :, ::-1].copy()
            print("已将图片从 RGB 转换为 BGR 格式")
        
        # 调整OCR参数，提高识别准确率
        result = ocr.ocr(image_np, cls=True, det=True, rec=True)
        
        print(f"PaddleOCR识别结果类型: {type(result)}")
        
        if not result or result[0] is None:
            return "OCR识别失败：未能识别到文本"
        
        text_list = []
        for line in result[0]:
            if line and len(line) >= 2:
                text = line[1][0]
                text_list.append(text)
        
        print(f"识别到的文本行数: {len(text_list)}")
        for i, text in enumerate(text_list):
            print(f"  [{i+1}] {text}")
        
        if not text_list:
            print("PaddleOCR未能提取到任何文本")
            return "OCR识别失败：未能识别到文本"
        
        print("\n========== 开始提取配料表 ==========")
        ingredients_lines = _extract_ingredients_section(text_list)
        
        if not ingredients_lines:
            print("未找到配料表信息")
            return "OCR识别失败：未找到配料表信息"
        
        print(f"提取到的配料表行数: {len(ingredients_lines)}")
        for i, line in enumerate(ingredients_lines):
            print(f"  配料行[{i+1}]: {line}")
        
        parsed_ingredients = _parse_ingredients(ingredients_lines)
        print(f"\n解析后的配料: {parsed_ingredients}")
        print("========== 配料表提取完成 ==========\n")
        
        if parsed_ingredients:
            return parsed_ingredients
        else:
            return "OCR识别失败：未能解析配料表"
            
    except Exception as e:
        print(f"OCR识别错误: {e}")
        import traceback
        traceback.print_exc()
        return f"OCR识别失败：{str(e)}"

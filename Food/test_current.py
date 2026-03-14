import re

def _extract_ingredients_section(text_list):
    """
    从OCR识别结果中提取配料表信息
    模糊匹配"配料"关键字，提取配料表内容
    """
    ingredients_lines = []
    found_ingredients = False
    skip_next = False
    
    for i, text in enumerate(text_list):
        if skip_next:
            skip_next = False
            continue
            
        text = text.strip()
        if not text:
            continue
        
        if not found_ingredients:
            if "配料" in text:
                found_ingredients = True
                match = re.search(r"配料\s*[：:]*\s*(.*)", text)
                if match:
                    content = match.group(1).strip()
                    if content:
                        ingredients_lines.append(content)
            elif text.endswith("配") and i + 1 < len(text_list):
                next_text = text_list[i + 1].strip()
                if next_text.startswith("料"):
                    found_ingredients = True
                    skip_next = True
                    match = re.search(r"料(?:表)?\s*[：:]*\s*(.*)", next_text)
                    if match:
                        content = match.group(1).strip()
                        if content:
                            ingredients_lines.append(content)
        else:
            stop_keywords = [
                "营养成分表", "营养成分", "营养信息",
                "净含量", "规格", "贮存条件", "贮存", "储存",
                "保质期", "生产日期", "食用方法", "生产许可证", "执行标准",
                "产品标准号", "厂家", "地址", "电话", "产地", "条形码",
                "生产商", "经销商", "服务热线", "如有"
            ]
            # 营养成分表特有的开头模式
            nutrition_start_patterns = [
                r"项目",  # "项目" 出现（营养成分表表头）
                r"每100[gm]l?",  # "每100ml" 或 "每100g"
                r"能量[\s\d]",  # "能量 136kJ" 等
                r"蛋白质[\s\d]",  # "蛋白质 0g" 等
                r"脂肪[\s\d]",  # "脂肪 0g" 等
                r"碳水化合物[\s\d]",  # "碳水化合物 8.0g" 等
                r"钠[\s\d]",  # "钠 15mg" 等
                r"N?R?V%",  # "NRV%" 出现
                r"NRV",  # "NRV" 出现
                r"\d+kJ",  # 包含能量单位
                r"\d+\s*kJ\s+\d+%",  # 能量值格式
                r"\d+g\s+\d+%",  # 其他营养成分格式
                r"\d+mg\s+\d+%",  # 钠的格式
            ]
            # 营养成分表包含的关键词（用于检测混入的内容）
            nutrition_content_keywords = [
                "NRV%", "每100ml", "每100g", "每100mL",
                "能量", "蛋白质", "脂肪", "碳水化合物", "钠",
                "膳食纤维", "维生素", "钙", "铁", "锌"
            ]
            should_stop = False
            
            # 首先检查是否是被错误识别的配料行
            ingredient_keywords = ["维生素", "柠檬酸", "柠檬酸钠", "钠", "香精", "糖", "浓缩", "浆", "汁", "三氯蔗糖", "苯甲酸钠", "二氧化碳"]
            has_ingredient = any(keyword in text for keyword in ingredient_keywords)
            
            if not has_ingredient:
                # 检查是否包含停止关键字
                for kw in stop_keywords:
                    if kw in text:
                        should_stop = True
                        break
                
                # 检查是否匹配营养成分表开头模式
                if not should_stop:
                    for pattern in nutrition_start_patterns:
                        if re.search(pattern, text):
                            should_stop = True
                            break
                
                # 检查是否包含多个营养成分关键词（可能是营养成分表内容）
                if not should_stop:
                    nutrition_keyword_count = sum(1 for kw in nutrition_content_keywords if kw in text)
                    if nutrition_keyword_count >= 2:
                        should_stop = True
            
            if should_stop:
                break
            
            # 移除可能的"营养成分表"错误识别前缀
            clean_text = text
            if "营养成分表" in clean_text:
                clean_text = clean_text.replace("营养成分表", "").strip()
            
            if clean_text:
                ingredients_lines.append(clean_text)
    
    return ingredients_lines

# 模拟当前OCR识别结果（包含错误）
test_data = [
    "LEMON REPUBLIC",
    "柠檬共和国",
    "云雾芭乐气泡饮（果汁型汽水",
    "NFC（非浓缩还原）红心芭乐浆添加量≥10g/L",
    "O产品名称：云雾芭乐气泡饮（果汁型汽水）O产品类型：果汁型汽水O配",
    "料表：水、果葡糖浆、红心番石榴（芭乐）浆、苹果浓缩汁、紫胡萝卜浓缩汁、",
    "营养成分表维生素C、柠檬酸、柠檬酸钠、三氯蔗糖、食用香精、苯甲酸钠、二氧化碳",
    "营养成分表",
    "项目 每100ml NRV% 能量 蛋白质 136kJ 2% 脂肪 Og 0% 碳水化合物 Og 8.0g 15mg 1%"
]

print("测试当前OCR错误情况:")
result = _extract_ingredients_section(test_data)
print(f"提取结果: {result}")
print(f"提取行数: {len(result)}")

# 测试解析函数
def _parse_ingredients(ingredients_lines):
    if not ingredients_lines:
        return ""
    
    full_text = " ".join(ingredients_lines)
    full_text = full_text.replace("（", "(").replace("）", ")")
    full_text = full_text.replace("；", "、").replace(";" , "、")
    full_text = full_text.replace("，", "、").replace("," , "、")
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

print("\n解析后的配料:")
parsed = _parse_ingredients(result)
print(parsed)

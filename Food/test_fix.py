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
            should_stop = False
            for kw in stop_keywords:
                if kw in text:
                    # 特殊处理：如果是"营养成分表"，检查是否真的是营养成分表
                    if kw == "营养成分表" and ingredients_lines:
                        # 检查前一行是否以顿号结尾，说明配料表还没结束
                        last_line = ingredients_lines[-1].strip()
                        if last_line.endswith("、") or last_line.endswith(","):
                            # 这可能是OCR错误，继续提取
                            should_stop = False
                        else:
                            # 检查下一行是否包含配料相关词汇
                            if i + 1 < len(text_list):
                                next_text = text_list[i + 1].strip()
                                # 如果下一行包含常见配料成分词汇，说明这是OCR错误
                                ingredient_keywords = ["维生素", "柠檬酸", "钠", "香精", "糖", "浓缩", "浆", "汁"]
                                has_ingredient = any(keyword in next_text for keyword in ingredient_keywords)
                                if has_ingredient:
                                    should_stop = False
                                else:
                                    should_stop = True
                            else:
                                should_stop = True
                    else:
                        should_stop = True
                    break
            
            if should_stop:
                break
            
            # 移除可能的"营养成分表"错误识别前缀
            clean_text = text
            if "营养成分表" in clean_text:
                clean_text = clean_text.replace("营养成分表", "").strip()
            
            if clean_text:
                ingredients_lines.append(clean_text)
    
    return ingredients_lines

# 模拟OCR识别结果（包含错误识别）
test_data = [
    "LEMON REPUBLIC",
    "柠檬共和国",
    "云雾芭乐气泡饮（果汁型汽水",
    "NFC（非浓缩还原）红心芭乐浆添加量≥10g/L",
    "O产品名称：云雾芭乐气泡饮（果汁型汽水）O产品类型：果汁型汽水O配",
    "料表：水、果葡糖浆、红心番石榴（芭乐）浆、苹果浓缩汁、紫胡萝卜浓缩汁、",
    "营养成分表维生素C、柠檬酸、柠檬酸钠、三氯蔗糖、食用香精、苯甲酸钠、二氧化碳",  # OCR错误识别，实际上这是配料表的第二行
    "营养成分表",  # 真正的营养成分表
    "项目",
    "每100ml",
    "NRV%"
]

print("测试OCR错误识别情况:")
result = _extract_ingredients_section(test_data)
print(f"提取结果: {result}")
print(f"提取行数: {len(result)}")

print("\n预期结果应该包含完整的配料表")

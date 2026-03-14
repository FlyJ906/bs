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
                    should_stop = True
                    break
            
            if should_stop:
                break
            
            ingredients_lines.append(text)
    
    return ingredients_lines

# 请在这里粘贴实际的OCR结果
test_data = [
    "LEMON REPUBLIC",
    "柠檬共和国",
    "云雾芭乐气泡饮（果汁型汽水",
    "NFC（非浓缩还原）红心芭乐浆添加量≥10g/L",
    "O产品名称：云雾芭乐气泡饮（果汁型汽水）O产品类型：果汁型汽水O配",
    "料表：水、果葡糖浆、红心番石榴（芭乐）浆、苹果浓缩汁、紫胡萝卜浓缩汁、",
    # 如果第7行不是营养成分表，请告诉我实际内容
]

print("请告诉我第7行的实际内容是什么？")
print("当前测试数据只有6行，第7行缺失")

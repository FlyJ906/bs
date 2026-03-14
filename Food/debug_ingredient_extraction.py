#!/usr/bin/env python3
"""
调试配料表提取逻辑
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import _extract_ingredients_section, _parse_ingredients

def debug_ingredient_extraction():
    """
    调试配料表提取逻辑
    """
    print("开始调试配料表提取逻辑...")
    
    # 测试用例：配和料表分开的情况
    test_case = [
        "产品名称：云雾芭乐气泡饮（果汁型汽水）",
        "O产品类型：果汁型汽水O配",
        "料表：水、果葡糖浆、红心番石榴（芭乐）浆、苹果浓缩汁、紫胡萝卜浓缩汁、",
        "营养成分表",
        "项目"
    ]
    
    print("输入文本：")
    for i, text in enumerate(test_case):
        print(f"  [{i+1}] {text}")
    
    # 手动跟踪提取过程
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
    
    for i, text in enumerate(test_case):
        print(f"\n处理第{i+1}行: {text}")
        
        if skip_next:
            print("  跳过该行")
            skip_next = False
            continue
            
        text = text.strip()
        if not text:
            print("  空行，跳过")
            continue
        
        if not found_ingredients:
            print("  尚未找到配料表")
            
            # 检查是否包含配料表开始关键词，优先匹配最长的关键词
            matched_kw = None
            max_length = 0
            for start_kw in start_keywords:
                if start_kw in text and len(start_kw) > max_length:
                    matched_kw = start_kw
                    max_length = len(start_kw)
            
            if matched_kw:
                print(f"  找到开始关键词: {matched_kw}")
                found_ingredients = True
                # 提取配料内容
                idx = text.find(matched_kw)
                content = text[idx + len(matched_kw):].strip()
                # 移除可能的冒号和空格
                if content.startswith("：") or content.startswith(":"):
                    content = content[1:].strip()
                print(f"  提取的内容: {content}")
                if content:
                    ingredients_lines.append(content)
            else:
                print("  未找到开始关键词")
                
                # 处理"配"和"料"分开的情况
                if "配" in text and i + 1 < len(test_case):
                    # 找到"配"字的位置
                    pei_pos = text.rfind("配")
                    if pei_pos != -1:
                        print(f"  找到'配'字在位置: {pei_pos}")
                        next_text = test_case[i + 1].strip()
                        print(f"  下一行: {next_text}")
                        if next_text.startswith("料"):
                            print("  下一行以'料'开头")
                            found_ingredients = True
                            skip_next = True
                            # 提取配料内容
                            # 处理"料表"的情况
                            if next_text.startswith("料表"):
                                print("  下一行以'料表'开头")
                                content = next_text[2:].strip()
                            else:
                                content = next_text[1:].strip()
                            # 移除可能的冒号
                            if content.startswith("：") or content.startswith(":"):
                                content = content[1:].strip()
                            print(f"  提取的内容: {content}")
                            if content:
                                ingredients_lines.append(content)
                        else:
                            print("  下一行不以'料'开头")
                    else:
                        print("  未找到'配'字")
                else:
                    print("  不包含'配'字或已到最后一行")
                
                # 自动识别配料：检查是否包含常见配料关键词
                if not found_ingredients:
                    keyword_count = sum(1 for kw in common_ingredient_keywords if kw in text)
                    print(f"  关键词数量: {keyword_count}")
                    # 如果包含3个或更多配料关键词，可能是配料内容
                    if keyword_count >= 3:
                        print("  关键词数量达到阈值，自动识别为配料")
                        found_ingredients = True
                        ingredients_lines.append(text)
                    else:
                        print("  关键词数量未达到阈值")
        else:
            print("  已找到配料表，检查是否结束")
            # 这里省略结束检查的逻辑
            break
    
    print(f"\n提取到的配料行：")
    for i, line in enumerate(ingredients_lines):
        print(f"  [{i+1}] {line}")
    
    # 解析配料
    parsed_ingredients = _parse_ingredients(ingredients_lines)
    print(f"\n解析后的配料：{parsed_ingredients}")
    
    if parsed_ingredients and "料表：" not in parsed_ingredients:
        print("✅ 修复成功：配料表提取正确，没有包含'料表：'前缀")
    else:
        print("❌ 修复失败：配料表提取仍然包含'料表：'前缀")
    
    print("\n调试完成")

if __name__ == "__main__":
    debug_ingredient_extraction()

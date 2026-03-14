#!/usr/bin/env python3
"""
测试修复后的配料表提取逻辑
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import _extract_ingredients_section, _parse_ingredients

def test_fix_ingredient_extraction():
    """
    测试修复后的配料表提取逻辑
    """
    print("开始测试修复后的配料表提取逻辑...")
    
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
    
    # 提取配料表
    ingredients_lines = _extract_ingredients_section(test_case)
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
    
    print("\n测试完成")

if __name__ == "__main__":
    test_fix_ingredient_extraction()

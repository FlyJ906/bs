#!/usr/bin/env python3
"""
测试配料表提取逻辑
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import _extract_ingredients_section, _parse_ingredients

def test_ingredient_extraction():
    """
    测试配料表提取逻辑
    """
    print("开始测试配料表提取逻辑...")
    
    # 测试用例1：标准配料表格式
    test_case_1 = [
        "产品名称：云雾芭乐气泡饮",
        "配料表：水、果葡糖浆、红心番石榴浆、苹果浓缩汁、紫胡萝卜浓缩汁",
        "营养成分表",
        "项目 每100ml",
        "能量 136kJ"
    ]
    
    # 测试用例2：配料和料分开的情况
    test_case_2 = [
        "产品名称：测试产品",
        "配",
        "料：水、糖、盐",
        "净含量：500ml"
    ]
    
    # 测试用例3：自动识别配料
    test_case_3 = [
        "产品名称：测试饮料",
        "水、果葡糖浆、苹果汁、柠檬酸、维生素C",
        "保质期：12个月"
    ]
    
    test_cases = [
        ("标准格式", test_case_1),
        ("配料分开", test_case_2),
        ("自动识别", test_case_3)
    ]
    
    for test_name, test_text_list in test_cases:
        print(f"\n=== 测试用例：{test_name} ===")
        print("输入文本：")
        for i, text in enumerate(test_text_list):
            print(f"  [{i+1}] {text}")
        
        # 提取配料表
        ingredients_lines = _extract_ingredients_section(test_text_list)
        print(f"\n提取到的配料行：")
        for i, line in enumerate(ingredients_lines):
            print(f"  [{i+1}] {line}")
        
        # 解析配料
        parsed_ingredients = _parse_ingredients(ingredients_lines)
        print(f"\n解析后的配料：{parsed_ingredients}")
        
        if parsed_ingredients:
            print("✅ 提取成功")
        else:
            print("❌ 提取失败")
    
    print("\n配料表提取逻辑测试完成")

if __name__ == "__main__":
    test_ingredient_extraction()

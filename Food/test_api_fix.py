#!/usr/bin/env python3
"""
测试修复后的Open Food Facts API调用
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import get_product_from_api

def test_api_fix():
    """
    测试修复后的API调用
    """
    print("开始测试修复后的Open Food Facts API调用...")
    
    # 测试用的条形码
    test_barcodes = [
        "6901234567892",  # 测试条形码1
        "6926265352880",  # 测试条形码2
        "6974653675301"   # 之前失败的条形码
    ]
    
    for barcode in test_barcodes:
        print(f"\n=== 测试条形码: {barcode} ===")
        product = get_product_from_api(barcode)
        if product:
            print(f"✅ API调用成功")
            print(f"商品名称: {product['product_name']}")
            print(f"配料表: {product['ingredients_raw']}")
            print(f"API来源: {product['api_source']}")
        else:
            print(f"❌ API调用失败")
    
    print("\nAPI测试完成")

if __name__ == "__main__":
    test_api_fix()

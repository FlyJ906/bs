#!/usr/bin/env python3
"""
测试数据库结构更新
"""
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database, save_product_to_local, query_local_product

def test_database_update():
    """
    测试数据库结构更新
    """
    print("开始测试数据库结构更新...")
    
    # 初始化数据库
    print("初始化数据库...")
    init_database()
    
    # 测试数据
    test_product = {
        "barcode": "1234567890123",
        "product_name": "测试商品",
        "ingredients_raw": "水、糖、盐",
        "ingredients_parsed": "水,糖,盐"
    }
    
    # 保存商品
    print("\n保存测试商品...")
    save_result = save_product_to_local(test_product)
    print(f"保存结果: {'成功' if save_result else '失败'}")
    
    # 查询商品
    print("\n查询测试商品...")
    product = query_local_product("1234567890123")
    if product:
        print("查询成功")
        print(f"条形码: {product['barcode']}")
        print(f"商品名称: {product['product_name']}")
        print(f"配料信息: {product['ingredients_raw']}")
    else:
        print("查询失败")
    
    # 测试更新商品
    print("\n更新测试商品...")
    updated_product = {
        "barcode": "1234567890123",
        "product_name": "更新后的测试商品",
        "ingredients_raw": "水、糖、盐、醋",
        "ingredients_parsed": "水,糖,盐,醋"
    }
    update_result = save_product_to_local(updated_product)
    print(f"更新结果: {'成功' if update_result else '失败'}")
    
    # 再次查询商品
    print("\n再次查询测试商品...")
    updated_product = query_local_product("1234567890123")
    if updated_product:
        print("查询成功")
        print(f"条形码: {updated_product['barcode']}")
        print(f"商品名称: {updated_product['product_name']}")
        print(f"配料信息: {updated_product['ingredients_raw']}")
    else:
        print("查询失败")
    
    print("\n数据库结构更新测试完成")

if __name__ == "__main__":
    test_database_update()

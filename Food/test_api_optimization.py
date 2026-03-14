#!/usr/bin/env python3
"""
测试API调用优化功能
"""
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import query_local_product, save_product_to_local, init_database
from api_client import get_product_from_api, failed_api_calls, failed_api_times

def test_local_database_priority():
    """测试本地数据库优先查询"""
    print("\n=== 测试本地数据库优先查询 ===")
    
    # 测试数据
    test_barcode = "1234567890123"
    test_product = {
        "barcode": test_barcode,
        "product_name": "测试商品",
        "ingredients_raw": "测试配料",
        "ingredients_parsed": "测试配料"
    }
    
    # 保存到本地数据库
    save_result = save_product_to_local(test_product)
    print(f"保存测试商品到本地数据库: {'成功' if save_result else '失败'}")
    
    # 测试本地查询
    local_product = query_local_product(test_barcode)
    print(f"本地数据库查询结果: {'找到' if local_product else '未找到'}")
    
    if local_product:
        print(f"商品名称: {local_product['product_name']}")
    
    return local_product is not None

def test_api_call_failure():
    """测试API调用失败处理"""
    print("\n=== 测试API调用失败处理 ===")
    
    # 使用一个不存在的条形码
    test_barcode = "6974653675301"  # 这个条形码在Open Food Facts中不存在
    
    # 清除之前的失败记录
    if test_barcode in failed_api_calls:
        failed_api_calls.remove(test_barcode)
    if test_barcode in failed_api_times:
        del failed_api_times[test_barcode]
    
    # 第一次调用API
    start_time = time.time()
    product = get_product_from_api(test_barcode)
    response_time = time.time() - start_time
    
    print(f"第一次API调用结果: {'成功' if product else '失败'}")
    print(f"API调用响应时间: {response_time:.2f}秒")
    
    # 检查是否记录了失败
    print(f"是否记录了API调用失败: {test_barcode in failed_api_calls}")
    
    # 第二次调用API（应该跳过）
    start_time = time.time()
    product2 = get_product_from_api(test_barcode)
    response_time2 = time.time() - start_time
    
    print(f"第二次API调用结果: {'成功' if product2 else '失败'}")
    print(f"第二次API调用响应时间: {response_time2:.2f}秒")
    
    # 验证第二次调用是否跳过了实际API请求
    if response_time2 < 0.1:  # 跳过API请求的响应时间应该非常短
        print("✓ 第二次API调用成功跳过了实际请求")
    else:
        print("✗ 第二次API调用没有跳过实际请求")
    
    return product is None and product2 is None

def test_response_time():
    """测试响应时间"""
    print("\n=== 测试响应时间 ===")
    
    # 测试数据
    test_barcode = "1234567890123"
    
    # 确保商品在本地数据库中
    local_product = query_local_product(test_barcode)
    if not local_product:
        test_product = {
            "barcode": test_barcode,
            "product_name": "测试商品",
            "ingredients_raw": "测试配料",
            "ingredients_parsed": "测试配料"
        }
        save_product_to_local(test_product)
    
    # 测试本地数据库查询响应时间
    start_time = time.time()
    product = query_local_product(test_barcode)
    response_time = time.time() - start_time
    
    print(f"本地数据库查询响应时间: {response_time:.4f}秒")
    
    if response_time < 1.0:
        print("✓ 本地数据库查询响应时间符合要求 (< 1秒)")
    else:
        print("✗ 本地数据库查询响应时间不符合要求 (> 1秒)")
    
    return response_time < 1.0

def run_all_tests():
    """运行所有测试"""
    print("开始测试API调用优化功能...")
    
    # 初始化数据库
    init_database()
    time.sleep(1)  # 等待数据库初始化
    
    # 运行测试
    test1_passed = test_local_database_priority()
    test2_passed = test_api_call_failure()
    test3_passed = test_response_time()
    
    # 输出测试结果
    print("\n=== 测试结果汇总 ===")
    print(f"本地数据库优先查询: {'通过' if test1_passed else '失败'}")
    print(f"API调用失败处理: {'通过' if test2_passed else '失败'}")
    print(f"响应时间测试: {'通过' if test3_passed else '失败'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\n总体测试结果: {'全部通过' if all_passed else '部分失败'}")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()

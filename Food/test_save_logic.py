import os

# 设置环境变量
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

from database import save_product_to_local, init_database
import threading

print("初始化数据库...")
init_thread = threading.Thread(target=init_database, daemon=True)
init_thread.start()

# 测试用例
test_cases = [
    {
        'name': '有效商品（API返回）',
        'product': {
            'barcode': '6901234567892',
            'product_name': '测试商品',
            'brand': '测试品牌',
            'ingredients_raw': '水、白砂糖、柠檬酸',
            'ingredients_parsed': '水,白砂糖,柠檬酸',
            'categories': '饮料',
            'serving_size': '100ml',
            'nutriscore': 'A',
            'api_source': '中文API'
        },
        'expected': True
    },
    {
        'name': 'OCR识别失败',
        'product': {
            'barcode': '6926265352880',
            'product_name': '未命名商品',
            'ingredients_raw': 'OCR识别失败：请确保图片清晰，配料表文字可见',
            'ingredients_parsed': 'OCR识别失败：请确保图片清晰，配料表文字可见'
        },
        'expected': False
    },
    {
        'name': '未命名商品',
        'product': {
            'barcode': '1234567890123',
            'product_name': '未命名商品',
            'ingredients_raw': '水、白砂糖',
            'ingredients_parsed': '水,白砂糖'
        },
        'expected': False
    },
    {
        'name': '缺少配料信息',
        'product': {
            'barcode': '9876543210987',
            'product_name': '测试商品',
            'ingredients_raw': '',
            'ingredients_parsed': ''
        },
        'expected': False
    },
    {
        'name': '空商品信息',
        'product': None,
        'expected': False
    }
]

print("\n测试保存商品逻辑...")

passed = 0
failed = 0

for test_case in test_cases:
    print(f"\n=== 测试: {test_case['name']} ===")
    result = save_product_to_local(test_case['product'])
    if result == test_case['expected']:
        print(f"✓ 测试通过")
        passed += 1
    else:
        print(f"✗ 测试失败 - 期望: {test_case['expected']}, 实际: {result}")
        failed += 1

print(f"\n测试完成: 通过 {passed}, 失败 {failed}")

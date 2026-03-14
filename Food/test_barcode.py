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

from barcode_scanner import scan_barcode_from_image
from api_client import get_product_from_api
from database import query_local_product, save_product_to_local, init_database
import threading

print("初始化数据库...")
init_thread = threading.Thread(target=init_database, daemon=True)
init_thread.start()

# 模拟测试条形码（使用真实的EAN-13条形码）
test_barcodes = [
    "6901234567892",  # 示例条形码
    "8857121507587",  # 示例产品
    "0000000000000"   # 不存在的产品
]

print("\n测试条形码识别商品功能...")

for barcode in test_barcodes:
    print(f"\n=== 测试条形码: {barcode} ===")
    
    # 1. 检查本地数据库
    print("1. 检查本地数据库...")
    local_product = query_local_product(barcode)
    if local_product:
        print(f"   本地数据库找到商品: {local_product.get('product_name')}")
    else:
        print("   本地数据库未找到商品")
    
    # 2. 调用Open Food Facts API
    print("2. 调用Open Food Facts API...")
    api_product = get_product_from_api(barcode)
    if api_product:
        print(f"   API找到商品: {api_product.get('product_name')}")
        print(f"   品牌: {api_product.get('brand')}")
        print(f"   配料: {api_product.get('ingredients_raw')[:100]}...")
        print(f"   数据来源: {api_product.get('api_source')}")
        
        # 3. 保存到本地数据库
        print("3. 保存到本地数据库...")
        saved = save_product_to_local(api_product)
        if saved:
            print("   保存成功")
        else:
            print("   保存失败")
    else:
        print("   API未找到商品")

print("\n测试完成！")

from api_client import get_product_from_api
from database import save_product_to_local, query_local_product, init_database

# 初始化数据库
print("初始化数据库...")
init_database()

# 测试条形码
barcode = "6926265352880"  # 上好佳薯片

# 1. 从API Byte获取商品信息
print("\n1. 从API Byte获取商品信息...")
product = get_product_from_api(barcode)
if product:
    print(f"获取成功: {product['product_name']}")
    print(f"API来源: {product['api_source']}")
    print(f"配料信息: {product['ingredients_raw'] or '无'}")
else:
    print("获取失败")

# 2. 保存到数据库
print("\n2. 保存到数据库...")
if product:
    saved = save_product_to_local(product)
    if saved:
        print("保存成功")
    else:
        print("保存失败")

# 3. 从数据库查询商品信息
print("\n3. 从数据库查询商品信息...")
local_product = query_local_product(barcode)
if local_product:
    print(f"查询成功: {local_product['product_name']}")
    print(f"配料信息: {local_product['ingredients_raw'] or '无'}")
else:
    print("查询失败")

print("\n测试完成！")

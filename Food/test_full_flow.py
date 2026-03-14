from api_client import get_product_from_api
from database import query_local_product, save_product_to_local, init_database

# 初始化数据库
print("初始化数据库...")
init_database()

# 测试用例1：API Byte调用成功，商品库中不存在商品
print("\n测试用例1：API Byte调用成功，商品库中不存在商品")
barcode1 = "6901234567892"  # 千岛木兰野生猕猴桃

# 1. 从API Byte获取商品信息
print("1. 从API Byte获取商品信息...")
product1 = get_product_from_api(barcode1)
if product1:
    print(f"获取成功: {product1['product_name']}")
    # 2. 检查商品库中是否存在该商品
    print("2. 检查商品库中是否存在该商品...")
    local_product1 = query_local_product(barcode1)
    if local_product1:
        print(f"商品库中已存在: {local_product1['product_name']}")
    else:
        print("商品库中不存在该商品")
        # 3. 保存到商品库
        print("3. 保存到商品库...")
        saved1 = save_product_to_local(product1)
        if saved1:
            print("保存成功")
        else:
            print("保存失败")
else:
    print("API Byte调用失败")

# 测试用例2：API Byte调用成功，商品库中已存在商品
print("\n测试用例2：API Byte调用成功，商品库中已存在商品")
barcode2 = "6926265352880"  # 上好佳薯片

# 1. 从API Byte获取商品信息
print("1. 从API Byte获取商品信息...")
product2 = get_product_from_api(barcode2)
if product2:
    print(f"获取成功: {product2['product_name']}")
    # 2. 检查商品库中是否存在该商品
    print("2. 检查商品库中是否存在该商品...")
    local_product2 = query_local_product(barcode2)
    if local_product2:
        print(f"商品库中已存在: {local_product2['product_name']}")
    else:
        print("商品库中不存在该商品")
        # 3. 保存到商品库
        print("3. 保存到商品库...")
        saved2 = save_product_to_local(product2)
        if saved2:
            print("保存成功")
        else:
            print("保存失败")
else:
    print("API Byte调用失败")

# 测试用例3：API Byte未找到商品
print("\n测试用例3：API Byte未找到商品")
barcode3 = "6974653675301"  # 未收录的商品

# 1. 从API Byte获取商品信息
print("1. 从API Byte获取商品信息...")
product3 = get_product_from_api(barcode3)
if product3:
    print(f"获取成功: {product3['product_name']}")
else:
    print("API Byte未找到商品")

print("\n测试完成！")

import requests
import json
from config import API_BYTE_URL, API_BYTE_KEY

# 测试API Byte条形码识别
def test_api_byte(barcode):
    print(f"测试API Byte条形码识别: {barcode}")
    
    # 构建请求
    headers = {
        'X-Api-Key': API_BYTE_KEY
    }
    
    params = {
        'barcode': barcode
    }
    
    try:
        # 发送GET请求
        response = requests.get(API_BYTE_URL, params=params, headers=headers, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 检查响应结构
                if data.get('code') == 200:
                    product_data = data.get('data', {})
                    if product_data.get('found'):
                        print(f"商品名称: {product_data.get('goods_name')}")
                        print(f"配料信息: 无 (API Byte暂不提供配料信息)")
                        return True
                    else:
                        print(f"API Byte未找到商品: {product_data.get('message', '未知错误')}")
                        return False
                else:
                    print(f"API Byte返回错误: {data.get('msg', '未知错误')}")
                    return False
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return False
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return False

# 测试多个条形码
if __name__ == "__main__":
    # 测试条形码列表
    test_barcodes = [
        "6901234567892",  # 示例条形码1
        "6926265352880",  # 示例条形码2
        "6974653675301"   # 示例条形码3
    ]
    
    for barcode in test_barcodes:
        print("=" * 50)
        test_api_byte(barcode)
        print("=" * 50)

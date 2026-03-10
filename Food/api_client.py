import requests
import time
from config import OPEN_FOOD_FACTS_API_URL
from ocr_processor import parse_ingredients

# API请求计数器和时间戳
api_requests = []
MAX_REQUESTS_PER_MINUTE = 100

# 检查API速率限制
def check_rate_limit():
    current_time = time.time()
    # 移除一分钟前的请求
    global api_requests
    api_requests = [t for t in api_requests if current_time - t < 60]
    # 检查是否超过速率限制
    if len(api_requests) >= MAX_REQUESTS_PER_MINUTE:
        # 等待直到有可用的请求配额
        wait_time = 60 - (current_time - api_requests[0])
        if wait_time > 0:
            print(f"API速率限制，等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)
    # 添加当前请求时间戳
    api_requests.append(time.time())

# 从Open Food Facts API获取商品信息
def get_product_from_api(barcode):
    # 检查速率限制
    check_rate_limit()
    
    # 使用v2版本的API
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    
    # 设置请求头，添加用户代理信息
    headers = {
        'User-Agent': 'FoodIngredientAnalyzer/1.0 (https://your-app-url.com)'
    }
    
    try:
        print(f"请求Open Food Facts API获取商品信息: {barcode}")
        response = requests.get(url, headers=headers, timeout=10)
        
        # 处理响应
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:
                product = data.get('product', {})
                product_name = product.get('product_name', '')
                brand = product.get('brands', '')
                ingredients_raw = product.get('ingredients_text', '')
                ingredients_parsed = parse_ingredients(ingredients_raw)
                return {
                    'barcode': barcode,
                    'product_name': product_name,
                    'brand': brand,
                    'ingredients_raw': ingredients_raw,
                    'ingredients_parsed': ingredients_parsed
                }
            else:
                print(f"商品未找到: {barcode}")
        elif response.status_code == 429:
            print("API速率限制 exceeded，等待后重试")
            time.sleep(60)
            return get_product_from_api(barcode)
        else:
            print(f"API请求失败，状态码: {response.status_code}")
    except requests.exceptions.Timeout:
        print("API请求超时")
    except requests.exceptions.RequestException as e:
        print(f"API请求错误: {e}")
    except Exception as e:
        print(f"处理API响应时出错: {e}")
    return None

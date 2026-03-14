import requests
import time
import json
from config import (
    API_BYTE_URL,
    API_BYTE_KEY,
    MAX_REQUESTS_PER_MINUTE,
    API_TIMEOUT,
    API_RETRY_COUNT,
    API_RETRY_DELAY
)
from ocr_processor import parse_ingredients

# API请求计数器和时间戳
api_requests = []

# API调用失败缓存（避免重复调用）
failed_api_calls = set()
# 缓存过期时间（秒）
FAILED_CACHE_EXPIRY = 3600  # 1小时
# 缓存时间记录
failed_api_times = {}

# 检查API调用是否已失败

def is_api_call_failed(barcode):
    """
    检查条形码的API调用是否已失败
    """
    if barcode not in failed_api_calls:
        return False
    # 检查缓存是否过期
    timestamp = failed_api_times.get(barcode, 0)
    if time.time() - timestamp > FAILED_CACHE_EXPIRY:
        # 缓存过期，移除
        failed_api_calls.remove(barcode)
        if barcode in failed_api_times:
            del failed_api_times[barcode]
        return False
    return True

# 记录API调用失败
def record_api_failure(barcode):
    """
    记录API调用失败
    """
    failed_api_calls.add(barcode)
    failed_api_times[barcode] = time.time()
    print(f"记录API调用失败: {barcode}")

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

# 从API Byte获取商品信息
def get_product_from_api(barcode):
    """
    从API Byte获取商品信息
    """
    # 检查是否已失败过
    if is_api_call_failed(barcode):
        print(f"API调用已失败，跳过重复调用: {barcode}")
        return None
    
    # 检查速率限制
    check_rate_limit()
    
    # 请求头
    headers = {
        'User-Agent': 'FoodIngredientAnalyzer/1.0 (https://food-ingredient-analyzer.example.com)'
    }
    
    # 只使用API Byte
    api_endpoints = [
        ("API Byte", API_BYTE_URL)
    ]
    
    for api_name, url in api_endpoints:
        print(f"尝试{api_name}获取商品信息: {barcode}")
        
        # 重试机制
        for attempt in range(API_RETRY_COUNT):
            try:
                # API Byte的调用方式，使用GET请求并添加API密钥
                # 添加API密钥到请求头
                api_headers = headers.copy()
                # 使用正确的请求头格式
                api_headers['X-Api-Key'] = API_BYTE_KEY
                # 构建URL参数
                params = {
                    'barcode': barcode
                }
                response = requests.get(url, params=params, headers=api_headers, timeout=API_TIMEOUT)
                
                # 处理响应
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        # 处理API Byte的响应格式
                        # 注意：实际响应格式需要根据API Byte的文档进行调整
                        if data.get('code') == 200:
                            product_data = data.get('data', {})
                            # 检查商品是否找到
                            if product_data.get('found'):
                                product_name = product_data.get('goods_name', '')
                                # API Byte目前没有配料信息字段
                                ingredients_raw = ""
                                ingredients_parsed = ""
                                
                                return {
                                    'barcode': barcode,
                                    'product_name': product_name,
                                    'ingredients_raw': ingredients_raw,
                                    'ingredients_parsed': ingredients_parsed,
                                    'api_source': api_name
                                }
                            else:
                                print(f"API Byte未找到商品: {barcode}")
                                print(f"API Byte响应: {data}")
                                break  # 跳到下一个API
                        else:
                            print(f"{api_name}未找到商品: {barcode}")
                            print(f"API Byte响应: {data}")
                            break  # 跳到下一个API
                    except json.JSONDecodeError as e:
                        print(f"{api_name}响应解析错误: {e}")
                        print(f"响应内容: {response.text[:200]}...")
                        break  # 跳到下一个API
                elif response.status_code == 429:
                    print(f"{api_name}速率限制 exceeded，等待后重试")
                    time.sleep(API_RETRY_DELAY * (attempt + 1))
                    continue  # 重试
                else:
                    print(f"{api_name}请求失败，状态码: {response.status_code}")
                    break  # 跳到下一个API
            except requests.exceptions.Timeout:
                print(f"{api_name}请求超时 (尝试 {attempt + 1}/{API_RETRY_COUNT})")
                if attempt < API_RETRY_COUNT - 1:
                    time.sleep(API_RETRY_DELAY * (attempt + 1))
                    continue
            except requests.exceptions.RequestException as e:
                print(f"{api_name}请求错误: {e}")
                break  # API Byte调用失败，结束尝试
            except Exception as e:
                print(f"处理{api_name}响应时出错: {e}")
                break  # API Byte处理失败，结束尝试
    
    # 记录API调用失败
    record_api_failure(barcode)
    return None

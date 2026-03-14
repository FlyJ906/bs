import requests
# 获取前100个中文食品条码（仅演示，可调整数量）
url = "https://cn.openfoodfacts.org/country/China.json?page=1&page_size=100"
response = requests.get(url, timeout=10)
barcodes = [item["code"] for item in response.json()["products"] if item.get("code")]
print("获取到条码列表：", barcodes[:10])  # 打印前10个
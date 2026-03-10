import cv2
import pyzbar.pyzbar as pyzbar
import csv
import requests
import json
import gradio as gr
import os
from paddleocr import PaddleOCR

# 初始化PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 健康身份列表
HEALTH_IDENTITIES = ["普通", "糖尿病", "肾病", "孕妇", "健身人群"]

# 本地数据库文件
PRODUCTS_CSV = "products.csv"
INGREDIENTS_CSV = "ingredients.csv"

# 初始化本地数据库文件
def init_database():
    # 创建products.csv
    if not os.path.exists(PRODUCTS_CSV):
        with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["barcode", "product_name", "ingredients_raw", "ingredients_parsed"])
    
    # 创建ingredients.csv
    if not os.path.exists(INGREDIENTS_CSV):
        with open(INGREDIENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["standard_name", "aliases", "role", "tag", "risk_for", "description"])
        # 添加一些常见成分作为示例
        with open(INGREDIENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["白砂糖", "白糖,蔗糖", "甜味剂", "添加剂", "糖尿病,健身人群", "高糖分，应控制摄入"])
            writer.writerow(["山梨酸钾", "山梨酸甲", "防腐剂", "添加剂", "", "常用防腐剂，适量使用安全"])
            writer.writerow(["抗坏血酸", "维C,维生素C", "抗氧化剂", "营养强化剂", "", "维生素C，对身体有益"])
            writer.writerow(["氯化钠", "食盐", "调味剂", "基础成分", "肾病", "高钠，肾病患者应控制"])
            writer.writerow(["葡萄糖", "葡糖", "甜味剂", "基础成分", "糖尿病,健身人群", "高血糖指数，应控制摄入"])

# 从本地数据库查询商品
def query_local_product(barcode):
    if not os.path.exists(PRODUCTS_CSV):
        return None
    
    with open(PRODUCTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['barcode'] == barcode:
                return row
    return None

# 从Open Food Facts API获取商品信息
def get_product_from_api(barcode):
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 1:
                product = data.get('product', {})
                product_name = product.get('product_name', '')
                ingredients_raw = product.get('ingredients_text', '')
                return {
                    'barcode': barcode,
                    'product_name': product_name,
                    'ingredients_raw': ingredients_raw,
                    'ingredients_parsed': parse_ingredients(ingredients_raw)
                }
    except Exception as e:
        print(f"API请求错误: {e}")
    return None

# 保存商品到本地数据库
def save_product_to_local(product):
    with open(PRODUCTS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            product['barcode'],
            product['product_name'],
            product['ingredients_raw'],
            product['ingredients_parsed']
        ])

# 解析配料表
def parse_ingredients(ingredients_raw):
    # 简单的配料解析逻辑
    if not ingredients_raw:
        return ""
    
    # 移除配料前缀
    ingredients_raw = ingredients_raw.replace("配料：", "").replace("配料:", "").replace("成分：", "").replace("成分:", "")
    
    # 按常见分隔符分割
    separators = ["、", ",", "，"]
    for sep in separators:
        if sep in ingredients_raw:
            ingredients = ingredients_raw.split(sep)
            return ",".join([ing.strip() for ing in ingredients])
    
    return ingredients_raw

# 标准化成分名称
def standardize_ingredient(name):
    with open(INGREDIENTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            aliases = row['aliases'].split(',')
            if name in aliases or name == row['standard_name']:
                return row['standard_name']
    return name

# 获取成分信息
def get_ingredient_info(name):
    standardized_name = standardize_ingredient(name)
    with open(INGREDIENTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['standard_name'] == standardized_name:
                return row
    return {
        'standard_name': standardized_name,
        'aliases': "",
        'role': "",
        'tag': "",
        'risk_for': "",
        'description': ""
    }

# 检查成分是否对特定健康身份有风险
def check_risk(ingredient_info, health_identity):
    risk_for = ingredient_info.get('risk_for', '')
    return health_identity in risk_for.split(',')

# 扫描条形码
def scan_barcode():
    cap = cv2.VideoCapture(0)
    start_time = cv2.getTickCount()
    found = False
    barcode_data = ""
    
    while not found:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 转换为灰度图
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 识别条形码
        barcodes = pyzbar.decode(gray)
        for barcode in barcodes:
            barcode_type = barcode.type
            if barcode_type == 'EAN13':
                barcode_data = barcode.data.decode('utf-8')
                if len(barcode_data) == 13:
                    found = True
                    break
        
        # 显示摄像头画面
        cv2.imshow('Barcode Scanner', frame)
        
        # 5秒超时
        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        if elapsed_time > 5:
            break
        
        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if found:
        return barcode_data
    else:
        return "请将条形码对准摄像头"

# OCR识别配料表
def ocr_ingredients(image):
    result = ocr.ocr(image, cls=True)
    text = ""
    for line in result:
        if line:
            for item in line:
                text += item[1][0] + "\n"
    
    # 提取配料部分
    lines = text.split('\n')
    ingredients_started = False
    ingredients_text = ""
    
    for line in lines:
        if not ingredients_started:
            if "配料" in line or "成分" in line:
                ingredients_started = True
                ingredients_text = line
        else:
            ingredients_text += line
    
    return parse_ingredients(ingredients_text)

# 处理扫描结果
def process_scan(health_identity):
    barcode = scan_barcode()
    if barcode == "请将条形码对准摄像头":
        return {
            "product_name": "",
            "ingredients_raw": "",
            "ingredients_table": []
        }
    
    # 查询本地数据库
    product = query_local_product(barcode)
    if not product:
        # 从API获取
        product = get_product_from_api(barcode)
        if product:
            save_product_to_local(product)
        else:
            return {
                "product_name": "",
                "ingredients_raw": "未找到商品信息",
                "ingredients_table": []
            }
    
    # 解析成分表
    ingredients_list = product['ingredients_parsed'].split(',') if product['ingredients_parsed'] else []
    ingredients_table = []
    
    for ingredient in ingredients_list:
        if ingredient:
            info = get_ingredient_info(ingredient)
            risk = check_risk(info, health_identity)
            health_tip = "⚠️ 身份需关注" if risk else "—"
            ingredients_table.append([
                info['standard_name'],
                info['tag'],
                info['role'],
                health_tip
            ])
    
    return {
        "product_name": product['product_name'],
        "ingredients_raw": product['ingredients_raw'],
        "ingredients_table": ingredients_table
    }

# 处理图片上传
def process_image(image, health_identity):
    ingredients_parsed = ocr_ingredients(image)
    ingredients_list = ingredients_parsed.split(',') if ingredients_parsed else []
    ingredients_table = []
    
    for ingredient in ingredients_list:
        if ingredient:
            info = get_ingredient_info(ingredient)
            risk = check_risk(info, health_identity)
            health_tip = "⚠️ 身份需关注" if risk else "—"
            ingredients_table.append([
                info['standard_name'],
                info['tag'],
                info['role'],
                health_tip
            ])
    
    return {
        "product_name": "",
        "ingredients_raw": ingredients_parsed,
        "ingredients_table": ingredients_table
    }

# 主函数
def main():
    # 初始化数据库
    init_database()
    
    # 创建Gradio界面
    with gr.Blocks(title="食品成分智能解读系统") as app:
        gr.Markdown("# 食品成分智能解读系统")
        
        with gr.Row():
            with gr.Column(scale=1):
                health_identity = gr.Dropdown(
                    choices=HEALTH_IDENTITIES,
                    label="健康身份",
                    value="普通"
                )
                scan_btn = gr.Button("扫描条形码")
                upload_btn = gr.UploadButton(
                    "上传包装照片",
                    file_types=["image"]
                )
            
            with gr.Column(scale=2):
                product_name = gr.Textbox(label="商品名称")
                ingredients_raw = gr.Textbox(label="配料表", lines=3)
                ingredients_table = gr.Dataframe(
                    headers=["成分名称", "成分标签", "作用", "健康提示"],
                    datatype=["str", "str", "str", "str"]
                )
        
        gr.Markdown("*数据本地处理，保障隐私与离线可用性*")
        gr.Markdown("*依据国家标准进行成分分析*")
        
        # 绑定事件
        def scan_handler(identity):
            result = process_scan(identity)
            return result["product_name"], result["ingredients_raw"], result["ingredients_table"]
        
        def upload_handler(image, identity):
            if image is None:
                return "", "", []
            result = process_image(image, identity)
            return result["product_name"], result["ingredients_raw"], result["ingredients_table"]
        
        scan_btn.click(
            fn=scan_handler,
            inputs=[health_identity],
            outputs=[product_name, ingredients_raw, ingredients_table]
        )
        
        upload_btn.upload(
            fn=upload_handler,
            inputs=[upload_btn, health_identity],
            outputs=[product_name, ingredients_raw, ingredients_table]
        )
    
    # 启动应用
    app.launch(share=False)

if __name__ == "__main__":
    main()

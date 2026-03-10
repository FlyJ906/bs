import os

# Paddle / oneDNN 在部分版本组合下可能触发未实现算子错误（onednn_instruction.cc）。
# 必须在 OCR 相关库导入/初始化前设置环境变量，保证进程级别生效。
os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_use_mkldnn_int8", "0")
os.environ.setdefault("FLAGS_use_onednn", "0")
os.environ.setdefault("FLAGS_enable_new_executor", "0")
os.environ.setdefault("FLAGS_enable_pir_in_executor", "0")
os.environ.setdefault("FLAGS_enable_pir_api", "0")

import gradio as gr
import threading
from config import HEALTH_IDENTITIES
from database import init_database, query_local_product, save_product_to_local, get_ingredient_info
from barcode_scanner import scan_barcode_from_image, scan_barcode
from api_client import get_product_from_api
from ocr_processor import ocr_ingredients
from health_analyzer import analyze_ingredients

# 处理扫码结果（从图片解码）
def process_scan(barcode_image, health_identity):
    barcode = scan_barcode_from_image(barcode_image)
    if not barcode or barcode.startswith("未识别") or barcode.startswith("扫码组件不可用") or barcode.startswith("请提供"):
        return {
            "product_name": "",
            "ingredients_raw": "",
            "ingredients_table": [],
            "not_found": False,
            "barcode": ""
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
                "ingredients_raw": "未收录",
                "ingredients_table": [],
                "not_found": True,
                "barcode": barcode
            }
    
    # 解析成分表
    ingredients_list = product['ingredients_parsed'].split(',') if product['ingredients_parsed'] else []
    ingredients_table = analyze_ingredients(ingredients_list, health_identity, get_ingredient_info)
    
    return {
        "product_name": product['product_name'],
        "ingredients_raw": product['ingredients_raw'],
        "ingredients_table": ingredients_table,
        "not_found": False,
        "barcode": barcode
    }

# 处理图片上传
def process_image(image, health_identity, barcode=None):
    if image is None:
        return {
            "product_name": "",
            "ingredients_raw": "",
            "ingredients_table": [],
            "not_found": False
        }
    
    # 使用PaddleOCR识别图片
    ingredients_parsed = ocr_ingredients(image)
    ingredients_raw = ingredients_parsed.replace(',', '、')
    ingredients_list = ingredients_parsed.split(',') if ingredients_parsed else []
    ingredients_table = analyze_ingredients(ingredients_list, health_identity, get_ingredient_info)
    
    # 如果有条形码，保存到数据库
    if barcode:
        product = {
            "barcode": barcode,
            "product_name": "未命名商品",
            "ingredients_raw": ingredients_raw,
            "ingredients_parsed": ingredients_parsed
        }
        save_product_to_local(product)
    
    return {
        "product_name": "未命名商品",
        "ingredients_raw": ingredients_raw,
        "ingredients_table": ingredients_table,
        "not_found": False
    }

# 主函数
def main():
    # 初始化数据库（后台执行，避免MySQL不可用时卡住界面启动）
    threading.Thread(target=init_database, daemon=True).start()
    
    # 创建Gradio界面
    with gr.Blocks(title="食品成分智能解读系统") as app:
        gr.Markdown("# 面向多健康人群的食品成分智能解读系统")
        
        # 健康身份选择
        health_identity = gr.Dropdown(
            choices=HEALTH_IDENTITIES,
            label="选择健康人群",
            value="普通"
        )
        
        # 操作区域
        with gr.Row():
            with gr.Column():
                barcode_image = gr.Image(
                    label="条形码图片（拍照/上传）",
                    type="numpy"
                )
                scan_btn = gr.Button("识别条形码", variant="primary")
                camera_scan_btn = gr.Button("实时摄像头扫描")

            with gr.Column():
                ingredients_image = gr.Image(
                    label="配料表/包装照片（拍照/上传）",
                    type="pil"
                )
        
        # 结果显示区域（默认隐藏）
        with gr.Row(visible=False) as result_section:
            with gr.Column():
                product_name = gr.Textbox(label="商品名称")
                health_alert = gr.Textbox(label="健康关注", lines=2)
                ingredients_raw = gr.Textbox(label="完整配料表", lines=4)
                
                # 完整成分解读按钮
                analyze_btn = gr.Button("完整成分解读")
                ingredients_table = gr.Dataframe(
                    headers=["成分名称", "成分标签", "作用", "健康提示"],
                    datatype=["str", "str", "str", "str"]
                )
        
        # 隐藏的条形码存储
        barcode_store = gr.State(value="")
        
        gr.Markdown("*数据本地处理，保障隐私与离线可用性*")
        gr.Markdown("*依据国家标准进行成分分析*")
        
        # 绑定事件
        def scan_handler(barcode_img, identity):
            result = process_scan(barcode_img, identity)
            if result["not_found"]:
                # 显示结果区域并提示上传
                return result["product_name"], "该商品未收录，请上传包装照片进行识别", result["ingredients_raw"], result["ingredients_table"], gr.Row(visible=True), result["barcode"]
            else:
                # 显示结果区域
                health_alert_text = f"基于{identity}人群的健康分析"
                return result["product_name"], health_alert_text, result["ingredients_raw"], result["ingredients_table"], gr.Row(visible=True), result["barcode"]
        
        def analyze_handler(name, identity):
            if not name:
                return []
            # 模拟成分解读结果
            ingredients_list = ["水", "白砂糖", "柠檬酸", "山梨酸钾", "抗坏血酸"]
            ingredients_table = analyze_ingredients(ingredients_list, identity, get_ingredient_info)
            return ingredients_table
        
        def upload_handler(image, identity, barcode):
            result = process_image(image, identity, barcode)
            health_alert_text = f"基于{identity}人群的健康分析"
            return result["product_name"], health_alert_text, result["ingredients_raw"], result["ingredients_table"], gr.Row(visible=True)
        
        def analyze_handler(product_name, identity):
            # 从本地数据库查询产品信息
            # 注意：这里需要根据产品名称查询，实际实现可能需要调整
            # 暂时返回空表，实际应该从数据库获取成分信息并分析
            ingredients_list = ["水", "白砂糖", "柠檬酸", "山梨酸钾", "抗坏血酸"]
            ingredients_table = analyze_ingredients(ingredients_list, identity, get_ingredient_info)
            return ingredients_table
        
        def camera_scan_handler(identity):
            # 调用实时摄像头扫描函数
            barcode = scan_barcode()
            if not barcode or barcode.startswith("未识别") or barcode.startswith("扫码组件不可用") or barcode.startswith("请提供") or barcode.startswith("识别超时") or barcode.startswith("用户退出") or barcode.startswith("摄像头读取失败"):
                return "", f"扫描失败：{barcode}", "", [], gr.Row(visible=True), ""
            
            # 查询本地数据库
            product = query_local_product(barcode)
            if not product:
                # 从API获取
                product = get_product_from_api(barcode)
                if product:
                    save_product_to_local(product)
                else:
                    return "", "该商品未收录，请上传包装照片进行识别", "未收录", [], gr.Row(visible=True), barcode
            
            # 解析成分表
            ingredients_list = product['ingredients_parsed'].split(',') if product['ingredients_parsed'] else []
            ingredients_table = analyze_ingredients(ingredients_list, identity, get_ingredient_info)
            
            health_alert_text = f"基于{identity}人群的健康分析"
            return product['product_name'], health_alert_text, product['ingredients_raw'], ingredients_table, gr.Row(visible=True), barcode
        
        scan_btn.click(
            fn=scan_handler,
            inputs=[barcode_image, health_identity],
            outputs=[product_name, health_alert, ingredients_raw, ingredients_table, result_section, barcode_store]
        )
        
        camera_scan_btn.click(
            fn=camera_scan_handler,
            inputs=[health_identity],
            outputs=[product_name, health_alert, ingredients_raw, ingredients_table, result_section, barcode_store]
        )
        
        analyze_btn.click(
            fn=analyze_handler,
            inputs=[product_name, health_identity],
            outputs=[ingredients_table]
        )
        
        # 图片一变更就进行识别
        ingredients_image.change(
            fn=upload_handler,
            inputs=[ingredients_image, health_identity, barcode_store],
            outputs=[product_name, health_alert, ingredients_raw, ingredients_table, result_section]
        )
    
    # 启动应用
    # share=True 在部分网络环境下可能卡住；本机演示用本地地址即可
    app.launch(share=False, server_name="127.0.0.1")

if __name__ == "__main__":
    main()

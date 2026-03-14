#!/usr/bin/env python3
"""
AI健康顾问模块
使用大型语言模型为用户提供个性化的健康建议
"""
import os
import time
import json
from typing import Dict, List, Optional

# 模拟AI API调用（实际使用时可替换为真实的AI API）
def get_ai_health_advice(product_name: str, ingredients: List[str], health_identity: str) -> str:
    """
    获取AI健康建议
    
    Args:
        product_name: 商品名称
        ingredients: 成分列表
        health_identity: 健康身份
    
    Returns:
        健康建议文本
    """
    # 模拟AI响应（实际实现时可调用OpenAI API等）
    # 这里使用预定义的响应模板
    
    # 健康身份对应的关注点
    health_focus = {
        "普通": "均衡饮食，多样化摄入",
        "糖尿病": "控制糖分和碳水化合物摄入",
        "肾病": "控制钠和蛋白质摄入",
        "孕妇": "关注营养均衡，避免有害物质",
        "健身人群": "关注蛋白质和营养补充"
    }
    
    focus = health_focus.get(health_identity, "均衡饮食")
    
    # 生成健康建议
    advice = f"# {product_name} - 健康分析\n\n"
    advice += f"## 健康身份：{health_identity}\n"
    advice += f"### 关注重点：{focus}\n\n"
    
    # 分析成分
    advice += "## 成分分析\n"
    if ingredients:
        advice += "- " + "\n- ".join(ingredients[:5])  # 只显示前5个成分
        if len(ingredients) > 5:
            advice += f"\n- ... 等{len(ingredients) - 5}种成分"
    else:
        advice += "- 无成分信息"
    
    # 基于健康身份给出建议
    advice += "\n\n## 健康建议\n"
    
    if health_identity == "糖尿病":
        advice += "- 建议控制食用量，注意成分中的糖分和碳水化合物含量\n"
        advice += "- 优先选择低糖、低GI值的食品\n"
        advice += "- 建议在医生或营养师的指导下食用"
    elif health_identity == "肾病":
        advice += "- 建议控制钠含量高的成分摄入\n"
        advice += "- 注意蛋白质的摄入量\n"
        advice += "- 建议在医生的指导下食用"
    elif health_identity == "孕妇":
        advice += "- 建议确保食品卫生安全\n"
        advice += "- 注意营养均衡，确保胎儿健康发育\n"
        advice += "- 避免食用可能含有有害物质的食品"
    elif health_identity == "健身人群":
        advice += "- 建议关注蛋白质含量，支持肌肉修复和生长\n"
        advice += "- 注意碳水化合物的摄入，提供训练能量\n"
        advice += "- 建议结合训练计划合理安排饮食"
    else:  # 普通
        advice += "- 建议保持均衡饮食，多样化摄入\n"
        advice += "- 注意控制总热量摄入\n"
        advice += "- 多摄入新鲜蔬菜水果"
    
    # 添加免责声明
    advice += "\n\n## 免责声明\n"
    advice += "本健康建议仅供参考，不构成医疗建议。\n"
    advice += "如有健康问题，请咨询专业医生或营养师。"
    
    return advice

def generate_detailed_analysis(product: Dict, health_identity: str) -> str:
    """
    生成详细的健康分析
    
    Args:
        product: 商品信息
        health_identity: 健康身份
    
    Returns:
        详细分析文本
    """
    product_name = product.get('product_name', '未命名商品')
    ingredients_raw = product.get('ingredients_raw', '')
    ingredients_parsed = product.get('ingredients_parsed', '')
    
    # 解析成分列表
    if ingredients_parsed:
        ingredients_list = [ing.strip() for ing in ingredients_parsed.split(',') if ing.strip()]
    else:
        ingredients_list = []
    
    # 获取AI健康建议
    advice = get_ai_health_advice(product_name, ingredients_list, health_identity)
    
    # 添加商品其他信息
    additional_info = "\n\n## 商品信息\n"
    if product.get('brand'):
        additional_info += f"- 品牌：{product['brand']}\n"
    if product.get('categories'):
        additional_info += f"- 分类：{product['categories']}\n"
    if product.get('serving_size'):
        additional_info += f"- 每份份量：{product['serving_size']}\n"
    if product.get('nutriscore'):
        additional_info += f"- 营养评分：{product['nutriscore']}\n"
    if product.get('api_source'):
        additional_info += f"- 数据来源：{product['api_source']}\n"
    
    advice += additional_info
    
    return advice

if __name__ == "__main__":
    # 测试AI健康顾问功能
    test_product = {
        "product_name": "测试饼干",
        "ingredients_parsed": "小麦粉,白砂糖,植物油,食盐,鸡蛋",
        "brand": "测试品牌",
        "categories": "饼干,零食",
        "serving_size": "30g",
        "nutriscore": "C"
    }
    
    for health_identity in ["普通", "糖尿病", "肾病", "孕妇", "健身人群"]:
        print(f"\n=== {health_identity}人群的健康建议 ===")
        advice = generate_detailed_analysis(test_product, health_identity)
        print(advice)
        print("=" * 50)

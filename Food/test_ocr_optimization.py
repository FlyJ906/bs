#!/usr/bin/env python3
"""
测试优化后的OCR识别效果
"""
import os
import sys
import time
import numpy as np
from PIL import Image

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import ocr_ingredients

def test_ocr_optimization():
    """
    测试优化后的OCR识别效果
    """
    print("开始测试优化后的OCR识别效果...")
    
    # 测试用的食品包装图片路径
    test_images = []
    
    # 检查是否有测试图片
    test_dir = os.path.join(os.path.dirname(__file__), "test_images")
    if os.path.exists(test_dir):
        for file in os.listdir(test_dir):
            if file.endswith(('.jpg', '.jpeg', '.png')):
                test_images.append(os.path.join(test_dir, file))
    
    if not test_images:
        print("未找到测试图片，请在 test_images 目录中添加食品包装图片")
        # 创建一个简单的测试图像
        create_test_image()
        test_images.append(os.path.join(test_dir, "test_ingredients.jpg"))
    
    print(f"找到 {len(test_images)} 张测试图片")
    
    total_time = 0
    success_count = 0
    
    # 测试每个图片的识别结果
    for i, image_path in enumerate(test_images):
        print(f"\n=== 测试图片 {i+1}: {os.path.basename(image_path)} ===")
        
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 记录识别开始时间
            start_time = time.time()
            
            # 调用OCR识别
            result = ocr_ingredients(image)
            
            # 计算识别时间
            recognition_time = time.time() - start_time
            total_time += recognition_time
            
            print(f"识别时间: {recognition_time:.2f}秒")
            print(f"识别结果: {result}")
            
            # 分析识别结果
            if "OCR识别失败" in result:
                print("❌ 识别失败")
            else:
                print("✅ 识别成功")
                success_count += 1
                # 检查识别结果的质量
                if len(result) < 5:
                    print("⚠️  识别结果过短，可能不完整")
                elif "营养成分表" in result:
                    print("⚠️  识别结果包含营养成分表，可能提取错误")
        except Exception as e:
            print(f"❌ 处理图片时出错: {e}")
    
    # 计算统计信息
    if test_images:
        avg_time = total_time / len(test_images)
        success_rate = (success_count / len(test_images)) * 100
        
        print(f"\n=== 测试结果统计 ===")
        print(f"测试图片数量: {len(test_images)}")
        print(f"成功识别数量: {success_count}")
        print(f"识别成功率: {success_rate:.1f}%")
        print(f"平均识别时间: {avg_time:.2f}秒")
    
    print("\nOCR识别优化测试完成")

def create_test_image():
    """
    创建一个简单的测试图像
    """
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建测试图片目录
    test_dir = os.path.join(os.path.dirname(__file__), "test_images")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 创建一个简单的测试图像
    width, height = 800, 600
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    # 尝试加载中文字体
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("SimHei", 36)
    except:
        # 如果没有中文字体，使用默认字体
        font = ImageFont.load_default()
    
    # 绘制测试文本
    text = "配料表：水、果葡糖浆、红心番石榴浆、苹果浓缩汁、紫胡萝卜浓缩汁"
    draw.text((50, 200), text, fill='white', font=font)
    
    # 保存测试图像
    test_image_path = os.path.join(test_dir, "test_ingredients.jpg")
    image.save(test_image_path)
    print(f"创建了测试图像: {test_image_path}")

if __name__ == "__main__":
    # 测试优化后的OCR识别效果
    test_ocr_optimization()

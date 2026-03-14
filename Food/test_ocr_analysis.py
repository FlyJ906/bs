#!/usr/bin/env python3
"""
分析当前OCR识别问题的测试脚本
"""
import os
import sys
import numpy as np
from PIL import Image

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ocr_processor import ocr_ingredients

def analyze_ocr_issues():
    """
    分析OCR识别问题
    """
    print("开始分析OCR识别问题...")
    
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
        return
    
    print(f"找到 {len(test_images)} 张测试图片")
    
    # 分析每个图片的识别结果
    for i, image_path in enumerate(test_images):
        print(f"\n=== 测试图片 {i+1}: {os.path.basename(image_path)} ===")
        
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 调用OCR识别
            result = ocr_ingredients(image)
            
            print(f"识别结果: {result}")
            
            # 分析识别结果
            if "OCR识别失败" in result:
                print("❌ 识别失败")
            else:
                print("✅ 识别成功")
                # 检查识别结果的质量
                if len(result) < 5:
                    print("⚠️  识别结果过短，可能不完整")
                elif "营养成分表" in result:
                    print("⚠️  识别结果包含营养成分表，可能提取错误")
        except Exception as e:
            print(f"❌ 处理图片时出错: {e}")
    
    print("\nOCR识别问题分析完成")

def test_image_preprocessing():
    """
    测试图像预处理对识别效果的影响
    """
    print("\n=== 测试图像预处理 ===")
    
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
        return
    
    print("测试不同图像处理方法对识别效果的影响...")
    
    for image_path in test_images[:2]:  # 只测试前2张图片
        print(f"\n测试图片: {os.path.basename(image_path)}")
        
        try:
            # 原始图片
            image = Image.open(image_path)
            print("原始图片识别结果:")
            result_original = ocr_ingredients(image)
            print(result_original)
            
            # 灰度处理
            print("\n灰度处理后识别结果:")
            gray_image = image.convert('L')
            result_gray = ocr_ingredients(gray_image)
            print(result_gray)
            
            # 二值化处理
            print("\n二值化处理后识别结果:")
            threshold = 128
            binary_image = gray_image.point(lambda x: 255 if x > threshold else 0, '1')
            result_binary = ocr_ingredients(binary_image)
            print(result_binary)
            
        except Exception as e:
            print(f"处理图片时出错: {e}")
    
    print("\n图像预处理测试完成")

if __name__ == "__main__":
    # 创建测试图片目录
    test_dir = os.path.join(os.path.dirname(__file__), "test_images")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        print(f"创建了测试图片目录: {test_dir}")
        print("请在该目录中添加食品包装图片进行测试")
    
    # 分析OCR识别问题
    analyze_ocr_issues()
    
    # 测试图像预处理
    test_image_preprocessing()

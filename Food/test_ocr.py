import os
import sys
from PIL import Image

# 确保使用与主应用相同的环境变量设置
os.environ.setdefault("FLAGS_use_mkldnn", "0")
os.environ.setdefault("FLAGS_use_mkldnn_int8", "0")
os.environ.setdefault("FLAGS_use_onednn", "0")
os.environ.setdefault("FLAGS_enable_new_executor", "0")
os.environ.setdefault("FLAGS_enable_pir_in_executor", "0")
os.environ.setdefault("FLAGS_enable_pir_api", "0")

try:
    # 导入OCR处理器
    from ocr_processor import ocr_ingredients
    print("✓ 成功导入ocr_processor模块")
    
    # 测试OCR功能
    print("测试OCR功能...")
    
    # 测试1: 检查PaddleOCR是否可以初始化
    print("\n测试1: 初始化PaddleOCR")
    try:
        from ocr_processor import _get_ocr
        ocr = _get_ocr()
        print("✓ PaddleOCR初始化成功")
    except Exception as e:
        print(f"✗ PaddleOCR初始化失败: {e}")
    
    # 测试2: 测试识别功能（使用示例图片路径）
    print("\n测试2: 测试OCR识别功能")
    try:
        # 这里使用一个示例图片路径，你可以替换为实际的测试图片
        test_image_path = "test_ingredients.jpg"
        if os.path.exists(test_image_path):
            image = Image.open(test_image_path)
            result = ocr_ingredients(image)
            print(f"✓ OCR识别成功，结果: {result}")
        else:
            print(f"⚠ 测试图片 {test_image_path} 不存在，跳过识别测试")
    except Exception as e:
        print(f"✗ OCR识别失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 测试不同类型的输入
    print("\n测试3: 测试不同类型的输入")
    try:
        # 测试字符串路径输入
        test_image_path = "test_ingredients.jpg"
        if os.path.exists(test_image_path):
            result = ocr_ingredients(test_image_path)
            print(f"✓ 字符串路径输入测试成功: {result}")
        else:
            print(f"⚠ 测试图片 {test_image_path} 不存在，跳过路径输入测试")
    except Exception as e:
        print(f"✗ 路径输入测试失败: {e}")
        import traceback
        traceback.print_exc()
        
    print("\nOCR功能测试完成!")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ 测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

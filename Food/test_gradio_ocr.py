import os
import sys
from PIL import Image
import numpy as np

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
    print("测试Gradio上传图片的OCR功能...")
    
    # 测试1: 测试PIL Image输入（模拟Gradio的type="pil"）
    print("\n测试1: 测试PIL Image输入")
    try:
        # 创建一个简单的测试图片
        test_image = Image.new('RGB', (400, 200), color='white')
        # 这里我们只是测试输入类型，不测试实际识别
        result = ocr_ingredients(test_image)
        print(f"✓ PIL Image输入测试成功")
        print(f"  识别结果: {result}")
    except Exception as e:
        print(f"✗ PIL Image输入测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 测试numpy数组输入
    print("\n测试2: 测试numpy数组输入")
    try:
        # 创建一个简单的numpy数组图片
        test_array = np.zeros((200, 400, 3), dtype=np.uint8)
        test_array[:] = 255  # 白色背景
        result = ocr_ingredients(test_array)
        print(f"✓ numpy数组输入测试成功")
        print(f"  识别结果: {result}")
    except Exception as e:
        print(f"✗ numpy数组输入测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 测试字典输入（模拟Gradio的上传格式）
    print("\n测试3: 测试字典输入")
    try:
        # 创建一个模拟的Gradio上传对象
        test_dict = {
            "name": "test_ingredients.jpg",
            "data": np.zeros((200, 400, 3), dtype=np.uint8)
        }
        # 注意：这里我们只是测试输入类型，实际中Gradio的格式可能不同
        result = ocr_ingredients(test_dict)
        print(f"✓ 字典输入测试成功")
        print(f"  识别结果: {result}")
    except Exception as e:
        print(f"✗ 字典输入测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nGradio上传图片OCR功能测试完成!")
    
except ImportError as e:
    print(f"✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"✗ 测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

def _decode_ean13_from_bgr(frame) -> str:
    if frame is None:
        return ""
    
    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    
    # 应用高斯模糊，减少噪声
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 应用阈值处理，增强对比度
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    try:
        # 尝试不同的配置来提高识别率
        barcodes = pyzbar.decode(gray)
    except Exception as e:
        # Windows 常见：缺 zbar 依赖导致 pyzbar 无法工作
        return f"扫码组件不可用：{e}"

    for barcode in barcodes:
        # 支持多种条形码类型，不仅仅是EAN13
        data = barcode.data.decode("utf-8", errors="ignore")
        # 检查是否为有效的条形码（13位数字）
        if len(data) == 13 and data.isdigit():
            return data
    return ""

# 从图像识别条形码（推荐：用于Gradio的webcam/upload）
def scan_barcode_from_image(image) -> str:
    """
    image: Gradio Image(type="numpy") 返回的 numpy(BGR/RGB均可能) 或 PIL Image
    """
    if image is None:
        return "请提供条形码图片"

    if isinstance(image, np.ndarray):
        frame = image
        # gr.Image(type="numpy") 通常是 RGB；OpenCV 默认按 BGR 处理，灰度转换对RGB/BGR都可用
        code = _decode_ean13_from_bgr(frame)
        return code if code else "未识别到EAN-13条形码"

    return "不支持的图片类型"

# 实时摄像头扫描（基于pyzbar优化版本）
def scan_barcode(timeout_seconds: float = None):
    # 快速初始化摄像头
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 使用DSHOW后端，提高Windows上的启动速度
    
    # 设置摄像头分辨率，平衡速度和识别率
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)  # 设置帧率
    
    # 预热摄像头
    for i in range(3):
        cap.read()
    
    last_error = ""
    
    # 预计算扫描区域
    ret, frame = cap.read()
    if not ret:
        last_error = "摄像头读取失败"
        cap.release()
        return last_error
    
    height, width = frame.shape[:2]
    center_x, center_y = width // 2, height // 2
    box_size = min(width, height) // 2

    while True:
        ret, frame = cap.read()
        if not ret:
            last_error = "摄像头读取失败"
            break

        # 翻转摄像头画面，使操作更直观
        frame = cv2.flip(frame, 1)

        # 绘制扫描区域引导框
        cv2.rectangle(frame, 
                      (center_x - box_size // 2, center_y - box_size // 2),
                      (center_x + box_size // 2, center_y + box_size // 2),
                      (0, 255, 0), 2)
        cv2.putText(frame, "请将条形码对准中心框", 
                    (center_x - box_size // 2, center_y - box_size // 2 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "按 'q' 键退出", 
                    (50, height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 只识别中心区域的条形码，提高识别速度
        roi = frame[center_y - box_size // 2:center_y + box_size // 2, 
                    center_x - box_size // 2:center_x + box_size // 2]
        code = _decode_ean13_from_bgr(roi)

        if code and not code.startswith("扫码组件不可用"):
            # 识别成功，在画面上显示条形码
            cv2.putText(frame, f"识别成功: {code}", 
                        (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Barcode Scanner", frame)
            cv2.waitKey(1000)  # 显示成功信息1秒
            cap.release()
            cv2.destroyAllWindows()
            return code
        if code.startswith("扫码组件不可用"):
            last_error = code
            break

        cv2.imshow("Barcode Scanner", frame)

        # 只检查用户输入，不设置超时
        if cv2.waitKey(1) & 0xFF == ord("q"):
            last_error = "用户退出"
            break

    cap.release()
    cv2.destroyAllWindows()
    return last_error or "请将条形码对准摄像头"

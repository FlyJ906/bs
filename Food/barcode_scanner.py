import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar

def _decode_ean13_from_bgr(frame) -> str:
    if frame is None:
        return ""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if frame.ndim == 3 else frame
    try:
        barcodes = pyzbar.decode(gray)
    except Exception as e:
        # Windows 常见：缺 zbar 依赖导致 pyzbar 无法工作
        return f"扫码组件不可用：{e}"

    for barcode in barcodes:
        if barcode.type == "EAN13":
            data = barcode.data.decode("utf-8", errors="ignore")
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

# 旧版：直接打开摄像头窗口扫描（仅本机桌面场景可用）
def scan_barcode(timeout_seconds: float = 8.0):
    cap = cv2.VideoCapture(0)
    start_time = cv2.getTickCount()
    last_error = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            last_error = "摄像头读取失败"
            break

        code = _decode_ean13_from_bgr(frame)
        if code and not code.startswith("扫码组件不可用"):
            cap.release()
            cv2.destroyAllWindows()
            return code
        if code.startswith("扫码组件不可用"):
            last_error = code
            break

        cv2.imshow("Barcode Scanner", frame)

        elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
        if elapsed_time > timeout_seconds:
            last_error = "识别超时"
            break
        if cv2.waitKey(1) & 0xFF == ord("q"):
            last_error = "用户退出"
            break

    cap.release()
    cv2.destroyAllWindows()
    return last_error or "请将条形码对准摄像头"

## Food 成分解读系统（本机运行）

### 环境说明（重要）

本项目依赖 `paddlepaddle`（导入名为 `paddle`）进行 OCR。你已在 **conda/Anaconda** 环境中配置成功，因此建议统一用 **conda 的 python** 运行，避免用 `.venv` 导致 `No module named 'paddle'`。

### 安装依赖

在 `D:\毕设\Food` 目录执行：

```powershell
pip install -r requirements.txt
```

### 启动

```powershell
python app.py
```

启动后按终端输出打开本地地址（通常是 `http://127.0.0.1:7860`）。

---

## OCR 环境配置说明

### 方案选择

本项目支持三种 OCR 引擎，可根据系统配置选择：

| OCR 引擎 | 内存占用 | 准确度 | 安装复杂度 |
|---------|---------|--------|-----------|
| PaddleOCR | 2-4GB | 高 | 中 |
| Tesseract OCR | <500MB | 中 | 低 |
| EasyOCR | 1-2GB | 高 | 低 |

### 方案1: PaddleOCR（默认）

**系统要求：**
- 内存：建议 8GB 以上
- 虚拟内存（页面文件）：建议设置 8GB 或更多

**安装：**
```powershell
pip install paddlepaddle paddleocr
```

**常见问题 - MKL 内存错误：**

如果出现以下错误：
```
INTEL MKL ERROR: 页面文件太小，无法完成操作。
Intel MKL FATAL ERROR: Cannot load mkl_intel_thread.1.dll.
```

**解决方案：**
1. **增加 Windows 虚拟内存（页面文件）：**
   - 右键"此电脑" -> 属性 -> 高级系统设置
   - 性能 -> 设置 -> 高级 -> 虚拟内存 -> 更改
   - 取消"自动管理"，选择系统盘
   - 设置"自定义大小"：建议初始大小 8192MB，最大大小 16384MB
   - 点击"设置"按钮，然后确定并重启电脑

2. **使用 Tesseract OCR 作为备选**（见方案2）

### 方案2: Tesseract OCR（轻量备选）

适合内存较小的系统，或者 PaddleOCR 出现 MKL 错误时使用。

**安装步骤：**

1. 下载安装 Tesseract 软件：
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载 Windows 安装包（如 tesseract-ocr-w64-setup-5.x.x.exe）
   - 安装时勾选"Additional language data"中的中文语言包（chi_sim）

2. 安装 Python 包：
```powershell
pip install pytesseract
```

3. 配置环境变量（可选）：
   - 将 Tesseract 安装目录添加到 PATH
   - 或在代码中指定：`pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'`

### 方案3: EasyOCR（中等备选）

**安装：**
```powershell
pip install easyocr
```

首次运行会自动下载模型文件（约 500MB）。

---

## 常见问题

### 1. 上传后提示 JSON 错误 / Internal Server Error
- 请查看终端 Traceback。最常见原因是用错 python 环境导致 `paddle` 缺失，或数据库游标参数错误。

### 2. MySQL 中中文显示乱码（如变成"ɰ"）
- 这是早期用错误字符集连接写入导致的历史数据问题。
- 处理方式：删除并重建数据库后重新运行 `python app.py` 初始化数据。
  - 例如在 MySQL 中执行：`DROP DATABASE food_analysis;`

### 3. OCR 识别失败：系统内存不足(MKL错误)
- 参考 [方案1](#方案1-paddleocr默认) 中的 MKL 错误解决方案
- 或切换到 Tesseract OCR / EasyOCR

### 4. PaddleOCR 模型下载失败
- 检查网络连接
- 首次运行需要下载模型文件（约 200MB）
- 可以手动下载模型放到 `~/.paddleocr/` 目录

### 5. Tesseract 中文识别效果差
- 确保安装了中文语言包（chi_sim）
- 尝试使用 PaddleOCR 或 EasyOCR 获得更好的中文识别效果

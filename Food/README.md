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

### 常见问题

- **上传后提示 JSON 错误 / Internal Server Error**
  - 请查看终端 Traceback。最常见原因是用错 python 环境导致 `paddle` 缺失，或数据库游标参数错误。

- **MySQL 中中文显示乱码（如变成“��ɰ��”）**
  - 这是早期用错误字符集连接写入导致的历史数据问题。
  - 处理方式：删除并重建数据库后重新运行 `python app.py` 初始化数据。
    - 例如在 MySQL 中执行：`DROP DATABASE food_analysis;`


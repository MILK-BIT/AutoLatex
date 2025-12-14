## 启动
```powershell
cd "根目录"
# 如需自定义端口/设备可加环境变量，否则用默认
# $env:OCR_CHECKPOINT_DIR="checkpoints\mixtex_lora_10k_final_tuned\epoch_2"
# $env:OCR_DEVICE="cuda"  # 或 cpu
uvicorn ocr_api:app --host 0.0.0.0 --port 8001
```

## 识别图片

### 方法1：使用 curl.exe（推荐）
```powershell
# 基本用法（使用默认参数：max_length=512, enhance=true）
curl.exe -X POST "http://127.0.0.1:8001/predict" `
  -H "accept: application/json" `
  -F "file=@微信图片_20251212135211_62_76.png;type=image/png"

# 自定义参数（推荐用于复杂公式）
# max_length: 生成的最大长度（默认512，复杂公式建议1024或更大）
# enhance: 是否启用图片增强（true/false，默认true）
curl.exe -X POST "http://127.0.0.1:8001/predict?max_length=1024&enhance=true" `
  -H "accept: application/json" `
  -F "file=@微信图片_20251212135211_62_76.png;type=image/png"

# 使用完整路径
curl.exe -X POST "http://127.0.0.1:8001/predict?max_length=1024&enhance=true" `
  -H "accept: application/json" `
  -F "file=@C:\Users\Ding\Desktop\NLP\AutoLatex\微信图片_20251212135211_62_76.png;type=image/png"
```

### 方法2：使用 Python 测试脚本（最简单）
```powershell
# 使用默认参数
python test_ocr_simple.py

# 指定图片和参数
python test_ocr_simple.py "微信图片_20251212135211_62_76.png" 1024 true
```

### 方法3：使用 PowerShell（需要 PowerShell 7+）
```powershell
# 基本用法
$filePath = "微信图片_20251212135211_62_76.png"
$uri = "http://127.0.0.1:8001/predict"
$form = @{
    file = Get-Item -Path $filePath
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form

# 带参数
$uri = "http://127.0.0.1:8001/predict?max_length=1024&enhance=true"
$form = @{
    file = Get-Item -Path $filePath
}
Invoke-RestMethod -Uri $uri -Method Post -Form $form
```

## API 参数说明

- **max_length** (查询参数，可选): 生成 LaTeX 代码的最大长度
  - 默认值: 512
  - 简单公式: 256-512
  - 复杂公式: 1024 或更大
  
- **enhance** (查询参数，可选): 是否启用图片增强预处理
  - 默认值: true
  - true: 自动检测并增强低质量图片（对比度、锐度、尺寸优化）
  - false: 禁用增强，直接使用原始图片

返回 JSON 中的 `latex` 字段即为识别结果。 



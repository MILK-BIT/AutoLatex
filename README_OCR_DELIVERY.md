# MixTex OCR 交付说明

本文档说明如何部署和使用 MixTex OCR 模型、API 服务和 CrewAI Tool。

## 📦 交付内容

1. **模型文件**：训练好的 MixTex 微调模型 checkpoint
2. **API 服务**：`ocr_api.py` - FastAPI 服务，提供 HTTP 接口
3. **CrewAI Tool**：`src/autolatex/tools/mixtex_ocr_tool.py` - 可在 CrewAI 中使用的工具类
4. **模型封装**：`ocr_model_wrapper.py` - 模型加载和推理封装

## 🚀 快速开始

### 方式一：仅使用 Tool（推荐，如果 API 服务已部署）

如果合作者只需要在 CrewAI 中使用 Tool，且 API 服务已由你部署：

```bash
# 安装 Tool 依赖
pip install crewai-tools>=1.5.0 "crewai[tools]>=1.5.0" requests>=2.31.0 pydantic>=2.0.0

# 使用 Tool
from autolatex.tools.mixtex_ocr_tool import MixTexOCRTool

tool = MixTexOCRTool()  # 默认连接 http://localhost:8000/predict
# 或指定 API 地址
tool = MixTexOCRTool(api_url="http://your-api-server:8000/predict")
```

### 方式二：部署 API 服务

如果合作者需要自己部署 API 服务：

#### 1. 安装依赖

```bash
# 安装 API 服务依赖
pip install fastapi>=0.123.0 uvicorn[standard]>=0.24.0 python-multipart>=0.0.20 Pillow>=10.0.0

# 安装模型推理依赖（根据硬件选择）
# CPU 版本：
pip install torch>=2.0.0 transformers>=4.44.0 accelerate>=0.33.0 peft>=0.12.0 numpy>=1.24.0

# GPU 版本（CUDA 11.8）：
pip install torch>=2.0.0+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install transformers>=4.44.0 accelerate>=0.33.0 peft>=0.12.0 numpy>=1.24.0
```

#### 2. 配置环境变量

```bash
# 设置模型 checkpoint 路径（必需）
export OCR_CHECKPOINT_DIR="checkpoints/mixtex_lora_10k_final_tuned/epoch_2"

# 设置基础模型路径（如果是 LoRA checkpoint，必需）
export OCR_BASE_MODEL_PATH="MixTex/ZhEn-Latex-OCR"

# 设置设备（可选，默认自动检测）
export OCR_DEVICE="cuda"  # 或 "cpu"

# 设置 API 服务端口（可选，默认 8000）
export OCR_API_PORT=8000

# 设置 API 服务主机（可选，默认 0.0.0.0）
export OCR_API_HOST="0.0.0.0"
```

#### 3. 启动 API 服务

```bash
python ocr_api.py
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 预测接口：http://localhost:8000/predict

#### 4. 使用 Tool

```python
from autolatex.tools.mixtex_ocr_tool import MixTexOCRTool

# 使用本地 API
tool = MixTexOCRTool()

# 或使用环境变量配置
import os
os.environ["MIXTEX_OCR_API_URL"] = "http://localhost:8000/predict"
tool = MixTexOCRTool()
```

## 📋 依赖说明

### 最小依赖（仅 Tool）

如果只需要使用 Tool 调用远程 API：

```
crewai-tools>=1.5.0
crewai[tools]>=1.5.0
requests>=2.31.0
pydantic>=2.0.0
```

### API 服务依赖

如果需要运行 API 服务：

```
fastapi>=0.123.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.20
Pillow>=10.0.0
```

### 模型推理依赖

如果需要加载和运行模型：

```
torch>=2.0.0              # 根据硬件选择 CPU 或 GPU 版本
transformers>=4.44.0
accelerate>=0.33.0
peft>=0.12.0
numpy>=1.24.0
```

## 🔧 配置说明

### API 服务配置

通过环境变量配置 API 服务：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `OCR_CHECKPOINT_DIR` | 模型 checkpoint 目录路径 | `checkpoints/mixtex_lora_10k_final_tuned/epoch_2` |
| `OCR_BASE_MODEL_PATH` | 基础模型路径（LoRA 必需） | `MixTex/ZhEn-Latex-OCR` |
| `OCR_DEVICE` | 设备类型（cuda/cpu） | 自动检测 |
| `OCR_API_PORT` | API 服务端口 | `8000` |
| `OCR_API_HOST` | API 服务主机 | `0.0.0.0` |

### Tool 配置

通过环境变量或参数配置 Tool：

```python
# 方式1：通过环境变量
import os
os.environ["MIXTEX_OCR_API_URL"] = "http://your-api:8000/predict"
tool = MixTexOCRTool()

# 方式2：通过参数
tool = MixTexOCRTool(api_url="http://your-api:8000/predict")
```

## 📝 API 接口说明

### POST /predict

上传图片进行 OCR 识别。

**请求参数：**
- `file`: 图片文件（multipart/form-data）
- `max_length`: 生成的最大长度（默认 512）
- `enhance`: 是否启用图片增强（默认 true）

**响应格式：**
```json
{
  "latex": "识别出的 LaTeX 代码",
  "success": true,
  "message": "识别成功"
}
```

### GET /health

健康检查接口。

**响应格式：**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## 🧪 测试

### 测试 API 服务

```bash
# 使用测试脚本
python test_ocr_api.py 1.png

# 或使用 curl
curl -X POST "http://localhost:8000/predict" \
  -F "file=@1.png" \
  -F "max_length=512" \
  -F "enhance=true"
```

### 测试 Tool

```bash
# 使用简单测试脚本
python test_mixtex_tool_simple.py 1.png

# 或使用完整测试套件
python tests/tools/test_mixtex_ocr_tool.py
```

## 📦 文件结构

```
.
├── ocr_api.py                    # FastAPI 服务
├── ocr_model_wrapper.py          # 模型封装
├── src/autolatex/tools/
│   └── mixtex_ocr_tool.py        # CrewAI Tool
├── requirements_ocr_delivery.txt  # 依赖文件
├── README_OCR_DELIVERY.md        # 本文档
└── checkpoints/                  # 模型 checkpoint 目录
    └── mixtex_lora_10k_final_tuned/
        └── epoch_2/
```

## ❓ 常见问题

### Q: 如何选择 PyTorch 版本？

A: 
- **CPU 版本**：`pip install torch>=2.0.0`
- **GPU (CUDA 11.8)**：`pip install torch>=2.0.0+cu118 --index-url https://download.pytorch.org/whl/cu118`
- **GPU (CUDA 12.1)**：`pip install torch>=2.0.0+cu121 --index-url https://download.pytorch.org/whl/cu121`

### Q: API 服务启动失败？

A: 检查：
1. 模型 checkpoint 路径是否正确
2. 如果是 LoRA checkpoint，是否设置了 `OCR_BASE_MODEL_PATH`
3. 设备是否可用（GPU 需要安装对应版本的 PyTorch）

### Q: Tool 调用失败？

A: 检查：
1. API 服务是否正在运行
2. API 地址是否正确（默认 `http://localhost:8000/predict`）
3. 图片路径是否存在
4. 网络连接是否正常

## 📞 支持

如有问题，请联系项目维护者。


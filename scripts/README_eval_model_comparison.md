# 模型评估对比脚本使用说明

## 功能说明

这个脚本用于对比评估本地微调模型和DeepSeek API在LaTeX OCR任务上的表现。

主要功能：
1. 从 `linxy/LaTeX_OCR` 数据集的 `test` split 中随机选择指定数量的样本（默认50个）
2. 下载评估用的图片到 `evaluation_results/eval_images/` 目录
3. 使用本地微调模型进行预测，记录处理时间
4. 使用DeepSeek API进行预测，记录处理时间和成本
5. 将每个模型的预测结果保存到单独的文件中（`evaluation_results/predictions/`）
6. 生成CSV格式的对比表格，方便导入Excel进行人工评估

## 环境准备

1. 确保已安装所需依赖：
```bash
pip install torch transformers peft datasets pillow requests python-dotenv tqdm
```

2. 在项目根目录创建 `.env` 文件（如果不存在），添加DeepSeek API密钥：
```
DEEPSEEK_API_KEY=your_api_key_here
```

## 使用方法

### 基本用法（仅评估微调模型）

**PowerShell (Windows):**
```powershell
python scripts/eval_model_comparison.py --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1
```

**Bash/Linux/Mac:**
```bash
python scripts/eval_model_comparison.py \
    --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1
```

### 包含基线模型评估（推荐）

**PowerShell (Windows):**
```powershell
python scripts/eval_model_comparison.py --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1 --include-baseline
```

**Bash/Linux/Mac:**
```bash
python scripts/eval_model_comparison.py \
    --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1 \
    --include-baseline
```

### 完整参数示例

**PowerShell (Windows):**
```powershell
python scripts/eval_model_comparison.py --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1 --base-model-path MixTex/ZhEn-Latex-OCR --subset-name small --num-samples 50 --seed 42 --device cpu
```

**Bash/Linux/Mac:**
```bash
python scripts/eval_model_comparison.py \
    --checkpoint-dir checkpoints/mixtex_lora_10k_shuffled/epoch_1 \
    --base-model-path MixTex/ZhEn-Latex-OCR \
    --subset-name small \
    --num-samples 50 \
    --seed 42 \
    --device cpu
```

### 参数说明

- `--checkpoint-dir` (必需): 微调后的模型checkpoint目录路径
- `--base-model-path` (可选): LoRA模型的基础模型路径。如果checkpoint是LoRA适配器且未指定此参数，将默认使用 `MixTex/ZhEn-Latex-OCR`
- `--include-baseline` (可选): 是否包含基线模型（原始MixTex）的评估。使用此选项可以对比微调前后的效果
- `--baseline-model-path` (可选): 基线模型路径，默认为 `MixTex/ZhEn-Latex-OCR`
- `--subset-name` (可选): 数据集子集名称，默认为 `small`。可选值：`small`, `full`, `synthetic_handwrite`, `human_handwrite`, `human_handwrite_print`
- `--num-samples` (可选): 随机选择的样本数量，默认为 50
- `--seed` (可选): 随机种子，默认为 42。使用相同的种子可以确保每次选择相同的样本
- `--device` (可选): 运行设备，默认为 `cpu`。如果有GPU，可以设置为 `cuda`

## 输出结果

脚本运行后会在项目根目录下创建 `evaluation_results/` 目录，包含以下内容：

```
evaluation_results/
├── eval_images/              # 评估用的图片
│   ├── test_00001.png
│   ├── test_00002.png
│   └── ...
├── predictions/              # 每个模型的预测结果
│   ├── test_00001_local_model.txt
│   ├── test_00001_deepseek_api.txt
│   ├── test_00002_local_model.txt
│   └── ...
├── evaluation_results.json   # 完整的评估结果（JSON格式）
└── evaluation_results.csv    # 对比表格（CSV格式，可导入Excel）
```

### CSV表格格式

CSV文件包含以下列（如果使用 `--include-baseline`，会额外包含基线模型的列）：
- `Image ID`: 图片ID
- `Ground Truth LaTeX`: 真实标签
- `基线模型-预测` (如果使用 `--include-baseline`): 原始MixTex模型的预测结果
- `基线模型-质量(1-5)` (如果使用 `--include-baseline`): **需要人工填写**
- `基线模型-耗时(秒)` (如果使用 `--include-baseline`): 基线模型处理时间
- `微调模型-预测`: 微调后模型的预测结果
- `DeepSeek-预测`: DeepSeek API的预测结果（如果API调用成功）
- `微调模型-质量(1-5)`: **需要人工填写**（根据评估标准.md中的5分制评分）
- `DeepSeek-质量(1-5)`: **需要人工填写**
- `微调模型-耗时(秒)`: 微调模型处理时间
- `DeepSeek-耗时(秒)`: DeepSeek API处理时间
- `备注`: **需要人工填写**（记录评估时的备注信息）

## 人工评估流程

1. 打开 `evaluation_results/evaluation_results.csv` 文件（可以用Excel打开）
2. 对于每一行（每个样本）：
   - 查看 `Ground Truth LaTeX`、`本地模型-预测`、`DeepSeek-预测` 三个结果
   - 根据 `评估标准.md` 中的5分制评分标准，为两个模型分别打分
   - 填写 `备注` 列，记录评估时的关键信息（如"修正了r/T错误"、"结构崩溃"等）
3. 完成所有样本的评估后，可以计算统计指标：
   - 计算两个模型获得5分和4分的样本占比
   - 对比平均处理时间
   - 对比总成本（DeepSeek API有成本，本地模型为$0）

## 注意事项

1. **DeepSeek API调用**: 
   - 脚本会尝试使用DeepSeek Chat API的vision模式（图片输入）
   - 如果API返回400错误，说明可能不支持图片输入，脚本会记录失败并继续运行
   - 如果API返回401错误，说明API密钥无效
   - 如果API返回402错误，说明账户余额不足
   - 如果API返回429错误，说明请求频率过高
   - 请确保您的API密钥有效且有足够的额度

2. **基线模型评估**: 
   - 使用 `--include-baseline` 选项可以同时评估原始MixTex模型，便于对比微调效果
   - 基线模型会从HuggingFace下载（如果本地没有缓存），首次运行可能需要一些时间

2. **成本估算**: 脚本中的成本估算基于假设的定价（每1000 tokens约0.0014元），实际成本请参考DeepSeek官方定价。

3. **网络连接**: 脚本需要从HuggingFace下载数据集，请确保网络连接正常。

4. **设备选择**: 如果有GPU，建议使用 `--device cuda` 以加快本地模型的推理速度。

5. **随机种子**: 使用相同的 `--seed` 参数可以确保每次运行选择相同的样本，便于对比不同模型的结果。

## 示例输出

```
使用设备: cpu
从 checkpoints/mixtex_lora_10k_shuffled/epoch_1 加载模型...
检测到LoRA checkpoint，使用默认基础模型: MixTex/ZhEn-Latex-OCR
从基础模型 MixTex/ZhEn-Latex-OCR 加载...
将 LoRA 适配器加载到 decoder ...

加载测试集: linxy/LaTeX_OCR, name=small, split=test
从 1000 个测试样本中随机选择了 50 个样本

开始评估...
评估进度: 100%|████████████| 50/50 [02:30<00:00,  3.00s/it]

结果已保存到: evaluation_results/evaluation_results.json
CSV文件已保存到: evaluation_results/evaluation_results.csv

============================================================
评估完成！
============================================================
总样本数: 50
本地模型平均耗时: 0.850 秒
DeepSeek API平均耗时: 1.230 秒
DeepSeek API总成本（估算）: 0.0123 元

图片保存在: evaluation_results/eval_images
预测结果保存在: evaluation_results/predictions

请打开 evaluation_results/evaluation_results.csv 进行人工评估，填写质量评分和备注
============================================================
```


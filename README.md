# 目前更新
整理了一下项目结构

# 项目使用指南
## 1. 项目结构
整体结构
```cmd
autolatex/
├── .gitignore
├── knowledge/
├── pyproject.toml
├── README.md
├── .env -- 到这里之前都是一些Crewai的文件
├── data/ -- 这是白同学以前存放论文模版的文件夹（似乎要改）
├── docs/ -- markdown格式的说明（包括帮助我配置的guideline和已完成的任务报告）
├── knowledge/ -- crewai自己建的关于用户的一些信息
├── Agent输出/ -- 我们的Agent的输出
├── 模板/ -- 目前存放的是一些BIT毕业论文模版
├── test_data/ -- hbk同学创建的用来测试的word、txt、markdown文件
├── vendor/ --有个deepseek-OCR的文件
├── checkpoints/mixtex_lora_10k_final_tuned --微调模型
├── scripts/ --模型训练和评估的代码
└── src/
    └── autolatex/
        ├── __init__.py
        ├── main.py
        ├── crew.py
        ├── tools/
        │   ├── custom_tool.py
        │   └── __init__.py
        └── config/
            ├── agents.yaml
            └── tasks.yaml
```

## 2. 配置环境
1. 在项目根目录下创建.env文件,输入您的LLMapi的url和key
以deepseek api为例
```
MODEL=openai/deepseek-chat
OPENAI_API_KEY = <填入你的key>
OPENAI_API_BASE=https://api.deepseek.com
```
2. 将终端切换到项目根目录，安装Python环境，我们建议使用Python3.11版本
```
uv venv --python 3.11 myenv
```
3. 安装所有依赖
在终端输入
```
uv pip install -r requirements.txt
```


## 3. 启动OCR工具
在终端输入
```
uvicorn ocr_api:app --host 0.0.0.0 --port 8001
```

## 4. 启动crewai将
### 4.1 在终端启动
### 4.2 在前端启动


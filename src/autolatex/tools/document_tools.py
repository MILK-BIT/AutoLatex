from crewai_tools import BaseTool

# ------------------- 接口定义 -------------------

class DocumentParserTool(BaseTool):
    name: str = "Document Parser Tool"
    description: str = "解析 Word, Markdown, 或 Txt 文件，返回其结构化的 JSON 内容。"

    def _run(self, file_path: str) -> str:
        # 这是 B 同学需要实现的部分
        # 1. 根据文件扩展名选择合适的解析器
        # 2. 解析文件
        # 3. 生成一个严格符合团队定义的 JSON Schema 的 Python 字典
        # 4. 将字典转换为 JSON 字符串并返回
        
        # 示例实现:
        # parsed_dict = parse_document_logic(file_path) # B 同学的核心逻辑
        # return json.dumps(parsed_dict, ensure_ascii=False)
        
        # 在 B 同学完成前，先用一个假数据来测试
        print(f"--- [工具模拟] 正在解析文档: {file_path} ---")
        return '{"metadata": {"title": "模拟标题"}, "content": [{"type": "paragraph", "text": "这是一个模拟段落。"}]}'


class LaTeXCompilerTool(BaseTool):
    name: str = "LaTeX Compiler and Debugger Tool"
    description: str = "编译一个 .tex 文件。如果成功，返回 PDF 路径；如果失败，返回完整的编译错误日志。"

    def _run(self, latex_file_path: str) -> str:
        # 这是 B 同学需要实现的部分
        # 1. 准备一个安全的 Docker 沙箱环境
        # 2. 将 latex_file_path 和相关模板文件挂载到容器中
        # 3. 在容器内执行 pdflatex 或 xelatex 命令
        # 4. 检查返回值。如果成功 (返回码 0)，找到 .pdf 文件并返回其路径
        # 5. 如果失败，读取 .log 文件的内容并返回
        
        # 示例实现:
        print(f"--- [工具模拟] 正在编译: {latex_file_path} ---")
        # 模拟编译失败的情况
        return "编译错误: ! Undefined control sequence. l.15 \includegraphics"
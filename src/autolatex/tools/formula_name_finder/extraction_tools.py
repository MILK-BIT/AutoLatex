import json
import os
import re  # 🔥 新增：引入正则模块
from typing import Type, List
from pathlib import Path
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class FormulaExtractorInput(BaseModel):
    parsed_json_path: str = Field(
        ..., 
        description="doc_parser_agent 生成的完整文档结构 JSON 文件的路径。"
    )

class FormulaExtractorTool(BaseTool):
    name: str = "Formula Image Extractor Tool"
    description: str = (
        "扫描解析后的文档 JSON 数据，提取所有公式块对应的图片路径。"
        "支持识别 {'type': 'equation'} 结构以及嵌入在 paragraph 中的 \\formula{...} 标记。"
        "返回生成的公式列表文件路径。"
    )
    args_schema: Type[BaseModel] = FormulaExtractorInput

    def _run(self, parsed_json_path: str) -> str:
        try:
            # 1. 读取原始解析结果
            if not os.path.exists(parsed_json_path):
                return f"Error: 文件不存在 {parsed_json_path}"

            with open(parsed_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            formulas_to_process = []
            
            # 🔥 定义正则模式：匹配 \formula{...} 中的内容
            # 解释：\\formula 匹配字面量，\{ 匹配左括号，([^}]+) 捕获内部内容，\} 匹配右括号
            formula_pattern = re.compile(r"\\formula\{([^}]+)\}")
            
            # 2. 遍历 content 列表提取公式
            content_list = data.get("content", [])
            
            for index, item in enumerate(content_list):
                item_type = item.get("type")
                
                # --- 情况 A: 标准 Equation 结构 (你之前的逻辑) ---
                if item_type == "equation" and item.get("image_path"):
                    formulas_to_process.append({
                        "content_index": index,
                        "image_path": item["image_path"],
                        "format": item.get("format", "display")
                    })
                
                # --- 情况 B: 嵌入在 Paragraph 中的标记 (针对你的数据) ---
                elif item_type == "paragraph":
                    text = item.get("text", "")
                    # 查找所有匹配项
                    matches = formula_pattern.findall(text)
                    
                    if matches:
                        for img_path in matches:
                            # img_path 就是 {} 里的内容，例如 "formula.png"
                            # 如果需要拼接绝对路径，可以在这里处理
                            # 假设 parsed_images 在项目根目录，这里尝试补全路径（可选）
                            
                            full_image_path = img_path
                            # 简单的路径修正逻辑：如果只是文件名，且前面没路径，可能需要拼上 parsed_images
                            if "/" not in img_path and "\\" not in img_path:
                                # 这是一个猜测逻辑，视你的实际存放位置而定
                                # 如果你之前的 parser 把图片放在了 parsed_images/ 下，这里可能需要拼接
                                pass 

                            formulas_to_process.append({
                                "content_index": index,
                                "image_path": full_image_path,
                                "format": "display" # 这种通常视作独立公式
                            })

             # 3. 确定输出路径 (修改版：精准定位根目录)
            try:
                current_tool_path = Path(__file__).resolve()
                
                # 🔥 核心修改：智能锚点定位
                # 逻辑：无论文件藏多深，只要它在 'src' 目录下，我们就找到 'src'，然后往上一层就是根目录
                if 'src' in current_tool_path.parts:
                    src_index = current_tool_path.parts.index('src')
                    # 取 'src' 之前的所有部分组成路径 (即 E:\Python项目\NLP3\autolatex)
                    project_root = Path(*current_tool_path.parts[:src_index])
                else:
                    # 如果目录结构不包含 src (极少见)，尝试回退到相对层级计算
                    # 假设结构: Root/autolatex/tools/extraction_tools.py (无src层)
                    project_root = current_tool_path.parents[2] 

            except Exception as e:
                print(f"DEBUG: 路径计算出错，使用 CWD: {e}")
                project_root = Path(os.getcwd())

            # 此时 project_root 应该是: E:\Python项目\NLP3\autolatex
            
            # 拼接目标路径: E:\Python项目\NLP3\autolatex\output\intermediate
            output_dir = project_root / "output" / "intermediate"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = output_dir / "formula_images_list.json"

            # 4. 写入新的 JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(formulas_to_process, f, indent=2, ensure_ascii=False)

            return str(output_file)

        except Exception as e:
            return f"Error extracting formulas: {str(e)}"
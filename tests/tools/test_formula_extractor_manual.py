"""
手动测试脚本：直接调用 FormulaExtractorTool._run
用法（在项目根目录下运行）：
    python .\tests\tools\test_formula_extractor_manual.py [可选: 解析后的JSON绝对路径]

默认会使用 data/uploads/sample_paper_full_parsed.json。
"""
import sys
from pathlib import Path
import json

# 确保 src 在 sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from autolatex.tools.formula_name_finder.extraction_tools import FormulaExtractorTool


def main():
    # 解析后的文档 JSON 路径
    if len(sys.argv) > 1:
        parsed_json = Path(sys.argv[1])
    else:
        parsed_json = r"E:\Python项目\NLP3\autolatex\data\IEEE_Paper_With_Cite_Markers\IEEE_Paper_With_Cite_Markers_parsed.json"

    print(f"Testing FormulaExtractorTool with: {parsed_json}")
    tool = FormulaExtractorTool()
    output_path = tool._run(str(parsed_json))

    print(f"\nFormula list path returned: {output_path}")

    # 如果生成成功，读取并打印内容
    p = Path(output_path)
    if p.exists():
        try:
            data = json.loads(p.read_text(encoding='utf-8'))
            print("\n--- Extracted formulas JSON ---\n")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            print("\n--- END ---\n")
        except Exception as e:
            print(f"读取生成文件失败: {e}")
    else:
        print("生成的文件不存在，可能路径计算有问题或输入 JSON 中没有公式条目。")


if __name__ == '__main__':
    main()

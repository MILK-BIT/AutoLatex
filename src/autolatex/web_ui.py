import gradio as gr
import os
import sys
import shutil
from pathlib import Path
import requests
import base64

# 添加项目根目录到路径，以便支持直接运行和模块导入
# 计算项目根目录（src/ 的父目录）
current_file = Path(__file__).resolve()
# web_ui.py 位于: src/autolatex/web_ui.py
# 向上2级到达 src/，再向上1级到达项目根目录
src_dir = current_file.parent.parent  # src/
project_root = src_dir.parent  # 项目根目录

# 添加 src 目录到路径（用于绝对导入 autolatex.*）
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 导入模板工具
from autolatex.tools.template_manager import list_available_journals
from autolatex.tools.template_tools import TemplateRetrievalTool
from autolatex.tools.knowledge_base import initialize_knowledge_base, get_all_journal_names

# 自定义 CSS 样式
custom_css = """
/* 整体布局 */
.gradio-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    max-width: 100% !important;
}

/* 主容器 */
.main-container {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
    width: 250px !important;
    background: #ffffff;
    border-right: 1px solid #e5e5e5;
    display: flex;
    flex-direction: column;
    height: 100vh;
    position: fixed !important;
    left: 0 !important;
    top: 0 !important;
    z-index: 1000;
    overflow-y: auto;
    transition: left 0.3s ease, display 0.3s ease;
}

.sidebar-header {
    padding: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #e5e5e5;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: bold;
    font-size: 20px;
}

.logo-text {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
}

.collapse-icon {
    color: #9ca3af;
    cursor: pointer;
    font-size: 18px;
    user-select: none;
    transition: color 0.2s;
}

.collapse-icon:hover {
    color: #6b7280;
}

/* 导航菜单 */
.nav-menu {
    flex: 1;
    padding: 10px 0;
    overflow-y: auto;
}

.nav-item {
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: background 0.2s;
    position: relative;
}

.nav-item:hover {
    background: #f9fafb;
}

.nav-item.active {
    background: #f0f0ff;
    border-left: 3px solid #8b5cf6;
}

.nav-item-icon {
    font-size: 20px;
    width: 24px;
    text-align: center;
}

.nav-item-content {
    flex: 1;
}

.nav-item-title {
    font-size: 14px;
    font-weight: 500;
    color: #1f2937;
    margin-bottom: 2px;
}

.nav-item-desc {
    font-size: 12px;
    color: #6b7280;
}

.nav-item-arrow {
    color: #9ca3af;
    font-size: 14px;
}

/* 底部链接 */
.sidebar-footer {
    padding: 20px;
    border-top: 1px solid #e5e5e5;
}

.footer-item {
    padding: 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    color: #1f2937;
    font-size: 14px;
    cursor: pointer;
}

.footer-item:hover {
    color: #8b5cf6;
}

/* 主内容区 */
.main-content {
    margin-left: 250px;
    flex: 1;
    background: #f5f5f5;
    min-height: 100vh;
    position: relative;
    padding: 30px 40px;
    width: calc(100% - 250px);
    transition: margin-left 0.3s ease, width 0.3s ease;
}

/* 点状网格背景 */
.main-content::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: radial-gradient(circle, #d1d5db 1px, transparent 1px);
    background-size: 20px 20px;
    opacity: 0.3;
    pointer-events: none;
}

.content-wrapper {
    position: relative;
    z-index: 1;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
}

/* 横幅 */
.banner {
    background: linear-gradient(135deg, #ffc107 0%, #ffb300 100%);
    border-radius: 12px;
    padding: 15px 20px;
    margin-bottom: 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.banner-text {
    color: #1f2937;
    font-size: 14px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}

.banner-close {
    color: #1f2937;
    cursor: pointer;
    font-size: 20px;
    font-weight: bold;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: background 0.2s;
}

.banner-close:hover {
    background: rgba(0,0,0,0.1);
}

/* 标题区域 */
.title-section {
    text-align: center;
    margin-bottom: 20px;
}

.main-title {
    font-size: 36px;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 12px;
}

.subtitle {
    font-size: 16px;
    color: #6b7280;
}

/* 上传卡片 */
.upload-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 45px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.pdf-icon-container {
    text-align: center;
    margin-bottom: 10px;
}

.pdf-icon {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 40px;
    font-weight: bold;
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.upload-button {
    width: auto !important;
    min-width: 280px;
    padding: 12px 24px !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin: 0 auto 12px auto;
    transition: transform 0.2s, box-shadow 0.2s;
}

.upload-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.file-info {
    text-align: center;
    color: #6b7280;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 10px;
}

.model-section {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #e5e5e5;
}

.model-label {
    font-size: 14px;
    color: #1f2937;
    font-weight: 500;
    white-space: nowrap;
}

.model-dropdown {
    flex: 1;
}

.translate-button {
    padding: 10px 20px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    transition: transform 0.2s, box-shadow 0.2s;
}

.translate-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

/* 隐藏 Gradio 默认样式 */
.hide-gradio-default {
    display: none !important;
}

/* 隐藏 Gradio 页脚链接 */
footer {
    display: none !important;
}

.gradio-footer {
    display: none !important;
}

a[href*="api"], a[href*="gradio"], a[href*="settings"] {
    display: none !important;
}

/* 使用 JavaScript 隐藏包含特定文本的元素 */

/* 调整 Gradio 组件样式 */
.gradio-container .main {
    padding: 0 !important;
}

/* 文件上传组件样式调整 */
input[type="file"] {
    display: none;
}

/* 下拉框样式 */
select, .gradio-dropdown {
    padding: 10px 12px;
    border: 1px solid #e5e5e5;
    border-radius: 8px;
    background: #ffffff;
    font-size: 14px;
    color: #1f2937;
}

/* 确保侧边栏在最上层 */
.sidebar {
    z-index: 1000;
}

/* 调整主内容区域以适应侧边栏 */
#root > div > div {
    margin-left: 250px;
}

/* 覆盖 Gradio 默认主题 */
.dark {
    --background-fill-primary: #f5f5f5;
}

/* 确保 body 和 html 没有默认边距 */
body, html {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

/* 调整 Gradio Blocks 容器 */
.gradio-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* 主内容区域样式增强 */
.main-content {
    padding: 30px 40px;
}

.sidebar-collapsed .main-content {
    margin-left: 0 !important;
    width: 100% !important;
}

.sidebar-collapsed #root > div > div {
    margin-left: 0 !important;
}

/* 按钮样式覆盖 */
button.upload-button {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    border: none !important;
    color: white !important;
}

button.translate-button {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    border: none !important;
    color: white !important;
}

button.delete-button {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    border: none !important;
    color: white !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    white-space: nowrap;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-top: 1px;
}

button.delete-button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.delete-button-container {
    text-align: center;
    margin-top: 8px;
}

/* 删除按钮行样式 - 减少间距 */
.delete-button-row {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

.delete-button-row > div {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* 展开侧边栏按钮（当侧边栏隐藏时显示） */
.expand-sidebar-btn {
    position: fixed;
    left: 0;
    top: 20px;
    width: 30px;
    height: 40px;
    background: #ffffff;
    border: 1px solid #e5e5e5;
    border-left: none;
    border-radius: 0 8px 8px 0;
    display: none;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 999;
    color: #6b7280;
    font-size: 16px;
    box-shadow: 2px 0 4px rgba(0,0,0,0.1);
    transition: all 0.2s;
}

.expand-sidebar-btn:hover {
    background: #f9fafb;
    color: #8b5cf6;
}

/* 处理结果输出框可拖拽缩放样式 */
.resizable-output {
    position: relative;
}

.resizable-output textarea {
    resize: both;
    min-height: 42px;  /* 约等于单行高度，便于收缩到最小 */
    max-height: 70vh;
    min-width: 320px;
    padding: 14px 16px;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    background: #ffffff;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    font-family: "Fira Code", "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    line-height: 1.5;
}

.resizable-output textarea:focus {
    outline: none;
    border-color: #8b5cf6;
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.25);
}

/* 下载链接样式 */
.download-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
    color: #ffffff;
    border-radius: 10px;
    text-decoration: none;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.2s;
}

.download-link:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(34, 197, 94, 0.35);
    opacity: 0.95;
}

/* 图片上传区域样式 */
.image-upload-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin-top: 20px;
}

.image-upload-title {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.image-upload-button {
    width: auto !important;
    min-width: 200px;
    padding: 10px 20px !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: transform 0.2s, box-shadow 0.2s;
}

.image-upload-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

/* 图片画廊样式 */
.image-gallery-container {
    margin-top: 20px;
}

.image-item-wrapper {
    position: relative;
    display: inline-block;
    margin: 10px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.image-item-wrapper:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.image-delete-btn {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 28px;
    height: 28px;
    background: rgba(239, 68, 68, 0.9);
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: bold;
    z-index: 10;
    transition: all 0.2s;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
}

.image-delete-btn:hover {
    background: rgba(220, 38, 38, 1);
    transform: scale(1.1);
    box-shadow: 0 4px 10px rgba(239, 68, 68, 0.4);
}

.image-item-wrapper img {
    display: block;
    max-width: 200px;
    max-height: 200px;
    object-fit: contain;
}

.empty-gallery-message {
    text-align: center;
    color: #6b7280;
    font-size: 14px;
    padding: 40px 20px;
    background: #f9fafb;
    border-radius: 8px;
    border: 2px dashed #d1d5db;
}

/* 隐藏删除索引输入框 */
.hidden-delete-index,
.hidden-delete-index * {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    width: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    opacity: 0 !important;
    position: absolute !important;
    left: -9999px !important;
}
"""

# HTML 模板
sidebar_html = """
<div class="sidebar">
    <div class="sidebar-header">
        <div class="logo-container">
            <div class="logo-icon">AT</div>
            <div class="logo-text">AutoTex</div>
        </div>
        <div class="collapse-icon" id="sidebar-toggle" onclick="window.toggleSidebar()">←</div>
    </div>
    <div class="nav-menu">
        <div class="nav-item active">
            <div class="nav-item-icon">📝</div>
            <div class="nav-item-content">
                <div class="nav-item-title">LaTeX排版</div>
                <div class="nav-item-desc">智能转换论文格式</div>
            </div>
            <div class="nav-item-arrow">→</div>
        </div>
        <div class="nav-item">
            <div class="nav-item-icon">📚</div>
            <div class="nav-item-content">
                <div class="nav-item-title">期刊模板</div>
                <div class="nav-item-desc">支持多种期刊格式</div>
            </div>
            <div class="nav-item-arrow">→</div>
        </div>
        <div class="nav-item">
            <div class="nav-item-icon">⚙️</div>
            <div class="nav-item-content">
                <div class="nav-item-title">格式设置</div>
                <div class="nav-item-desc">自定义排版参数</div>
            </div>
            <div class="nav-item-arrow">→</div>
        </div>
    </div>
    <div class="sidebar-footer">
        <div class="footer-item">
            <span>📖</span>
            <span>使用文档</span>
        </div>
        <div class="footer-item">
            <span>👤</span>
            <span>登录/注册</span>
        </div>
    </div>
</div>
"""

title_html = """
<div class="title-section">
    <div class="main-title">LaTeX智能排版专家</div>
    <div class="subtitle">将Word/Markdown/Txt论文智能转换为符合期刊要求的LaTeX格式</div>
</div>
"""

def get_available_templates():
    """从向量数据库获取所有可用的模板列表"""
    try:
        # 从向量数据库获取所有期刊名称
        db = initialize_knowledge_base()
        
        # 获取所有文档及其元数据
        all_results = db.collection.get()
        
        if all_results and all_results.get('metadatas'):
            # 从元数据中提取 journal_name
            journal_names = set()
            for metadata in all_results.get('metadatas', []):
                if metadata and 'journal_name' in metadata:
                    journal_name = metadata['journal_name']
                    if journal_name:
                        journal_names.add(journal_name)
            
            # 转换为列表并排序（英文在前，中文在后）
            templates = sorted(journal_names, key=lambda x: (not x.isascii(), x))
            
            # 添加"自定义模板"选项
            templates.append("自定义模板")
            
            if templates:
                return templates
        
        # 如果向量数据库为空或获取失败，尝试使用备用方法
        try:
            templates = get_all_journal_names()
            templates.append("自定义模板")
            return templates
        except Exception:
            pass
        
        # 最后的备用方案：返回默认列表
        return ["IEEE Transactions", "ACM Conference", "Springer LNCS", "Elsevier Article", "Nature", "Science", "自定义模板"]
    except Exception as e:
        # 如果获取失败，返回默认列表
        print(f"[Web UI] 从向量数据库获取模板列表失败: {e}")
        try:
            # 尝试使用备用方法
            templates = get_all_journal_names()
            templates.append("自定义模板")
            return templates
        except Exception:
            return ["IEEE Transactions", "ACM Conference", "Springer LNCS", "Elsevier Article", "Nature", "Science", "自定义模板"]

def preview_template(template_name: str) -> str:
    """预览模板内容"""
    if not template_name or template_name == "自定义模板":
        return "请选择一个模板名称进行预览"
    
    try:
        tool = TemplateRetrievalTool()
        template_content = tool._run(template_name)
        
        # 如果内容太长，只显示前5000个字符
        if len(template_content) > 5000:
            return f"{template_content[:5000]}\n\n... (内容已截断，共 {len(template_content)} 个字符)"
        return template_content
    except Exception as e:
        return f"预览模板失败: {str(e)}"

def process_file(file, journal_type):
    """处理上传的文件并生成LaTeX（通过后端 REST API 上传 + 转换）"""
    print("[Web UI] process_file 被调用")  # 调试日志
    if file is None:
        print("[Web UI] 未选择文件")
        return "请先上传论文文件", gr.update(visible=False, value=None)

    # 1. 调用后端 /api/v1/paper/upload 接口上传文件
    api_base = os.environ.get("AUTOLATEX_API_BASE", "http://127.0.0.1:8000")
    upload_url = f"{api_base}/api/v1/paper/upload"
    convert_url = f"{api_base}/api/v1/paper/convert"

    def build_download_link(pdf_url, pdf_name=None):
        """生成下载链接的 HTML 更新对象"""
        if not pdf_url:
            return gr.update(visible=False, value=None)
        full_url = pdf_url if str(pdf_url).startswith("http") else f"{api_base.rstrip('/')}{pdf_url}"
        display_name = pdf_name or "生成结果.pdf"
        html = (
            f'<a class="download-link" href="{full_url}" target="_blank" '
            f'download="{display_name}">⬇️ 下载PDF（{display_name}）</a>'
        )
        return gr.update(value=html, visible=True)

    try:
        # Gradio `file` 为一个带临时路径的对象，file.name 为临时文件路径
        # 尝试获取原始文件名（部分 Gradio 版本会带有 orig_name）
        orig_name = getattr(file, "orig_name", None) or os.path.basename(file.name)

        print(f"[Web UI] 准备上传文件: {orig_name}, 临时路径: {file.name}")
        with open(file.name, "rb") as f:
            files = {"file": (orig_name, f, "application/octet-stream")}
            resp = requests.post(upload_url, files=files, timeout=60)

        if resp.status_code != 200:
            print(f"[Web UI] 上传接口 HTTP {resp.status_code}: {resp.text}")
            return f"❌ 调用上传接口失败，HTTP {resp.status_code}: {resp.text}", gr.update(visible=False, value=None)

        data = resp.json()
        print(f"[Web UI] 上传接口返回: {data}")
        if not data.get("success"):
            return f"❌ 上传接口返回失败: {data.get('message') or data}", gr.update(visible=False, value=None)

        file_path = data.get("file_path")
        filename = data.get("filename", orig_name)
    except Exception as e:
        print(f"[Web UI] 通过 REST API 上传文件失败: {e}")
        return f"❌ 通过 REST API 上传文件失败: {str(e)}", gr.update(visible=False, value=None)

    # 2. 调用 /api/v1/paper/convert 进行论文转换
    try:
        payload = {
            "file_path": file_path,
            "journal_name": journal_type or "",
            "topic": "自动将word、txt、markdown格式论文转化为Latex格式论文",
        }
        print(f"[Web UI] 调用转换接口, payload={payload}")
        resp_conv = requests.post(convert_url, json=payload, timeout=600)
        if resp_conv.status_code != 200:
            print(f"[Web UI] 转换接口 HTTP {resp_conv.status_code}: {resp_conv.text}")
            return (
                "✅ 文件上传成功，但转换接口调用失败。\n"
                f"文件名: {filename}\n"
                f"后端保存路径: {file_path}\n\n"
                f"调用 /api/v1/paper/convert 失败，HTTP {resp_conv.status_code}: {resp_conv.text}",
                gr.update(visible=False, value=None),
            )

        conv_data = resp_conv.json()
        print(f"[Web UI] 转换接口返回: {conv_data}")
        if not conv_data.get("success"):
            return (
                "✅ 文件上传成功，但转换失败。\n"
                f"文件名: {filename}\n"
                f"后端保存路径: {file_path}\n\n"
                f"转换消息: {conv_data.get('message')}\n"
                f"错误信息: {conv_data.get('error')}",
                gr.update(visible=False, value=None),
            )

        output_path = conv_data.get("output_path")
        message = conv_data.get("message", "论文转换成功")
        pdf_url = conv_data.get("pdf_url")
        pdf_name = conv_data.get("pdf_filename")
        download_update = build_download_link(pdf_url, pdf_name)

        return (
            f"✅ 论文文件已通过 REST API 上传并转换成功。\n"
            f"文件名: {filename}\n"
            f"上传保存路径: {file_path}\n\n"
            f"转换结果: {message}\n"
            f"LaTeX 输出路径: {output_path}",
            download_update,
        )
    except Exception as e:
        print(f"[Web UI] 调用转换接口异常: {e}")
        return (
            "✅ 文件上传成功，但在调用转换接口时发生异常。\n"
            f"文件名: {filename}\n"
            f"后端保存路径: {file_path}\n\n"
            f"异常信息: {str(e)}",
            gr.update(visible=False, value=None),
        )

# JavaScript 代码用于布局调整
sidebar_toggle_js = """
<script>
window.toggleSidebar = window.toggleSidebar || function() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    let expandBtn = document.getElementById('expand-sidebar-btn');
    const body = document.body;

    if (!expandBtn) {
        expandBtn = document.createElement('div');
        expandBtn.id = 'expand-sidebar-btn';
        expandBtn.className = 'expand-sidebar-btn';
        expandBtn.textContent = '→';
        expandBtn.onclick = function() { window.showSidebar(); };
        expandBtn.style.display = 'none';
        document.body.appendChild(expandBtn);
    }

    if (sidebar && mainContent) {
        sidebar.style.display = 'none';
        sidebar.style.left = '-250px';
        mainContent.style.marginLeft = '0';
        mainContent.style.width = '100%';
        expandBtn.style.display = 'flex';
        if (body) {
            body.classList.add('sidebar-collapsed');
        }
    }
};

window.showSidebar = window.showSidebar || function() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const expandBtn = document.getElementById('expand-sidebar-btn');
    const body = document.body;

    if (sidebar && mainContent) {
        sidebar.style.display = 'flex';
        sidebar.style.left = '0';
        mainContent.style.marginLeft = '250px';
        mainContent.style.width = 'calc(100% - 250px)';
        if (expandBtn) {
            expandBtn.style.display = 'none';
        }
        if (body) {
            body.classList.remove('sidebar-collapsed');
        }
    }
};
</script>
"""


layout_js = """
<script>
// 确保函数在全局作用域中定义
window.toggleSidebar = function() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    let expandBtn = document.getElementById('expand-sidebar-btn');
    const body = document.body;
    
    if (!expandBtn) {
        expandBtn = document.createElement('div');
        expandBtn.id = 'expand-sidebar-btn';
        expandBtn.className = 'expand-sidebar-btn';
        expandBtn.textContent = '→';
        expandBtn.onclick = function() { window.showSidebar(); };
        expandBtn.style.display = 'none';
        document.body.appendChild(expandBtn);
    }
    
    if (sidebar && mainContent) {
        sidebar.style.display = 'none';
        sidebar.style.left = '-250px';
        mainContent.style.marginLeft = '0';
        mainContent.style.width = '100%';
        expandBtn.style.display = 'flex';
        if (body) {
            body.classList.add('sidebar-collapsed');
        }
    }
};

window.showSidebar = function() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const expandBtn = document.getElementById('expand-sidebar-btn');
    const body = document.body;
    
    if (sidebar && mainContent) {
        sidebar.style.display = 'flex';
        sidebar.style.left = '0';
        mainContent.style.marginLeft = '250px';
        mainContent.style.width = 'calc(100% - 250px)';
        if (expandBtn) {
            expandBtn.style.display = 'none';
        }
        if (body) {
            body.classList.remove('sidebar-collapsed');
        }
    }
};

(function() {
    // 等待 DOM 加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initLayout);
    } else {
        initLayout();
    }
    
    function initLayout() {
        // 确保侧边栏固定在左侧
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.position = 'fixed';
            sidebar.style.left = '0';
            sidebar.style.top = '0';
            sidebar.style.height = '100vh';
            sidebar.style.zIndex = '1000';
        }
        
        // 调整主内容区域的左边距
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.style.marginLeft = '250px';
        }
        
        // 调整 Gradio 容器
        const gradioContainer = document.querySelector('.gradio-container');
        if (gradioContainer) {
            gradioContainer.style.maxWidth = '100%';
            gradioContainer.style.padding = '0';
        }
        
        // 隐藏 Gradio 页脚链接
        const footer = document.querySelector('footer');
        if (footer) {
            footer.style.display = 'none';
        }
        
        // 隐藏所有包含特定文本的链接
        const allLinks = document.querySelectorAll('a');
        allLinks.forEach(link => {
            const text = link.textContent || link.innerText;
            if (text.includes('APIを介して使用') || 
                text.includes('Gradioで作成') || 
                text.includes('設定') ||
                link.href.includes('/api') ||
                link.href.includes('/gradio') ||
                link.href.includes('/settings')) {
                link.style.display = 'none';
                // 也隐藏父元素（如果是单独的链接容器）
                if (link.parentElement && link.parentElement.tagName === 'SPAN') {
                    link.parentElement.style.display = 'none';
                }
            }
        });
        
        // 隐藏整个页脚容器
        const footerContainers = document.querySelectorAll('footer, .gradio-footer');
        footerContainers.forEach(container => {
            container.style.display = 'none';
        });
        
    }
    
    // 监听 Gradio 加载完成事件
    window.addEventListener('load', initLayout);
    
    // 使用 MutationObserver 监听 DOM 变化
    const observer = new MutationObserver(function(mutations) {
        initLayout();
        // 确保事件绑定
        setupSidebarToggle();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // 单独的函数来设置侧边栏切换
    function setupSidebarToggle() {
        const sidebarToggle = document.getElementById('sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (sidebarToggle && sidebar && mainContent && !sidebarToggle.dataset.listenerAttached) {
            sidebarToggle.dataset.listenerAttached = 'true';
            
            // 创建展开按钮
            let expandBtn = document.getElementById('expand-sidebar-btn');
            if (!expandBtn) {
                expandBtn = document.createElement('div');
                expandBtn.id = 'expand-sidebar-btn';
                expandBtn.className = 'expand-sidebar-btn';
                expandBtn.textContent = '→';
                expandBtn.style.display = 'none';
                document.body.appendChild(expandBtn);
            }
            
            function hideSidebar() {
                if (sidebar && mainContent && expandBtn) {
                    sidebar.style.display = 'none';
                    sidebar.style.left = '-250px';
                    mainContent.style.marginLeft = '0';
                    mainContent.style.width = '100%';
                    expandBtn.style.display = 'flex';
                }
            }
            
            function showSidebar() {
                if (sidebar && mainContent && expandBtn) {
                    sidebar.style.display = 'flex';
                    sidebar.style.left = '0';
                    mainContent.style.marginLeft = '250px';
                    mainContent.style.width = 'calc(100% - 250px)';
                    expandBtn.style.display = 'none';
                }
            }
            
            sidebarToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Toggle clicked');
                window.toggleSidebar();
            });
            
            expandBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                window.showSidebar();
            });
        }
    }
    
    // 使用事件委托作为备用方案
    document.addEventListener('click', function(e) {
        if (e.target && (e.target.id === 'sidebar-toggle' || e.target.classList.contains('collapse-icon'))) {
            e.preventDefault();
            e.stopPropagation();
            window.toggleSidebar();
        }
        if (e.target && e.target.id === 'expand-sidebar-btn') {
            e.preventDefault();
            e.stopPropagation();
            window.showSidebar();
        }
    });
    
    // 立即尝试设置
    setupSidebarToggle();
    
    // 延迟设置，确保 Gradio 完全加载
    setTimeout(setupSidebarToggle, 500);
    setTimeout(setupSidebarToggle, 1000);
    setTimeout(setupSidebarToggle, 2000);
    setInterval(setupSidebarToggle, 3000);
    
    // 图片删除功能
    window.deleteImage = function(index) {
        console.log('删除图片，索引:', index);
        
        function findAndUpdateInput() {
            try {
                let deleteIndexInput = null;
                let containerElement = null;
                
                // 辅助函数：从容器中提取实际的 input 元素
                function extractInputFromContainer(container) {
                    if (!container) return null;
                    
                    // 如果容器本身就是 input 或 textarea，直接返回
                    if (container.tagName === 'INPUT' || container.tagName === 'TEXTAREA') {
                        return container;
                    }
                    
                    // 在容器内查找 input 或 textarea（使用更广泛的查询）
                    let input = container.querySelector('input[type="text"]');
                    if (input) return input;
                    
                    input = container.querySelector('input:not([type])');
                    if (input) return input;
                    
                    input = container.querySelector('textarea');
                    if (input) return input;
                    
                    // 查找任何 input 元素
                    input = container.querySelector('input');
                    if (input) return input;
                    
                    // 如果还是没找到，尝试递归查找子元素
                    const allInputs = container.querySelectorAll('input, textarea');
                    for (let inp of allInputs) {
                        if (inp.tagName === 'INPUT' || inp.tagName === 'TEXTAREA') {
                            return inp;
                        }
                    }
                    
                    return null;
                }
                
                // 方法1: 直接通过ID查找容器，然后提取 input
                containerElement = document.getElementById('delete-image-index');
                if (containerElement) {
                    deleteIndexInput = extractInputFromContainer(containerElement);
                    // 如果没找到，尝试更深层的查找
                    if (!deleteIndexInput) {
                        // 查找所有可能的 input
                        const allInputsInContainer = containerElement.querySelectorAll('input, textarea');
                        for (let inp of allInputsInContainer) {
                            if (inp.tagName === 'INPUT' || inp.tagName === 'TEXTAREA') {
                                deleteIndexInput = inp;
                                break;
                            }
                        }
                    }
                }
                
                // 方法2: 通过 data-testid 查找
                if (!deleteIndexInput) {
                    containerElement = document.querySelector('[data-testid="delete-image-index"]');
                    if (containerElement) {
                        deleteIndexInput = extractInputFromContainer(containerElement);
                    }
                }
                
                // 方法3: 查找所有包含 delete-image-index 的元素
                if (!deleteIndexInput) {
                    const candidates = document.querySelectorAll('[id*="delete-image-index"], [data-testid*="delete-image-index"]');
                    for (let candidate of candidates) {
                        deleteIndexInput = extractInputFromContainer(candidate);
                        if (deleteIndexInput) break;
                    }
                }
                
                // 方法4: 通过查找所有 textbox 类型的 input，然后检查父元素
                if (!deleteIndexInput) {
                    const allInputs = document.querySelectorAll('input[type="text"], input:not([type]), textarea');
                    for (let input of allInputs) {
                        // 检查父元素或祖先元素是否包含 delete-image-index
                        let parent = input.parentElement;
                        let depth = 0;
                        while (parent && depth < 10) {
                            const parentId = parent.id || '';
                            const parentTestId = parent.getAttribute('data-testid') || '';
                            const parentClass = parent.className || '';
                            if (parentId.includes('delete-image-index') || 
                                parentTestId.includes('delete-image-index') ||
                                parentClass.includes('delete-image-index')) {
                                deleteIndexInput = input;
                                break;
                            }
                            parent = parent.parentElement;
                            depth++;
                        }
                        if (deleteIndexInput) break;
                    }
                }
                
                // 方法5: 使用 Gradio 的内部 API（如果可用）
                if (!deleteIndexInput) {
                    try {
                        const gradioApp = window.__gradio_app__ || 
                                         (document.querySelector('gradio-app') && document.querySelector('gradio-app').__gradio_app__);
                        if (gradioApp) {
                            const componentMap = gradioApp._id_to_component || {};
                            for (let [compId, component] of Object.entries(componentMap)) {
                                if (compId.includes('delete-image-index')) {
                                    if (component.querySelector) {
                                        deleteIndexInput = component.querySelector('input, textarea');
                                    } else if (component.tagName === 'INPUT' || component.tagName === 'TEXTAREA') {
                                        deleteIndexInput = component;
                                    }
                                    if (deleteIndexInput) break;
                                }
                            }
                        }
                    } catch (e) {
                        // 忽略错误
                    }
                }
                
                // 如果找到的是容器而不是 input，尝试从容器中提取
                if (containerElement && !deleteIndexInput) {
                    console.log('找到容器但未找到 input，尝试深度查找:', containerElement);
                    // 尝试所有可能的选择器
                    const selectors = [
                        'input[type="text"]',
                        'input:not([type])',
                        'textarea',
                        'input',
                        '*[contenteditable="true"]'
                    ];
                    for (let selector of selectors) {
                        const found = containerElement.querySelector(selector);
                        if (found && (found.tagName === 'INPUT' || found.tagName === 'TEXTAREA')) {
                            deleteIndexInput = found;
                            console.log('通过选择器找到 input:', selector, found);
                            break;
                        }
                    }
                }
                
                if (deleteIndexInput && (deleteIndexInput.tagName === 'INPUT' || deleteIndexInput.tagName === 'TEXTAREA')) {
                    console.log('找到有效的 input 元素:', deleteIndexInput.tagName, deleteIndexInput);
                    // 设置值
                    const oldValue = deleteIndexInput.value || '';
                    deleteIndexInput.value = String(index);
                    console.log('设置值:', oldValue, '->', deleteIndexInput.value);
                    
                    // 如果值没有改变，强制触发事件
                    if (oldValue === String(index)) {
                        // 先清空再设置，确保触发 change 事件
                        deleteIndexInput.value = '';
                        deleteIndexInput.value = String(index);
                    }
                    
                    // 触发多个事件以确保 Gradio 检测到变化
                    const events = ['input', 'change', 'blur', 'keyup'];
                    events.forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        deleteIndexInput.dispatchEvent(event);
                        console.log('触发事件:', eventType);
                    });
                    
                    // 也尝试触发 focus 和 blur 来确保更新
                    try {
                        deleteIndexInput.focus();
                        setTimeout(() => {
                            if (deleteIndexInput) deleteIndexInput.blur();
                        }, 10);
                    } catch (e) {
                        console.log('focus/blur 错误:', e);
                    }
                    
                    // 使用 InputEvent 来模拟真实的输入
                    try {
                        const inputEvent = new InputEvent('input', {
                            bubbles: true,
                            cancelable: true,
                            data: String(index)
                        });
                        deleteIndexInput.dispatchEvent(inputEvent);
                    } catch (e) {
                        console.log('InputEvent 不支持:', e);
                    }
                    
                    // 使用 CustomEvent 触发 change
                    try {
                        const customEvent = new CustomEvent('change', {
                            bubbles: true,
                            cancelable: true,
                            detail: { value: String(index) }
                        });
                        deleteIndexInput.dispatchEvent(customEvent);
                    } catch (e) {
                        console.log('CustomEvent 错误:', e);
                    }
                    
                    // 尝试使用 Gradio 的内部更新机制
                    try {
                        const gradioApp = window.__gradio_app__ || 
                                         (document.querySelector('gradio-app') && document.querySelector('gradio-app').__gradio_app__);
                        if (gradioApp && gradioApp._id_to_component) {
                            for (let [compId, component] of Object.entries(gradioApp._id_to_component)) {
                                if (compId.includes('delete-image-index')) {
                                    console.log('找到 Gradio 组件:', compId);
                                    if (component.value !== undefined) {
                                        component.value = String(index);
                                        console.log('更新组件值:', component.value);
                                    }
                                    if (component.dispatch_event) {
                                        component.dispatch_event('change', String(index));
                                        console.log('触发组件事件');
                                    }
                                    if (component.update) {
                                        component.update({ value: String(index) });
                                        console.log('调用组件 update');
                                    }
                                    break;
                                }
                            }
                        }
                    } catch (e) {
                        console.log('Gradio API 更新失败:', e);
                    }
                    
                    // 延迟再次触发 change 事件
                    setTimeout(() => {
                        const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                        deleteIndexInput.dispatchEvent(changeEvent);
                        console.log('延迟触发 change 事件');
                    }, 50);
                    
                    console.log('已设置删除索引:', index, '最终值:', deleteIndexInput.value);
                    return true;
                } else {
                    console.warn('未找到有效的 input 元素');
                    console.warn('找到的元素:', deleteIndexInput);
                    console.warn('元素类型:', deleteIndexInput ? deleteIndexInput.tagName : 'null');
                    if (containerElement) {
                        console.warn('容器元素:', containerElement);
                        console.warn('容器内的所有元素:', containerElement.innerHTML.substring(0, 200));
                    }
                    return false;
                }
            } catch (e) {
                console.error('删除图片时出错:', e);
                return false;
            }
        }
        
        if (!findAndUpdateInput()) {
            // 延迟重试（最多重试10次）
            if (!window._deleteImageRetryCount) {
                window._deleteImageRetryCount = 0;
            }
            if (window._deleteImageRetryCount < 10) {
                window._deleteImageRetryCount++;
                setTimeout(function() {
                    window.deleteImage(index);
                }, 300);
            } else {
                window._deleteImageRetryCount = 0;
                console.error('删除图片失败：无法找到输入组件，已重试10次');
            }
        } else {
            window._deleteImageRetryCount = 0;
        }
    };
})();
</script>
"""

def create_interface():
    with gr.Blocks(
        css=custom_css,
        theme=gr.themes.Soft(),
        head=sidebar_toggle_js + layout_js,
    ) as app:
        # 添加侧边栏 HTML（固定在左侧）
        gr.HTML(sidebar_html)
        
        # 主内容区域
        with gr.Column(elem_classes=["main-content"]):
            content_wrapper = gr.Column(elem_classes=["content-wrapper"])
            with content_wrapper:
                # 标题
                gr.HTML(title_html)
                
                # 上传卡片
                with gr.Column(elem_classes=["upload-card"]):
                    gr.HTML("""
                    <div class="pdf-icon-container">
                        <div class="pdf-icon">📄</div>
                    </div>
                    """)
                    
                    # 文件上传组件（隐藏默认样式）
                    file_upload = gr.File(
                        label="",
                        file_types=[".doc", ".docx", ".txt", ".md", ".markdown"],
                        elem_classes=["hide-gradio-default"]
                    )
                    
                    # 自定义上传按钮和删除按钮（居中显示）
                    with gr.Column():
                        with gr.Row():
                            gr.HTML('<div style="flex: 1;"></div>')
                            upload_btn = gr.Button(
                                "上传论文文件 ↑",
                                elem_classes=["upload-button"],
                                scale=0
                            )
                            gr.HTML('<div style="flex: 1;"></div>')
                        
                        # 删除按钮容器（初始隐藏，紧贴上传按钮）
                        with gr.Row(elem_classes=["delete-button-row"]):
                            gr.HTML('<div style="flex: 1;"></div>')
                            delete_btn = gr.Button(
                                "删除文件 ✕",
                                elem_classes=["delete-button"],
                                scale=0,
                                visible=False
                            )
                            gr.HTML('<div style="flex: 1;"></div>')
                    
                    gr.HTML("""
                    <div class="file-info">
                        <div>支持文件类型: Word (.doc, .docx) | Markdown (.md, .markdown) | 文本 (.txt)</div>
                        <div>最大文件大小: 50MB</div>
                    </div>
                    """)
                    
                    # 期刊类型选择和生成按钮
                    with gr.Row(elem_classes=["model-section"]):
                        gr.HTML('<div class="model-label">期刊类型</div>')
                        # 动态获取模板列表
                        available_templates = get_available_templates()
                        journal_dropdown = gr.Dropdown(
                            choices=available_templates,
                            value=available_templates[0] if available_templates else "自定义模板",
                            label="",
                            scale=2,
                            elem_classes=["model-dropdown"],
                            container=False,
                            allow_custom_value=True,
                            info="从下拉列表选择或输入自定义模板名称"
                        )
                        preview_btn = gr.Button(
                            "预览模板 👁️",
                            elem_classes=["translate-button"],
                            scale=0,
                            size="sm"
                        )
                        generate_btn = gr.Button(
                            "生成LaTeX 📦",
                            elem_classes=["translate-button"],
                            scale=0
                        )
                
                # 图片上传卡片
                with gr.Column(elem_classes=["image-upload-card"]):
                    gr.HTML("""
                    <div class="image-upload-title">
                        <span>🖼️</span>
                        <span>上传图片</span>
                    </div>
                    """)
                    
                    # 图片上传组件（隐藏默认样式）
                    image_upload = gr.File(
                        label="",
                        file_types=["image"],
                        file_count="multiple",
                        elem_classes=["hide-gradio-default"]
                    )
                    
                    # 图片上传按钮
                    with gr.Row():
                        gr.HTML('<div style="flex: 1;"></div>')
                        image_upload_btn = gr.Button(
                            "选择图片 📷",
                            elem_classes=["image-upload-button"],
                            scale=0
                        )
                        gr.HTML('<div style="flex: 1;"></div>')
                    
                    gr.HTML("""
                    <div class="file-info" style="margin-top: 10px;">
                        <div>支持格式: JPG, PNG, GIF, WebP</div>
                        <div>可同时上传多张图片</div>
                    </div>
                    """)
                    
                    # 图片画廊（使用State存储图片列表）
                    uploaded_images_state = gr.State(value=[])  # 存储图片路径列表
                    
                    # 图片显示区域（使用HTML显示，支持删除按钮）
                    image_display = gr.HTML(
                        value='<div class="empty-gallery-message">暂无图片，请上传图片</div>',
                        elem_id="image-display"
                    )
                    
                    # 隐藏的删除索引输入（用于传递要删除的图片索引）
                    # 使用CSS隐藏但仍在DOM中，确保JavaScript能找到
                    delete_image_index = gr.Textbox(
                        value="",
                        label="",
                        visible=True,  # 设置为可见，但通过CSS隐藏
                        interactive=True,
                        elem_id="delete-image-index",
                        elem_classes=["hidden-delete-index"]
                    )
                
                # 模板预览区域
                template_preview = gr.Code(
                    label="模板预览",
                    language="latex",
                    visible=False,
                    lines=15,
                    interactive=False
                )
                
                # 输出区域（用于显示处理结果）
                output = gr.Textbox(
                    label="处理结果",
                    visible=True,   # 默认显示，便于直接看到上传/转换结果
                    interactive=False,
                    elem_classes=["resizable-output"]
                )
                
                download_link = gr.HTML(
                    value="",
                    visible=False
                )
                
                # 绑定事件
                def trigger_upload():
                    return gr.update()
                
                upload_btn.click(
                    fn=trigger_upload,
                    inputs=[],
                    outputs=[],
                    js="() => { const fileInputs = document.querySelectorAll('input[type=file]'); if(fileInputs && fileInputs[0]) fileInputs[0].click(); }"
                )
                
                # 图片上传相关函数
                def trigger_image_upload():
                    """触发图片文件选择"""
                    return gr.update()
                
                image_upload_btn.click(
                    fn=trigger_image_upload,
                    inputs=[],
                    outputs=[],
                    js="""
                    () => { 
                        // 查找图片上传的file input
                        // 由于Gradio会为每个File组件创建input，我们需要找到第二个（图片上传的）
                        const fileInputs = Array.from(document.querySelectorAll('input[type=file]'));
                        // 找到accept属性包含image的input，或者第二个file input
                        let imageInput = fileInputs.find(input => 
                            input.accept && (
                                input.accept.includes('image') || 
                                input.accept.includes('image/*')
                            )
                        );
                        // 如果找不到，使用第二个file input（假设第一个是文档上传）
                        if (!imageInput && fileInputs.length > 1) {
                            imageInput = fileInputs[1];
                        }
                        if (imageInput) {
                            imageInput.click();
                        }
                    }
                    """
                )
                
                def generate_image_html(image_list):
                    """生成图片显示的HTML，包含删除按钮"""
                    if not image_list or len(image_list) == 0:
                        return '<div class="empty-gallery-message">暂无图片，请上传图片</div>'
                    
                    html_parts = ['<div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 10px;">']
                    
                    for idx, image_path in enumerate(image_list):
                        # 获取图片文件名用于显示
                        image_name = os.path.basename(image_path) if image_path else f"image_{idx}"
                        # 确保路径是有效的
                        if not image_path or not os.path.exists(image_path):
                            continue
                        
                        # 读取图片并转换为base64（用于在HTML中显示）
                        try:
                            with open(image_path, 'rb') as f:
                                image_data = f.read()
                                image_base64 = base64.b64encode(image_data).decode('utf-8')
                                # 根据文件扩展名确定MIME类型
                                ext = os.path.splitext(image_path)[1].lower()
                                mime_type = {
                                    '.jpg': 'image/jpeg',
                                    '.jpeg': 'image/jpeg',
                                    '.png': 'image/png',
                                    '.gif': 'image/gif',
                                    '.webp': 'image/webp'
                                }.get(ext, 'image/jpeg')
                                
                                image_src = f"data:{mime_type};base64,{image_base64}"
                        except Exception as e:
                            print(f"[Web UI] 读取图片失败 {image_path}: {e}")
                            continue
                        
                        html_parts.append(f'''
                        <div class="image-item-wrapper" data-image-index="{idx}">
                            <img src="{image_src}" alt="{image_name}" style="max-width: 200px; max-height: 200px; display: block;" />
                            <button class="image-delete-btn" onclick="window.deleteImage({idx})" title="删除图片">✕</button>
                        </div>
                        ''')
                    
                    html_parts.append('</div>')
                    return ''.join(html_parts)
                
                def handle_image_upload(files, current_images):
                    """处理图片上传：将新图片添加到列表"""
                    if files is None:
                        image_list = current_images or []
                        html_content = generate_image_html(image_list)
                        return image_list, gr.update(value=html_content)
                    
                    # 将单个文件或文件列表转换为列表
                    if not isinstance(files, list):
                        files = [files]
                    
                    # 获取当前图片列表
                    image_list = list(current_images) if current_images else []
                    
                    # 添加新图片
                    for file in files:
                        if file is not None:
                            # 获取图片路径
                            image_path = file.name if hasattr(file, 'name') else str(file)
                            # 避免重复添加
                            if image_path not in image_list:
                                image_list.append(image_path)
                    
                    html_content = generate_image_html(image_list)
                    return image_list, gr.update(value=html_content)
                
                def trigger_delete_image(delete_index_str, current_images):
                    """触发删除图片（从JavaScript调用）"""
                    try:
                        # 从字符串转换为整数
                        if not delete_index_str or delete_index_str == "":
                            image_list = current_images or []
                            html_content = generate_image_html(image_list)
                            return image_list, gr.update(value=html_content), gr.update(value="")
                        
                        delete_index = int(delete_index_str)
                        
                        if not current_images or delete_index < 0 or delete_index >= len(current_images):
                            image_list = current_images or []
                            html_content = generate_image_html(image_list)
                            return image_list, gr.update(value=html_content), gr.update(value="")
                        
                        # 创建新列表，移除指定索引的图片
                        new_images = list(current_images)
                        del new_images[delete_index]
                        
                        html_content = generate_image_html(new_images)
                        return new_images, gr.update(value=html_content), gr.update(value="")
                    except (ValueError, TypeError) as e:
                        print(f"[Web UI] 删除图片时出错: {e}")
                        image_list = current_images or []
                        html_content = generate_image_html(image_list)
                        return image_list, gr.update(value=html_content), gr.update(value="")
                
                # 删除图片事件（当delete_image_index改变时触发）
                delete_image_index.change(
                    fn=trigger_delete_image,
                    inputs=[delete_image_index, uploaded_images_state],
                    outputs=[uploaded_images_state, image_display, delete_image_index]
                )
                
                # 图片上传变化事件
                image_upload.change(
                    fn=handle_image_upload,
                    inputs=[image_upload, uploaded_images_state],
                    outputs=[uploaded_images_state, image_display]
                )
                
                # 文件上传/删除处理函数
                def handle_file_change(file):
                    """处理文件变化：显示/隐藏删除按钮，更新输出信息"""
                    if file is not None:
                        return (
                            gr.update(visible=True),  # 显示删除按钮
                            f"文件已上传: {os.path.basename(file.name)}"
                        )
                    else:
                        return (
                            gr.update(visible=False),  # 隐藏删除按钮
                            "请上传文件"
                        )
                
                def delete_file():
                    """删除文件：清除文件选择并隐藏删除按钮"""
                    return (
                        None,  # 清除文件
                        gr.update(visible=False),  # 隐藏删除按钮
                        "文件已删除，请重新上传文件"
                    )
                
                # 文件上传变化事件
                file_upload.change(
                    fn=handle_file_change,
                    inputs=[file_upload],
                    outputs=[delete_btn, output]
                )
                
                # 删除按钮点击事件
                delete_btn.click(
                    fn=delete_file,
                    inputs=[],
                    outputs=[file_upload, delete_btn, output]
                )
                
                # 预览模板按钮事件
                def show_template_preview(template_name):
                    preview_content = preview_template(template_name)
                    return gr.update(value=preview_content, visible=True)
                
                preview_btn.click(
                    fn=show_template_preview,
                    inputs=[journal_dropdown],
                    outputs=[template_preview]
                )
                
                # 生成按钮状态切换：点击后显示“正在生成中”，完成后恢复
                def set_generating_state():
                    return gr.update(value="正在生成中", interactive=False)

                def reset_generate_state():
                    return gr.update(value="生成LaTeX 📦", interactive=True)

                generate_btn.click(
                    fn=set_generating_state,
                    inputs=[],
                    outputs=[generate_btn],
                    queue=False,
                ).then(
                    fn=process_file,
                    inputs=[file_upload, journal_dropdown],
                    outputs=[output, download_link],
                ).then(
                    fn=reset_generate_state,
                    inputs=[],
                    outputs=[generate_btn],
                    queue=False,
                )
    
    return app

# 向后兼容：保留 create_ui 作为别名
def create_ui() -> gr.Blocks:
    """创建 Gradio Web UI（向后兼容别名）"""
    return create_interface()

if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)


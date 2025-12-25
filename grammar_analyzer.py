"""
语法分析核心模块
基于 LangExtract 的语法分析实现
"""

import os
import langextract as lx
from typing import List, Dict, Any, Optional
import tempfile


class GrammarAnalyzer:
    """语法分析器"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_id: str = "gemini-2.5-flash"
    ):
        """
        初始化语法分析器
        
        Args:
            api_key: API密钥（如果不提供，会从环境变量读取）
            model_id: 使用的模型ID
        """
        self.api_key = api_key or os.environ.get('LANGEXTRACT_API_KEY')
        self.model_id = model_id
        
        if not self.api_key:
            raise ValueError(
                "未找到 API Key。请设置 LANGEXTRACT_API_KEY 环境变量或传入 api_key 参数。"
            )
    
    def analyze_grammar(
        self,
        text: str,
        prompt: str,
        examples: List[lx.data.ExampleData]
    ) -> lx.data.AnnotatedDocument:
        """
        分析文本的语法结构
        
        Args:
            text: 要分析的文本
            prompt: 分析提示词
            examples: 示例数据
            
        Returns:
            分析结果
        """
        try:
            result = lx.extract(
                text_or_documents=text,
                prompt_description=prompt,
                examples=examples,
                model_id=self.model_id,
                api_key=self.api_key,
                fence_output=False,  # Gemini 不需要 fence
                use_schema_constraints=True  # 使用 schema 约束
            )
            return result
        except Exception as e:
            raise Exception(f"分析失败: {str(e)}")
    
    def generate_visualization(
        self,
        result: lx.data.AnnotatedDocument
    ) -> str:
        """
        生成可视化 HTML
        
        Args:
            result: 分析结果
            
        Returns:
            HTML 内容字符串
        """
        import json
        import shutil
        
        temp_dir = None
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp(prefix='langextract_')
            output_name = "grammar_analysis"
            
            # 方案1: 使用 LangExtract 的保存方法
            try:
                lx.io.save_annotated_documents(
                    [result],
                    output_name=output_name,
                    output_dir=temp_dir
                )
                
                # 检查多种可能的文件名
                possible_files = [
                    os.path.join(temp_dir, f"{output_name}.jsonl"),
                    os.path.join(temp_dir, "grammar_analysis.jsonl"),
                    os.path.join(temp_dir, "annotated_documents.jsonl"),
                ]
                
                output_path = None
                for path in possible_files:
                    if os.path.exists(path):
                        output_path = path
                        break
                
                if not output_path:
                    # 列出临时目录中的文件
                    files = os.listdir(temp_dir) if os.path.exists(temp_dir) else []
                    raise Exception(f"未找到 JSONL 文件。目录内容: {files}")
                
            except Exception as save_error:
                # 方案2: 手动创建 JSONL 文件
                output_path = os.path.join(temp_dir, f"{output_name}.jsonl")
                
                # 手动构建 JSONL 格式
                doc_dict = {
                    "text": result.text,
                    "extractions": [
                        {
                            "extraction_class": e.extraction_class,
                            "extraction_text": e.extraction_text,
                            "attributes": e.attributes,
                            "char_interval": {
                                "start_pos": e.char_interval.start_pos if e.char_interval else 0,
                                "end_pos": e.char_interval.end_pos if e.char_interval else len(e.extraction_text)
                            },
                        }
                        for e in result.extractions
                    ]
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(doc_dict, f, ensure_ascii=False)
                    f.write('\n')
            
            # 验证文件内容
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                if file_size == 0:
                    raise Exception("JSONL 文件为空")
            
            # 生成可视化
            html_content = lx.visualize(output_path)
            
            # 提取 HTML 内容
            if hasattr(html_content, 'data'):
                html_content = html_content.data
            elif not isinstance(html_content, str):
                html_content = str(html_content)
            
            return html_content
            
        except Exception as e:
            error_msg = f"可视化生成失败: {str(e)}"
            
            # 添加调试信息
            if temp_dir and os.path.exists(temp_dir):
                try:
                    files = os.listdir(temp_dir)
                    error_msg += f"\n临时目录文件: {files}"
                except:
                    pass
            
            raise Exception(error_msg)
            
        finally:
            # 清理临时文件
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
    
    def format_extractions(
        self,
        result: lx.data.AnnotatedDocument
    ) -> List[Dict[str, Any]]:
        """
        格式化提取结果为易读的字典列表
        
        Args:
            result: 分析结果
            
        Returns:
            格式化后的提取结果列表
        """
        formatted = []
        
        for extraction in result.extractions:
            # 尝试获取位置信息
            start_pos = extraction.char_interval.start_pos if extraction.char_interval else 0
            end_pos = extraction.char_interval.end_pos if extraction.char_interval else 0
            
            formatted.append({
                "类型": extraction.extraction_class,
                "文本": extraction.extraction_text,
                "属性": extraction.attributes,
                "位置": {
                    "开始": start_pos,
                    "结束": end_pos
                }
            })
        
        return formatted
    
    def get_statistics(
        self,
        result: lx.data.AnnotatedDocument
    ) -> Dict[str, Any]:
        """
        获取分析统计信息
        
        Args:
            result: 分析结果
            
        Returns:
            统计信息字典
        """
        extractions = result.extractions
        
        # 按类型统计
        type_counts = {}
        for extraction in extractions:
            extraction_type = extraction.extraction_class
            type_counts[extraction_type] = type_counts.get(extraction_type, 0) + 1
        
        # 计算覆盖率（安全处理位置信息）
        total_chars = 0
        for e in extractions:
            start = e.char_interval.start_pos if e.char_interval else 0
            end = e.char_interval.end_pos if e.char_interval else 0
            total_chars += (end - start)
        
        coverage = f"{total_chars / len(result.text) * 100:.1f}%" if len(result.text) > 0 else "0%"
        
        return {
            "总提取数": len(extractions),
            "类型统计": type_counts,
            "原文长度": len(result.text),
            "覆盖率": coverage
        }


def format_result_for_display(
    extractions: List[Dict[str, Any]],
    group_by: str = "类型"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    格式化结果用于展示
    
    Args:
        extractions: 提取结果列表
        group_by: 分组依据（类型/难度等）
        
    Returns:
        分组后的结果
    """
    grouped = {}
    
    for extraction in extractions:
        if group_by == "类型":
            key = extraction["类型"]
        elif group_by == "难度":
            key = extraction["属性"].get("level", "未知")
        else:
            key = "全部"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(extraction)
    
    return grouped


def create_simple_html_visualization(
    text: str,
    extractions: List[Dict[str, Any]],
    title: str = "语法分析结果"
) -> str:
    """
    创建简单的 HTML 可视化（不依赖 LangExtract）
    
    Args:
        text: 原始文本
        extractions: 提取结果列表
        title: 标题
        
    Returns:
        HTML 字符串
    """
    # 颜色映射
    color_map = {
        "subject": {"bg": "#FFE5E5", "border": "#FF6B6B", "label": "主语"},
        "verb": {"bg": "#E5F9F9", "border": "#4ECDC4", "label": "谓语"},
        "object": {"bg": "#E5F0FF", "border": "#45B7D1", "label": "宾语"},
        "direct_object": {"bg": "#E5F0FF", "border": "#45B7D1", "label": "直接宾语"},
        "indirect_object": {"bg": "#E8F5E9", "border": "#95D5B2", "label": "间接宾语"},
        "adverbial": {"bg": "#FFF3E0", "border": "#FFA07A", "label": "状语"},
        "phrasal_verb": {"bg": "#E8F5E9", "border": "#98D8C8", "label": "短语动词"},
        "key_word": {"bg": "#FFF9E6", "border": "#F7DC6F", "label": "重点词汇"},
        "idiom": {"bg": "#FFEEE5", "border": "#DDA15E", "label": "习语"},
        "attributive": {"bg": "#F5E6D3", "border": "#BC6C25", "label": "定语"},
        "complement": {"bg": "#E0F7FA", "border": "#A8DADC", "label": "补语"},
    }
    
    # 构建 HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="UTF-8">',
        f"<title>{title}</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f8f9fa; }",
        ".container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }",
        "h1 { color: #2c3e50; margin-bottom: 10px; }",
        ".subtitle { color: #7f8c8d; margin-bottom: 30px; }",
        ".text-container { background: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 2; font-size: 16px; margin-bottom: 30px; }",
        ".highlight { padding: 3px 6px; margin: 0 2px; border-radius: 4px; cursor: help; display: inline-block; transition: transform 0.2s; }",
        ".highlight:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }",
        ".legend { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px; }",
        ".legend-item { display: flex; align-items: center; gap: 8px; padding: 8px 15px; border-radius: 6px; background: #f8f9fa; }",
        ".legend-box { width: 20px; height: 20px; border-radius: 4px; border: 2px solid; }",
        ".details { margin-top: 30px; }",
        ".extraction-card { background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid; }",
        ".extraction-header { font-weight: bold; font-size: 18px; margin-bottom: 10px; }",
        ".extraction-text { background: white; padding: 10px 15px; border-radius: 6px; font-family: monospace; margin: 10px 0; }",
        ".attribute { display: inline-block; margin-right: 15px; margin-top: 5px; }",
        ".attribute-key { font-weight: bold; color: #7f8c8d; }",
        ".attribute-value { color: #2c3e50; }",
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f'<h1>{title}</h1>',
        '<p class="subtitle">点击或悬停查看详细信息</p>',
    ]
    
    # 图例
    used_types = set(e["类型"] for e in extractions)
    if used_types:
        html_parts.append('<div class="legend">')
        for extraction_type in used_types:
            if extraction_type in color_map:
                colors = color_map[extraction_type]
                html_parts.append(
                    f'<div class="legend-item">'
                    f'<div class="legend-box" style="background: {colors["bg"]}; border-color: {colors["border"]};"></div>'
                    f'<span>{colors["label"]} ({extraction_type})</span>'
                    f'</div>'
                )
        html_parts.append('</div>')
    
    # 带标注的文本
    html_parts.append('<div class="text-container">')
    
    # 过滤有效的提取
    valid_extractions = [
        e for e in extractions
        if e["位置"]["开始"] is not None and e["位置"]["结束"] is not None
        and 0 <= e["位置"]["开始"] < e["位置"]["结束"] <= len(text)
    ]
    
    if valid_extractions:
        sorted_extractions = sorted(valid_extractions, key=lambda x: x["位置"]["开始"])
        last_pos = 0
        
        for i, extraction in enumerate(sorted_extractions):
            start = extraction["位置"]["开始"]
            end = extraction["位置"]["结束"]
            
            # 添加未标记的文本
            if start > last_pos:
                html_parts.append(text[last_pos:start])
            
            # 添加标记的文本
            extraction_type = extraction["类型"]
            colors = color_map.get(extraction_type, {"bg": "#e9ecef", "border": "#adb5bd", "label": extraction_type})
            
            # 构建 tooltip
            attrs = extraction['属性']
            tooltip_parts = [f"{extraction_type}"]
            if 'role' in attrs:
                tooltip_parts.append(f"语法功能: {attrs['role']}")
            if 'meaning' in attrs:
                tooltip_parts.append(f"含义: {attrs['meaning']}")
            if 'type' in attrs and attrs['type'] != extraction_type:
                tooltip_parts.append(f"类型: {attrs['type']}")
            tooltip = " | ".join(tooltip_parts)
            
            html_parts.append(
                f'<span class="highlight" id="ext-{i}" '
                f'style="background: {colors["bg"]}; border: 2px solid {colors["border"]};" '
                f'title="{tooltip}" '
                f'onclick="scrollToDetail({i})">'
                f'{text[start:end]}'
                f'</span>'
            )
            
            last_pos = end
        
        # 添加剩余文本
        if last_pos < len(text):
            html_parts.append(text[last_pos:])
    else:
        html_parts.append(text)
    
    html_parts.append('</div>')
    
    # 详细信息
    if valid_extractions:
        html_parts.append('<div class="details">')
        html_parts.append('<h2>详细分析</h2>')
        
        for i, extraction in enumerate(sorted_extractions):
            extraction_type = extraction["类型"]
            colors = color_map.get(extraction_type, {"bg": "#e9ecef", "border": "#adb5bd"})
            
            html_parts.append(
                f'<div class="extraction-card" id="detail-{i}" style="border-color: {colors["border"]};">'
                f'<div class="extraction-header">#{i+1} {extraction["类型"]}</div>'
                f'<div class="extraction-text">{extraction["文本"]}</div>'
            )
            
            # 属性
            if extraction["属性"]:
                for key, value in extraction["属性"].items():
                    html_parts.append(
                        f'<div class="attribute">'
                        f'<span class="attribute-key">{key}:</span> '
                        f'<span class="attribute-value">{value}</span>'
                        f'</div>'
                    )
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # JavaScript
    html_parts.extend([
        "<script>",
        "function scrollToDetail(index) {",
        "  const element = document.getElementById('detail-' + index);",
        "  if (element) {",
        "    element.scrollIntoView({ behavior: 'smooth', block: 'center' });",
        "    element.style.background = '#fff3cd';",
        "    setTimeout(() => { element.style.background = '#f8f9fa'; }, 1000);",
        "  }",
        "}",
        "</script>",
        "</div>",
        "</body>",
        "</html>"
    ])
    
    return '\n'.join(html_parts)


def create_colored_text(
    extractions: List[Dict[str, Any]],
    group_by: str = "类型"
) -> Dict[str, List[Dict[str, Any]]]:
    """
    格式化结果用于展示
    
    Args:
        extractions: 提取结果列表
        group_by: 分组依据（类型/难度等）
        
    Returns:
        分组后的结果
    """
    grouped = {}
    
    for extraction in extractions:
        if group_by == "类型":
            key = extraction["类型"]
        elif group_by == "难度":
            key = extraction["属性"].get("level", "未知")
        else:
            key = "全部"
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(extraction)
    
    return grouped


def create_simple_html_visualization(
    text: str,
    extractions: List[Dict[str, Any]],
    title: str = "语法分析结果"
) -> str:
    """
    创建简单的 HTML 可视化（不依赖 LangExtract）
    
    Args:
        text: 原始文本
        extractions: 提取结果列表
        title: 标题
        
    Returns:
        HTML 字符串
    """
    # 颜色映射
    color_map = {
        "subject": {"bg": "#FFE5E5", "border": "#FF6B6B", "label": "主语"},
        "verb": {"bg": "#E5F9F9", "border": "#4ECDC4", "label": "谓语"},
        "object": {"bg": "#E5F0FF", "border": "#45B7D1", "label": "宾语"},
        "direct_object": {"bg": "#E5F0FF", "border": "#45B7D1", "label": "直接宾语"},
        "indirect_object": {"bg": "#E8F5E9", "border": "#95D5B2", "label": "间接宾语"},
        "adverbial": {"bg": "#FFF3E0", "border": "#FFA07A", "label": "状语"},
        "phrasal_verb": {"bg": "#E8F5E9", "border": "#98D8C8", "label": "短语动词"},
        "key_word": {"bg": "#FFF9E6", "border": "#F7DC6F", "label": "重点词汇"},
        "idiom": {"bg": "#FFEEE5", "border": "#DDA15E", "label": "习语"},
        "attributive": {"bg": "#F5E6D3", "border": "#BC6C25", "label": "定语"},
        "complement": {"bg": "#E0F7FA", "border": "#A8DADC", "label": "补语"},
    }
    
    # 构建 HTML
    html_parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="UTF-8">',
        f"<title>{title}</title>",
        "<style>",
        "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; padding: 20px; background: #f8f9fa; }",
        ".container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }",
        "h1 { color: #2c3e50; margin-bottom: 10px; }",
        ".subtitle { color: #7f8c8d; margin-bottom: 30px; }",
        ".text-container { background: #f8f9fa; padding: 20px; border-radius: 8px; line-height: 2; font-size: 16px; margin-bottom: 30px; }",
        ".highlight { padding: 3px 6px; margin: 0 2px; border-radius: 4px; cursor: help; display: inline-block; transition: transform 0.2s; }",
        ".highlight:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }",
        ".legend { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 30px; }",
        ".legend-item { display: flex; align-items: center; gap: 8px; padding: 8px 15px; border-radius: 6px; background: #f8f9fa; }",
        ".legend-box { width: 20px; height: 20px; border-radius: 4px; border: 2px solid; }",
        ".details { margin-top: 30px; }",
        ".extraction-card { background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid; }",
        ".extraction-header { font-weight: bold; font-size: 18px; margin-bottom: 10px; }",
        ".extraction-text { background: white; padding: 10px 15px; border-radius: 6px; font-family: monospace; margin: 10px 0; }",
        ".attribute { display: inline-block; margin-right: 15px; margin-top: 5px; }",
        ".attribute-key { font-weight: bold; color: #7f8c8d; }",
        ".attribute-value { color: #2c3e50; }",
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f'<h1>{title}</h1>',
        '<p class="subtitle">点击或悬停查看详细信息</p>',
    ]
    
    # 图例
    used_types = set(e["类型"] for e in extractions)
    if used_types:
        html_parts.append('<div class="legend">')
        for extraction_type in used_types:
            if extraction_type in color_map:
                colors = color_map[extraction_type]
                html_parts.append(
                    f'<div class="legend-item">'
                    f'<div class="legend-box" style="background: {colors["bg"]}; border-color: {colors["border"]};"></div>'
                    f'<span>{colors["label"]} ({extraction_type})</span>'
                    f'</div>'
                )
        html_parts.append('</div>')
    
    # 带标注的文本
    html_parts.append('<div class="text-container">')
    
    # 过滤有效的提取
    valid_extractions = [
        e for e in extractions
        if e["位置"]["开始"] is not None and e["位置"]["结束"] is not None
        and 0 <= e["位置"]["开始"] < e["位置"]["结束"] <= len(text)
    ]
    
    if valid_extractions:
        sorted_extractions = sorted(valid_extractions, key=lambda x: x["位置"]["开始"])
        last_pos = 0
        
        for i, extraction in enumerate(sorted_extractions):
            start = extraction["位置"]["开始"]
            end = extraction["位置"]["结束"]
            
            # 添加未标记的文本
            if start > last_pos:
                html_parts.append(text[last_pos:start])
            
            # 添加标记的文本
            extraction_type = extraction["类型"]
            colors = color_map.get(extraction_type, {"bg": "#e9ecef", "border": "#adb5bd", "label": extraction_type})
            
            # 构建 tooltip
            attrs = extraction['属性']
            tooltip_parts = [f"{extraction_type}"]
            if 'role' in attrs:
                tooltip_parts.append(f"语法功能: {attrs['role']}")
            if 'meaning' in attrs:
                tooltip_parts.append(f"含义: {attrs['meaning']}")
            if 'type' in attrs and attrs['type'] != extraction_type:
                tooltip_parts.append(f"类型: {attrs['type']}")
            tooltip = " | ".join(tooltip_parts)
            
            html_parts.append(
                f'<span class="highlight" id="ext-{i}" '
                f'style="background: {colors["bg"]}; border: 2px solid {colors["border"]};" '
                f'title="{tooltip}" '
                f'onclick="scrollToDetail({i})">'
                f'{text[start:end]}'
                f'</span>'
            )
            
            last_pos = end
        
        # 添加剩余文本
        if last_pos < len(text):
            html_parts.append(text[last_pos:])
    else:
        html_parts.append(text)
    
    html_parts.append('</div>')
    
    # 详细信息
    if valid_extractions:
        html_parts.append('<div class="details">')
        html_parts.append('<h2>详细分析</h2>')
        
        for i, extraction in enumerate(sorted_extractions):
            extraction_type = extraction["类型"]
            colors = color_map.get(extraction_type, {"bg": "#e9ecef", "border": "#adb5bd"})
            
            html_parts.append(
                f'<div class="extraction-card" id="detail-{i}" style="border-color: {colors["border"]};">'
                f'<div class="extraction-header">#{i+1} {extraction["类型"]}</div>'
                f'<div class="extraction-text">{extraction["文本"]}</div>'
            )
            
            # 属性
            if extraction["属性"]:
                for key, value in extraction["属性"].items():
                    html_parts.append(
                        f'<div class="attribute">'
                        f'<span class="attribute-key">{key}:</span> '
                        f'<span class="attribute-value">{value}</span>'
                        f'</div>'
                    )
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
    
    # JavaScript
    html_parts.extend([
        "<script>",
        "function scrollToDetail(index) {",
        "  const element = document.getElementById('detail-' + index);",
        "  if (element) {",
        "    element.scrollIntoView({ behavior: 'smooth', block: 'center' });",
        "    element.style.background = '#fff3cd';",
        "    setTimeout(() => { element.style.background = '#f8f9fa'; }, 1000);",
        "  }",
        "}",
        "</script>",
        "</div>",
        "</body>",
        "</html>"
    ])
    
    return '\n'.join(html_parts)


def create_colored_text(
    text: str,
    extractions: List[Dict[str, Any]],
    color_map: Optional[Dict[str, str]] = None
) -> str:
    """
    创建带颜色标记的文本（用于 Streamlit 展示）
    
    Args:
        text: 原始文本
        extractions: 提取结果
        color_map: 类型到颜色的映射
        
    Returns:
        HTML 格式的彩色文本
    """
    if color_map is None:
        color_map = {
            "subject": "#FF6B6B",
            "verb": "#4ECDC4",
            "object": "#45B7D1",
            "direct_object": "#45B7D1",
            "indirect_object": "#95D5B2",
            "adverbial": "#FFA07A",
            "phrasal_verb": "#98D8C8",
            "key_word": "#F7DC6F",
            "idiom": "#DDA15E",
            "attributive": "#BC6C25",
            "complement": "#A8DADC",
        }
    
    # 过滤掉没有有效位置信息的提取
    valid_extractions = [
        e for e in extractions 
        if e["位置"]["开始"] is not None and e["位置"]["结束"] is not None
        and e["位置"]["开始"] >= 0 and e["位置"]["结束"] > e["位置"]["开始"]
    ]
    
    # 如果没有有效的位置信息，返回原文
    if not valid_extractions:
        return text
    
    # 按位置排序
    sorted_extractions = sorted(
        valid_extractions,
        key=lambda x: x["位置"]["开始"]
    )
    
    # 构建 HTML
    html_parts = []
    last_pos = 0
    
    for extraction in sorted_extractions:
        start = extraction["位置"]["开始"]
        end = extraction["位置"]["结束"]
        
        # 跳过无效范围
        if start >= len(text) or end > len(text) or start >= end:
            continue
        
        # 添加未标记的文本
        if start > last_pos:
            html_parts.append(text[last_pos:start])
        
        # 添加标记的文本
        color = color_map.get(extraction["类型"], "#CCCCCC")
        
        # 构建丰富的 tooltip 内容
        tooltip_lines = [f"<strong>{extraction['类型']}</strong>"]
        if extraction['属性']:
            tooltip_lines.append("<hr style='margin: 5px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.3);'>")
            for k, v in extraction['属性'].items():
                tooltip_lines.append(f"<div><span style='opacity:0.8'>{k}:</span> {v}</div>")
        
        tooltip_html = "".join(tooltip_lines)
        
        html_parts.append(
            f'<span class="tooltip-wrapper" style="background-color: {color}; '
            f'padding: 2px 4px; border-radius: 3px;">'
            f'{text[start:end]}'
            f'<span class="tooltip-text">{tooltip_html}</span>'
            f'</span>'
        )
        
        last_pos = max(last_pos, end)  # 避免重叠
    
    # 添加剩余文本
    if last_pos < len(text):
        html_parts.append(text[last_pos:])
    
    return ''.join(html_parts)


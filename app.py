"""
语法分析 Demo - Streamlit 应用
基于 Google LangExtract
"""

import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from grammar_analyzer import (
    GrammarAnalyzer, 
    format_result_for_display, 
    create_colored_text,
    create_simple_html_visualization
)
from examples import (
    get_grammar_examples,
    get_phrase_examples,
    get_keyword_examples,
    get_combined_examples,
    PROMPTS
)

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="语法分析 Demo - LangExtract",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    /* Custom Tooltip CSS */
    .tooltip-wrapper {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted black; /* If you want to underline */
        cursor: help;
    }

    .tooltip-text {
        visibility: hidden;
        min-width: 200px;
        max-width: 400px;
        background-color: #262730 !important;
        color: #fff !important;
        text-align: left;
        border-radius: 8px;
        padding: 12px;
        position: absolute;
        z-index: 999999;
        top: 130%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.2s;
        font-size: 0.9rem;
        font-family: sans-serif;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        white-space: normal;
        pointer-events: none;
    }
    
    .tooltip-text::after {
        content: "";
        position: absolute;
        bottom: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: transparent transparent #262730 transparent;
    }

    .tooltip-wrapper:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* Custom Button Colors */
    
    /* Button 1: Grammar (Blue) */
    div[data-testid="column"]:nth-of-type(1) button[kind="primary"],
    div[data-testid="stColumn"]:nth-of-type(1) button[kind="primary"] {
        background-color: #2196F3 !important;
        border-color: #2196F3 !important;
    }
    div[data-testid="column"]:nth-of-type(1) button[kind="primary"]:hover,
    div[data-testid="stColumn"]:nth-of-type(1) button[kind="primary"]:hover {
        background-color: #1976D2 !important;
        border-color: #1976D2 !important;
    }
    
    /* Button 2: Keyword (Orange) */
    div[data-testid="column"]:nth-of-type(2) button[kind="primary"],
    div[data-testid="stColumn"]:nth-of-type(2) button[kind="primary"] {
        background-color: #FF9800 !important;
        border-color: #FF9800 !important;
    }
    div[data-testid="column"]:nth-of-type(2) button[kind="primary"]:hover,
    div[data-testid="stColumn"]:nth-of-type(2) button[kind="primary"]:hover {
        background-color: #F57C00 !important;
        border-color: #F57C00 !important;
    }


</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<h1 class="main-header">📝 语法分析 Demo</h1>', unsafe_allow_html=True)


# 初始化 session state
if 'user_text' not in st.session_state:
    st.session_state.user_text = ""

# API Key Check
api_key = os.environ.get('LANGEXTRACT_API_KEY')

# 尝试从 Streamlit Secrets 获取 (用于云端部署)
if not api_key:
    try:
        if 'LANGEXTRACT_API_KEY' in st.secrets:
            api_key = st.secrets['LANGEXTRACT_API_KEY']
    except FileNotFoundError:
        pass

if not api_key:
    st.error("⚠️ 未设置 API Key，请在 .env 文件中配置 LANGEXTRACT_API_KEY，或在 Streamlit Cloud Secrets 中配置。")
    st.stop()

# Hardcoded model
model_id = "gemini-3-flash-preview"

# 初始化分析器
try:
    analyzer = GrammarAnalyzer(api_key=api_key, model_id=model_id)
except Exception as e:
    st.error(f"初始化失败: {str(e)}")
    st.stop()

# 输入区域
st.markdown('<div class="info-box">输入你想分析的英语句子，或从下方选择示例</div>', unsafe_allow_html=True)

user_text = st.text_area(
    "输入文本",
    height=150,
    placeholder="例如: The quick brown fox jumps over the lazy dog.",
    label_visibility="collapsed",
    key="user_text"
)

# 示例句子 (紧凑展示)
sample_sentences = [
    "I can share another truth with you. Because of a global supply chain shortage, there are not enough folding chairs. So half of you had to sit on blankets today. Fortunately, our staff, who are amazing, creative, resilient, and made this commencement become a reality.",
    "Photosynthesis is the biological process by which plants convert light energy into chemical energy, creating oxygen as a byproduct, which supports life on Earth.",
    "The algorithm demonstrates remarkable efficiency in processing large datasets, utilizing advanced heuristics to minimize computational complexity while maintaining high accuracy.",
    "Despite the heavy rain and strong winds, the dedicated team continued their rescue mission, determined to save every stranded villager before nightfall.",
    "Understanding quantum mechanics requires abandoning classical intuition, as particles exist in superposition states until observed, challenging our fundamental perception of reality.",
    "The quick brown fox jumps over the lazy dog."
]

st.markdown('<div style="margin-bottom: 5px; color: #666; font-size: 0.9em;">📚 试一试:</div>', unsafe_allow_html=True)
sample_cols = st.columns(2)  # 使用两列布局使其更紧凑

for i, sentence in enumerate(sample_sentences, 1):
    # 使用回调函数更新 session_state
    def update_text(text=sentence):
        st.session_state.user_text = text
    
    col_idx = (i - 1) % 2
    with sample_cols[col_idx]:
        st.button(
            f"{i}. {sentence[:40]}..." if len(sentence) > 40 else f"{i}. {sentence}",
            key=f"sample_{i}",
            on_click=update_text,
            use_container_width=True,
            help=sentence
        )

st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

# 功能入口按钮
col1, col2 = st.columns(2)
action = None

with col1:
    if st.button("语法成分分析", use_container_width=True, type="primary"):
        action = "grammar"
with col2:
    if st.button("重点单词标记", use_container_width=True, type="primary"):
        action = "keyword"

# 执行分析
if action and user_text:
    if action == "grammar":
        examples = get_grammar_examples()
        prompt = PROMPTS["grammar"]
        analysis_type = "语法成分分析"
    elif action == "keyword":
        examples = get_keyword_examples()
        prompt = PROMPTS["keyword"]
        analysis_type = "重点单词标记"
    
    with st.spinner(f"正在进行 {analysis_type}..."):
        try:
            # 执行分析
            result = analyzer.analyze_grammar(
                text=user_text,
                prompt=prompt,
                examples=examples
            )
            
            # 格式化结果
            extractions = analyzer.format_extractions(result)
            
            # 显示结果标题
            st.markdown(f'<h3 class="sub-header">📊 {analysis_type}结果</h3>', unsafe_allow_html=True)
            
            # 原文标注展示
            st.subheader("原文标注")
            
            # 创建彩色文本
            colored_html = create_colored_text(user_text, extractions)
            st.markdown(f'<div class="tooltip-container" style="line-height: 2.0; font-size: 1.1em;">{colored_html}</div>', unsafe_allow_html=True)
            
            # 详细结果 (默认折叠)
            st.markdown('<h3 class="sub-header">📋 详细分析</h3>', unsafe_allow_html=True)
            
            # 按类型分组展示
            grouped = format_result_for_display(extractions, group_by="类型")
            
            for extraction_type, items in grouped.items():
                with st.expander(f"**{extraction_type}** ({len(items)} 个)", expanded=False):
                    for item in items:
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.markdown(f"**文本**: `{item['文本']}`")
                        with col_b:
                            # Safe attributes handling
                            attrs = item.get('属性') or {}
                            if attrs:
                                attributes_str = " | ".join(
                                    [f"**{k}**: {v}" for k, v in attrs.items()]
                                )
                                st.markdown(attributes_str)
                            else:
                                st.caption("无详细属性")
                        st.divider()
            
        except Exception as e:
            st.error(f"❌ 分析失败: {str(e)}")
            st.exception(e)




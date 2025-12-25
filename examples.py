"""
语法分析示例数据
用于 LangExtract 的 few-shot learning
"""

import langextract as lx

def get_grammar_examples():
    """
    语法成分分析示例
    包括：主语、谓语、宾语、定语、状语、补语
    注意：所有示例都包含精确的位置信息（start_char, end_char）
    """
    return [
        lx.data.ExampleData(
            text="The quick brown fox jumps over the lazy dog.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="subject",
                    extraction_text="The quick brown fox",
                    char_interval=lx.data.CharInterval(start_pos=0, end_pos=19),
                    attributes={
                        "type": "noun_phrase",
                        "role": "主语",
                        "description": "句子的执行者"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="verb",
                    extraction_text="jumps",
                    char_interval=lx.data.CharInterval(start_pos=20, end_pos=25),
                    attributes={
                        "type": "intransitive_verb",
                        "tense": "present",
                        "role": "谓语",
                        "description": "描述动作"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="adverbial",
                    extraction_text="over the lazy dog",
                    char_interval=lx.data.CharInterval(start_pos=26, end_pos=43),
                    attributes={
                        "type": "prepositional_phrase",
                        "role": "状语",
                        "description": "修饰动词，表示地点"
                    }
                ),
            ]
        ),
        lx.data.ExampleData(
            text="She gave me a beautiful gift yesterday.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="subject",
                    extraction_text="She",
                    char_interval=lx.data.CharInterval(start_pos=0, end_pos=3),
                    attributes={
                        "type": "pronoun",
                        "role": "主语",
                        "description": "句子的执行者"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="verb",
                    extraction_text="gave",
                    char_interval=lx.data.CharInterval(start_pos=4, end_pos=8),
                    attributes={
                        "type": "transitive_verb",
                        "tense": "past",
                        "role": "谓语",
                        "description": "描述动作"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="indirect_object",
                    extraction_text="me",
                    char_interval=lx.data.CharInterval(start_pos=9, end_pos=11),
                    attributes={
                        "type": "pronoun",
                        "role": "间接宾语",
                        "description": "动作的接受者"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="direct_object",
                    extraction_text="a beautiful gift",
                    char_interval=lx.data.CharInterval(start_pos=12, end_pos=28),
                    attributes={
                        "type": "noun_phrase",
                        "role": "直接宾语",
                        "description": "动作的对象"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="adverbial",
                    extraction_text="yesterday",
                    char_interval=lx.data.CharInterval(start_pos=29, end_pos=38),
                    attributes={
                        "type": "time_adverb",
                        "role": "状语",
                        "description": "修饰动词，表示时间"
                    }
                ),
            ]
        ),
    ]


def get_phrase_examples():
    """
    固定搭配识别示例
    包括：短语动词、固定搭配、习惯用语
    注意：包含精确的位置信息
    """
    return [
        lx.data.ExampleData(
            text="I'm looking forward to hearing from you soon.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="phrasal_verb",
                    extraction_text="looking forward to",
                    char_interval=lx.data.CharInterval(start_pos=4, end_pos=22),
                    attributes={
                        "type": "固定搭配",
                        "meaning": "期待",
                        "usage": "look forward to + 动名词",
                        "level": "中级"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="phrasal_verb",
                    extraction_text="hearing from",
                    char_interval=lx.data.CharInterval(start_pos=23, end_pos=35),
                    attributes={
                        "type": "动词短语",
                        "meaning": "收到...的来信",
                        "usage": "hear from + 人",
                        "level": "基础"
                    }
                ),
            ]
        ),
        lx.data.ExampleData(
            text="She decided to give up smoking for health reasons.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="phrasal_verb",
                    extraction_text="give up",
                    char_interval=lx.data.CharInterval(start_pos=18, end_pos=25),
                    attributes={
                        "type": "短语动词",
                        "meaning": "放弃",
                        "usage": "give up + 动名词/名词",
                        "level": "基础"
                    }
                ),
            ]
        ),
        lx.data.ExampleData(
            text="It's raining cats and dogs outside.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="idiom",
                    extraction_text="raining cats and dogs",
                    char_interval=lx.data.CharInterval(start_pos=5, end_pos=26),
                    attributes={
                        "type": "习惯用语",
                        "meaning": "倾盆大雨",
                        "usage": "形容雨下得很大",
                        "level": "高级"
                    }
                ),
            ]
        ),
    ]


def get_keyword_examples():
    """
    重点单词标记示例
    包括：高级词汇、学术词汇、专业术语
    注意：包含精确的位置信息
    """
    return [
        lx.data.ExampleData(
            text="Photosynthesis is the biological process by which plants convert light energy into chemical energy.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="Photosynthesis",
                    char_interval=lx.data.CharInterval(start_pos=0, end_pos=14),
                    attributes={
                        "level": "高级",
                        "type": "学术词汇",
                        "meaning": "光合作用",
                        "subject": "生物学",
                        "importance": "高"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="biological",
                    char_interval=lx.data.CharInterval(start_pos=22, end_pos=32),
                    attributes={
                        "level": "中级",
                        "type": "形容词",
                        "meaning": "生物学的",
                        "subject": "科学",
                        "importance": "中"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="convert",
                    char_interval=lx.data.CharInterval(start_pos=62, end_pos=69),
                    attributes={
                        "level": "中级",
                        "type": "动词",
                        "meaning": "转换，转化",
                        "subject": "通用",
                        "importance": "中"
                    }
                ),
            ]
        ),
        lx.data.ExampleData(
            text="The algorithm demonstrates remarkable efficiency in processing large datasets.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="algorithm",
                    char_interval=lx.data.CharInterval(start_pos=4, end_pos=13),
                    attributes={
                        "level": "高级",
                        "type": "专业术语",
                        "meaning": "算法",
                        "subject": "计算机科学",
                        "importance": "高"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="efficiency",
                    char_interval=lx.data.CharInterval(start_pos=38, end_pos=48),
                    attributes={
                        "level": "中级",
                        "type": "名词",
                        "meaning": "效率",
                        "subject": "通用",
                        "importance": "中"
                    }
                ),
            ]
        ),
    ]


def get_combined_examples():
    """
    综合分析示例（包含所有类型）
    注意：包含精确的位置信息，这个例子展示了如何标注同一个词（looked up）的多重功能
    """
    return [
        lx.data.ExampleData(
            text="The talented student looked up the difficult vocabulary in the dictionary.",
            extractions=[
                # 语法成分
                lx.data.Extraction(
                    extraction_class="subject",
                    extraction_text="The talented student",
                    char_interval=lx.data.CharInterval(start_pos=0, end_pos=20),
                    attributes={
                        "type": "noun_phrase",
                        "role": "主语"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="verb",
                    extraction_text="looked up",
                    char_interval=lx.data.CharInterval(start_pos=21, end_pos=30),
                    attributes={
                        "type": "phrasal_verb",
                        "role": "谓语"
                    }
                ),
                lx.data.Extraction(
                    extraction_class="object",
                    extraction_text="the difficult vocabulary",
                    char_interval=lx.data.CharInterval(start_pos=31, end_pos=55),
                    attributes={
                        "type": "noun_phrase",
                        "role": "宾语"
                    }
                ),
                # 固定搭配（和谓语重叠，但从不同角度分析）
                lx.data.Extraction(
                    extraction_class="phrasal_verb",
                    extraction_text="looked up",
                    char_interval=lx.data.CharInterval(start_pos=21, end_pos=30),
                    attributes={
                        "type": "短语动词",
                        "meaning": "查阅",
                        "level": "基础"
                    }
                ),
                # 重点单词
                lx.data.Extraction(
                    extraction_class="key_word",
                    extraction_text="vocabulary",
                    char_interval=lx.data.CharInterval(start_pos=45, end_pos=55),
                    attributes={
                        "level": "中级",
                        "type": "名词",
                        "meaning": "词汇",
                        "importance": "高"
                    }
                ),
            ]
        ),
    ]


# 预设的提示词模板
PROMPTS = {
    "grammar": """
分析英语句子的语法结构，提取以下成分：

1. **主语 (subject)**: 句子的执行者或主题
2. **谓语 (verb)**: 描述动作或状态的动词
3. **宾语 (object/direct_object/indirect_object)**: 动作的接受者或对象
4. **定语 (attributive)**: 修饰名词的成分
5. **状语 (adverbial)**: 修饰动词、形容词或句子的成分
6. **补语 (complement)**: 补充说明主语或宾语的成分

要求：
- **必须提供精确的 start_char 和 end_char**，这对于准确高亮非常重要
- 准确识别每个成分在原文中的位置
- 为每个成分提供中文释义
- 说明成分的语法功能
- 使用完整的原文片段，不要截断
""",
    
    "phrase": """
识别英语句子中的固定搭配和短语：

1. **短语动词 (phrasal_verb)**: 如 look up, give up, take off 等
2. **固定搭配 (collocation)**: 如 make a decision, take a break 等
3. **习惯用语 (idiom)**: 如 break the ice, piece of cake 等
4. **介词短语 (prepositional_phrase)**: 常用的介词搭配

要求：
- **必须提供精确的 start_char 和 end_char**，对于重复短语，每个位置都要独立标注
- 识别完整的短语，不要遗漏介词或副词
- 提供中文释义和用法说明
- 标注难度等级（基础/中级/高级）
- 说明使用场景和注意事项
""",
    
    "keyword": """
标记句子中的重点单词和核心词汇：

1. **高级词汇**: 高中及以上水平的词汇
2. **学术词汇**: 学科专业术语
3. **核心动词**: 重要的行为动词
4. **关键名词**: 主题相关的核心名词

要求：
- **必须提供精确的 start_char 和 end_char**，对于重复单词，每次出现都要标注
- 只标记重要的词汇，不要标记基础词汇（如 the, is, a 等）
- 提供中文释义
- 标注难度等级和学科领域
- 说明重要程度（高/中/低）
""",
    
    "combined": """
对英语句子进行全面的语法和词汇分析：

1. **语法成分**: 主语、谓语、宾语、状语等
2. **固定搭配**: 短语动词、习惯用语等
3. **重点词汇**: 高级词汇、专业术语等

要求：
- **必须为所有提取提供精确的 start_char 和 end_char**
- 全面分析句子结构和关键内容
- 为每个提取的内容提供详细的属性说明
- 使用中文进行解释
- 标注难度等级和重要程度
- 对于重复内容或重叠标注，确保每个都有独立的位置信息
"""
}


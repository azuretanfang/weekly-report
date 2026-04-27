# 项目架构说明

## 📁 项目结构

```
english-reading-skill/
├── skill.yaml                          # Skill配置文件
├── README.md                           # 功能介绍
├── QUICKSTART.md                       # 快速开始指南
├── requirements.txt                    # Python依赖
├── __init__.py                         # Python包初始化
├── main.py                             # 主程序入口
├── test_functionality.py               # 功能测试脚本
│
├── src/                                # 核心模块目录
│   ├── __init__.py
│   ├── parser.py                       # 内容解析器（URL/文件/文本）
│   ├── nlp_analyzer.py                 # NLP分析引擎
│   ├── ai_analysis.py                  # AI分析（Claude API）
│   ├── html_generator.py               # HTML报告生成器
│   ├── tts_handler.py                  # TTS音频和Anki导出
│   └── vocab_manager.py                # [待实现] 单词本管理
│
└── assets/                             # 资源文件
    └── vocab_db.json                   # 开源词汇库
```

---

## 🔧 核心模块详解

### 1. **parser.py** - 内容解析器
```python
ContentParser.parse(content, input_type='auto')
```
- 支持文本、URL、文件输入
- 自动类型检测
- HTML文本提取
- 返回标题和正文

**功能**：
- `parse_text()` - 解析纯文本
- `parse_url()` - 从网页提取正文
- `parse_file()` - 读取.txt/.md文件

---

### 2. **nlp_analyzer.py** - NLP分析引擎
```python
analyzer = NLPAnalyzer()
vocab_info = analyzer.extract_vocabulary(text)
readability = analyzer.analyze_readability(text)
complex_sents = analyzer.extract_complex_sentences(text)
```

**功能**：
- 词汇等级分类（Common/Intermediate/Advanced）
- 难度评分（0-1，基于COCA语料库频率）
- 可读性指标（句长、平均音节数、CEFR等级）
- 复杂句子识别和简化建议

**输出示例**：
```json
{
  "unique_words": 150,
  "difficulty_score": 0.65,
  "vocabulary_by_level": {
    "common": ["the", "is", "and"],
    "intermediate": ["artificial", "intelligence"],
    "advanced": ["sophisticated", "paradigm"]
  },
  "complexity_level": "B2"
}
```

---

### 3. **ai_analysis.py** - Claude API驱动分析

#### ErrorPatternAnalyzer - 错误句型识别
```python
errors = ErrorPatternAnalyzer.identify_error_patterns(sentences)
breakdown = SentenceBreakdownHelper.breakdown_sentence(sentence)
```

**识别类型**：
- ❌ 搭配错误 (Collocation)
- ❌ 时态误用 (Tense Issues)
- ❌ 冠词问题 (Article Errors)
- ❌ 单复数 (Number Agreement)
- ❌ 介词错误 (Preposition Errors)
- ❌ 语序问题 (Word Order)
- ❌ 情态动词 (Modal Verb Issues)

**输出格式**：
```json
{
  "error_type": "Collocation Error",
  "sentence": "She make a mistake.",
  "incorrect_form": "❌ make a mistake",
  "correct_form": "✅ make a mistake",
  "explanation": "Wrong subject-verb agreement..."
}
```

---

### 4. **html_generator.py** - HTML报告生成
```python
html = HTMLReportGenerator.generate_report(
    title, original_text, analysis_data, error_patterns,
    complex_sentences, summary
)
```

**报告特性**：
- 📖 **双栏响应式设计**
  - 左栏：原文（句子可点击高亮）
  - 右栏：注解（错误、词汇、分析）
  
- 🎨 **交互功能**
  - 点击生词添加到词汇表
  - 句子高亮和定位
  - 标签页切换
  
- 📊 **内容模块**
  - 元数据（难度、词数、错误数）
  - 错误句型分析
  - 复杂句子分解
  - 词汇分布分析
  - 文章摘要

---

### 5. **tts_handler.py** - 音频和Anki导出

#### 组件：
```python
# 1. 音标生成
ipa = PhoneticTranscriber.generate_ipa_proper("beautiful")
# 返回: /ˈbjuːtɪfl/

# 2. TTS音频生成
TTSAudioGenerator.generate_sentence_audio(
    "Artificial intelligence is transforming industries.",
    "output.mp3"
)

# 3. Anki卡片创建
card = VocabularyCardGenerator.create_anki_card(
    word="intelligence",
    pronunciation="/ɪnˈtelɪdʒəns/",
    definition="智力，聪慧",
    example_sentence="...",
    example_translation="...",
    difficulty_level="intermediate"
)

# 4. 导出为CSV或APKG
AnkiExporter.export_to_csv(cards, "output.csv")
AnkiExporter.export_to_apkg(cards, "English Reading", "output.apkg")
```

**Anki卡片结构**：
```
正面：
  [单词] / [音标] / [单词音频]

反面：
  [中文释义]
  [例句] / [例句翻译] / [例句音频]
  [难度等级]
```

---

## 🔄 完整分析流程

```
输入 (URL/文件/文本)
    ↓
[1] 内容解析 (parser.py)
    ├─ URL → HTML提取正文
    ├─ 文件 → 文本读取
    └─ 文本 → 直接处理
    ↓
[2] NLP分析 (nlp_analyzer.py)
    ├─ 句子分词
    ├─ 词汇提取 + 等级分类
    ├─ 可读性分析
    └─ 复杂句子识别
    ↓
[3] AI分析 (ai_analysis.py)
    ├─ 错误句型识别 (Claude API)
    ├─ 句子分解
    └─ 关键句子提取
    ↓
[4] HTML报告 (html_generator.py)
    ├─ 双栏布局生成
    ├─ 交互脚本注入
    └─ CSS样式应用
    ↓
[5] Anki导出 (tts_handler.py)
    ├─ 音标生成 (IPA)
    ├─ 音频生成 (Google TTS)
    └─ 卡片导出 (CSV/APKG)
    ↓
输出 (HTML + CSV + 音频文件)
```

---

## 🚀 使用示例

### 命令行用法

```bash
# 基础用法
python main.py "Your English text"

# 分析网页
python main.py "https://www.bbc.com/news"

# 分析文件
python main.py "article.txt" --input-type file

# 指定输出目录
python main.py "text" -o ./reports

# 跳过某些导出
python main.py "text" --no-html --no-anki
```

### Python API用法

```python
from main import EnglishReadingAnalyzer

analyzer = EnglishReadingAnalyzer(output_dir="./reports")

result = analyzer.analyze(
    content="Your English text here",
    input_type='text',
    export_anki=True,
    export_html=True
)

print(f"HTML report: {result['html_report']}")
print(f"Anki export: {result['anki_export']}")
```

---

## 📊 数据流转

### 词汇库 (vocab_db.json)
```json
{
  "common": [单词列表],      // A1-B1常用词
  "intermediate": [单词列表], // B2中级词
  "advanced": [单词列表]     // C1-C2高级词
}
```

### 输出JSON示例
```json
{
  "success": true,
  "title": "Article Title",
  "vocabulary_info": {
    "unique_words": 150,
    "difficulty_score": 0.65,
    "vocabulary_by_level": {...}
  },
  "readability": {
    "complexity_level": "B2",
    "sentence_count": 10,
    "word_count": 200
  },
  "error_patterns": [{...}],
  "complex_sentences": [{...}],
  "html_report": "/path/to/report.html",
  "anki_export": "/path/to/vocab.csv"
}
```

---

## 🔌 依赖关系

```
main.py
  ├─ parser.py ─────────────┐
  ├─ nlp_analyzer.py ────────┼─ Shared data flow
  ├─ ai_analysis.py ─────────┤
  ├─ html_generator.py ──────┤
  └─ tts_handler.py ─────────┘

外部依赖：
  ├─ Claude API (anthropic)
  ├─ Google TTS (gtts)
  ├─ Anki导出 (genanki)
  ├─ NLP工具 (nltk)
  └─ 网页解析 (requests, html.parser)
```

---

## 🎯 Phase 2 - 智能分析功能

计划添加：

1. **句子分解优化**
   - 更深入的语法树分析
   - 从句识别和分类
   - 语法成分标注

2. **高级错误识别**
   - 习惯用语（Idioms）错误
   - 方言和寄存器混淆
   - 常见语言陷阱

3. **学习路径生成**
   - 基于难度的学习建议
   - 个性化词汇推荐
   - 复习间隔优化

---

## 📝 维护和扩展

### 添加新的错误类型

编辑 `ai_analysis.py`，更新 `ERROR_PATTERNS_PROMPT`：

```python
ERROR_PATTERNS_PROMPT = """
    ... 现有内容 ...
    8. **新错误类型** - 具体描述
"""
```

### 扩展词汇库

编辑 `assets/vocab_db.json`，添加更多词汇或使用专业词汇库：
- Academic Word List (AWL)
- TOEFL/IELTS专项词汇
- 行业专用词汇

### 改进难度算法

修改 `nlp_analyzer.py` 的 `_estimate_complexity_level()` 方法。

---

**最后更新**: 2026-04-24
**版本**: 1.0.0
**维护者**: fangtan

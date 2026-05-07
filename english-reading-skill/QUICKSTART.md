# 🚀 Quick Start Guide

> ⚠️ **v1.2.0 公告**：自 v1.2.0 起已**移除 Anki 单词卡生成与导出**能力。本文档中涉及 `--no-anki`、`genanki`、`export_anki=...`、`anki_export` 的内容仅作历史参考，当前版本不再支持。请直接使用 HTML 精读报告。
>
> 🆕 **v1.3.0 公告**：CEFR 算法已从经验公式升级为 `textstat`（Flesch-Kincaid Grade + Dale-Chall），词汇分级新增 `wordfreq` 频率 fallback。新增依赖：`wordfreq>=3.0.0`（约 70MB）；缺失时自动降级，不影响主流程。安装命令请见 `requirements.txt`。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 基础使用

### 1️⃣ 分析纯文本

```bash
python main.py "Your English text here"
```

### 2️⃣ 分析网页URL

```bash
python main.py "https://www.bbc.com/news/article"
```

### 3️⃣ 分析本地文件

```bash
python main.py "./article.txt" --input-type file
```

## 高级选项

### 指定输出目录

```bash
python main.py "text" -o ./my_reports
```

### 跳过HTML报告

```bash
python main.py "text" --no-html
```

### 跳过Anki导出

```bash
python main.py "text" --no-anki
```

## 输出文件

每次分析会生成：

1. **HTML报告** - `{title}_report.html`
   - 双栏响应式设计
   - 常见错误句型分析
   - 词汇等级分类
   - 复杂句子分解

2. **Anki卡片** - `{title}_vocab.csv`
   - 包含音标
   - 词汇等级标注
   - 可直接导入Anki

## 示例流程

```bash
# 1. 分析BBC新闻
python main.py "https://www.bbc.com/news/business" -o ./reports

# 2. 打开生成的HTML报告
# 报告文件位置: ./reports/news_report.html

# 3. 导入Anki卡片
# 打开Anki -> 导入 -> 选择 ./reports/news_vocab.csv
```

## 常见问题

### Q: 如何获取Claude API密钥？

A: 访问 https://console.anthropic.com/，获取API密钥并设置环境变量：

```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Q: Anki导出失败怎么办？

A: 确保已安装genanki：
```bash
pip install genanki
```

### Q: 如何加快分析速度？

A: 
- 使用 `--no-html` 跳过HTML报告生成
- 使用较短的文本进行测试
- 增加Claude API超时设置

## 特性说明

✨ **AI驱动分析**
- 使用Claude 3.5 Sonnet识别常见错误
- 自动拆解复杂句子
- 智能摘要提取

📊 **词汇分析**
- 自动分类词汇等级（Common/Intermediate/Advanced）
- 统计词汇分布
- 生成难度评分

🎤 **音频支持**
- Google TTS生成音频
- 支持单词发音
- 支持例句朗读

📱 **响应式设计**
- 支持桌面、平板、手机
- 双栏联动滚动
- 点击生词添加到词汇表

---

**需要帮助？**
查看 README.md 了解完整功能说明

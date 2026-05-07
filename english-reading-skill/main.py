#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 - 英文精读报告生成器入口
"""

import os
import re
import sys
import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Tuple, List

# 导入模块
from src.parser import ContentParser
from src.nlp_analyzer import NLPAnalyzer
from src.ai_analysis import ErrorPatternAnalyzer, SentenceBreakdownHelper
from src.html_generator import HTMLReportGenerator
from src.tts_handler import (
    PhoneticTranscriber,
    TTSAudioGenerator,
)

# ============= v1.1.1 新增常量 =============
# Y-14：最小文本阈值（词数），低于此值进入"简化模式"，避免 73:1 膨胀比输出
MIN_WORDS_FOR_FULL_ANALYSIS = 10
# 并行度（Y-28/Y-29）：3 足以覆盖目前 2~3 个独立 AI 步骤，避免过高并发触发 Claude 速率限制
MAX_PARALLEL_WORKERS = 3

# ============= v1.2.0 新增：输入安全检测常量 =============
# P1-2：CJK 字符比例阈值（≥30% 即判为非英文输入，礼貌拒绝）
CJK_REJECT_RATIO = 0.30
# CJK 字符范围：CJK Unified Ideographs 主要区段（覆盖中日韩汉字主体）
_CJK_PATTERN = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]')

# P1-3：Prompt 注入检测正则（覆盖常见劫持模式，case-insensitive）
_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r'\[\s*system\s+override\s*\]', re.IGNORECASE),
    re.compile(r'\bignore\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|prompts?|rules?)', re.IGNORECASE),
    re.compile(r'\bdisregard\s+(?:all\s+)?(?:previous|above|prior)\s+(?:instructions?|prompts?|rules?)', re.IGNORECASE),
    re.compile(r'<\s*/?\s*(?:system|admin|developer)\s*>', re.IGNORECASE),
    re.compile(r'\bact\s+as\s+(?:a\s+)?(?:dan|jailbreak|developer\s+mode)', re.IGNORECASE),
    re.compile(r'\bnew\s+(?:instructions?|task|role)\s*:\s*', re.IGNORECASE),
    re.compile(r'###\s*(?:system|instructions?|new\s+task)\s*###', re.IGNORECASE),
]


def _detect_cjk(text: str) -> Tuple[bool, float]:
    """
    P1-2：检测输入文本中 CJK 字符比例。

    Returns:
        (is_cjk_dominant, ratio): 是否判定为 CJK 主导输入；CJK 字符占比（0~1）
    """
    if not text:
        return False, 0.0
    cjk_chars = _CJK_PATTERN.findall(text)
    # 仅统计非空白字符作为分母，避免空格/换行稀释比例
    non_space_chars = [c for c in text if not c.isspace()]
    if not non_space_chars:
        return False, 0.0
    ratio = len(cjk_chars) / len(non_space_chars)
    return ratio >= CJK_REJECT_RATIO, ratio


def _detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
    """
    P1-3：检测 Prompt 注入模式，返回命中的注入片段列表（用于透明展示）。

    Returns:
        (is_injected, hits): 是否检测到注入；命中的原文片段列表（截断至 80 字符）
    """
    if not text:
        return False, []
    hits: List[str] = []
    for pattern in _INJECTION_PATTERNS:
        for match in pattern.finditer(text):
            snippet = match.group(0).strip()
            if snippet and snippet[:80] not in hits:
                hits.append(snippet[:80])
    return bool(hits), hits


def _strip_injection(text: str) -> str:
    """剥离注入片段后返回剩余文本（用于继续分析合法部分）。"""
    cleaned = text
    for pattern in _INJECTION_PATTERNS:
        cleaned = pattern.sub(' ', cleaned)
    # 折叠多余空白
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


class EnglishReadingAnalyzer:
    """英文精读分析器 - 主控制器"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化分析器

        Args:
            output_dir: 输出目录（默认当前目录）
        """
        self.output_dir = Path(output_dir or ".")
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.nlp_analyzer = NLPAnalyzer()
        self.temp_dir = tempfile.TemporaryDirectory()

    def analyze(
        self,
        content: str,
        input_type: str = 'auto',
        export_html: bool = True,
    ) -> dict:
        """
        完整的分析流程

        Args:
            content: 输入内容（文本/URL/文件路径）
            input_type: 输入类型 ('auto'/'url'/'file'/'text')
            export_html: 是否导出HTML报告

        Returns:
            分析结果字典
        """
        print("=" * 60)
        print("🚀 Starting English Reading Analysis")
        print("=" * 60)

        # Step 1: 解析输入
        print("\n[1/6] Parsing input content...")
        try:
            title, text = ContentParser.parse(content, input_type)
            print(f"✅ Title: {title}")
            print(f"✅ Content length: {len(text)} characters")
        except Exception as e:
            print(f"❌ Parse error: {str(e)}")
            return {'success': False, 'error': str(e)}

        # ========== v1.2.0 P1-2：CJK 输入检测（解析后第一道闸） ==========
        is_cjk, cjk_ratio = _detect_cjk(text)
        if is_cjk:
            msg = (
                f"⚠️ 检测到输入文本包含 {cjk_ratio:.0%} 的 CJK（中日韩）字符，"
                "本工具仅支持英文文本精读分析。"
            )
            print(f"\n{msg}")
            return {
                'success': False,
                'reason': 'non_english_input',
                'cjk_ratio': round(cjk_ratio, 4),
                'error': msg,
                'guidance': (
                    "请提供英文文本/URL/文件作为输入。"
                    "如需中文翻译，建议使用专门的翻译工具。"
                ),
            }

        # ========== v1.2.0 P1-3：Prompt 注入检测（剥离后再分析） ==========
        injected, injection_hits = _detect_prompt_injection(text)
        injection_notice = None
        if injected:
            cleaned_text = _strip_injection(text)
            injection_notice = (
                f"⚠️ 检测到 {len(injection_hits)} 处疑似 Prompt 注入指令，已忽略并剥离："
                + "; ".join(f"`{h}`" for h in injection_hits[:5])
            )
            print(f"\n{injection_notice}")
            # 若剥离后剩余内容过短，直接拒绝
            if len(cleaned_text.split()) < MIN_WORDS_FOR_FULL_ANALYSIS:
                return {
                    'success': False,
                    'reason': 'prompt_injection_dominant',
                    'injection_hits': injection_hits,
                    'error': '输入主要由注入指令构成，无可分析的合法英文内容。',
                    'notice': injection_notice,
                }
            # 否则替换 text 继续走完整流程
            text = cleaned_text

        # Y-14：极短文本切换简化模式
        word_count_quick = len(text.split())
        simplified_mode = word_count_quick < MIN_WORDS_FOR_FULL_ANALYSIS
        if simplified_mode:
            print(
                f"\n⚠️ 输入仅 {word_count_quick} 词，低于最小阈值 {MIN_WORDS_FOR_FULL_ANALYSIS}，"
                "进入简化模式（跳过 AI 深度分析以避免空洞输出）"
            )
            return self._analyze_simplified(title, text, word_count_quick, export_html)

        # Step 2: NLP分析
        print("\n[2/6] Performing NLP analysis...")
        try:
            vocab_info = self.nlp_analyzer.extract_vocabulary(text)
            readability = self.nlp_analyzer.analyze_readability(text)

            print(f"✅ Unique words: {vocab_info['unique_words']}")
            print(f"✅ Complexity level: {readability['complexity_level']}")
            print(f"✅ Difficulty score: {vocab_info['difficulty_score']:.2f}")
        except Exception as e:
            print(f"❌ NLP analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}

        # Y-28/Y-29：Step 3 & 4 & 5 并行（这三步互不依赖，都只读 text/sentences）
        print("\n[3-5/6] Running AI / key-sentence steps in parallel...")
        sentences = self.nlp_analyzer.tokenize_sentences(text)

        def _task_error_patterns():
            try:
                result = ErrorPatternAnalyzer.identify_error_patterns(sentences[:10])
                # 兼容 v1.1.0：result 为 dict，错误时 errors=[]
                if isinstance(result, dict):
                    return result.get('errors', []) or [], result.get('error_flag', False), result.get('error_message')
                return result or [], False, None
            except Exception as e:
                return [], True, str(e)

        def _task_complex_sentences():
            try:
                return self.nlp_analyzer.extract_complex_sentences(text), None
            except Exception as e:
                return [], str(e)

        def _task_key_sentences():
            try:
                return ErrorPatternAnalyzer.extract_key_sentences(text, 3), None
            except Exception as e:
                return [], str(e)

        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as pool:
            fut_err = pool.submit(_task_error_patterns)
            fut_cx = pool.submit(_task_complex_sentences)
            fut_key = pool.submit(_task_key_sentences)

            error_patterns, err_flag, err_msg = fut_err.result()
            complex_sentences, cx_err = fut_cx.result()
            key_sentences, key_err = fut_key.result()

        if err_flag:
            print(f"⚠️ Error pattern analysis degraded: {err_msg or 'unknown'}")
        else:
            print(f"✅ Error patterns found: {len(error_patterns)}")
        if cx_err:
            print(f"⚠️ Complex sentence analysis error: {cx_err}")
        else:
            print(f"✅ Complex sentences found: {len(complex_sentences)}")

        # Step 5: 生成摘要（依赖 key_sentences）
        summary = " ".join(key_sentences[:2]) if key_sentences else (text[:200] + "...")
        if key_err:
            print(f"⚠️ Summary fallback to prefix due to: {key_err}")
        else:
            print(f"✅ Summary generated: {len(summary)} characters")

        # Step 6: 生成HTML报告
        print("\n[6/6] Generating HTML report...")
        html_path = None
        try:
            analysis_data = {
                'vocabulary_info': vocab_info,
                'readability': readability,
            }

            html_content = HTMLReportGenerator.generate_report(
                title=title,
                original_text=text,
                analysis_data=analysis_data,
                error_patterns=error_patterns,
                complex_sentences=complex_sentences,
                summary=summary
            )

            if export_html:
                html_path = self.output_dir / f"{title}_report.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ HTML report saved: {html_path}")

        except Exception as e:
            print(f"❌ HTML generation error: {str(e)}")
            html_content = ""

        # 总结
        print("\n" + "=" * 60)
        print("✨ Analysis Complete!")
        print("=" * 60)

        return {
            'success': True,
            'mode': 'full',
            'title': title,
            'vocabulary_info': vocab_info,
            'readability': readability,
            'error_patterns': error_patterns,
            'complex_sentences': complex_sentences,
            'summary': summary,
            'html_report': str(html_path) if (export_html and html_path) else None,
            'injection_notice': injection_notice,
        }

    # ---------- Y-14：简化模式 ----------
    def _analyze_simplified(
        self,
        title: str,
        text: str,
        word_count: int,
        export_html: bool,
    ) -> dict:
        """
        极短文本（<10 词）的简化分析路径。
        - 不调用 Claude API（避免为 2~3 个词调一次深度拆解）
        - 仅输出基础信息 + 明确的提示语
        """
        try:
            vocab_info = self.nlp_analyzer.extract_vocabulary(text)
            readability = self.nlp_analyzer.analyze_readability(text)
        except Exception as e:
            return {'success': False, 'error': f'simplified-mode NLP error: {e}'}

        notice = (
            f"⚠️ 输入文本仅 {word_count} 词（阈值 {MIN_WORDS_FOR_FULL_ANALYSIS} 词），"
            "已自动切换到简化模式。如需完整的错误句型识别、复杂句拆解，"
            "请提供至少 10 词的英文段落或文章。"
        )
        print(notice)

        html_path = None
        if export_html:
            try:
                html_content = HTMLReportGenerator.generate_report(
                    title=title,
                    original_text=text,
                    analysis_data={
                        'vocabulary_info': vocab_info,
                        'readability': readability,
                        'simplified_mode_notice': notice,
                    },
                    error_patterns=[],
                    complex_sentences=[],
                    summary=text,  # 文本太短，摘要即原文
                )
                html_path = self.output_dir / f"{title}_report.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"✅ HTML report (simplified) saved: {html_path}")
            except Exception as e:
                print(f"⚠️ HTML generation error (simplified): {e}")

        return {
            'success': True,
            'mode': 'simplified',
            'title': title,
            'word_count': word_count,
            'notice': notice,
            'vocabulary_info': vocab_info,
            'readability': readability,
            'error_patterns': [],
            'complex_sentences': [],
            'summary': text,
            'html_report': str(html_path) if html_path else None,
        }

    def cleanup(self):
        """清理临时文件"""
        self.temp_dir.cleanup()


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-Powered English Reading Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Your English text here"
  python main.py "https://www.bbc.com/news/article"
  python main.py "./article.txt" --input-type file
  python main.py "text.txt" -o ./reports
        """
    )

    parser.add_argument(
        'content',
        help='Input content (text, URL, or file path)'
    )
    parser.add_argument(
        '-t', '--input-type',
        choices=['auto', 'text', 'url', 'file'],
        default='auto',
        help='Input type (default: auto-detect)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory'
    )
    parser.add_argument(
        '--no-html',
        action='store_true',
        help='Skip HTML report generation'
    )

    args = parser.parse_args()

    # 创建分析器
    analyzer = EnglishReadingAnalyzer(output_dir=args.output_dir)

    try:
        # 执行分析
        result = analyzer.analyze(
            content=args.content,
            input_type=args.input_type,
            export_html=not args.no_html,
        )

        # 输出结果
        if result['success']:
            print(f"\n📊 Report generated successfully!")
            if result.get('html_report'):
                print(f"📄 HTML: {result['html_report']}")
        else:
            print(f"\n❌ Analysis failed: {result.get('error')}")
            sys.exit(1)

    finally:
        analyzer.cleanup()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序 - 英文精读报告生成器入口
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Optional

# 导入模块
from src.parser import ContentParser
from src.nlp_analyzer import NLPAnalyzer
from src.ai_analysis import ErrorPatternAnalyzer, SentenceBreakdownHelper
from src.html_generator import HTMLReportGenerator
from src.tts_handler import (
    PhoneticTranscriber,
    TTSAudioGenerator,
    VocabularyCardGenerator,
    AnkiExporter
)


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
        export_anki: bool = True,
        export_html: bool = True
    ) -> dict:
        """
        完整的分析流程
        
        Args:
            content: 输入内容（文本/URL/文件路径）
            input_type: 输入类型 ('auto'/'url'/'file'/'text')
            export_anki: 是否导出Anki卡片
            export_html: 是否导出HTML报告
            
        Returns:
            分析结果字典
        """
        print("=" * 60)
        print("🚀 Starting English Reading Analysis")
        print("=" * 60)
        
        # Step 1: 解析输入
        print("\n[1/7] Parsing input content...")
        try:
            title, text = ContentParser.parse(content, input_type)
            print(f"✅ Title: {title}")
            print(f"✅ Content length: {len(text)} characters")
        except Exception as e:
            print(f"❌ Parse error: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        # Step 2: NLP分析
        print("\n[2/7] Performing NLP analysis...")
        try:
            vocab_info = self.nlp_analyzer.extract_vocabulary(text)
            readability = self.nlp_analyzer.analyze_readability(text)
            
            print(f"✅ Unique words: {vocab_info['unique_words']}")
            print(f"✅ Complexity level: {readability['complexity_level']}")
            print(f"✅ Difficulty score: {vocab_info['difficulty_score']:.2f}")
        except Exception as e:
            print(f"❌ NLP analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}
        
        # Step 3: 错误句型识别
        print("\n[3/7] Identifying error patterns...")
        try:
            sentences = self.nlp_analyzer.tokenize_sentences(text)
            error_patterns = ErrorPatternAnalyzer.identify_error_patterns(sentences[:10])
            print(f"✅ Error patterns found: {len(error_patterns)}")
        except Exception as e:
            print(f"⚠️ Error pattern analysis error: {str(e)}")
            error_patterns = []
        
        # Step 4: 复杂句子分析
        print("\n[4/7] Analyzing complex sentences...")
        try:
            complex_sentences = self.nlp_analyzer.extract_complex_sentences(text)
            print(f"✅ Complex sentences found: {len(complex_sentences)}")
        except Exception as e:
            print(f"⚠️ Complex sentence analysis error: {str(e)}")
            complex_sentences = []
        
        # Step 5: 生成摘要
        print("\n[5/7] Generating summary...")
        try:
            key_sentences = ErrorPatternAnalyzer.extract_key_sentences(text, 3)
            summary = " ".join(key_sentences[:2])
            if not summary:
                summary = text[:200] + "..."
            print(f"✅ Summary generated: {len(summary)} characters")
        except Exception as e:
            print(f"⚠️ Summary generation error: {str(e)}")
            summary = text[:200] + "..."
        
        # Step 6: 生成HTML报告
        print("\n[6/7] Generating HTML report...")
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
        
        # Step 7: Anki导出
        print("\n[7/7] Generating Anki cards...")
        anki_path = None
        try:
            if export_anki:
                cards = []
                vocab_by_level = vocab_info.get('vocabulary_by_level', {})
                
                # 从高级词汇开始创建卡片
                for level in ['advanced', 'intermediate', 'common']:
                    for word in vocab_by_level.get(level, [])[:5]:  # 每个等级最多5个词
                        # 生成音标
                        ipa = PhoneticTranscriber.generate_ipa_proper(word)
                        
                        # 创建卡片（不生成音频，以加快速度）
                        card = VocabularyCardGenerator.create_anki_card(
                            word=word,
                            pronunciation=ipa,
                            definition=f"Word from reading: {title}",
                            example_sentence=text[:100],
                            example_translation="Example from the article",
                            difficulty_level=level
                        )
                        cards.append(card)
                
                if cards:
                    # 导出为CSV（更快）
                    csv_path = self.output_dir / f"{title}_vocab.csv"
                    success = AnkiExporter.export_to_csv(cards, str(csv_path))
                    if success:
                        print(f"✅ Anki cards exported: {csv_path} ({len(cards)} cards)")
                        anki_path = str(csv_path)
                    else:
                        print(f"⚠️ Anki export failed")
                
        except Exception as e:
            print(f"⚠️ Anki generation error: {str(e)}")
        
        # 总结
        print("\n" + "=" * 60)
        print("✨ Analysis Complete!")
        print("=" * 60)
        
        return {
            'success': True,
            'title': title,
            'vocabulary_info': vocab_info,
            'readability': readability,
            'error_patterns': error_patterns,
            'complex_sentences': complex_sentences,
            'summary': summary,
            'html_report': html_path if export_html else None,
            'anki_export': anki_path,
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
  python main.py "text.txt" -o ./reports --export-anki
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
    parser.add_argument(
        '--no-anki',
        action='store_true',
        help='Skip Anki export'
    )
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = EnglishReadingAnalyzer(output_dir=args.output_dir)
    
    try:
        # 执行分析
        result = analyzer.analyze(
            content=args.content,
            input_type=args.input_type,
            export_anki=not args.no_anki,
            export_html=not args.no_html
        )
        
        # 输出结果
        if result['success']:
            print(f"\n📊 Report generated successfully!")
            if result.get('html_report'):
                print(f"📄 HTML: {result['html_report']}")
            if result.get('anki_export'):
                print(f"🃏 Anki: {result['anki_export']}")
        else:
            print(f"\n❌ Analysis failed: {result.get('error')}")
            sys.exit(1)
    
    finally:
        analyzer.cleanup()


if __name__ == '__main__':
    main()

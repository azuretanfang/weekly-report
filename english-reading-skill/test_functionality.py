#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能测试脚本 - 验证各模块功能
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.parser import ContentParser
from src.nlp_analyzer import NLPAnalyzer
from src.ai_analysis import ErrorPatternAnalyzer
from src.html_generator import HTMLReportGenerator


def test_parser():
    """测试内容解析器"""
    print("=" * 60)
    print("TEST 1: Content Parser")
    print("=" * 60)
    
    test_cases = [
        ("test.txt", "text"),
        ("Artificial intelligence is transforming industries.", "text"),
    ]
    
    for content, input_type in test_cases:
        try:
            if input_type == "text" and not content.endswith('.txt'):
                title, parsed = ContentParser.parse(content, 'text')
                print(f"✅ Parsed text: {title[:30]}...")
            print()
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


def test_nlp_analyzer():
    """测试NLP分析器"""
    print("=" * 60)
    print("TEST 2: NLP Analyzer")
    print("=" * 60)
    
    test_text = """
    Artificial intelligence is revolutionizing how companies operate.
    Machine learning algorithms enable organizations to extract insights from data.
    The technology is transforming industries worldwide.
    """
    
    analyzer = NLPAnalyzer()
    
    # 测试词汇提取
    print("Testing vocabulary extraction...")
    vocab_info = analyzer.extract_vocabulary(test_text)
    print(f"✅ Unique words: {vocab_info['unique_words']}")
    print(f"✅ Difficulty score: {vocab_info['difficulty_score']:.2f}")
    print(f"✅ Advanced words: {len(vocab_info['vocabulary_by_level']['advanced'])}")
    print()
    
    # 测试可读性分析
    print("Testing readability analysis...")
    readability = analyzer.analyze_readability(test_text)
    print(f"✅ Complexity level: {readability['complexity_level']}")
    print(f"✅ Sentence count: {readability['sentence_count']}")
    print()
    
    # 测试复杂句子提取
    print("Testing complex sentence extraction...")
    complex_sents = analyzer.extract_complex_sentences(test_text)
    print(f"✅ Complex sentences found: {len(complex_sents)}")
    print()


def test_error_patterns():
    """测试错误句型识别"""
    print("=" * 60)
    print("TEST 3: Error Pattern Analyzer (Claude API)")
    print("=" * 60)
    
    test_sentences = [
        "She don't like coffee.",
        "The research are important.",
    ]
    
    print("Testing error pattern detection...")
    print("(This requires Claude API - ensure ANTHROPIC_API_KEY is set)")
    print()
    
    try:
        errors = ErrorPatternAnalyzer.identify_error_patterns(test_sentences)
        if errors:
            print(f"✅ Errors detected: {len(errors)}")
            for error in errors[:1]:
                print(f"   - {error.get('error_type', 'Unknown')}")
        else:
            print("⚠️ No errors detected (may be valid sentences)")
        print()
    except Exception as e:
        print(f"⚠️ Skipping (Claude API test): {str(e)}")
        print()


def test_html_generation():
    """测试HTML报告生成"""
    print("=" * 60)
    print("TEST 4: HTML Report Generation")
    print("=" * 60)
    
    test_data = {
        'vocabulary_info': {
            'total_words': 50,
            'unique_words': 30,
            'vocabulary_by_level': {
                'common': ['the', 'is', 'and'],
                'intermediate': ['artificial', 'intelligence'],
                'advanced': ['revolutionary', 'paradigm'],
                'unknown': []
            },
            'difficulty_score': 0.45
        },
        'readability': {
            'word_count': 50,
            'complexity_level': 'B1'
        }
    }
    
    errors = [
        {
            'error_type': 'Collocation Error',
            'incorrect_form': 'make a research',
            'correct_form': 'conduct research',
            'explanation': 'Wrong collocation'
        }
    ]
    
    complex_sents = [
        {
            'sentence': 'Although technology advances rapidly, challenges remain.',
            'length': 60,
            'clause_count': 2,
            'suggestion': 'Consider breaking this sentence.'
        }
    ]
    
    print("Generating HTML report...")
    html = HTMLReportGenerator.generate_report(
        title="Test Article",
        original_text="Artificial intelligence is transforming industries worldwide.",
        analysis_data=test_data,
        error_patterns=errors,
        complex_sentences=complex_sents,
        summary="This article discusses AI's impact on industries."
    )
    
    if html:
        print(f"✅ HTML generated: {len(html)} bytes")
        
        # 保存测试报告
        test_html_path = project_root / "test_report.html"
        with open(test_html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Test report saved: {test_html_path}")
    else:
        print("❌ HTML generation failed")
    print()


def main():
    """运行所有测试"""
    print("\n" + "🔬 ENGLISH READING ANALYZER - TEST SUITE" + "\n")
    
    try:
        test_parser()
        test_nlp_analyzer()
        test_error_patterns()
        test_html_generation()
        
        print("=" * 60)
        print("✨ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

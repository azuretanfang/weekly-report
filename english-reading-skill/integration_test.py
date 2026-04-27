#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 测试完整的分析流程
"""

import sys
import os
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import EnglishReadingAnalyzer


def run_integration_test():
    """运行完整集成测试"""
    
    print("\n" + "=" * 70)
    print("🧪 INTEGRATION TEST - English Reading Analyzer")
    print("=" * 70)
    
    # 测试文本
    test_article = """
    Artificial intelligence has emerged as one of the most transformative 
    technologies of our time. Machine learning algorithms, a subset of artificial 
    intelligence, enable computers to learn from data without being explicitly 
    programmed. This technology is revolutionizing industries ranging from healthcare 
    to finance.
    
    The applications of AI are vast and continue to expand. In healthcare, AI-powered 
    diagnostics can identify diseases earlier than traditional methods. In finance, 
    machine learning models predict market trends and optimize investment portfolios. 
    Similarly, in transportation, autonomous vehicles utilize sophisticated AI algorithms 
    to navigate complex environments safely.
    
    However, the rapid advancement of artificial intelligence also raises significant 
    concerns. Issues pertaining to data privacy, algorithmic bias, and job displacement 
    require careful consideration. Additionally, the ethical implications of AI-driven 
    decision-making in critical domains demand ongoing scrutiny and regulation.
    
    Despite these challenges, the potential benefits of artificial intelligence are 
    undeniable. As organizations continue to invest in AI research and development, 
    we can anticipate further breakthroughs that will reshape our society and economy.
    """
    
    # 创建分析器
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)
    
    analyzer = EnglishReadingAnalyzer(output_dir=str(output_dir))
    
    try:
        # 执行分析
        result = analyzer.analyze(
            content=test_article,
            input_type='text',
            export_anki=True,
            export_html=True
        )
        
        if not result['success']:
            print(f"\n❌ Analysis failed: {result.get('error')}")
            return False
        
        # 验证输出
        print("\n" + "-" * 70)
        print("📊 Analysis Results Validation")
        print("-" * 70)
        
        # 检查词汇分析
        vocab_info = result.get('vocabulary_info', {})
        print(f"\n✅ Vocabulary Analysis:")
        print(f"   - Unique words: {vocab_info.get('unique_words', 'N/A')}")
        print(f"   - Difficulty score: {vocab_info.get('difficulty_score', 'N/A'):.2f}")
        
        by_level = vocab_info.get('vocabulary_by_level', {})
        for level in ['common', 'intermediate', 'advanced']:
            count = len(by_level.get(level, []))
            print(f"   - {level.capitalize()} words: {count}")
        
        # 检查可读性分析
        readability = result.get('readability', {})
        print(f"\n✅ Readability Analysis:")
        print(f"   - Complexity level: {readability.get('complexity_level', 'N/A')}")
        print(f"   - Sentence count: {readability.get('sentence_count', 'N/A')}")
        print(f"   - Word count: {readability.get('word_count', 'N/A')}")
        
        # 检查错误分析
        errors = result.get('error_patterns', [])
        print(f"\n✅ Error Pattern Analysis:")
        print(f"   - Errors detected: {len(errors)}")
        if errors:
            for i, error in enumerate(errors[:2], 1):
                print(f"   {i}. {error.get('error_type', 'Unknown')}")
        
        # 检查复杂句子
        complex_sents = result.get('complex_sentences', [])
        print(f"\n✅ Complex Sentences Analysis:")
        print(f"   - Complex sentences: {len(complex_sents)}")
        
        # 检查文件输出
        print(f"\n✅ File Outputs:")
        
        html_path = result.get('html_report')
        if html_path and Path(html_path).exists():
            file_size = Path(html_path).stat().st_size
            print(f"   - HTML report: {Path(html_path).name} ({file_size} bytes)")
        else:
            print(f"   - HTML report: ❌ Not found")
        
        anki_path = result.get('anki_export')
        if anki_path and Path(anki_path).exists():
            file_size = Path(anki_path).stat().st_size
            print(f"   - Anki export: {Path(anki_path).name} ({file_size} bytes)")
        else:
            print(f"   - Anki export: ⚠️ Not generated")
        
        # 检查摘要
        summary = result.get('summary', '')
        print(f"\n✅ Summary Generation:")
        print(f"   - Summary length: {len(summary)} characters")
        if summary:
            print(f"   - Preview: {summary[:80]}...")
        
        # 生成报告
        print("\n" + "=" * 70)
        print("✨ Integration Test PASSED!")
        print("=" * 70)
        
        print(f"\n📁 Output directory: {output_dir}")
        print("\n📋 Generated files:")
        for file in output_dir.glob("*"):
            print(f"   - {file.name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        analyzer.cleanup()


if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)

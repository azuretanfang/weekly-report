#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成器 - 生成双栏响应式精读报告
"""

import json
import html as html_escape
from typing import Dict, List, Any
from datetime import datetime


class HTMLReportGenerator:
    """生成HTML精读报告"""
    
    TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - 英文精读报告</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 0.9em;
                opacity: 0.9;
            }}
            
            .meta-info {{
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-bottom: 1px solid #ddd;
                font-size: 0.9em;
            }}
            
            .meta-item {{
                display: flex;
                gap: 10px;
            }}
            
            .meta-label {{
                font-weight: bold;
                color: #667eea;
            }}
            
            .content {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0;
                min-height: 600px;
            }}
            
            .original-text {{
                padding: 30px;
                border-right: 2px solid #ddd;
                overflow-y: auto;
                max-height: 600px;
                background: #ffffff;
            }}
            
            .annotations {{
                padding: 30px;
                overflow-y: auto;
                max-height: 600px;
                background: #f8f9fa;
            }}
            
            .text-content {{
                line-height: 1.8;
                font-size: 1.05em;
                color: #333;
            }}
            
            .sentence {{
                margin: 20px 0;
                padding: 15px;
                border-left: 4px solid transparent;
                transition: all 0.3s ease;
            }}
            
            .sentence:hover {{
                background: #f0f0f0;
                border-left-color: #667eea;
                cursor: pointer;
            }}
            
            .sentence.highlighted {{
                background: #fff3cd;
                border-left-color: #ffc107;
            }}
            
            .difficult-word {{
                background: #fff3cd;
                padding: 2px 6px;
                border-radius: 3px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s;
            }}
            
            .difficult-word:hover {{
                background: #ffe69c;
                text-decoration: underline;
            }}
            
            .word-level-common {{
                color: #28a745;
            }}
            
            .word-level-intermediate {{
                color: #ff9800;
            }}
            
            .word-level-advanced {{
                color: #dc3545;
            }}
            
            .annotation-item {{
                margin: 15px 0;
                padding: 15px;
                background: white;
                border-left: 4px solid #667eea;
                border-radius: 4px;
                font-size: 0.95em;
            }}
            
            .annotation-title {{
                font-weight: bold;
                color: #667eea;
                margin-bottom: 8px;
            }}
            
            .error-pattern {{
                margin: 15px 0;
                padding: 15px;
                background: #ffe6e6;
                border-left: 4px solid #dc3545;
                border-radius: 4px;
            }}
            
            .error-pattern .error-type {{
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 5px;
            }}
            
            .error-pattern .incorrect {{
                color: #dc3545;
                text-decoration: line-through;
                margin: 5px 0;
            }}
            
            .error-pattern .correct {{
                color: #28a745;
                font-weight: bold;
                margin: 5px 0;
            }}
            
            .error-pattern .explanation {{
                font-size: 0.9em;
                color: #666;
                margin-top: 8px;
                line-height: 1.6;
            }}
            
            .complex-sentence {{
                margin: 15px 0;
                padding: 15px;
                background: #e8f4f8;
                border-left: 4px solid #17a2b8;
                border-radius: 4px;
            }}
            
            .complex-sentence-title {{
                font-weight: bold;
                color: #17a2b8;
                margin-bottom: 8px;
            }}
            
            .breakdown {{
                background: white;
                padding: 10px;
                border-radius: 3px;
                margin: 8px 0;
                font-size: 0.9em;
            }}
            
            .summary-section {{
                padding: 30px;
                background: #e8f4f8;
                border-top: 2px solid #17a2b8;
            }}
            
            .summary-title {{
                font-size: 1.3em;
                font-weight: bold;
                color: #17a2b8;
                margin-bottom: 15px;
            }}
            
            .summary-content {{
                line-height: 1.8;
                color: #333;
            }}
            
            .key-phrases {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 15px 0;
            }}
            
            .phrase-tag {{
                background: #667eea;
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.85em;
            }}
            
            .tabs {{
                display: flex;
                gap: 10px;
                margin: 15px 0;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            
            .tab {{
                padding: 8px 16px;
                background: transparent;
                border: none;
                cursor: pointer;
                font-weight: 500;
                color: #666;
                border-bottom: 3px solid transparent;
                transition: all 0.2s;
            }}
            
            .tab.active {{
                color: #667eea;
                border-bottom-color: #667eea;
            }}
            
            .tab-content {{
                display: none;
            }}
            
            .tab-content.active {{
                display: block;
            }}
            
            @media (max-width: 1024px) {{
                .content {{
                    grid-template-columns: 1fr;
                    gap: 0;
                }}
                
                .original-text {{
                    border-right: none;
                    border-bottom: 2px solid #ddd;
                    max-height: none;
                }}
                
                .annotations {{
                    max-height: none;
                }}
            }}
            
            .difficulty-badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 0.8em;
                font-weight: bold;
                margin: 5px 0;
            }}
            
            .difficulty-A1 {{ background: #d4edda; color: #155724; }}
            .difficulty-A2 {{ background: #d1ecf1; color: #0c5460; }}
            .difficulty-B1 {{ background: #fff3cd; color: #856404; }}
            .difficulty-B2 {{ background: #ffe5cc; color: #804d00; }}
            .difficulty-C1 {{ background: #f8d7da; color: #721c24; }}
            .difficulty-C2 {{ background: #d1d0d0; color: #333; }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                color: #666;
                font-size: 0.9em;
                border-top: 1px solid #ddd;
            }}
            
            button {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                transition: all 0.2s;
            }}
            
            button:hover {{
                background: #764ba2;
            }}
            
            .vocab-action {{
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }}
            
            .btn-small {{
                padding: 6px 12px;
                font-size: 0.85em;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📖 {title}</h1>
                <p>AI-Powered English Reading Comprehension Report</p>
            </div>
            
            <div class="meta-info">
                <div class="meta-item">
                    <span class="meta-label">📊 Difficulty:</span>
                    <span class="difficulty-badge difficulty-{difficulty_level}">{difficulty_level}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">📝 Words:</span>
                    <span>{word_count}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">📚 Unique Words:</span>
                    <span>{unique_words}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">🔍 Error Patterns Found:</span>
                    <span>{error_count}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">⏱️ Generated:</span>
                    <span>{timestamp}</span>
                </div>
            </div>
            
            {main_content}
            
            <div class="summary-section">
                <div class="summary-title">📋 Article Summary & Learning Points</div>
                <div class="summary-content">
                    {summary}
                </div>
            </div>
            
            <div class="footer">
                <p>Generated by English Reading Analyzer | Powered by Claude AI</p>
                <p>💾 Save this report | 📥 Download PDF</p>
            </div>
        </div>
        
        <script>
            // 联动滚动逻辑
            const sentences = document.querySelectorAll('.sentence');
            sentences.forEach((sent, index) => {{
                sent.addEventListener('click', function() {{
                    // 移除其他高亮
                    sentences.forEach(s => s.classList.remove('highlighted'));
                    // 添加当前高亮
                    sent.classList.add('highlighted');
                }});
            }});
            
            // 词汇收藏功能
            const difficultWords = document.querySelectorAll('.difficult-word');
            difficultWords.forEach(word => {{
                word.addEventListener('click', function() {{
                    const vocab = this.textContent;
                    alert('词汇已添加到单词本: ' + vocab);
                    // TODO: 实现LocalStorage保存
                }});
            }});
            
            // 标签页切换
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    const tabContent = this.getAttribute('data-tab');
                    document.querySelectorAll('.tab-content').forEach(content => {{
                        content.classList.remove('active');
                    }});
                    tabs.forEach(t => t.classList.remove('active'));
                    document.getElementById(tabContent).classList.add('active');
                    this.classList.add('active');
                }});
            }});
        </script>
    </body>
    </html>
    """
    
    @staticmethod
    def generate_report(
        title: str,
        original_text: str,
        analysis_data: Dict[str, Any],
        error_patterns: List[Dict],
        complex_sentences: List[Dict],
        summary: str
    ) -> str:
        """
        生成完整的HTML报告
        """
        # 准备数据
        vocab_info = analysis_data.get('vocabulary_info', {})
        readability = analysis_data.get('readability', {})
        
        word_count = readability.get('word_count', 0)
        unique_words = vocab_info.get('unique_words', 0)
        difficulty_level = readability.get('complexity_level', 'B1')
        error_count = len(error_patterns)
        
        # 生成错误句型HTML
        error_html = ""
        if error_patterns:
            error_html += '<div class="annotation-item">'
            error_html += '<div class="annotation-title">❌ 常见错误句型 (Error Patterns)</div>'
            for error in error_patterns[:5]:  # 显示前5个错误
                error_html += f"""
                <div class="error-pattern">
                    <div class="error-type">{html_escape.escape(error.get('error_type', 'Unknown Error'))}</div>
                    <div class="incorrect">❌ {html_escape.escape(error.get('incorrect_form', ''))}</div>
                    <div class="correct">✅ {html_escape.escape(error.get('correct_form', ''))}</div>
                    <div class="explanation">{html_escape.escape(error.get('explanation', ''))}</div>
                </div>
                """
            error_html += '</div>'
        
        # 生成复杂句子分析HTML
        complex_html = ""
        if complex_sentences:
            complex_html += '<div class="annotation-item">'
            complex_html += '<div class="annotation-title">🔍 复杂句子分析 (Complex Sentences)</div>'
            for sent in complex_sentences[:3]:
                complex_html += f"""
                <div class="complex-sentence">
                    <div class="complex-sentence-title">Sentence Structure Analysis</div>
                    <div class="breakdown">{html_escape.escape(sent.get('sentence', ''))}</div>
                    <div class="breakdown"><strong>Length:</strong> {sent.get('length', 0)} chars | 
                                           <strong>Clauses:</strong> {sent.get('clause_count', 0)}</div>
                    {f'<div class="breakdown"><strong>Tip:</strong> {html_escape.escape(sent.get("suggestion", ""))}</div>' if sent.get('suggestion') else ''}
                </div>
                """
            complex_html += '</div>'
        
        # 生成词汇分析HTML
        vocab_html = ""
        vocab_by_level = vocab_info.get('vocabulary_by_level', {})
        if vocab_by_level:
            vocab_html += '<div class="annotation-item">'
            vocab_html += '<div class="annotation-title">📚 词汇分析 (Vocabulary Analysis)</div>'
            
            for level, words in vocab_by_level.items():
                if words and len(words) > 0:
                    level_map = {
                        'common': ('Common Words 🟢', 'word-level-common'),
                        'intermediate': ('Intermediate Words 🟡', 'word-level-intermediate'),
                        'advanced': ('Advanced Words 🔴', 'word-level-advanced'),
                        'unknown': ('Unknown Words ⚪', ''),
                    }
                    label, css_class = level_map.get(level, (level, ''))
                    
                    vocab_html += f'<div class="breakdown"><strong>{label}:</strong> {len(words)} words</div>'
                    vocab_html += '<div class="key-phrases">'
                    for word in list(words)[:10]:
                        vocab_html += f'<span class="phrase-tag {css_class}">{word}</span>'
                    vocab_html += '</div>'
            
            vocab_html += '</div>'
        
        # 组合注解区域
        annotations_section = error_html + complex_html + vocab_html
        
        # 生成句子标注版本
        sentences = original_text.split('.')
        marked_sentences = []
        for sent in sentences:
            if sent.strip():
                marked_sentences.append(f'<div class="sentence">{html_escape.escape(sent.strip())}.</div>')
        
        marked_text = '\n'.join(marked_sentences)
        
        # 生成主要内容
        main_content = f"""
        <div class="content">
            <div class="original-text">
                <h3 style="margin-bottom: 20px;">📄 Original Text</h3>
                <div class="text-content">
                    {marked_text}
                </div>
            </div>
            <div class="annotations">
                <h3 style="margin-bottom: 20px;">📝 Annotations & Analysis</h3>
                {annotations_section}
            </div>
        </div>
        """
        
        # 使用模板生成最终HTML
        html_content = HTMLReportGenerator.TEMPLATE.format(
            title=html_escape.escape(title),
            difficulty_level=difficulty_level,
            word_count=word_count,
            unique_words=unique_words,
            error_count=error_count,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            main_content=main_content,
            summary=html_escape.escape(summary)
        )
        
        return html_content


# 测试
if __name__ == '__main__':
    test_text = "Artificial intelligence is revolutionizing industries. The technology enables organizations to optimize operations."
    
    test_analysis = {
        'vocabulary_info': {
            'total_words': 20,
            'unique_words': 15,
            'vocabulary_by_level': {
                'common': ['is', 'the', 'to', 'and', 'enables'],
                'intermediate': ['artificial', 'intelligence', 'revolutionizing', 'industries', 'technology'],
                'advanced': ['optimize', 'operations'],
                'unknown': []
            }
        },
        'readability': {
            'word_count': 20,
            'complexity_level': 'B2'
        }
    }
    
    test_errors = [
        {
            'error_type': 'Collocation Error',
            'incorrect_form': 'make a research',
            'correct_form': 'conduct research',
            'explanation': 'The correct collocation is "conduct research", not "make a research".'
        }
    ]
    
    test_complex = [
        {
            'sentence': 'Although artificial intelligence has been developed extensively, its implications remain unclear.',
            'length': 95,
            'clause_count': 2,
            'suggestion': 'Consider breaking this into shorter clauses.'
        }
    ]
    
    html = HTMLReportGenerator.generate_report(
        "Test Article",
        test_text,
        test_analysis,
        test_errors,
        test_complex,
        "This article discusses how AI is changing industries."
    )
    
    with open('/tmp/test_report.html', 'w') as f:
        f.write(html)
    
    print("Report generated: /tmp/test_report.html")

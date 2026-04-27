#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI分析引擎 - 使用Claude API识别常见错误句型
"""

import os
import json
import re
from typing import List, Dict, Optional
from anthropic import Anthropic

# 初始化Anthropic客户端
client = Anthropic()


class ErrorPatternAnalyzer:
    """使用Claude识别常见错误句型"""
    
    ERROR_PATTERNS_PROMPT = """
    You are an expert English grammar teacher. Analyze the following English sentences and identify common error patterns.
    
    For EACH sentence, check for:
    1. **Collocation Errors** - Incorrect word combinations (e.g., "do a mistake" instead of "make a mistake")
    2. **Tense Issues** - Incorrect verb tenses (e.g., using simple past instead of present perfect)
    3. **Article Errors** - Incorrect use of a/an/the
    4. **Number Agreement** - Subject-verb disagreement or singular/plural issues
    5. **Preposition Errors** - Incorrect prepositions (e.g., "in time" vs "on time")
    6. **Word Order** - Incorrect word order in sentences
    7. **Modal Verb Issues** - Incorrect use of can/could, will/would, etc.
    
    For EACH error found, provide:
    - error_type: The category of error
    - sentence: The original sentence
    - issue: Description of the problem
    - incorrect_form: ❌ Show the incorrect structure
    - correct_form: ✅ Show the corrected version
    - explanation: Why this is wrong and how to fix it
    
    Output format: JSON array of error objects or empty array if no errors
    
    Sentences to analyze:
    {sentences}
    
    Return ONLY valid JSON, no other text.
    """
    
    SENTENCE_ANALYSIS_PROMPT = """
    You are an English language expert. Perform a deep analysis of the following English sentence:
    
    Sentence: "{sentence}"
    
    Provide:
    1. **Grammatical Analysis**: Identify the subject, verb, objects, and clauses
    2. **Vocabulary Level**: Mark each key word as 'common', 'intermediate', or 'advanced'
    3. **Syntax Structure**: Describe the sentence structure (simple/compound/complex)
    4. **Possible Errors**: Any grammar or vocabulary issues (if none, say "No errors detected")
    5. **Simplification**: If complex, provide a simpler version
    6. **Key Takeaway**: One learning point from this sentence
    
    Output format: JSON object
    
    Return ONLY valid JSON, no other text.
    """
    
    @staticmethod
    def identify_error_patterns(sentences: List[str]) -> List[Dict]:
        """
        识别常见错误句型
        
        Args:
            sentences: 句子列表
            
        Returns:
            错误模式列表
        """
        if not sentences:
            return []
        
        # 构建prompt
        sentence_text = '\n'.join([f"{i+1}. {s}" for i, s in enumerate(sentences)])
        prompt = ErrorPatternAnalyzer.ERROR_PATTERNS_PROMPT.format(sentences=sentence_text)
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # 尝试解析JSON
            # 处理可能的markdown代码块
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            errors = json.loads(response_text)
            return errors if isinstance(errors, list) else []
            
        except Exception as e:
            print(f"Error analyzing patterns: {str(e)}")
            return []
    
    @staticmethod
    def analyze_sentence_deep(sentence: str) -> Dict:
        """
        深度分析单个句子
        
        Args:
            sentence: 句子文本
            
        Returns:
            分析结果字典
        """
        prompt = ErrorPatternAnalyzer.SENTENCE_ANALYSIS_PROMPT.format(sentence=sentence)
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # 处理markdown代码块
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            analysis = json.loads(response_text)
            return analysis
            
        except Exception as e:
            print(f"Error in deep analysis: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def extract_key_sentences(text: str, num_sentences: int = 5) -> List[str]:
        """
        从文本中提取关键句子进行分析
        
        Args:
            text: 输入文本
            num_sentences: 提取的句子数量
            
        Returns:
            关键句子列表
        """
        # 简单的句子分割
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # 优先选择较长的句子（通常更复杂）
        sentences = sorted(sentences, key=len, reverse=True)[:num_sentences]
        
        return sentences


class SentenceBreakdownHelper:
    """句子分解辅助工具"""
    
    BREAKDOWN_PROMPT = """
    Break down the following English sentence into simpler parts and explain each component:
    
    Sentence: "{sentence}"
    
    Provide:
    1. **Main Clause**: Identify the main independent clause
    2. **Subordinate Clauses**: List any dependent clauses
    3. **Key Phrases**: Identify important phrases (noun phrases, verb phrases, etc.)
    4. **Word-by-word Translation**: Provide a literal translation
    5. **Simplified Version**: Rewrite it as 2-3 simpler sentences
    6. **Common Mistakes**: What learners often get wrong in sentences like this
    
    Output format: JSON object
    
    Return ONLY valid JSON, no other text.
    """
    
    @staticmethod
    def breakdown_sentence(sentence: str) -> Dict:
        """
        分解复杂句子
        """
        prompt = SentenceBreakdownHelper.BREAKDOWN_PROMPT.format(sentence=sentence)
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = message.content[0].text.strip()
            
            # 处理markdown
            if response_text.startswith('```'):
                response_text = re.sub(r'^```(?:json)?\n', '', response_text)
                response_text = re.sub(r'\n```$', '', response_text)
            
            breakdown = json.loads(response_text)
            return breakdown
            
        except Exception as e:
            print(f"Error breaking down sentence: {str(e)}")
            return {"error": str(e)}


# 测试
if __name__ == '__main__':
    # 测试句子（包含常见错误）
    test_sentences = [
        "She don't like coffee.",  # 动词不一致
        "I'm interested in to play football.",  # 介词+动名词错误
        "The research are important for science.",  # 主谓不一致
    ]
    
    print("=" * 50)
    print("Testing Error Pattern Detection")
    print("=" * 50)
    
    errors = ErrorPatternAnalyzer.identify_error_patterns(test_sentences)
    print(f"Errors found: {json.dumps(errors, indent=2)}")
    
    print("\n" + "=" * 50)
    print("Testing Sentence Breakdown")
    print("=" * 50)
    
    complex_sentence = "Although the research has been conducted extensively, the implications remain unclear because of the complex nature of the phenomena."
    breakdown = SentenceBreakdownHelper.breakdown_sentence(complex_sentence)
    print(f"Breakdown: {json.dumps(breakdown, indent=2)}")

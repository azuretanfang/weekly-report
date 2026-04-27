#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP 分析引擎 - 词汇等级、句子复杂度、难度分析
"""

import re
import nltk
from typing import List, Dict, Tuple, Optional
from collections import Counter
import json
from pathlib import Path

# 下载必要的NLTK资源
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class VocabularyLevel:
    """词汇等级定义"""
    
    # 开源词汇库映射（基于COCA频率）
    VOCAB_DB = {
        'common': set(),  # A1-B1 (高频词)
        'intermediate': set(),  # B2 (中级词)
        'advanced': set(),  # C1-C2 (高级词)
    }
    
    @classmethod
    def load_vocab_db(cls):
        """加载词汇库（使用开源ANKI词库）"""
        vocab_file = Path(__file__).parent.parent / 'assets' / 'vocab_db.json'
        if vocab_file.exists():
            with open(vocab_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls.VOCAB_DB = data
        else:
            # 如果没有，使用默认的常用词列表
            cls._load_default_vocab()
    
    @classmethod
    def _load_default_vocab(cls):
        """加载默认词汇库"""
        # 这里可以集成开源的ANKI词库或COCA语料库
        # 为演示用途，这里使用简化版本
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
            'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
            'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'being', 'has',
            'had', 'does', 'did', 'having', 'may', 'might', 'must', 'shall', 'should'
        }
        
        intermediate_words = {
            'artificial', 'intelligence', 'machine', 'learning', 'algorithm',
            'optimize', 'transform', 'industry', 'technology', 'innovation',
            'implement', 'develop', 'analysis', 'research', 'evidence',
            'significant', 'approach', 'method', 'technique', 'solution',
            'challenge', 'opportunity', 'benefit', 'strategy', 'framework',
            'perspective', 'concept', 'principle', 'theory', 'model',
            'establish', 'demonstrate', 'investigate', 'evaluate', 'examine',
            'comprehensive', 'thorough', 'detailed', 'systematic', 'structured',
            'facilitate', 'enhance', 'improve', 'increase', 'reduce'
        }
        
        advanced_words = {
            'sophisticated', 'paradigm', 'methodology', 'infrastructure',
            'accumulation', 'heterogeneous', 'proliferation', 'proliferating',
            'circumvent', 'ubiquitous', 'phenomenon', 'synergistic', 'empirical',
            'amalgamation', 'juxtaposition', 'dichotomy', 'dichotomous',
            'categorical', 'taxonomic', 'epistemological', 'ontological',
            'ethereal', 'substantive', 'ameliorate', 'exacerbate', 'propagate',
            'synthesize', 'extrapolate', 'interpolate', 'correlate', 'expedite'
        }
        
        cls.VOCAB_DB = {
            'common': common_words,
            'intermediate': intermediate_words,
            'advanced': advanced_words,
        }
    
    @classmethod
    def get_level(cls, word: str) -> str:
        """获取单词等级"""
        word_lower = word.lower()
        
        # 确保已加载词汇库
        if not cls.VOCAB_DB['common']:
            cls.load_vocab_db()
        
        if word_lower in cls.VOCAB_DB['common']:
            return 'common'
        elif word_lower in cls.VOCAB_DB['intermediate']:
            return 'intermediate'
        elif word_lower in cls.VOCAB_DB['advanced']:
            return 'advanced'
        else:
            return 'unknown'


class NLPAnalyzer:
    """NLP分析器"""
    
    def __init__(self):
        VocabularyLevel.load_vocab_db()
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """句子分词"""
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def tokenize_words(self, text: str) -> List[str]:
        """单词分词"""
        words = nltk.word_tokenize(text)
        # 过滤纯标点
        words = [w for w in words if w.isalnum() or "'" in w]
        return words
    
    def extract_vocabulary(self, text: str) -> Dict[str, any]:
        """
        提取词汇信息
        返回: {
            'words': [...],
            'unique_words': int,
            'vocabulary_by_level': {'common': [...], 'intermediate': [...], 'advanced': [...]},
            'difficulty_score': float  # 0-1, 越高越难
        }
        """
        words = self.tokenize_words(text)
        word_lower = [w.lower() for w in words if w.isalpha()]
        unique_words = set(word_lower)
        
        vocab_by_level = {'common': [], 'intermediate': [], 'advanced': [], 'unknown': []}
        
        for word in unique_words:
            level = VocabularyLevel.get_level(word)
            vocab_by_level[level].append(word)
        
        # 计算难度分数 (0-1)
        # 难度 = (intermediate_count + 2*advanced_count) / total_unique_words
        total = len(unique_words)
        difficulty = (
            len(vocab_by_level['intermediate']) + 2 * len(vocab_by_level['advanced'])
        ) / (total + 1)  # 避免除以0
        
        return {
            'total_words': len(word_lower),
            'unique_words': len(unique_words),
            'vocabulary_by_level': vocab_by_level,
            'difficulty_score': min(difficulty, 1.0),
            'common_ratio': len(vocab_by_level['common']) / (total + 1),
            'intermediate_ratio': len(vocab_by_level['intermediate']) / (total + 1),
            'advanced_ratio': len(vocab_by_level['advanced']) / (total + 1),
        }
    
    def analyze_readability(self, text: str) -> Dict[str, any]:
        """
        分析可读性指标
        返回Flesch Kincaid等级、句子复杂度等
        """
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)
        
        avg_sentence_length = len(words) / (len(sentences) + 1)
        
        # 简单启发式：平均单词长度
        syllable_count = sum(self._count_syllables(w) for w in words if w.isalpha())
        avg_syllables = syllable_count / (len(words) + 1)
        
        return {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(sum(len(w) for w in words) / (len(words) + 1), 2),
            'avg_syllables': round(avg_syllables, 2),
            'complexity_level': self._estimate_complexity_level(avg_sentence_length, avg_syllables),
        }
    
    @staticmethod
    def _count_syllables(word: str) -> int:
        """估算音节数（简化版）"""
        word = word.lower()
        syllables = 0
        vowels = "aeiouy"
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel
        
        # 规则调整
        if word.endswith('e'):
            syllables -= 1
        if word.endswith('le') and len(word) > 2:
            syllables += 1
        
        return max(1, syllables)
    
    @staticmethod
    def _estimate_complexity_level(avg_sent_len: float, avg_syllables: float) -> str:
        """
        估算复杂度等级 (CEFR标准)
        A1-A2: 简单 | B1: 中等 | B2-C1: 复杂 | C2: 非常复杂
        """
        complexity_score = avg_sent_len * 0.3 + avg_syllables * 0.7
        
        if complexity_score < 1.5:
            return 'A1'
        elif complexity_score < 2.0:
            return 'A2'
        elif complexity_score < 2.5:
            return 'B1'
        elif complexity_score < 3.0:
            return 'B2'
        elif complexity_score < 3.5:
            return 'C1'
        else:
            return 'C2'
    
    def extract_complex_sentences(self, text: str, threshold: float = 15) -> List[Dict]:
        """
        提取复杂句子（超过阈值长度的句子）
        
        Args:
            text: 输入文本
            threshold: 字符长度阈值
            
        Returns:
            复杂句子列表，每个包含原文和简化建议
        """
        sentences = self.tokenize_sentences(text)
        complex_sentences = []
        
        for sentence in sentences:
            if len(sentence) > threshold:
                # 简化建议：如果句子包含多个从句，提示分解
                clause_count = len(re.findall(r'\b(which|that|because|although|when|where)\b', sentence, re.I))
                
                complex_sentences.append({
                    'sentence': sentence,
                    'length': len(sentence),
                    'clause_count': clause_count,
                    'suggestion': 'Consider breaking this sentence into shorter clauses' if clause_count > 2 else None
                })
        
        return complex_sentences


# 测试
if __name__ == '__main__':
    analyzer = NLPAnalyzer()
    
    test_text = """
    Artificial intelligence is revolutionizing how we approach problem-solving.
    The implementation of sophisticated machine learning algorithms enables organizations
    to extract valuable insights from vast datasets.
    """
    
    vocab_info = analyzer.extract_vocabulary(test_text)
    print(f"Vocabulary Info: {json.dumps(vocab_info, indent=2)}")
    
    readability = analyzer.analyze_readability(test_text)
    print(f"\nReadability: {json.dumps(readability, indent=2)}")
    
    complex_sents = analyzer.extract_complex_sentences(test_text)
    print(f"\nComplex Sentences: {complex_sents}")

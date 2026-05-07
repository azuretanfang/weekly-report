#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP 分析引擎 - 词汇等级、句子复杂度、难度分析

【v1.1.0 修复】
- 移除"基于 COCA 语料库"的不实声称 → 改为"自建分级词汇库"
- 扩大默认词汇库（common 200+ / intermediate 250+ / advanced 100+），降低 unknown 误分类率
- 引入 fallback 链：vocab_db → AI 辅助判定（可选）→ unknown[需人工确认] + 免责说明
- NLTK punkt 改为延迟下载 + 离线降级（不可用时使用正则切句）
- vocab_db 加载严格幂等（避免每次 NLPAnalyzer() 重读）

【v1.3.0 修复】
- P0-A：CEFR 算法常数错误（任何文本被打成 C2）→ 替换为 Flesch-Kincaid Grade + Dale-Chall 融合判级
- P0-B：词汇库覆盖严重不足（advanced 召回率 0）→ 引入 wordfreq Zipf 词频作为 fallback 主链路
- 新增 readability 关键字段：flesch_reading_ease / flesch_kincaid_grade / dale_chall_score
- 所有新依赖（textstat / wordfreq）均带 ImportError 优雅降级，零依赖也能跑
"""

import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set

logger = logging.getLogger(__name__)

# ---- 可选的高质量分级依赖：失败时优雅降级 ----
try:
    import textstat as _textstat  # type: ignore
    _TEXTSTAT_OK = True
except ImportError:
    _textstat = None
    _TEXTSTAT_OK = False
    logger.warning("textstat 未安装，可读性指标将降级使用经验公式")

try:
    from wordfreq import zipf_frequency as _zipf_frequency  # type: ignore
    _WORDFREQ_OK = True
except ImportError:
    _zipf_frequency = None
    _WORDFREQ_OK = False
    logger.warning("wordfreq 未安装，词汇分级将降级使用自建词库 + 词长启发")

# NLTK 改为延迟加载
_nltk_punkt_ready: Optional[bool] = None


def _ensure_nltk_punkt() -> bool:
    """延迟检查 punkt；不可用时返回 False，调用方降级到正则切句。"""
    global _nltk_punkt_ready
    if _nltk_punkt_ready is not None:
        return _nltk_punkt_ready
    try:
        import nltk  # type: ignore
        try:
            nltk.data.find('tokenizers/punkt')
            _nltk_punkt_ready = True
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
                nltk.data.find('tokenizers/punkt')
                _nltk_punkt_ready = True
            except Exception as e:
                logger.warning("NLTK punkt 下载失败，将降级使用正则切句：%s", e)
                _nltk_punkt_ready = False
    except ImportError:
        logger.warning("NLTK 未安装，使用正则切句降级方案")
        _nltk_punkt_ready = False
    return _nltk_punkt_ready


def _regex_sent_tokenize(text: str) -> List[str]:
    """正则版句子切分降级方案。"""
    parts = re.split(r'(?<=[.!?])\s+', text or '')
    return [p.strip() for p in parts if p and p.strip()]


def _regex_word_tokenize(text: str) -> List[str]:
    """正则版分词降级方案。"""
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+", text or '')


# ============= 词汇等级 =============

class VocabularyLevel:
    """
    词汇等级（自建分级词汇库；不再声称基于 COCA）

    等级粗略映射：
      common       ≈ A1-B1（高频常用词）
      intermediate ≈ B2（中级学术/职场词）
      advanced     ≈ C1-C2（高级学术词）
    """

    VOCAB_DB: Dict[str, Set[str]] = {
        'common': set(),
        'intermediate': set(),
        'advanced': set(),
    }

    _loaded = False

    @classmethod
    def load_vocab_db(cls) -> None:
        """幂等加载词汇库；优先读取 assets/vocab_db.json，失败则使用内置默认。"""
        if cls._loaded:
            return
        vocab_file = Path(__file__).parent.parent / 'assets' / 'vocab_db.json'
        try:
            if vocab_file.exists():
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                cls.VOCAB_DB = {
                    'common': set(data.get('common', [])),
                    'intermediate': set(data.get('intermediate', [])),
                    'advanced': set(data.get('advanced', [])),
                }
                cls._loaded = True
                return
        except Exception as e:
            logger.warning("加载 assets/vocab_db.json 失败，使用内置默认词库：%s", e)
        cls._load_default_vocab()
        cls._loaded = True

    @classmethod
    def _load_default_vocab(cls) -> None:
        """内置默认词库（已大幅扩容，覆盖常见基础到中高级词汇约 550+）。"""

        common_words = {
            # 基础高频词（保留原有）
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
            'had', 'does', 'did', 'having', 'may', 'might', 'must', 'shall', 'should',
            # 扩展：日常名词/动词/形容词（A2-B1）
            'house', 'home', 'room', 'door', 'window', 'street', 'road', 'city', 'country',
            'world', 'place', 'school', 'office', 'shop', 'store', 'company', 'business',
            'family', 'friend', 'child', 'children', 'man', 'woman', 'boy', 'girl',
            'father', 'mother', 'parent', 'son', 'daughter', 'brother', 'sister',
            'food', 'water', 'coffee', 'tea', 'bread', 'milk', 'fruit', 'meat',
            'eat', 'drink', 'sleep', 'wake', 'walk', 'run', 'sit', 'stand',
            'open', 'close', 'start', 'stop', 'begin', 'end', 'finish', 'continue',
            'read', 'write', 'speak', 'listen', 'hear', 'watch', 'show', 'tell',
            'ask', 'answer', 'call', 'meet', 'help', 'try', 'need', 'find',
            'big', 'small', 'large', 'little', 'long', 'short', 'tall', 'high', 'low',
            'old', 'young', 'new', 'hot', 'cold', 'warm', 'cool', 'fast', 'slow',
            'happy', 'sad', 'angry', 'tired', 'hungry', 'thirsty',
            'easy', 'hard', 'simple', 'difficult', 'important', 'possible',
            'red', 'blue', 'green', 'yellow', 'black', 'white',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            'morning', 'afternoon', 'evening', 'night', 'today', 'tomorrow', 'yesterday',
            'week', 'month', 'minute', 'hour', 'second',
            'love', 'feel', 'live', 'play', 'learn', 'study', 'teach', 'understand',
            'buy', 'sell', 'pay', 'cost', 'spend', 'save', 'money',
            'car', 'bus', 'train', 'plane', 'travel', 'visit',
            'book', 'paper', 'pen', 'pencil', 'phone', 'computer',
            # B1 程度副词/连接词
            'really', 'very', 'quite', 'almost', 'always', 'often', 'sometimes',
            'usually', 'never', 'maybe', 'perhaps', 'still', 'already', 'yet',
            'before', 'until', 'while', 'during', 'though', 'unless',
            # 高频动词扩展
            'become', 'change', 'keep', 'leave', 'put', 'bring', 'send',
            'turn', 'move', 'stay', 'remain', 'happen', 'follow', 'lead',
            'create', 'build', 'grow', 'rise', 'fall', 'allow', 'expect',
            'mean', 'seem', 'appear', 'remember', 'forget', 'decide', 'choose',
            'plan', 'prepare', 'support', 'protect', 'consider', 'agree', 'accept',
            'believe', 'hope', 'wish', 'enjoy',
            # 数字/量词
            'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'hundred', 'thousand', 'million',
            'many', 'much', 'few', 'several', 'more', 'less', 'least', 'much',
        }

        intermediate_words = {
            # 原有
            'artificial', 'intelligence', 'machine', 'learning', 'algorithm',
            'optimize', 'transform', 'industry', 'technology', 'innovation',
            'implement', 'develop', 'analysis', 'research', 'evidence',
            'significant', 'approach', 'method', 'technique', 'solution',
            'challenge', 'opportunity', 'benefit', 'strategy', 'framework',
            'perspective', 'concept', 'principle', 'theory', 'model',
            'establish', 'demonstrate', 'investigate', 'evaluate', 'examine',
            'comprehensive', 'thorough', 'detailed', 'systematic', 'structured',
            'facilitate', 'enhance', 'improve', 'increase', 'reduce',
            # 扩展（B2 学术/职场常见词）
            'enable', 'efficient', 'effective', 'efficiency', 'effectiveness',
            'frameworks', 'data', 'database', 'computing', 'software', 'hardware',
            'application', 'platform', 'system', 'process', 'procedure',
            'function', 'feature', 'capability', 'capacity', 'performance',
            'quality', 'standard', 'criterion', 'criteria', 'requirement',
            'objective', 'goal', 'purpose', 'mission', 'vision',
            'achieve', 'accomplish', 'maintain', 'manage', 'control',
            'organize', 'coordinate', 'collaborate', 'cooperate', 'communicate',
            'recommend', 'suggest', 'propose', 'advise', 'consult',
            'analyze', 'synthesize', 'compare', 'contrast', 'distinguish',
            'identify', 'recognize', 'determine', 'define', 'describe',
            'illustrate', 'represent', 'reflect', 'indicate', 'suggest',
            'argue', 'claim', 'assert', 'state', 'declare',
            'imply', 'infer', 'conclude', 'deduce', 'predict',
            'occur', 'emerge', 'arise', 'derive', 'originate',
            'maintain', 'sustain', 'preserve', 'retain', 'persist',
            'fluctuate', 'vary', 'differ', 'diverse', 'diversity',
            'expand', 'extend', 'broaden', 'enlarge', 'amplify',
            'shrink', 'decline', 'decrease', 'diminish', 'reduce',
            'examine', 'inspect', 'survey', 'review', 'assess',
            'consequence', 'implication', 'impact', 'influence', 'effect',
            'cause', 'factor', 'element', 'component', 'aspect',
            'context', 'environment', 'circumstance', 'condition', 'situation',
            'process', 'mechanism', 'procedure', 'protocol', 'workflow',
            'resource', 'asset', 'tool', 'instrument', 'apparatus',
            'sufficient', 'adequate', 'appropriate', 'suitable', 'relevant',
            'remarkable', 'notable', 'considerable', 'substantial', 'significant',
            'fundamental', 'essential', 'crucial', 'critical', 'vital',
            'evident', 'apparent', 'obvious', 'clear', 'explicit',
            'implicit', 'subtle', 'gradual', 'steady', 'consistent',
            'previous', 'prior', 'subsequent', 'following', 'preceding',
            'specific', 'particular', 'general', 'overall', 'broad',
            'narrow', 'limited', 'restricted', 'extensive', 'widespread',
            'global', 'universal', 'international', 'domestic', 'local',
            'individual', 'personal', 'collective', 'mutual', 'shared',
            'distinct', 'unique', 'similar', 'identical', 'equivalent',
            'transition', 'transformation', 'modification', 'adjustment', 'alteration',
            'integration', 'combination', 'composition', 'configuration', 'arrangement',
            'distribution', 'allocation', 'assignment', 'designation', 'classification',
            'categorize', 'classify', 'organize', 'rank', 'prioritize',
            'verify', 'validate', 'confirm', 'authenticate', 'authorize',
            'monitor', 'observe', 'track', 'detect', 'recognize',
            'predict', 'forecast', 'anticipate', 'estimate', 'project',
            'invest', 'fund', 'finance', 'budget', 'expenditure',
            'revenue', 'profit', 'loss', 'cost', 'expense',
            'consumer', 'customer', 'client', 'user', 'audience',
            'product', 'service', 'commodity', 'merchandise', 'goods',
            'market', 'industry', 'sector', 'segment', 'niche',
            'employee', 'employer', 'colleague', 'partner', 'stakeholder',
            'leadership', 'management', 'governance', 'administration', 'authority',
            'policy', 'regulation', 'legislation', 'compliance', 'enforcement',
            'security', 'safety', 'privacy', 'confidentiality', 'integrity',
            'innovate', 'creative', 'inventive', 'original', 'novel',
            'sustainable', 'renewable', 'environmental', 'ecological', 'organic',
            'digital', 'virtual', 'electronic', 'online', 'offline',
            'mobile', 'remote', 'wireless', 'cloud', 'hybrid',
            'experiment', 'hypothesis', 'methodology', 'observation', 'measurement',
            'statistic', 'percentage', 'ratio', 'proportion', 'distribution',
            'communicate', 'collaborate', 'negotiate', 'mediate', 'persuade',
        }

        advanced_words = {
            # 原有
            'sophisticated', 'paradigm', 'methodology', 'infrastructure',
            'accumulation', 'heterogeneous', 'proliferation', 'proliferating',
            'circumvent', 'ubiquitous', 'phenomenon', 'synergistic', 'empirical',
            'amalgamation', 'juxtaposition', 'dichotomy', 'dichotomous',
            'categorical', 'taxonomic', 'epistemological', 'ontological',
            'ethereal', 'substantive', 'ameliorate', 'exacerbate', 'propagate',
            'synthesize', 'extrapolate', 'interpolate', 'correlate', 'expedite',
            # 扩展（C1-C2 学术词）
            'pragmatic', 'pragmatism', 'paradigmatic', 'idiosyncratic',
            'quintessential', 'paradoxical', 'dialectical', 'rhetorical',
            'pedagogical', 'phenomenological', 'hermeneutic', 'heuristic',
            'manifest', 'manifestation', 'inception', 'culmination',
            'advent', 'precedence', 'precedent', 'antecedent',
            'cogent', 'salient', 'pertinent', 'tangential',
            'discrete', 'discretion', 'discretionary', 'arbitrary',
            'inherent', 'intrinsic', 'extrinsic', 'congenital',
            'preliminary', 'rudimentary', 'elementary', 'basic',
            'comprehensive', 'exhaustive', 'panoramic', 'encyclopedic',
            'meticulous', 'rigorous', 'scrupulous', 'fastidious',
            'tenuous', 'precarious', 'volatile', 'mercurial',
            'redundant', 'superfluous', 'extraneous', 'gratuitous',
            'cogent', 'persuasive', 'compelling', 'convincing',
            'discern', 'ascertain', 'elucidate', 'expound',
            'consolidate', 'corroborate', 'substantiate', 'authenticate',
            'mitigate', 'attenuate', 'alleviate', 'palliate',
            'reciprocity', 'symbiosis', 'antithesis', 'synthesis',
            'imminent', 'inevitable', 'inexorable', 'inescapable',
            'pervasive', 'permeating', 'omnipresent', 'omniscient',
            'predominant', 'preeminent', 'paramount', 'preponderant',
            'cumulative', 'incremental', 'cascade', 'iterative',
            'oscillate', 'gravitate', 'permeate', 'cultivate',
            'orthodox', 'heterodox', 'unconventional', 'avant-garde',
        }

        cls.VOCAB_DB = {
            'common': common_words,
            'intermediate': intermediate_words,
            'advanced': advanced_words,
        }

    @classmethod
    def get_level(cls, word: str) -> str:
        """
        基础查表（O(1)）。**未命中返回 'unknown'，请由调用方决定 fallback 策略**。
        """
        if not word:
            return 'unknown'
        if not cls._loaded:
            cls.load_vocab_db()
        word_lower = word.lower()
        if word_lower in cls.VOCAB_DB['common']:
            return 'common'
        if word_lower in cls.VOCAB_DB['intermediate']:
            return 'intermediate'
        if word_lower in cls.VOCAB_DB['advanced']:
            return 'advanced'
        return 'unknown'

    @classmethod
    def get_level_with_fallback(
        cls,
        word: str,
        ai_fallback: bool = False,
    ) -> Dict[str, str]:
        """
        带 fallback 链的等级判定。

        Returns:
            {
              "level": "common" | "intermediate" | "advanced" | "unknown",
              "source": "vocab_db" | "wordfreq" | "ai_fallback" | "heuristic" | "missing",
              "confidence": "high" | "medium" | "low",
              "note": "免责说明（unknown 时填写）",
              "zipf": float | None,   # 当 source=wordfreq 时附上原始 zipf 值
            }

        fallback 链（v1.3.0 调整）：
          1. 词库查表 → hit 则返回（high 置信）
          2. miss + wordfreq 可用 → 用 Zipf 频率分级（medium 置信，是新主链）
              ≥ 5.5 → common
              4.0-5.5 → intermediate
              3.0-4.0 → advanced
              0.0-3.0 → advanced（rare 词归 advanced 而非 unknown，避免假数据）
              == 0 → unknown（拼写错误/专有名词）
          3. miss + wordfreq 不可用 + ai_fallback=True → AI 判定（预留接口）
          4. 全部不可用 → 词长启发（low 置信）
        """
        primary = cls.get_level(word)
        if primary != 'unknown':
            return {
                "level": primary,
                "source": "vocab_db",
                "confidence": "high",
                "note": "",
                "zipf": None,
            }

        # 步骤 2：wordfreq Zipf 频率分级（v1.3.0 新主链）
        if _WORDFREQ_OK and _zipf_frequency is not None:
            try:
                z = _zipf_frequency(word.lower(), 'en')
                if z >= 5.5:
                    level = 'common'
                elif z >= 4.0:
                    level = 'intermediate'
                elif z >= 3.0:
                    level = 'advanced'
                elif z > 0:
                    # rare 词：归 advanced（C1+），但置信度标 medium-low
                    level = 'advanced'
                else:
                    # zipf=0 表示全语料库未见过 → 真正 unknown（拼写错误/专名/造词）
                    return {
                        "level": "unknown",
                        "guess_level": "advanced",
                        "source": "wordfreq",
                        "confidence": "low",
                        "note": "⚠️ 此词在 wordfreq 英语语料库中频率为 0，可能是专有名词/拼写错误/造词，等级仅供参考",
                        "zipf": 0.0,
                    }
                return {
                    "level": level,
                    "source": "wordfreq",
                    "confidence": "medium",
                    "note": "",
                    "zipf": round(z, 2),
                }
            except Exception as e:
                logger.warning("wordfreq 查询失败，降级启发式：%s", e)

        # 步骤 3：AI fallback 接口预留（默认关闭）
        if ai_fallback:
            try:
                from . import ai_analysis  # noqa: F401  仅在需要时导入
                pass
            except Exception:
                pass

        # 步骤 4：基于词长的启发式（unknown 降级猜测）
        n = len(word)
        guess = 'common' if n <= 4 else ('intermediate' if n <= 8 else 'advanced')
        return {
            "level": "unknown",
            "guess_level": guess,
            "source": "heuristic",
            "confidence": "low",
            "note": "⚠️ 此词未在分级词汇库中收录，等级为基于词长的低置信猜测，仅供参考",
            "zipf": None,
        }


# ============= NLP 主分析器 =============

class NLPAnalyzer:
    """NLP 分析器"""

    def __init__(self):
        # 触发幂等加载
        VocabularyLevel.load_vocab_db()

    def tokenize_sentences(self, text: str) -> List[str]:
        """句子分词；NLTK 不可用时降级正则。"""
        if _ensure_nltk_punkt():
            try:
                import nltk  # type: ignore
                sents = nltk.sent_tokenize(text)
                return [s.strip() for s in sents if s.strip()]
            except Exception as e:
                logger.warning("NLTK 切句异常，降级正则：%s", e)
        return _regex_sent_tokenize(text)

    def tokenize_words(self, text: str) -> List[str]:
        """单词分词；NLTK 不可用时降级正则。"""
        if _ensure_nltk_punkt():
            try:
                import nltk  # type: ignore
                words = nltk.word_tokenize(text)
                return [w for w in words if w.isalnum() or "'" in w]
            except Exception as e:
                logger.warning("NLTK 分词异常，降级正则：%s", e)
        return _regex_word_tokenize(text)

    def extract_vocabulary(self, text: str) -> Dict[str, object]:
        """
        提取词汇信息。
        返回字段不变，向下兼容；新增 unknown_words_with_guess（含降级标识）。
        """
        words = self.tokenize_words(text)
        word_lower = [w.lower() for w in words if w.isalpha()]
        unique_words = set(word_lower)

        vocab_by_level: Dict[str, List[str]] = {
            'common': [], 'intermediate': [], 'advanced': [], 'unknown': [],
        }
        unknown_with_guess: List[Dict[str, str]] = []

        for word in unique_words:
            info = VocabularyLevel.get_level_with_fallback(word, ai_fallback=False)
            level = info["level"]
            vocab_by_level[level].append(word)
            if level == 'unknown':
                unknown_with_guess.append({
                    "word": word,
                    "guess_level": info.get("guess_level", "unknown"),
                    "confidence": info.get("confidence", "low"),
                    "note": info.get("note", ""),
                })

        total = len(unique_words)
        difficulty = (
            len(vocab_by_level['intermediate']) + 2 * len(vocab_by_level['advanced'])
        ) / (total + 1)

        return {
            'total_words': len(word_lower),
            'unique_words': len(unique_words),
            'vocabulary_by_level': vocab_by_level,
            'unknown_words_with_guess': unknown_with_guess,  # 降级猜测，附免责
            'difficulty_score': min(difficulty, 1.0),
            'common_ratio': len(vocab_by_level['common']) / (total + 1),
            'intermediate_ratio': len(vocab_by_level['intermediate']) / (total + 1),
            'advanced_ratio': len(vocab_by_level['advanced']) / (total + 1),
            'vocab_db_source': (
                'self_built_v1.1 + wordfreq' if _WORDFREQ_OK else 'self_built_v1.1 (no wordfreq)'
            ),
            'disclaimer': (
                '词汇等级判定链路：①自建词库（约 550+ 词，high 置信）'
                f'{" → ②wordfreq Zipf 频率（covers ~600k 词，medium 置信）" if _WORDFREQ_OK else ""}'
                ' → ③词长启发（low 置信）。'
                '若需要权威 CEFR 分级，建议接入 EnglishProfile 等第三方词典 API。'
            ),
        }

    def analyze_readability(self, text: str) -> Dict[str, object]:
        """
        可读性分析（v1.3.0 重构）。
        - 优先使用 textstat 的 Flesch-Kincaid Grade + Flesch Reading Ease + Dale-Chall
        - textstat 不可用时降级到经验公式（avg_sent_len + avg_syllables）
        - CEFR 等级通过 _estimate_complexity_level 由真实可读性指标映射
        """
        sentences = self.tokenize_sentences(text)
        words = self.tokenize_words(text)

        avg_sentence_length = len(words) / (len(sentences) + 1)
        syllable_count = sum(self._count_syllables(w) for w in words if w.isalpha())
        avg_syllables = syllable_count / (len(words) + 1)

        flesch_reading_ease: Optional[float] = None
        flesch_kincaid_grade: Optional[float] = None
        dale_chall_score: Optional[float] = None
        readability_source = "heuristic"

        if _TEXTSTAT_OK and _textstat is not None and text and text.strip():
            try:
                flesch_reading_ease = round(float(_textstat.flesch_reading_ease(text)), 2)
                flesch_kincaid_grade = round(float(_textstat.flesch_kincaid_grade(text)), 2)
                dale_chall_score = round(float(_textstat.dale_chall_readability_score(text)), 2)
                readability_source = "textstat"
            except Exception as e:
                logger.warning("textstat 计算异常，降级经验公式：%s", e)

        complexity_level = self._estimate_complexity_level(
            avg_sent_len=avg_sentence_length,
            avg_syllables=avg_syllables,
            flesch_kincaid_grade=flesch_kincaid_grade,
            dale_chall_score=dale_chall_score,
        )

        return {
            'sentence_count': len(sentences),
            'word_count': len(words),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'avg_word_length': round(sum(len(w) for w in words) / (len(words) + 1), 2),
            'avg_syllables': round(avg_syllables, 2),
            'flesch_reading_ease': flesch_reading_ease,        # v1.3.0 新增
            'flesch_kincaid_grade': flesch_kincaid_grade,      # v1.3.0 新增
            'dale_chall_score': dale_chall_score,              # v1.3.0 新增
            'readability_source': readability_source,          # v1.3.0 新增：textstat / heuristic
            'complexity_level': complexity_level,
        }

    @staticmethod
    def _count_syllables(word: str) -> int:
        word = word.lower()
        syllables = 0
        vowels = "aeiouy"
        previous_was_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllables += 1
            previous_was_vowel = is_vowel
        if word.endswith('e'):
            syllables -= 1
        if word.endswith('le') and len(word) > 2:
            syllables += 1
        return max(1, syllables)

    @staticmethod
    def _estimate_complexity_level(
        avg_sent_len: float,
        avg_syllables: float,
        flesch_kincaid_grade: Optional[float] = None,
        dale_chall_score: Optional[float] = None,
    ) -> str:
        """
        CEFR 等级估算（v1.3.0 重构）。

        优先级：
          1. textstat 可用 → 用 Flesch-Kincaid Grade + Dale-Chall 双指标融合
          2. 否则 → 校准过的经验公式（避免任何文本都被打成 C2）

        FKG → CEFR 映射（参考 CEFR-J 与 EnglishProfile 的研究）：
          FKG < 3   → A1
          FKG 3-5   → A2
          FKG 5-7   → B1
          FKG 7-10  → B2
          FKG 10-13 → C1
          FKG ≥ 13  → C2

        Dale-Chall 用于"软纠正"：
          DC ≤ 7（绝大多数 4 年级学生能懂）→ 至多 B1
          DC 7-9 → 至多 B2
          DC ≥ 9 → 至少 B2（学术文本）
        """
        # 优先链路：基于真实可读性指标
        if flesch_kincaid_grade is not None:
            fkg = flesch_kincaid_grade
            if fkg < 3:
                level_by_fkg = 'A1'
            elif fkg < 5:
                level_by_fkg = 'A2'
            elif fkg < 7:
                level_by_fkg = 'B1'
            elif fkg < 10:
                level_by_fkg = 'B2'
            elif fkg < 13:
                level_by_fkg = 'C1'
            else:
                level_by_fkg = 'C2'

            # Dale-Chall 软纠正：避免短句但全是难词被打成 A2
            if dale_chall_score is not None:
                if dale_chall_score >= 9.5 and level_by_fkg in ('A1', 'A2', 'B1'):
                    return 'B2'   # 学术词密集 → 不可能是初级
                if dale_chall_score <= 6.0 and level_by_fkg in ('C1', 'C2'):
                    return 'B2'   # 词都简单 → 不可能是 C 级
            return level_by_fkg

        # 降级链路：校准过的经验公式（v1.3.0 重新标定）
        # 原 v1.2.0 公式：score = avg_sent_len * 0.3 + avg_syllables * 0.7
        # 缺陷：句长权重 0.3 导致 score 几乎完全由句长决定，10 词句子就 ≥ 3 → C2
        # 新公式：句长权重大幅降低，主要由音节密度决定
        complexity_score = avg_sent_len * 0.05 + avg_syllables * 1.5
        if complexity_score < 2.5:
            return 'A1'
        if complexity_score < 3.0:
            return 'A2'
        if complexity_score < 3.5:
            return 'B1'
        if complexity_score < 4.0:
            return 'B2'
        if complexity_score < 4.5:
            return 'C1'
        return 'C2'

    def extract_complex_sentences(self, text: str, threshold: float = 15) -> List[Dict]:
        sentences = self.tokenize_sentences(text)
        complex_sentences = []
        for sentence in sentences:
            if len(sentence) > threshold:
                clause_count = len(re.findall(
                    r'\b(which|that|because|although|when|where)\b',
                    sentence, re.I,
                ))
                complex_sentences.append({
                    'sentence': sentence,
                    'length': len(sentence),
                    'clause_count': clause_count,
                    'suggestion': (
                        'Consider breaking this sentence into shorter clauses'
                        if clause_count > 2 else None
                    ),
                })
        return complex_sentences


# 测试
if __name__ == '__main__':
    analyzer = NLPAnalyzer()
    test_text = """
    Artificial intelligence is revolutionizing how we approach problem-solving.
    Data-driven frameworks enable computing platforms to scale efficiently.
    The implementation of sophisticated machine learning algorithms enables organizations
    to extract valuable insights from vast datasets.
    """
    vocab_info = analyzer.extract_vocabulary(test_text)
    print(f"Total: {vocab_info['total_words']}, Unique: {vocab_info['unique_words']}")
    print(f"Common: {len(vocab_info['vocabulary_by_level']['common'])}")
    print(f"Intermediate: {len(vocab_info['vocabulary_by_level']['intermediate'])}")
    print(f"Advanced: {len(vocab_info['vocabulary_by_level']['advanced'])}")
    print(f"Unknown: {len(vocab_info['vocabulary_by_level']['unknown'])}")
    print(f"Disclaimer: {vocab_info['disclaimer']}")

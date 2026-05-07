#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 分析引擎 - 使用 Claude API 识别常见错误句型 / 句子拆解 / 深度分析

【v1.1.0 修复】
- 移除"裸 except 返回空列表"的静默失败反模式 → 改为返回结构化结果（含 error_flag/error_type/error_message）
- 三处 client.messages.create 统一加 timeout=30s
- 用户友好的错误信息（不再把 anthropic.APIConnectionError 等堆栈直接抛给用户）
- 错误信息写日志（logging），用户侧只暴露简短提示
- ERROR_PATTERNS_PROMPT 紧凑化（紧凑列表代替冗长描述，约压缩 30%）
- 客户端延迟初始化 + 缺失 API Key 时不再 import 报错

【v1.1.1 优化】
- Y-24：合并 SENTENCE_ANALYSIS_PROMPT 与 BREAKDOWN_PROMPT 为参数化统一模板（JSON schema 驱动）
- Y-25：_safe_call_claude 增加线程安全 LRU 结果缓存（默认 128 条），避免主/子分析重叠调用
         可通过环境变量 ENGLISH_SKILL_CACHE_SIZE 调整；设为 0 禁用缓存
"""

import os
import json
import re
import hashlib
import logging
import threading
from collections import OrderedDict
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

# Anthropic 客户端延迟创建（缺少 ANTHROPIC_API_KEY 时也不会在 import 阶段崩溃）
_anthropic_client = None
_anthropic_import_error: Optional[str] = None

DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
API_TIMEOUT_SECONDS = 30.0

# ============= Y-25：LRU 结果缓存 =============

try:
    _CACHE_SIZE = int(os.getenv("ENGLISH_SKILL_CACHE_SIZE", "128"))
except ValueError:
    _CACHE_SIZE = 128

_cache_lock = threading.Lock()
_cache: "OrderedDict[str, Dict[str, Any]]" = OrderedDict()
_cache_stats = {"hit": 0, "miss": 0}


def _cache_key(prompt: str, max_tokens: int, model: str) -> str:
    """基于 prompt 内容+token 上限+model 生成稳定缓存 key。"""
    h = hashlib.sha256()
    h.update(model.encode("utf-8"))
    h.update(b"|")
    h.update(str(max_tokens).encode("utf-8"))
    h.update(b"|")
    h.update(prompt.encode("utf-8"))
    return h.hexdigest()


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    if _CACHE_SIZE <= 0:
        return None
    with _cache_lock:
        if key in _cache:
            # 访问后移到末尾（LRU）
            _cache.move_to_end(key)
            _cache_stats["hit"] += 1
            return _cache[key]
    return None


def _cache_put(key: str, value: Dict[str, Any]) -> None:
    if _CACHE_SIZE <= 0:
        return
    # 仅缓存成功结果；失败结果不入缓存以便下次重试
    if not value.get("ok"):
        return
    with _cache_lock:
        _cache[key] = value
        _cache.move_to_end(key)
        while len(_cache) > _CACHE_SIZE:
            _cache.popitem(last=False)
        _cache_stats["miss"] += 1


def cache_stats() -> Dict[str, int]:
    """对外暴露缓存命中统计（单测/性能排查用）。"""
    with _cache_lock:
        return {**_cache_stats, "size": len(_cache), "capacity": _CACHE_SIZE}


def cache_clear() -> None:
    with _cache_lock:
        _cache.clear()
        _cache_stats["hit"] = 0
        _cache_stats["miss"] = 0


def _get_client():
    """延迟初始化的 Anthropic 客户端；失败返回 None。"""
    global _anthropic_client, _anthropic_import_error
    if _anthropic_client is not None:
        return _anthropic_client
    try:
        from anthropic import Anthropic  # type: ignore
        _anthropic_client = Anthropic()
        return _anthropic_client
    except Exception as e:  # ImportError / API key missing / 配置问题
        _anthropic_import_error = str(e)
        logger.warning("Anthropic 客户端初始化失败: %s", e)
        return None


# ============= 错误结果工厂 =============

def _service_unavailable_payload(reason: str, where: str = "") -> Dict[str, Any]:
    """构造统一的"服务不可用"结构化结果（用户侧能据此识别降级）。"""
    return {
        "error_flag": True,
        "error_type": "service_unavailable",
        "error_message": "⚠️ 语法分析服务暂时不可用，请稍后重试",
        "_internal_reason": reason,  # 仅供日志/排查
        "_where": where,
    }


def _parse_error_payload(reason: str, where: str = "") -> Dict[str, Any]:
    return {
        "error_flag": True,
        "error_type": "parse_error",
        "error_message": "⚠️ 分析结果解析失败，本次结果可能不可用",
        "_internal_reason": reason,
        "_where": where,
    }


# ============= JSON 输出清洗 =============

def _strip_codeblock(text: str) -> str:
    """去除 LLM 输出可能附带的 ```json fenced block。"""
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*\n', '', text)
        text = re.sub(r'\n```\s*$', '', text)
    return text.strip()


def _safe_call_claude(prompt: str, max_tokens: int, where: str) -> Dict[str, Any]:
    """
    封装统一的 Claude 调用：
    - 加 timeout
    - 捕获具体异常类型（ImportError / anthropic.APIError / json 解析）
    - 失败返回结构化 error 字典；成功返回 {"ok": True, "raw": "..."}
    - Y-25：同 prompt+max_tokens+model 命中 LRU 缓存直接返回
    """
    # 1) 查缓存
    key = _cache_key(prompt, max_tokens, DEFAULT_MODEL)
    cached = _cache_get(key)
    if cached is not None:
        logger.debug("[%s] cache hit", where)
        return cached

    client = _get_client()
    if client is None:
        return {
            "ok": False,
            "payload": _service_unavailable_payload(
                f"client_init_failed: {_anthropic_import_error}", where
            ),
        }

    try:
        # 尝试导入 anthropic 异常类型用于精细化处理
        try:
            from anthropic import APIConnectionError, APITimeoutError, APIStatusError, APIError  # type: ignore
        except ImportError:
            APIConnectionError = APITimeoutError = APIStatusError = APIError = Exception  # type: ignore

        message = client.messages.create(
            model=DEFAULT_MODEL,
            max_tokens=max_tokens,
            timeout=API_TIMEOUT_SECONDS,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text.strip() if message.content else ""
        result = {"ok": True, "raw": raw}
        _cache_put(key, result)
        return result

    except APITimeoutError as e:
        logger.warning("[%s] Claude API 超时: %s", where, e)
        return {"ok": False, "payload": _service_unavailable_payload(f"timeout: {e}", where)}
    except APIConnectionError as e:
        logger.warning("[%s] Claude API 连接失败: %s", where, e)
        return {"ok": False, "payload": _service_unavailable_payload(f"connection: {e}", where)}
    except APIStatusError as e:
        logger.warning("[%s] Claude API 状态错误: %s", where, e)
        return {"ok": False, "payload": _service_unavailable_payload(f"status: {e}", where)}
    except APIError as e:
        logger.warning("[%s] Claude API 错误: %s", where, e)
        return {"ok": False, "payload": _service_unavailable_payload(f"api: {e}", where)}
    except Exception as e:  # 兜底，但只在日志里记录详细信息
        logger.exception("[%s] Claude 调用未预期异常", where)
        return {"ok": False, "payload": _service_unavailable_payload(f"unexpected: {e}", where)}


# ============= Y-24：统一 JSON 分析模板 =============

# schema_lines：传入 "- key\n- key2\n..." 形式的 JSON schema 键列表
_UNIFIED_ANALYSIS_TEMPLATE = """{task_instruction}

Sentence: "{sentence}"

Output ONLY a JSON object with these keys:
{schema_lines}

No code fences. No prose.
"""


def _build_json_prompt(task_instruction: str, sentence: str, schema_items: List[str]) -> str:
    """
    基于统一模板构建 JSON 输出型 prompt。
    Args:
        task_instruction: 任务首行指令（如 "Analyze the English sentence below."）
        sentence: 待分析句子
        schema_items: schema 键列表（每项形如 "key (描述)" 或 "key"）
    """
    schema_lines = "\n".join(f"- {item}" for item in schema_items)
    return _UNIFIED_ANALYSIS_TEMPLATE.format(
        task_instruction=task_instruction.strip(),
        sentence=sentence,
        schema_lines=schema_lines,
    )


def _parse_json_object_response(
    raw: str, where: str,
) -> Tuple[bool, Dict[str, Any]]:
    """
    将 LLM 返回解析为 JSON object。返回 (ok, data_or_error_payload)。
    """
    cleaned = _strip_codeblock(raw)
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            data["error_flag"] = False
            return True, data
        logger.warning("%s: 非对象响应: %r", where, cleaned[:200])
        return False, _parse_error_payload("non-object response", where)
    except json.JSONDecodeError as e:
        logger.warning("%s: JSON 解析失败: %s | raw=%r", where, e, cleaned[:200])
        return False, _parse_error_payload(f"json_decode: {e}", where)


class ErrorPatternAnalyzer:
    """使用 Claude 识别常见错误句型（已修复静默失败）"""

    # 紧凑化的 prompt（节省 ~30% tokens）
    ERROR_PATTERNS_PROMPT = """You are an expert English grammar teacher. For each sentence below, detect errors of these 7 types:
1.collocation 2.tense 3.article 4.number_agreement 5.preposition 6.word_order 7.modal_verb

For each error, output JSON object with keys:
error_type, sentence, issue, incorrect_form, correct_form, explanation

Output: ONLY a JSON array (use [] if no errors). No prose, no code fences.

Sentences:
{sentences}
"""

    # Y-24：以下两个深度分析任务共享 _UNIFIED_ANALYSIS_TEMPLATE，仅任务指令 + schema 不同
    _SENTENCE_ANALYSIS_TASK = "Analyze the English sentence below."
    _SENTENCE_ANALYSIS_SCHEMA = [
        "grammatical_analysis (subject/verb/objects/clauses)",
        "vocabulary_level (map of word->common|intermediate|advanced)",
        "syntax_structure (simple|compound|complex)",
        "possible_errors (string; \"No errors detected\" if none)",
        "simplification (string; or null if not needed)",
        "key_takeaway (one sentence)",
    ]

    @staticmethod
    def identify_error_patterns(sentences: List[str]) -> Dict[str, Any]:
        """
        识别常见错误句型。

        Returns:
            成功：{"error_flag": False, "errors": [ {...}, ... ]}
            失败：{"error_flag": True, "error_type": "...", "error_message": "...", "errors": []}
            **永远返回 dict，调用方据 error_flag 判定**
        """
        if not sentences:
            return {"error_flag": False, "errors": []}

        sentence_text = '\n'.join(f"{i+1}. {s}" for i, s in enumerate(sentences))
        prompt = ErrorPatternAnalyzer.ERROR_PATTERNS_PROMPT.format(sentences=sentence_text)

        result = _safe_call_claude(prompt, max_tokens=2048, where="identify_error_patterns")
        if not result["ok"]:
            payload = result["payload"]
            payload["errors"] = []  # 保证 errors 字段始终存在
            return payload

        raw = _strip_codeblock(result["raw"])
        try:
            errors = json.loads(raw)
            if not isinstance(errors, list):
                logger.warning("identify_error_patterns: 模型返回非数组: %r", raw[:200])
                payload = _parse_error_payload("non-array response", "identify_error_patterns")
                payload["errors"] = []
                return payload
            return {"error_flag": False, "errors": errors}
        except json.JSONDecodeError as e:
            logger.warning("identify_error_patterns: JSON 解析失败: %s | raw=%r", e, raw[:200])
            payload = _parse_error_payload(f"json_decode: {e}", "identify_error_patterns")
            payload["errors"] = []
            return payload

    @staticmethod
    def analyze_sentence_deep(sentence: str) -> Dict[str, Any]:
        """
        深度分析单个句子。
        成功返回 {"error_flag": False, ...analysis_fields...}
        失败返回 {"error_flag": True, "error_type": "...", "error_message": "..."}
        """
        prompt = _build_json_prompt(
            ErrorPatternAnalyzer._SENTENCE_ANALYSIS_TASK,
            sentence,
            ErrorPatternAnalyzer._SENTENCE_ANALYSIS_SCHEMA,
        )
        result = _safe_call_claude(prompt, max_tokens=1024, where="analyze_sentence_deep")
        if not result["ok"]:
            return result["payload"]
        ok, data = _parse_json_object_response(result["raw"], "analyze_sentence_deep")
        return data

    @staticmethod
    def extract_key_sentences(text: str, num_sentences: int = 5) -> List[str]:
        """从文本中提取关键句子（按长度排序选取）。无 API 调用。"""
        sentences = re.split(r'[.!?]+', text or "")
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        sentences = sorted(sentences, key=len, reverse=True)[:num_sentences]
        return sentences


class SentenceBreakdownHelper:
    """句子分解辅助工具（Y-24：已使用统一模板）"""

    _BREAKDOWN_TASK = "Break down the English sentence below."
    _BREAKDOWN_SCHEMA = [
        "main_clause",
        "subordinate_clauses (array)",
        "key_phrases (array of {type, text})",
        "literal_translation",
        "simplified_versions (array of 2-3 simpler sentences)",
        "common_mistakes (array)",
    ]

    @staticmethod
    def breakdown_sentence(sentence: str) -> Dict[str, Any]:
        """
        分解复杂句子。
        成功返回 {"error_flag": False, ...}
        失败返回 {"error_flag": True, ...}
        """
        prompt = _build_json_prompt(
            SentenceBreakdownHelper._BREAKDOWN_TASK,
            sentence,
            SentenceBreakdownHelper._BREAKDOWN_SCHEMA,
        )
        result = _safe_call_claude(prompt, max_tokens=1024, where="breakdown_sentence")
        if not result["ok"]:
            return result["payload"]
        ok, data = _parse_json_object_response(result["raw"], "breakdown_sentence")
        return data


# 测试
if __name__ == '__main__':
    test_sentences = [
        "She don't like coffee.",
        "I'm interested in to play football.",
        "The research are important for science.",
    ]
    print("=" * 50)
    print("Testing Error Pattern Detection")
    print("=" * 50)
    result = ErrorPatternAnalyzer.identify_error_patterns(test_sentences)
    print(f"error_flag: {result.get('error_flag')}")
    if result.get('error_flag'):
        print(f"⚠️ {result.get('error_message')}")
    else:
        print(f"Errors found: {len(result.get('errors', []))}")

    print("\n=== Cache stats ===")
    print(cache_stats())
    # 同样的调用应命中缓存
    _ = ErrorPatternAnalyzer.identify_error_patterns(test_sentences)
    print("After 2nd call:", cache_stats())

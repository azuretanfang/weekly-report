#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS 音频处理器 - 生成例句/单词音频和音标

【v1.1.0 修复】
- 移除"伪 IPA 占位符"反模式：g2p_en 失败时返回 "N/A"，**禁止返回 /word/ 假数据**
- G2p 单例缓存（避免每次实例化耗 ~3s）
- gTTS 失败不返回 True，失败/降级状态显式区分

【v1.2.0 变更】
- 移除 VocabularyCardGenerator / AnkiExporter（不再支持 Anki 卡片生成与导出）
- 仅保留 PhoneticTranscriber（IPA 音标）与 TTSAudioGenerator（gTTS 音频）
"""

import os
import re
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


# ============= G2p 单例（线程安全）=============

_g2p_instance = None
_g2p_lock = threading.Lock()
_g2p_init_failed = False


def _get_g2p():
    """单例 G2p；初始化失败后不再重试，避免重复 3s 加载。"""
    global _g2p_instance, _g2p_init_failed
    if _g2p_init_failed:
        return None
    if _g2p_instance is not None:
        return _g2p_instance
    with _g2p_lock:
        if _g2p_instance is not None:
            return _g2p_instance
        try:
            from g2p_en import G2p  # type: ignore
            _g2p_instance = G2p()
            return _g2p_instance
        except Exception as e:
            logger.warning("G2p 初始化失败，IPA 将降级为 N/A：%s", e)
            _g2p_init_failed = True
            return None


# ARPAbet → IPA 简化映射（覆盖常见音素，未覆盖时保留 ARPAbet 标识，避免胡编）
ARPABET_TO_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð",
    "EH": "ɛ", "ER": "ɝ", "EY": "eɪ", "F": "f", "G": "ɡ",
    "HH": "h", "IH": "ɪ", "IY": "i", "JH": "dʒ",
    "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ",
    "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "r", "S": "s", "SH": "ʃ",
    "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u",
    "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}


def _arpabet_to_ipa(phonemes: list) -> str:
    """ARPAbet 列表转 IPA，去除重音数字（如 AH0/AH1/AH2 → AH）。"""
    out = []
    for p in phonemes:
        if not p:
            continue
        # 跳过非音素（标点等）
        if not p[0].isalpha():
            continue
        base = re.sub(r'\d+$', '', p).upper()
        out.append(ARPABET_TO_IPA.get(base, base.lower()))  # 未知音素 fallback 为小写 ARPAbet
    return ''.join(out)


# ============= 音标生成 =============

class PhoneticTranscriber:
    """音标生成器。失败明确返回 N/A，禁止返回假音标。"""

    @staticmethod
    def generate_ipa(word: str) -> str:
        """
        生成 IPA 音标。

        Returns:
            "/ɪnˈtelɪdʒəns/" 形式的真实 IPA；
            如果 g2p 库不可用 → 返回 "N/A"（**绝不返回 /word/ 这种假音标**）
        """
        if not word or not isinstance(word, str):
            return "N/A"

        g2p = _get_g2p()
        if g2p is None:
            return "N/A"

        try:
            phonemes = g2p(word)
            ipa = _arpabet_to_ipa(phonemes)
            if not ipa:
                return "N/A"
            return f"/{ipa}/"
        except Exception as e:
            logger.warning("IPA 生成失败 word=%r: %s", word, e)
            return "N/A"

    # 向后兼容旧 API
    @staticmethod
    def generate_ipa_proper(word: str) -> str:
        return PhoneticTranscriber.generate_ipa(word)


# ============= TTS 音频 =============

class TTSAudioGenerator:
    """Google TTS 音频生成器（gTTS）"""

    @staticmethod
    def _safe_generate(text: str, output_path: str, language: str, slow: bool) -> bool:
        try:
            from gtts import gTTS  # type: ignore
        except ImportError as e:
            logger.warning("gTTS 未安装：%s", e)
            return False

        try:
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(output_path)
            # 校验产物
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                logger.warning("gTTS 保存后文件不存在或为空：%s", output_path)
                return False
            return True
        except Exception as e:
            logger.warning("gTTS 生成失败 text=%r: %s", text[:50], e)
            return False

    @staticmethod
    def generate_sentence_audio(sentence: str, output_path: str, language: str = 'en') -> bool:
        return TTSAudioGenerator._safe_generate(sentence, output_path, language, slow=False)

    @staticmethod
    def generate_word_audio(word: str, output_path: str, language: str = 'en') -> bool:
        return TTSAudioGenerator._safe_generate(word, output_path, language, slow=True)

    # Y-29：并行批量生成音频
    @staticmethod
    def generate_batch(
        tasks: List[Tuple[str, str]],
        language: str = 'en',
        slow: bool = False,
        max_workers: int = 4,
    ) -> Dict[str, bool]:
        """
        并行批量生成音频。
        Args:
            tasks: [(text, output_path), ...]
            language: 语种
            slow: 是否慢速（单词场景常用 True）
            max_workers: 并发数（gTTS 基于 Google 公开接口，过高会被限流，4 较稳）
        Returns:
            {output_path: success_bool}
        """
        if not tasks:
            return {}

        results: Dict[str, bool] = {}
        # 去重（同一文本多次生成毫无意义）
        seen = {}
        unique_tasks = []
        for text, path in tasks:
            key = (text, path)
            if key in seen:
                continue
            seen[key] = True
            unique_tasks.append((text, path))

        def _run(text: str, path: str) -> Tuple[str, bool]:
            ok = TTSAudioGenerator._safe_generate(text, path, language, slow)
            return path, ok

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = [pool.submit(_run, t, p) for t, p in unique_tasks]
            for fut in as_completed(futures):
                try:
                    path, ok = fut.result()
                    results[path] = ok
                except Exception as e:
                    logger.warning("batch TTS task failed: %s", e)
        return results


# ============= 测试 =============
if __name__ == '__main__':
    print("=== IPA Test ===")
    for w in ["beautiful", "intelligence", "infrastructure"]:
        print(f"{w}: {PhoneticTranscriber.generate_ipa(w)}")

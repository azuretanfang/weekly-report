#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TTS音频处理器 - 生成例句音频和音标
"""

import os
import json
import re
from typing import Dict, List, Optional
from pathlib import Path
from gtts import gTTS
import tempfile


class PhoneticTranscriber:
    """音标生成器"""
    
    # 简化的G2P映射（实际应使用g2p_en库）
    PHONEME_MAP = {
        'a': 'æ', 'e': 'ɛ', 'i': 'i', 'o': 'ɔ', 'u': 'ʊ',
        'oa': 'oʊ', 'ai': 'eɪ', 'oi': 'ɔɪ', 'ou': 'aʊ',
    }
    
    @staticmethod
    def generate_ipa(word: str) -> str:
        """
        生成IPA音标（简化版）
        实际应集成g2p_en库
        
        Args:
            word: 英文单词
            
        Returns:
            IPA音标
        """
        word_lower = word.lower()
        
        # 这里应使用g2p_en库：
        # from g2p_en import G2p
        # g2p = G2p()
        # phonemes = g2p(word)
        # return ''.join(phonemes)
        
        # 简化示例（实际应使用真实库）
        return f"/{word_lower}/"  # 占位符
    
    @staticmethod
    def generate_ipa_proper(word: str) -> str:
        """
        使用g2p_en生成真实的IPA音标
        """
        try:
            from g2p_en import G2p
            g2p = G2p()
            phonemes = g2p(word)
            ipa = ''.join(phonemes)
            return f"/{ipa}/"
        except Exception as e:
            # 降级处理
            return f"/{word.lower()}/"


class TTSAudioGenerator:
    """Google TTS音频生成器"""
    
    @staticmethod
    def generate_sentence_audio(
        sentence: str,
        output_path: str,
        language: str = 'en'
    ) -> bool:
        """
        使用Google TTS生成句子音频
        
        Args:
            sentence: 句子文本
            output_path: 输出MP3文件路径
            language: 语言代码 (默认 'en')
            
        Returns:
            成功标志
        """
        try:
            tts = gTTS(text=sentence, lang=language, slow=False)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return False
    
    @staticmethod
    def generate_word_audio(
        word: str,
        output_path: str,
        language: str = 'en'
    ) -> bool:
        """
        生成单个单词的音频
        
        Args:
            word: 单词
            output_path: 输出MP3文件路径
            language: 语言代码
            
        Returns:
            成功标志
        """
        try:
            tts = gTTS(text=word, lang=language, slow=True)
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"Error generating word audio: {str(e)}")
            return False


class VocabularyCardGenerator:
    """Anki卡片生成器"""
    
    @staticmethod
    def create_anki_card(
        word: str,
        pronunciation: str,
        definition: str,
        example_sentence: str,
        example_translation: str,
        example_audio_path: Optional[str] = None,
        word_audio_path: Optional[str] = None,
        difficulty_level: str = 'intermediate'
    ) -> Dict:
        """
        创建Anki卡片数据
        
        Args:
            word: 单词
            pronunciation: 音标/发音
            definition: 中文定义
            example_sentence: 例句
            example_translation: 例句翻译
            example_audio_path: 例句音频路径
            word_audio_path: 单词音频路径
            difficulty_level: 难度等级
            
        Returns:
            卡片数据字典
        """
        # 生成音频标记（Anki格式）
        example_audio_tag = f'[sound:{Path(example_audio_path).name}]' if example_audio_path else ''
        word_audio_tag = f'[sound:{Path(word_audio_path).name}]' if word_audio_path else ''
        
        return {
            'front': f"""
            <div style="font-size: 1.5em; font-weight: bold;">{word}</div>
            <div style="color: #666; font-size: 1.1em;">{pronunciation}</div>
            <div style="margin-top: 10px; font-size: 0.9em;">{word_audio_tag}</div>
            """,
            'back': f"""
            <div style="font-size: 1.2em; font-weight: bold;">Definition</div>
            <div style="margin: 10px 0; color: #333;">{definition}</div>
            
            <div style="font-size: 1.2em; font-weight: bold; margin-top: 15px;">Example Sentence</div>
            <div style="margin: 10px 0; color: #333;">{example_sentence}</div>
            <div style="margin: 10px 0; color: #999; font-size: 0.9em;">{example_translation}</div>
            <div style="margin: 10px 0; font-size: 0.9em;">{example_audio_tag}</div>
            
            <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 0.8em; color: #999;">
                Level: {difficulty_level}
            </div>
            """,
            'audio_files': [f for f in [example_audio_path, word_audio_path] if f],
            'difficulty_level': difficulty_level,
            'word': word,
            'pronunciation': pronunciation,
        }


class AnkiExporter:
    """Anki导出器"""
    
    @staticmethod
    def export_to_apkg(
        cards: List[Dict],
        deck_name: str = "English Reading",
        output_path: str = "output.apkg"
    ) -> bool:
        """
        导出为Anki格式（.apkg文件）
        
        Args:
            cards: 卡片列表
            deck_name: 卡牌组名称
            output_path: 输出文件路径
            
        Returns:
            成功标志
        """
        try:
            import genanki
            
            # 创建卡片组
            deck = genanki.Deck(2023, deck_name)
            
            # 定义卡片模型
            model = genanki.Model(
                1671467743,
                'English Reading Card',
                fields=[
                    {'name': 'Front'},
                    {'name': 'Back'},
                    {'name': 'Word'},
                    {'name': 'Pronunciation'},
                    {'name': 'DifficultyLevel'},
                ],
                templates=[{
                    'name': 'Card 1',
                    'qfmt': '{{Front}}',
                    'afmt': '{{Back}}',
                }]
            )
            
            # 添加卡片
            for card_data in cards:
                note = genanki.Note(
                    model=model,
                    fields=[
                        card_data.get('front', ''),
                        card_data.get('back', ''),
                        card_data.get('word', ''),
                        card_data.get('pronunciation', ''),
                        card_data.get('difficulty_level', ''),
                    ]
                )
                
                # 添加音频文件
                if 'audio_files' in card_data:
                    for audio_file in card_data['audio_files']:
                        if audio_file and os.path.exists(audio_file):
                            note.fields[1] += f' [sound:{Path(audio_file).name}]'
                
                deck.add_notes(note)
            
            # 保存为.apkg
            package = genanki.Package(deck)
            
            # 添加音频文件
            for card_data in cards:
                if 'audio_files' in card_data:
                    for audio_file in card_data['audio_files']:
                        if audio_file and os.path.exists(audio_file):
                            package.media_files.append(audio_file)
            
            package.write_to_file(output_path)
            return True
            
        except Exception as e:
            print(f"Error exporting to Anki: {str(e)}")
            return False
    
    @staticmethod
    def export_to_csv(
        cards: List[Dict],
        output_path: str = "output.csv"
    ) -> bool:
        """
        导出为CSV格式
        """
        try:
            import csv
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Word', 'Pronunciation', 'Front', 'Back', 'Difficulty Level'])
                
                for card in cards:
                    writer.writerow([
                        card.get('word', ''),
                        card.get('pronunciation', ''),
                        card.get('front', '').replace('\n', ' '),
                        card.get('back', '').replace('\n', ' '),
                        card.get('difficulty_level', ''),
                    ])
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False


# 测试
if __name__ == '__main__':
    # 测试音标生成
    word = "beautiful"
    ipa = PhoneticTranscriber.generate_ipa(word)
    print(f"Word: {word}, IPA: {ipa}")
    
    # 测试音频生成
    print("\nGenerating audio...")
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "test.mp3")
        success = TTSAudioGenerator.generate_sentence_audio(
            "Artificial intelligence is transforming industries.",
            audio_path
        )
        print(f"Audio generation success: {success}")
        
        if success:
            print(f"Audio file size: {os.path.getsize(audio_path)} bytes")
    
    # 测试卡片生成
    print("\nGenerating Anki card...")
    card = VocabularyCardGenerator.create_anki_card(
        word="intelligence",
        pronunciation="/ɪnˈtelɪdʒəns/",
        definition="智力，聪慧；信息",
        example_sentence="Artificial intelligence is transforming industries.",
        example_translation="人工智能正在改变各个行业。",
        difficulty_level="intermediate"
    )
    print(f"Card created: {card['word']}")

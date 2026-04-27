#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入解析器 - 支持文本/URL/文件输入
"""

import re
import requests
from pathlib import Path
from typing import Tuple, Optional
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """从HTML中提取纯文本"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.skip = True
            
    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.skip = False
            
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)
                
    def get_text(self):
        return '\n'.join(self.text)


class ContentParser:
    """内容解析器"""
    
    @staticmethod
    def parse_url(url: str) -> Tuple[str, str]:
        """
        从URL提取内容
        返回: (title, content)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            
            # 提取标题
            title_match = re.search(r'<title>([^<]+)</title>', response.text)
            title = title_match.group(1) if title_match else 'Untitled'
            
            # 提取正文（简单启发式）
            # 移除script和style
            content = re.sub(r'<script[^>]*>.*?</script>', '', response.text, flags=re.DOTALL)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
            
            # 使用HTMLParser提取文本
            parser = HTMLTextExtractor()
            parser.feed(content)
            text = parser.get_text()
            
            # 清理空白和特殊字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            return title, text
        except Exception as e:
            raise ValueError(f"URL解析失败: {str(e)}")
    
    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, str]:
        """
        从文件读取内容
        支持 .txt, .md 格式
        返回: (filename, content)
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            if path.suffix not in ['.txt', '.md']:
                raise ValueError(f"不支持的文件格式: {path.suffix}")
            
            content = path.read_text(encoding='utf-8')
            
            # 清理markdown语法（如果是md文件）
            if path.suffix == '.md':
                content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
                content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
            
            return path.stem, content
        except Exception as e:
            raise ValueError(f"文件解析失败: {str(e)}")
    
    @staticmethod
    def parse_text(text: str) -> Tuple[str, str]:
        """
        解析纯文本
        返回: (title_auto, content)
        """
        text = text.strip()
        if not text:
            raise ValueError("输入文本为空")
        
        # 第一句作为title（最多50字符）
        lines = text.split('\n')
        title = lines[0][:50] if lines[0] else "Untitled"
        
        return title, text
    
    @staticmethod
    def parse(content: str, input_type: str = 'auto') -> Tuple[str, str]:
        """
        自动或指定类型解析内容
        
        Args:
            content: 输入内容
            input_type: 'url' | 'file' | 'text' | 'auto'
            
        Returns:
            (title, parsed_content)
        """
        if input_type == 'auto':
            # 自动检测类型
            if content.startswith('http://') or content.startswith('https://'):
                return ContentParser.parse_url(content)
            elif Path(content).exists():
                return ContentParser.parse_file(content)
            else:
                return ContentParser.parse_text(content)
        elif input_type == 'url':
            return ContentParser.parse_url(content)
        elif input_type == 'file':
            return ContentParser.parse_file(content)
        elif input_type == 'text':
            return ContentParser.parse_text(content)
        else:
            raise ValueError(f"未知的输入类型: {input_type}")


# 测试
if __name__ == '__main__':
    test_text = """
    The artificial intelligence revolution is transforming industries worldwide.
    Companies are increasingly adopting machine learning algorithms to optimize operations.
    """
    
    title, content = ContentParser.parse(test_text, 'text')
    print(f"Title: {title}")
    print(f"Content: {content[:100]}...")

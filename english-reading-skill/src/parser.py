#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入解析器 - 支持文本/URL/文件输入

【v1.1.0 安全加固】
- SSRF 防护：URL 校验（仅允许 https + 公网域名/IP；屏蔽私有/回环/链路本地/保留地址）
- 响应体大小限制（默认 1MB），防资源耗尽
- 文件大小限制（默认 1MB）
- 详细的可定位错误（不再统一裹成 ValueError "URL解析失败"）
"""

import re
import socket
import ipaddress
from urllib.parse import urlparse
import requests
from pathlib import Path
from typing import Tuple, Optional
from html.parser import HTMLParser

# ===== 安全配置 =====
MAX_RESPONSE_BYTES = 1 * 1024 * 1024  # 1 MB
MAX_FILE_BYTES = 1 * 1024 * 1024  # 1 MB
HTTP_TIMEOUT_SECONDS = 10

# 仅允许的协议
ALLOWED_SCHEMES = {"https"}

# 域名级黑名单（即使解析为公网 IP 也拒绝）
BLOCKED_HOSTNAMES = {
    "localhost", "ip6-localhost", "ip6-loopback",
    "metadata.google.internal",
    "metadata.tencentyun.com",
    "100.100.100.200",  # aliyun metadata
}


class URLValidationError(ValueError):
    """URL 安全校验失败"""
    pass


def _is_blocked_ip(ip_str: str) -> bool:
    """判断 IP 是否属于受限范围（私有/回环/链路本地/保留/多播）"""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        # 不是合法 IP，让上层继续处理（按域名走）
        return False
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def validate_url(url: str) -> str:
    """
    SSRF 防御：校验 URL 是否安全可访问。

    Returns:
        normalized url

    Raises:
        URLValidationError: 校验失败时抛出，调用方应据此返回友好提示
    """
    if not isinstance(url, str) or not url.strip():
        raise URLValidationError("URL 为空")

    url = url.strip()
    parsed = urlparse(url)

    # 1. 协议白名单（仅 https）
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise URLValidationError(
            f"出于安全考虑，仅支持 HTTPS 协议（当前：{parsed.scheme or '空'}）"
        )

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise URLValidationError("URL 缺少有效主机名")

    # 2. 域名级黑名单
    if hostname in BLOCKED_HOSTNAMES:
        raise URLValidationError(f"出于安全考虑，不允许访问该主机：{hostname}")

    # 3. 端口限制（仅允许默认端口和常见 https 端口）
    if parsed.port is not None and parsed.port not in (443, 8443):
        raise URLValidationError(
            f"出于安全考虑，仅允许访问默认 https 端口（当前端口：{parsed.port}）"
        )

    # 4. 主机解析后的 IP 不能是私有/回环/链路本地
    #    使用 getaddrinfo 解析所有 A/AAAA 记录，任意一条命中黑名单就拒绝
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        raise URLValidationError(f"无法解析域名 {hostname}：{e}")

    resolved_ips = {info[4][0] for info in addr_infos}
    for ip_str in resolved_ips:
        if _is_blocked_ip(ip_str):
            raise URLValidationError(
                f"出于安全考虑，不允许访问内网/保留地址（{hostname} → {ip_str}）"
            )

    return url


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
        从 URL 提取内容（含 SSRF 防护 + 响应大小限制）

        Returns:
            (title, content)

        Raises:
            URLValidationError: URL 不通过安全校验
            ValueError: 抓取失败 / 响应过大 / 解析失败
        """
        # 1. 安全校验
        safe_url = validate_url(url)

        # 2. 安全抓取（流式 + 限制大小 + 超时）
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; EnglishReadingSkill/1.1)'
        }
        try:
            with requests.get(
                safe_url,
                headers=headers,
                timeout=HTTP_TIMEOUT_SECONDS,
                stream=True,
                allow_redirects=True,
            ) as response:
                # 二次校验：重定向后的最终 URL
                final_url = response.url
                if final_url != safe_url:
                    # 对最终 URL 再做一次安全校验
                    validate_url(final_url)

                # Content-Length 预检
                content_length = response.headers.get('Content-Length')
                if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                    raise ValueError(
                        f"目标资源过大（{content_length} 字节，上限 {MAX_RESPONSE_BYTES} 字节）"
                    )

                # 流式读取，超过上限即截断
                chunks = []
                total = 0
                for chunk in response.iter_content(chunk_size=8192, decode_unicode=False):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > MAX_RESPONSE_BYTES:
                        raise ValueError(
                            f"目标资源超过 {MAX_RESPONSE_BYTES} 字节上限，已中止抓取"
                        )
                    chunks.append(chunk)

                raw = b''.join(chunks)
                # 字符集探测
                response.encoding = response.apparent_encoding or 'utf-8'
                text_html = raw.decode(response.encoding, errors='replace')

        except requests.exceptions.Timeout:
            raise ValueError(f"URL 抓取超时（>{HTTP_TIMEOUT_SECONDS}s）")
        except requests.exceptions.ConnectionError as e:
            raise ValueError(f"URL 连接失败：{e}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"URL 抓取失败：{e}")

        # 3. 内容解析
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', text_html, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else 'Untitled'

        content = re.sub(r'<script[^>]*>.*?</script>', '', text_html, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

        parser = HTMLTextExtractor()
        try:
            parser.feed(content)
        except Exception as e:
            raise ValueError(f"HTML 解析失败：{e}")

        text = parser.get_text()
        text = re.sub(r'\s+', ' ', text).strip()

        if not text:
            raise ValueError("URL 抓取成功但未能提取出有效正文")

        return title, text

    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, str]:
        """
        从文件读取内容（含大小限制）

        支持 .txt, .md
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() not in ['.txt', '.md']:
            raise ValueError(f"不支持的文件格式: {path.suffix}（仅支持 .txt / .md）")

        # 大小限制
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError(
                f"文件过大（{size} 字节，上限 {MAX_FILE_BYTES} 字节）"
            )

        try:
            content = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # 兼容性兜底
            content = path.read_text(encoding='utf-8', errors='replace')

        # 清理 markdown 语法
        if path.suffix.lower() == '.md':
            content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
            content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

        if not content.strip():
            raise ValueError("文件内容为空")

        return path.stem, content

    @staticmethod
    def parse_text(text: str) -> Tuple[str, str]:
        """解析纯文本，返回 (auto_title, content)"""
        if not isinstance(text, str):
            raise ValueError("输入必须是字符串")

        text = text.strip()
        if not text:
            raise ValueError("输入文本为空")

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
            if isinstance(content, str) and (content.startswith('http://') or content.startswith('https://')):
                return ContentParser.parse_url(content)
            try:
                exists = Path(content).exists()
            except (OSError, ValueError):
                exists = False
            if exists:
                return ContentParser.parse_file(content)
            return ContentParser.parse_text(content)

        if input_type == 'url':
            return ContentParser.parse_url(content)
        if input_type == 'file':
            return ContentParser.parse_file(content)
        if input_type == 'text':
            return ContentParser.parse_text(content)

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

    # SSRF 防御自测
    bad_urls = [
        "http://example.com",          # 非 https
        "https://localhost/x",         # 黑名单
        "https://10.0.0.1/x",          # 私有 IP
        "https://127.0.0.1/x",         # 回环
        "https://169.254.169.254/x",   # 链路本地（云元数据）
    ]
    for u in bad_urls:
        try:
            validate_url(u)
            print(f"❌ 未拦截: {u}")
        except URLValidationError as e:
            print(f"✅ 已拦截 {u}: {e}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR行业资讯周报 - 企业微信群推送脚本

功能：
  1. 将周报截图为高清长图
  2. 通过企业微信群机器人推送 Markdown 摘要 + 长图
  3. 支持自动检测最新周报

使用方式：
  python send_wechat.py                          # 自动检测最新周报并推送
  python send_wechat.py --file hr-weekly-report-0401-0406  # 指定文件前缀
  python send_wechat.py --test                    # 测试模式（不实际发送）

前置条件：
  1. 在企业微信群中添加群机器人，获取 Webhook URL
  2. 安装依赖: pip install requests
  3. 如需截图功能: pip install pyppeteer 或使用 auto_screenshot.py
"""

import os
import sys
import glob
import json
import hashlib
import base64
import argparse
import requests
from datetime import datetime


# ==================== 配置区域 ====================

# 企业微信群机器人 Webhook URL（在群设置 → 群机器人 → 添加机器人 → 获取）
# ⚠️ 请替换为实际的 Webhook URL
WECHAT_WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_WEBHOOK_KEY"

# 周报在线版本的基础URL（GitHub Pages 或其他托管平台）
ONLINE_BASE_URL = "https://azuretanfang.github.io/weekly-report/HR行业周报"

# ==================== 配置区域结束 ====================


def auto_detect_latest_report():
    """自动检测最新一期HR周报文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(script_dir, "hr-weekly-report-????-????.html")
    html_files = sorted(glob.glob(pattern))
    
    if not html_files:
        print("❌ 未找到任何HR周报 HTML 文件")
        sys.exit(1)
    
    latest_html = os.path.basename(html_files[-1])
    prefix = latest_html.replace(".html", "")
    parts = prefix.split("-")  # ['hr', 'weekly', 'report', '0401', '0406']
    start_mmdd = parts[3]
    end_mmdd = parts[4]
    
    start_display = f"{start_mmdd[:2]}.{start_mmdd[2:]}"
    end_display = f"{end_mmdd[:2]}.{end_mmdd[2:]}"
    period = f"{start_display} - {end_display}"
    
    year = datetime.now().year
    start_month = int(start_mmdd[:2])
    start_day = int(start_mmdd[2:])
    week_num = (start_day - 1) // 7 + 1
    title = f"{year}年{start_month}月第{week_num}周 HR行业资讯周报"
    
    return prefix, title, period


def send_markdown_message(title, period, prefix):
    """发送 Markdown 格式的周报摘要到企微群"""
    
    online_url = f"{ONLINE_BASE_URL}/{prefix}.html"
    
    markdown_content = f"""## 📋 {title}
> 📅 {period} · 聚焦互联网与游戏行业
> 🔒 HRBP 团队内部参阅

### 本期板块
- ⚖️ **政策法规** — 劳动法/社保/合规动态
- 💼 **薪酬与人才市场** — 招聘趋势/薪资报告
- 🏆 **行业标杆实践** — 大厂HR创新做法
- 🤖 **AI+HR趋势** — 技术前沿/工具推荐
- 🔥 **热点事件** — 舆情监控/案例借鉴

> 🏢 标记了 **"与我们相关"** 的条目需重点关注

📄 [点击查看完整在线版本]({online_url})"""
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }
    
    return payload


def send_image_message(image_path):
    """发送图片消息到企微群"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # 企微要求的 base64 和 md5
    base64_data = base64.b64encode(image_data).decode('utf-8')
    md5_hash = hashlib.md5(image_data).hexdigest()
    
    payload = {
        "msgtype": "image",
        "image": {
            "base64": base64_data,
            "md5": md5_hash
        }
    }
    
    return payload


def send_news_card(title, period, prefix, highlights=None):
    """发送图文卡片消息"""
    online_url = f"{ONLINE_BASE_URL}/{prefix}.html"
    
    description = f"📅 {period}\n聚焦互联网与游戏行业 · HRBP内部参阅"
    if highlights:
        description += f"\n\n本期看点：{' | '.join(highlights[:3])}"
    
    payload = {
        "msgtype": "news",
        "news": {
            "articles": [
                {
                    "title": f"📋 {title}",
                    "description": description,
                    "url": online_url,
                    "picurl": ""  # 可放周报封面图URL
                }
            ]
        }
    }
    
    return payload


def do_send(payload, test_mode=False):
    """实际发送消息到企微"""
    if test_mode:
        print("\n🧪 测试模式 - 以下为将要发送的消息内容:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return True
    
    if "YOUR_WEBHOOK_KEY" in WECHAT_WEBHOOK_URL:
        print("❌ 请先配置企业微信群机器人的 Webhook URL")
        print("   打开 send_wechat.py，修改 WECHAT_WEBHOOK_URL 变量")
        return False
    
    try:
        resp = requests.post(
            WECHAT_WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        result = resp.json()
        
        if result.get("errcode") == 0:
            print("✅ 消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="HR周报企业微信群推送")
    parser.add_argument("--file", help="指定周报文件前缀（如 hr-weekly-report-0401-0406）")
    parser.add_argument("--test", action="store_true", help="测试模式，不实际发送")
    parser.add_argument("--image", help="附带发送的长图文件路径")
    parser.add_argument("--mode", choices=["markdown", "news", "all"], default="markdown",
                        help="发送模式: markdown(摘要), news(图文卡片), all(全部)")
    args = parser.parse_args()
    
    # 检测周报
    if args.file:
        prefix = args.file
        parts = prefix.split("-")
        start_mmdd = parts[3]
        end_mmdd = parts[4]
        start_display = f"{start_mmdd[:2]}.{start_mmdd[2:]}"
        end_display = f"{end_mmdd[:2]}.{end_mmdd[2:]}"
        period = f"{start_display} - {end_display}"
        year = datetime.now().year
        start_month = int(start_mmdd[:2])
        start_day = int(start_mmdd[2:])
        week_num = (start_day - 1) // 7 + 1
        title = f"{year}年{start_month}月第{week_num}周 HR行业资讯周报"
    else:
        prefix, title, period = auto_detect_latest_report()
    
    print("=" * 60)
    print(f"📤 HR行业资讯周报 - 企微群推送")
    print(f"📋 标题: {title}")
    print(f"📅 周期: {period}")
    print(f"📁 文件: {prefix}")
    print(f"🧪 模式: {'测试' if args.test else '正式发送'}")
    print("=" * 60)
    
    success = True
    
    # 发送 Markdown 摘要
    if args.mode in ("markdown", "all"):
        print("\n📝 发送 Markdown 摘要...")
        payload = send_markdown_message(title, period, prefix)
        success = do_send(payload, args.test) and success
    
    # 发送图文卡片
    if args.mode in ("news", "all"):
        print("\n📰 发送图文卡片...")
        payload = send_news_card(title, period, prefix)
        success = do_send(payload, args.test) and success
    
    # 发送长图（如果提供）
    if args.image:
        if os.path.exists(args.image):
            print(f"\n🖼️ 发送长图: {args.image}")
            payload = send_image_message(args.image)
            success = do_send(payload, args.test) and success
        else:
            print(f"⚠️ 图片文件不存在: {args.image}")
    
    if success:
        print("\n🎉 推送完成！")
    else:
        print("\n⚠️ 部分消息推送失败，请检查配置")


if __name__ == "__main__":
    main()

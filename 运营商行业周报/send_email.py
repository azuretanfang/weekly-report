#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营商行业周报邮件发送脚本
- 邮件正文以高清长图为主体（CID内嵌，不依赖外链）
- 点击图片跳转在线HTML版本
- 支持自动日期计算，无需手动修改参数
"""

import os
import sys
import glob
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header


# ==================== 配置区域 ====================

# SMTP 邮件服务器配置
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465  # SSL端口
SENDER_EMAIL = "340191272@qq.com"
SENDER_PASSWORD = "pjbwfffghxmmbhge"  # QQ邮箱授权码

# 收件人列表
RECIPIENTS = [
    "fangtan@tencent.com",
    "klauskuang@tencent.com",
    "winnieezhu@tencent.com",
    "rebeccaxrlu@tencent.com",
    "estherfan@tencent.com",
    "angelaxzhao@tencent.com",
    "kimimczhang@tencent.com",
    "peterxsun@tencent.com",
    "mosessun@tencent.com",
    "selinapang@tencent.com",
    "davidmuxu@tencent.com",
    "nikizzhang@tencent.com",
    "eonefeng@tencent.com",
]

# 抄送列表（CC）
CC_RECIPIENTS = [
    "jamesjgbai@tencent.com",
    "anankeli@tencent.com",
    "coolkang@tencent.com",
    "ottozhou@tencent.com",
]

GITHUB_PAGES_BASE = "https://azuretanfang.github.io/weekly-report/运营商行业周报"

# ==================== 配置区域结束 ====================


def auto_detect_latest_report():
    """自动检测最新一期周报文件，返回 (file_prefix, title, period)"""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 扫描所有 weekly-report-MMDD-MMDD.html 文件
    pattern = os.path.join(script_dir, "weekly-report-????-????.html")
    html_files = sorted(glob.glob(pattern))

    if not html_files:
        print("❌ 未找到任何周报 HTML 文件")
        sys.exit(1)

    # 取最后一个（按文件名排序，即日期最新的）
    latest_html = os.path.basename(html_files[-1])
    # 例: weekly-report-0309-0315.html
    prefix = latest_html.replace(".html", "")  # weekly-report-0309-0315
    parts = prefix.split("-")  # ['weekly', 'report', '0309', '0315']
    start_mmdd = parts[2]  # 0309
    end_mmdd = parts[3]    # 0315

    # 格式化日期显示
    start_display = f"{start_mmdd[:2]}.{start_mmdd[2:]}"  # 03.09
    end_display = f"{end_mmdd[:2]}.{end_mmdd[2:]}"        # 03.15
    period = f"{start_display} - {end_display}"

    # 计算年份和周数 —— 用当前年份
    year = datetime.now().year
    start_month = int(start_mmdd[:2])

    # 计算是当月第几周
    start_day = int(start_mmdd[2:])
    week_num = (start_day - 1) // 7 + 1
    title = f"{year}年{start_month}月第{week_num}周运营商行业周报"

    return prefix, title, period


def auto_detect_or_manual(file_prefix=None):
    """根据传入参数或自动检测来确定周报参数"""
    if file_prefix:
        # 手动指定文件前缀
        parts = file_prefix.split("-")
        start_mmdd = parts[2]
        end_mmdd = parts[3]
        start_display = f"{start_mmdd[:2]}.{start_mmdd[2:]}"
        end_display = f"{end_mmdd[:2]}.{end_mmdd[2:]}"
        period = f"{start_display} - {end_display}"
        year = datetime.now().year
        start_month = int(start_mmdd[:2])
        start_day = int(start_mmdd[2:])
        week_num = (start_day - 1) // 7 + 1
        title = f"{year}年{start_month}月第{week_num}周运营商行业周报"
        return file_prefix, title, period
    else:
        return auto_detect_latest_report()


def build_html_content(report_title, report_period, report_file_prefix):
    """构建邮件HTML正文 —— 高清长图通过 CID 内嵌，点击跳转在线HTML"""

    html_url = f"{GITHUB_PAGES_BASE}/{report_file_prefix}.html"

    # 图片使用 cid:report_image 引用内嵌附件
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f0f2f5; font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f0f2f5;">
        <tr>
            <td align="center" style="padding: 20px 10px;">
                <table width="680" cellpadding="0" cellspacing="0" border="0" style="background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">

                    <!-- 顶部标题栏 -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px 30px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 20px; margin: 0; font-weight: 600;">
                                📡 {report_title}
                            </h1>
                            <p style="color: rgba(255,255,255,0.85); font-size: 13px; margin: 8px 0 0 0;">
                                {report_period} · 点击长图可查看在线HTML版本
                            </p>
                        </td>
                    </tr>

                    <!-- 高清长图主体（CID内嵌） -->
                    <tr>
                        <td style="padding: 0; text-align: center; font-size: 0; line-height: 0;">
                            <a href="{html_url}" target="_blank" style="display: block; text-decoration: none;">
                                <img src="cid:report_image"
                                     alt="{report_title}"
                                     width="680"
                                     style="display: block; width: 100%; height: auto; border: none;">
                            </a>
                        </td>
                    </tr>

                    <!-- 底部操作区 -->
                    <tr>
                        <td style="padding: 24px 30px; text-align: center; background: #fafbfc;">
                            <a href="{html_url}"
                               target="_blank"
                               style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 12px 32px; text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">
                                📄 查看在线HTML版周报
                            </a>
                            <p style="color: #94A3B8; font-size: 12px; margin: 16px 0 0 0;">
                                👆 点击上方按钮或长图均可查看完整在线版本
                            </p>
                        </td>
                    </tr>

                    <!-- 页脚 -->
                    <tr>
                        <td style="padding: 16px 30px; text-align: center; border-top: 1px solid #E2E8F0;">
                            <p style="color: #94A3B8; font-size: 11px; margin: 0;">
                                运营商行业资讯 · 数据来源：三大运营商公告、工信部、国资委、C114通信网、澎湃新闻、新华社、东方财富网
                            </p>
                            <p style="color: #94A3B8; font-size: 11px; margin: 6px 0 0 0;">
                                报告周期：2026.{report_period} · 仅供内部参考
                            </p>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def send_weekly_report(file_prefix=None):
    """发送运营商行业周报邮件
    
    Args:
        file_prefix: 可选，指定周报文件前缀（如 'weekly-report-0309-0315'）。
                     如不传则自动检测最新一期。
    """
    # 自动检测或使用指定参数
    report_file_prefix, report_title, report_period = auto_detect_or_manual(file_prefix)
    report_image_file = f"{report_file_prefix}-hd.png"

    print(f"📋 周报文件前缀: {report_file_prefix}")
    print(f"📝 邮件标题: {report_title}")
    print(f"📅 报告周期: {report_period}")

    # 定位图片文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, report_image_file)

    if not os.path.exists(image_path):
        print(f"❌ 找不到图片文件: {image_path}")
        return False

    image_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    print(f"📎 内嵌图片: {report_image_file} ({image_size_mb:.1f} MB)")

    # 构建 related 类型的邮件（支持 CID 内嵌图片）
    message = MIMEMultipart('related')
    message['From'] = SENDER_EMAIL
    message['To'] = ", ".join(RECIPIENTS)
    if CC_RECIPIENTS:
        message['Cc'] = ", ".join(CC_RECIPIENTS)
    message['Subject'] = Header(report_title, 'utf-8')

    # HTML 正文部分
    html_content = build_html_content(report_title, report_period, report_file_prefix)
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)

    # 内嵌图片附件（CID: report_image）
    with open(image_path, 'rb') as f:
        img_data = f.read()

    img_part = MIMEImage(img_data, _subtype='png')
    img_part.add_header('Content-ID', '<report_image>')
    img_part.add_header('Content-Disposition', 'inline', filename=report_image_file)
    message.attach(img_part)

    try:
        print("正在连接邮件服务器...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        all_recipients = RECIPIENTS + CC_RECIPIENTS
        print(f"正在发送邮件到: {', '.join(RECIPIENTS)}")
        if CC_RECIPIENTS:
            print(f"抄送: {', '.join(CC_RECIPIENTS)}")
        server.sendmail(SENDER_EMAIL, all_recipients, message.as_string())
        server.quit()

        print(f"✅ 邮件发送成功！共 {len(RECIPIENTS)} 位收件人，{len(CC_RECIPIENTS)} 位抄送")
        return True

    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 支持命令行参数指定文件前缀，否则自动检测
    file_prefix = sys.argv[1] if len(sys.argv) > 1 else None
    report_file_prefix, report_title, report_period = auto_detect_or_manual(file_prefix)

    print("=" * 50)
    print("运营商行业周报邮件发送")
    print(f"主题: {report_title}")
    print(f"周期: {report_period}")
    print(f"收件人: {len(RECIPIENTS)} 人")
    if CC_RECIPIENTS:
        print(f"抄送: {len(CC_RECIPIENTS)} 人")
    print("=" * 50)
    send_weekly_report(file_prefix)

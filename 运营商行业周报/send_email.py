#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营商行业周报邮件发送脚本
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

def send_weekly_report():
    """发送运营商行业周报邮件"""
    
    # 邮件配置（需要根据实际情况修改）
    smtp_server = "smtp.qq.com"  # QQ邮箱SMTP服务器
    smtp_port = 465  # SSL端口
    sender_email = "340191272@qq.com"  # 发件人邮箱
    sender_password = "pjbwfffghxmmbhge"  # QQ邮箱授权码（去除空格）
    
    # 收件人列表
    recipients = [
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
        "nikizzhang@tencent.com"
    ]
    
    # 邮件主题
    subject = "2026年2月第5周运营商行业周报"
    
    # HTML邮件正文
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .email-container {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .header {
            border-bottom: 3px solid #6366F1;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            color: #1E293B;
            font-size: 24px;
            margin: 0 0 10px 0;
        }
        .subtitle {
            color: #64748B;
            font-size: 14px;
            margin: 0;
        }
        .image-container {
            text-align: center;
            margin: 30px 0;
        }
        .report-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .link-button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 20px;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #E2E8F0;
            text-align: center;
            color: #94A3B8;
            font-size: 12px;
        }
        .highlight {
            background: #F0F9FF;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #0EA5E9;
        }
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📡 2026年2月第5周运营商行业周报</h1>
            <p class="subtitle">02.23 - 02.28 | 聚焦2月运营数据、MWC 2026前瞻、工信部算力节点布局与人事调整余波</p>
        </div>

        <div class="highlight">
            <strong>本周要点：</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
                <li>5G套餐用户达13.9亿，净增2730万</li>
                <li>中国移动占比57.6%，电信渗透率79.1%</li>
                <li>何腾→国家广电总局副局长（已就任）</li>
                <li>MWC 2026前瞻：5G-A全量商用冲刺</li>
            </ul>
        </div>

        <div class="image-container">
            <a href="https://azuretanfang.github.io/weekly-report/weekly-report-0223-0228.html" target="_blank">
                <img src="https://azuretanfang.github.io/weekly-report/weekly-report-0223-0228-9x16.png" 
                     alt="运营商行业周报" 
                     class="report-image">
            </a>
            <p style="color: #64748B; font-size: 13px; margin-top: 10px;">
                👆 点击图片查看在线HTML版本
            </p>
        </div>

        <div style="text-align: center;">
            <a href="https://azuretanfang.github.io/weekly-report/weekly-report-0223-0228.html" 
               class="link-button" 
               target="_blank">
                📄 查看完整HTML版周报
            </a>
        </div>

        <div class="footer">
            <p>运营商行业咨询 · 数据来源：工信部、国资委、通信产业报等公开资料</p>
            <p style="margin-top: 8px;">报告周期：2026.02.23 - 2026.02.28 · 仅供参考</p>
        </div>
    </div>
</body>
</html>
    """
    
    # 创建邮件对象
    message = MIMEMultipart('alternative')
    message['From'] = sender_email  # QQ邮箱要求使用标准格式
    message['To'] = ", ".join(recipients)
    message['Subject'] = Header(subject, 'utf-8')
    
    # 添加HTML内容
    html_part = MIMEText(html_content, 'html', 'utf-8')
    message.attach(html_part)
    
    try:
        # 连接SMTP服务器 - 使用SSL方式（QQ邮箱）
        print("正在连接邮件服务器...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)
        
        # 发送邮件
        print(f"正在发送邮件到: {', '.join(recipients)}")
        server.sendmail(sender_email, recipients, message.as_string())
        server.quit()
        
        print("✅ 邮件发送成功！")
        return True
        
    except Exception as e:
        print(f"❌ 邮件发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("运营商行业周报邮件发送")
    print("=" * 50)
    send_weekly_report()

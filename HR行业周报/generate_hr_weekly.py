#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HR行业资讯周报 - 内容自动生成脚本
功能：AI搜索互联网/游戏行业HR领域资讯 → 结构化分类 → 生成HTML周报

使用方式：
  python generate_hr_weekly.py                    # 自动生成本周周报
  python generate_hr_weekly.py --start 0401 --end 0406  # 指定日期范围
  python generate_hr_weekly.py --dry-run           # 仅搜索不生成文件
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from string import Template

# ==================== 配置区域 ====================

# 搜索关键词库 —— 按模块分组
SEARCH_KEYWORDS = {
    "政策法规": [
        "劳动法 修订 2026",
        "社保 缴费基数 调整 2026",
        "公积金 新政策",
        "互联网 劳动争议",
        "竞业限制 互联网",
        "灵活用工 政策 新规",
        "个税 专项扣除 调整",
        "工伤认定 互联网 加班",
        "产假 育儿假 新规",
        "人社部 HR 新规",
    ],
    "薪酬与人才市场": [
        "互联网 薪酬报告 2026",
        "游戏行业 招聘 趋势",
        "AI人才 薪资 涨幅",
        "互联网 裁员 2026",
        "游戏行业 人才 流动",
        "应届生 互联网 就业",
        "大厂 校招 春招",
        "互联网 离职率 Q1",
        "技术人才 供需 报告",
        "游戏 美术 策划 招聘",
    ],
    "行业标杆实践": [
        "互联网 HR 创新实践",
        "AI面试 互联网 游戏",
        "OKR 绩效管理 互联网",
        "员工关怀 大厂 福利",
        "腾讯 网易 字节 HR",
        "游戏行业 团队管理",
        "HRSSC 共享服务中心",
        "雇主品牌 互联网",
        "远程办公 混合办公 政策",
        "员工心理健康 互联网",
    ],
    "AI+HR趋势": [
        "AI HR 人力资源 技术",
        "AI面试官 招聘 自动化",
        "AI 离职预测 人才保留",
        "HR SaaS 新工具 2026",
        "智能招聘 ATS 系统",
        "AI 培训 学习 个性化",
        "AI 绩效管理 自动化",
        "HR Agent 智能体",
        "人才画像 AI 数据驱动",
        "AI 组织诊断 效能分析",
    ],
    "热点事件": [
        "互联网 劳动争议 热搜",
        "大厂 裁员 优化 舆情",
        "游戏行业 加班 996",
        "互联网 年龄歧视 35岁",
        "企业文化 丑闻 互联网",
        "互联网 员工权益 事件",
        "游戏公司 工作环境",
        "互联网 HR 舆情 本周",
    ],
}

# "与我们相关"的判定关键词 —— 命中任一则标记
RELEVANCE_KEYWORDS = [
    "腾讯", "游戏", "互联网大厂", "社保基数", "劳动法", "加班",
    "竞业限制", "深圳", "员工关怀", "心理健康", "校招", "秋招",
    "春招", "AI面试", "离职预测", "绩效管理", "OKR", "远程办公",
]

# HTML模板路径
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== 配置区域结束 ====================


def get_week_range():
    """自动计算上周一到周日的日期范围"""
    today = datetime.now()
    # 找到上周一
    last_monday = today - timedelta(days=today.weekday() + 7)
    last_sunday = last_monday + timedelta(days=6)
    
    start_str = last_monday.strftime("%m%d")
    end_str = last_sunday.strftime("%m%d")
    start_display = last_monday.strftime("%m.%d")
    end_display = last_sunday.strftime("%m.%d")
    
    return start_str, end_str, f"{start_display} - {end_display}"


def check_relevance(title, summary):
    """判断资讯是否与我们相关"""
    text = f"{title} {summary}"
    for kw in RELEVANCE_KEYWORDS:
        if kw in text:
            return True
    return False


def generate_news_item_html(item, show_relevance=True):
    """生成单条资讯的HTML片段"""
    tag_color_map = {
        "政策法规": ("red", "⚠️ 重点"),
        "薪酬与人才市场": ("blue", "📊 数据"),
        "行业标杆实践": ("green", "🏆 实践"),
        "AI+HR趋势": ("violet", "🤖 AI"),
        "热点事件": ("amber", "🔥 热点"),
    }
    
    category = item.get("category", "")
    color, tag_text = tag_color_map.get(category, ("gray", "📌 资讯"))
    
    is_relevant = check_relevance(item.get("title", ""), item.get("summary", ""))
    
    relevance_tag = ""
    if is_relevant and show_relevance:
        relevance_tag = '<span class="tag-us text-white text-xs font-bold px-2 py-0.5 rounded-full">🏢 与我们相关</span>'
    
    relevance_block = ""
    if is_relevant and item.get("impact"):
        relevance_block = f"""
          <div class="mt-3 bg-orange-50 border border-orange-200 rounded-xl p-3">
            <div class="text-xs font-bold text-[#E8590C] mb-1">💡 对我们的影响</div>
            <div class="text-xs text-[#64748B] leading-relaxed">{item['impact']}</div>
          </div>"""
    
    return f"""
        <div class="bg-white p-5 rounded-2xl border border-slate-200">
          <div class="flex items-center gap-2 mb-2">
            <span class="bg-{color}-100 text-{color}-700 text-xs font-bold px-2 py-0.5 rounded-full">{tag_text}</span>
            {relevance_tag}
            <span class="text-sm font-bold text-[#1E293B]">{item['title']}</span>
          </div>
          <div class="text-xs text-[#64748B] leading-relaxed">
            {item['summary']}
          </div>{relevance_block}
        </div>"""


def build_html_report(news_data, period_display, date_range_start, date_range_end):
    """根据结构化数据构建完整的HTML周报"""
    
    # 分类整理
    categories = {
        "政策法规": [],
        "薪酬与人才市场": [],
        "行业标杆实践": [],
        "AI+HR趋势": [],
        "热点事件": [],
    }
    
    for item in news_data:
        cat = item.get("category", "")
        if cat in categories:
            categories[cat].append(item)
    
    # 生成各模块HTML
    sections_html = ""
    
    section_config = [
        ("政策法规", "from-red-500 to-rose-600", "⚖️", "red", "关注合规风险"),
        ("薪酬与人才市场", "from-blue-500 to-cyan-600", "💼", "blue", "市场动态追踪"),
        ("行业标杆实践", "from-emerald-500 to-green-600", "🏆", "emerald", "学习借鉴"),
        ("AI+HR趋势", "from-violet-500 to-purple-600", "🤖", "violet", "技术前沿"),
        ("热点事件", "from-amber-500 to-orange-600", "🔥", "amber", "舆情监控"),
    ]
    
    for cat_name, gradient, icon, color, subtitle in section_config:
        items = categories.get(cat_name, [])
        if not items:
            continue
        
        items_html = "\n".join([generate_news_item_html(item) for item in items])
        
        sections_html += f"""
    <div class="mb-10">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-2xl font-bold text-[#1E293B] flex items-center">
          <span class="bg-gradient-to-r {gradient} text-white w-8 h-8 rounded-lg flex items-center justify-center mr-2 text-sm">{icon}</span>
          {cat_name}
        </h2>
        <span class="bg-{color}-50 text-{color}-600 text-xs font-medium px-3 py-1 rounded-full">{subtitle}</span>
      </div>
      <div class="space-y-4">
        {items_html}
      </div>
    </div>
"""
    
    # 组装完整HTML
    today_str = datetime.now().strftime("%Y年%m月%d日")
    
    # 提取本期看点（取前4条标题）
    highlights = [item["title"][:20] for item in news_data[:4]]
    highlights_str = " | ".join(highlights)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HR行业资讯周报 {period_display}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    body {{ font-family: 'Inter', 'PingFang SC', sans-serif; }}
    .tag-us {{ 
      background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
      animation: pulse-soft 2s ease-in-out infinite;
    }}
    @keyframes pulse-soft {{
      0%, 100% {{ box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.3); }}
      50% {{ box-shadow: 0 0 0 4px rgba(255, 107, 53, 0.1); }}
    }}
  </style>
</head>
<body class="bg-slate-50">
  <div class="w-[800px] bg-[#FFFBF7] p-10 font-sans shadow-2xl mx-auto my-8">
    <!-- Header -->
    <div class="mb-10">
      <span class="bg-[#FFF0E6] text-[#E8590C] text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
        HR Weekly Report
      </span>
      <h1 class="text-4xl font-extrabold text-[#1E293B] mt-4 mb-2">
        HR行业资讯周报 <span class="text-[#E8590C]">{period_display}</span>
      </h1>
      <p class="text-[#64748B] text-sm">聚焦互联网与游戏行业 · HRBP 内部参阅</p>
      <p class="text-[#94A3B8] text-xs mt-1">本期看点：{highlights_str}</p>
    </div>

    {sections_html}

    <!-- Footer -->
    <div class="mt-8 pt-6 border-t border-slate-200 text-center text-xs text-[#94A3B8]">
      <p>数据来源：人社部、猎聘、脉脉、Gartner、领英、HR Tech China、各公司官方公告</p>
      <p class="mt-1">聚焦：互联网与游戏行业 · 仅供 HRBP 团队内部参阅</p>
      <p class="mt-1">制作日期：{today_str}</p>
    </div>
  </div>
</body>
</html>"""
    
    return html


def save_report(html_content, date_range_start, date_range_end):
    """保存周报HTML文件"""
    filename = f"hr-weekly-report-{date_range_start}-{date_range_end}.html"
    filepath = os.path.join(TEMPLATE_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 周报已生成: {filepath}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="HR行业资讯周报生成器")
    parser.add_argument("--start", help="起始日期 MMDD，如 0401")
    parser.add_argument("--end", help="结束日期 MMDD，如 0406")
    parser.add_argument("--dry-run", action="store_true", help="仅输出搜索关键词，不生成文件")
    parser.add_argument("--data", help="JSON数据文件路径（跳过搜索，直接从文件生成）")
    args = parser.parse_args()
    
    # 确定日期范围
    if args.start and args.end:
        start = args.start
        end = args.end
        start_display = f"{start[:2]}.{start[2:]}"
        end_display = f"{end[:2]}.{end[2:]}"
        period = f"{start_display} - {end_display}"
    else:
        start, end, period = get_week_range()
    
    print("=" * 60)
    print(f"📋 HR行业资讯周报生成器")
    print(f"📅 周期: {period}")
    print(f"🎯 聚焦: 互联网 & 游戏行业")
    print("=" * 60)
    
    if args.dry_run:
        print("\n🔍 搜索关键词库:")
        for category, keywords in SEARCH_KEYWORDS.items():
            print(f"\n  [{category}]")
            for kw in keywords:
                print(f"    - {kw}")
        print(f"\n总计 {sum(len(v) for v in SEARCH_KEYWORDS.values())} 个关键词组合")
        return
    
    if args.data:
        # 从JSON文件加载数据
        with open(args.data, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        print(f"\n📂 从文件加载了 {len(news_data)} 条资讯")
    else:
        print("\n💡 提示: 当前版本需手动准备数据文件（JSON格式），或使用 AI 对话生成内容")
        print("   使用方式: python generate_hr_weekly.py --data news_data.json")
        print("\n📝 JSON数据格式示例:")
        sample = [
            {
                "category": "政策法规",
                "title": "《劳动合同法》修订草案二审",
                "summary": "详细摘要内容...",
                "impact": "对我们的影响分析...",
                "source": "人社部",
            }
        ]
        print(json.dumps(sample, ensure_ascii=False, indent=2))
        return
    
    # 生成HTML
    html = build_html_report(news_data, period, start, end)
    filepath = save_report(html, start, end)
    
    print(f"\n🎉 完成! 可以用浏览器打开查看: {filepath}")


if __name__ == "__main__":
    main()

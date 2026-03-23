#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营商行业周报一键发布脚本
串联完整流程：截图 → 更新归档 → 推送 GitHub → 邮件群发

用法:
    python3 publish.py                    # 自动检测最新周报
    python3 publish.py 0309-0315          # 指定日期范围
    python3 publish.py --skip-screenshot  # 跳过截图（已有 -hd.png 时）
    python3 publish.py --skip-email       # 跳过邮件发送
    python3 publish.py --skip-git         # 跳过 git 推送
"""

import os
import sys
import glob
import subprocess
import argparse
from datetime import datetime


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def find_latest_report():
    """自动检测最新一期周报文件前缀"""
    pattern = os.path.join(SCRIPT_DIR, "weekly-report-????-????.html")
    html_files = sorted(glob.glob(pattern))
    if not html_files:
        print("❌ 未找到任何周报 HTML 文件")
        sys.exit(1)
    latest = os.path.basename(html_files[-1])
    return latest.replace(".html", "")


def parse_prefix(prefix):
    """从文件前缀解析日期信息"""
    parts = prefix.split("-")
    start_mmdd = parts[2]  # 0309
    end_mmdd = parts[3]    # 0315
    start_display = f"{start_mmdd[:2]}.{start_mmdd[2:]}"
    end_display = f"{end_mmdd[:2]}.{end_mmdd[2:]}"
    period = f"{start_display} - {end_display}"

    year = datetime.now().year
    start_month = int(start_mmdd[:2])
    start_day = int(start_mmdd[2:])
    week_num = (start_day - 1) // 7 + 1
    title = f"{year}年{start_month}月第{week_num}周运营商行业周报"
    return title, period


def step_screenshot(prefix):
    """步骤1: 自动截图 + 裁剪"""
    hd_png = os.path.join(SCRIPT_DIR, f"{prefix}-hd.png")

    print("\n" + "=" * 50)
    print("📸 步骤1: 高清截图 + 裁剪")
    print("=" * 50)

    from auto_screenshot import screenshot_report
    screenshot_report(prefix)

    if not os.path.exists(hd_png):
        print("❌ 截图失败，-hd.png 文件未生成")
        return False

    print("✅ 截图完成")
    return True


def step_update_index(prefix):
    """步骤2: 更新 index.html 归档列表"""
    print("\n" + "=" * 50)
    print("📝 步骤2: 更新 index.html 归档列表")
    print("=" * 50)

    index_path = os.path.join(SCRIPT_DIR, "index.html")
    if not os.path.exists(index_path):
        print("⚠️ index.html 不存在，跳过更新")
        return True

    title, period = parse_prefix(prefix)

    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否已经包含此期周报
    if f"{prefix}.html" in content:
        print(f"ℹ️ index.html 已包含 {prefix}，无需更新")
        return True

    # 构建新的卡片 HTML
    parts = prefix.split("-")
    start_mmdd = parts[2]
    end_mmdd = parts[3]
    year = datetime.now().year

    new_card = f'''      <a href="{prefix}.html" class="report-card">
        <span class="report-badge">Latest</span>
        <div class="report-title">{year}年 ({start_mmdd[:2]}.{start_mmdd[2:]} - {end_mmdd[:2]}.{end_mmdd[2:]})</div>
        <div class="report-desc">
          {title} - 查看最新一期周报
        </div>
        <div class="report-meta">
          <span>📅 {year}年{int(start_mmdd[:2])}月</span>
          <span>🏷️ 运营商行业周报</span>
        </div>
      </a>'''

    # 去掉之前的 Latest 标签
    content = content.replace('<span class="report-badge">Latest</span>\n        ', '')

    # 在 report-list div 后插入新卡片
    insert_marker = '<div class="report-list">'
    if insert_marker in content:
        content = content.replace(
            insert_marker,
            f"{insert_marker}\n{new_card}\n"
        )

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ index.html 已更新，新增 {prefix}")
    else:
        print("⚠️ 未找到插入位置，跳过 index.html 更新")

    return True


def step_git_push(prefix):
    """步骤3: 推送到 GitHub"""
    print("\n" + "=" * 50)
    print("🚀 步骤3: 推送到 GitHub")
    print("=" * 50)

    title, period = parse_prefix(prefix)

    try:
        # git add
        subprocess.run(
            ["git", "add", "-A"],
            cwd=SCRIPT_DIR, check=True, capture_output=True, text=True
        )
        print("   ✅ git add 完成")

        # 检查是否有变更
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SCRIPT_DIR, capture_output=True, text=True
        )
        if not result.stdout.strip():
            print("   ℹ️ 没有变更需要提交")
            return True

        # git commit
        commit_msg = f"📡 {title} ({period})"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=SCRIPT_DIR, check=True, capture_output=True, text=True
        )
        print(f"   ✅ git commit: {commit_msg}")

        # git push
        subprocess.run(
            ["git", "push"],
            cwd=SCRIPT_DIR, check=True, capture_output=True, text=True,
            timeout=60
        )
        print("   ✅ git push 完成")
        print("   ⏳ GitHub Actions 将自动部署到 Pages...")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Git push 超时")
        return False


def step_send_email(prefix):
    """步骤4: 邮件群发"""
    print("\n" + "=" * 50)
    print("📧 步骤4: 邮件群发")
    print("=" * 50)

    from send_email import send_weekly_report
    return send_weekly_report(prefix)


def main():
    parser = argparse.ArgumentParser(description="运营商行业周报一键发布")
    parser.add_argument("date_range", nargs="?", default=None,
                        help="日期范围，如 '0309-0315'。不传则自动检测最新")
    parser.add_argument("--skip-screenshot", action="store_true",
                        help="跳过截图步骤（已有 -hd.png 时使用）")
    parser.add_argument("--skip-email", action="store_true",
                        help="跳过邮件发送")
    parser.add_argument("--skip-git", action="store_true",
                        help="跳过 git 推送")
    parser.add_argument("--skip-index", action="store_true",
                        help="跳过更新 index.html")

    args = parser.parse_args()

    # 确定文件前缀
    if args.date_range:
        prefix = f"weekly-report-{args.date_range}"
    else:
        prefix = find_latest_report()

    title, period = parse_prefix(prefix)

    print("🚀 运营商行业周报一键发布")
    print("=" * 50)
    print(f"📋 文件前缀: {prefix}")
    print(f"📝 标题: {title}")
    print(f"📅 周期: {period}")
    print(f"📸 截图: {'跳过' if args.skip_screenshot else '执行'}")
    print(f"📝 归档: {'跳过' if args.skip_index else '执行'}")
    print(f"🚀 推送: {'跳过' if args.skip_git else '执行'}")
    print(f"📧 邮件: {'跳过' if args.skip_email else '执行'}")

    results = {}

    # 步骤1: 截图
    if not args.skip_screenshot:
        results["截图"] = step_screenshot(prefix)
        if not results["截图"]:
            print("\n❌ 截图失败，流程中止")
            sys.exit(1)
    else:
        # 检查 -hd.png 是否已存在
        hd_png = os.path.join(SCRIPT_DIR, f"{prefix}-hd.png")
        if not os.path.exists(hd_png):
            print(f"\n❌ 跳过截图但 {prefix}-hd.png 不存在！请先截图")
            sys.exit(1)
        print("\n⏭️ 跳过截图（已有 -hd.png）")

    # 步骤2: 更新 index.html
    if not args.skip_index:
        results["归档"] = step_update_index(prefix)

    # 步骤3: 推送 GitHub
    if not args.skip_git:
        results["推送"] = step_git_push(prefix)
    else:
        print("\n⏭️ 跳过 git 推送")

    # 步骤4: 邮件群发
    if not args.skip_email:
        results["邮件"] = step_send_email(prefix)
    else:
        print("\n⏭️ 跳过邮件发送")

    # 汇总报告
    print("\n" + "=" * 50)
    print("📊 发布结果汇总")
    print("=" * 50)
    for step_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"   {step_name}: {status}")

    all_success = all(results.values())
    if all_success:
        print(f"\n🎉 {title} 发布完成！")
    else:
        print(f"\n⚠️ 部分步骤失败，请检查日志")
        sys.exit(1)


if __name__ == "__main__":
    main()

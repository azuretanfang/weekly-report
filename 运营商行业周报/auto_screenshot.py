#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运营商行业周报自动截图脚本
- 使用 Playwright 高清截图
- 自动裁剪底部空白
- 输出 -hd.png 文件
"""

import os
import sys
import glob
import subprocess


def find_latest_report():
    """查找最新的周报 HTML 文件，返回文件前缀"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(script_dir, "weekly-report-????-????.html")
    html_files = sorted(glob.glob(pattern))

    if not html_files:
        print("❌ 未找到任何周报 HTML 文件")
        sys.exit(1)

    latest = os.path.basename(html_files[-1])
    prefix = latest.replace(".html", "")
    return prefix


def screenshot_report(file_prefix=None):
    """对周报 HTML 进行高清截图并裁剪
    
    Args:
        file_prefix: 可选，指定周报文件前缀。如不传则自动检测最新一期。
    
    Returns:
        str: 最终高清长图的文件路径
    """
    if not file_prefix:
        file_prefix = find_latest_report()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, f"{file_prefix}.html")
    raw_png_path = os.path.join(script_dir, f"{file_prefix}-raw.png")
    hd_png_path = os.path.join(script_dir, f"{file_prefix}-hd.png")

    if not os.path.exists(html_path):
        print(f"❌ 找不到 HTML 文件: {html_path}")
        sys.exit(1)

    print(f"📸 开始截图: {file_prefix}.html")
    print(f"   HTML 路径: {html_path}")

    # Step 1: 使用 Playwright 截图
    file_url = f"file://{html_path}"

    playwright_script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
    const browser = await chromium.launch();
    const page = await browser.newPage({{
        viewport: {{ width: 800, height: 600 }},
        deviceScaleFactor: 2
    }});
    await page.goto('{file_url}', {{ waitUntil: 'networkidle' }});
    // 等待渲染完成
    await page.waitForTimeout(2000);
    await page.screenshot({{
        path: '{raw_png_path}',
        fullPage: true
    }});
    await browser.close();
    console.log('截图完成');
}})();
"""

    # 写入临时 JS 文件
    temp_js = os.path.join(script_dir, "_temp_screenshot.js")
    with open(temp_js, "w") as f:
        f.write(playwright_script)

    try:
        print("   正在启动 Playwright 截图...")
        result = subprocess.run(
            ["node", temp_js],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            print(f"❌ Playwright 截图失败: {result.stderr}")
            sys.exit(1)
        print("   ✅ 原始截图完成")
    finally:
        # 清理临时文件
        if os.path.exists(temp_js):
            os.remove(temp_js)

    # Step 2: 裁剪空白
    print("   正在裁剪底部空白...")
    from crop_image import crop_image_intelligent
    crop_image_intelligent(raw_png_path, hd_png_path)

    # 清理原始截图
    if os.path.exists(raw_png_path):
        os.remove(raw_png_path)

    # 显示结果
    file_size_mb = os.path.getsize(hd_png_path) / (1024 * 1024)
    print(f"   ✅ 高清长图已生成: {file_prefix}-hd.png ({file_size_mb:.1f} MB)")

    return hd_png_path


if __name__ == "__main__":
    file_prefix = sys.argv[1] if len(sys.argv) > 1 else None
    screenshot_report(file_prefix)

#!/usr/bin/env python3
"""
HR行业周报 HTML 转高清长图脚本
基于 Playwright 无头浏览器截图，2倍 DPI 输出
"""
import os
import sys
import glob
from pathlib import Path
from playwright.sync_api import sync_playwright

def screenshot_html(html_path: str, output_path: str):
    """
    使用 Playwright 截取 HTML 的全页面高清截图
    
    Args:
        html_path: HTML 文件路径
        output_path: 输出图片路径
    """
    with sync_playwright() as p:
        # 启动 Chromium
        browser = p.chromium.launch(headless=True)
        
        # 创建页面上下文，设置视口和 DPI
        context = browser.new_context(
            viewport={'width': 800, 'height': 600},  # 宽度与 HTML 的 w-[800px] 一致
            device_scale_factor=2  # 2倍 DPI，输出 1600px 宽的高清图
        )
        
        page = context.new_page()
        
        # 加载本地 HTML 文件
        html_full_path = Path(html_path).resolve().as_uri()
        print(f"📄 正在加载: {html_full_path}")
        
        # 等待 Tailwind CDN 加载完成（networkidle + 额外等待）
        page.goto(html_full_path, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(3000)  # 额外等待 3 秒确保样式渲染完成
        
        print(f"📸 正在截图...")
        
        # 全页面截图
        page.screenshot(
            path=output_path,
            full_page=True,
            type='png'
        )
        
        browser.close()
        
        # 获取文件大小
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ 截图完成: {output_path}")
        print(f"📊 文件大小: {file_size_mb:.2f} MB")

def main():
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    # 查找最新的 HR 周报 HTML
    html_files = list(current_dir.glob('hr-weekly-report-*.html'))
    
    if not html_files:
        print("❌ 未找到 hr-weekly-report-*.html 文件")
        sys.exit(1)
    
    # 按修改时间排序，取最新的
    latest_html = max(html_files, key=lambda p: p.stat().st_mtime)
    
    print(f"🎯 找到最新报告: {latest_html.name}")
    
    # 生成输出文件名
    base_name = latest_html.stem  # 不含扩展名的文件名
    raw_output = current_dir / f"{base_name}-raw.png"
    
    # 截图
    screenshot_html(str(latest_html), str(raw_output))
    
    print(f"\n🎉 下一步：运行 crop_image.py 裁剪空白边距")
    print(f"   python3 crop_image.py")

if __name__ == '__main__':
    main()

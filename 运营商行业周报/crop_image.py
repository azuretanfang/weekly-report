#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能图片裁剪脚本 - 自动去除底部多余空白
"""

from PIL import Image
import sys

def crop_image_intelligent(img_path, output_path):
    """智能裁剪图片，去除底部空白"""
    print(f"正在处理图片: {img_path}")
    
    # 打开图片
    img = Image.open(img_path)
    width, height = img.size
    print(f"原始尺寸: {width}x{height}")
    
    # 获取像素数据
    pixels = img.load()
    
    def is_background_color(pixel):
        """判断是否为背景色（白色、浅灰色、slate-50等浅色背景）"""
        if isinstance(pixel, int):  # 灰度图
            return pixel > 235
        if len(pixel) >= 3:
            r, g, b = pixel[:3]
            # 判断是否为接近白色或浅色的背景
            # 覆盖 bg-slate-50(#F8FAFC)、bg-white(#FFF)、#F8FAFF、#f0f2f5 等
            return r > 235 and g > 235 and b > 235
        return False
    
    # 从底部向上扫描，找到最后一行有内容的位置
    last_content_row = height - 1
    print("正在扫描图片内容...")
    
    for y in range(height - 1, -1, -1):
        has_content = False
        # 每隔10个像素采样一次（提高速度）
        for x in range(0, width, 10):
            try:
                pixel = pixels[x, y]
                if not is_background_color(pixel):
                    has_content = True
                    break
            except:
                continue
        
        if has_content:
            last_content_row = y
            print(f"找到最后内容行: {last_content_row}")
            break
    
    # 添加一些边距（100像素），并确保不超过原始高度
    crop_height = min(last_content_row + 100, height)
    print(f"裁剪高度: {crop_height}")
    
    # 裁剪图片
    cropped_img = img.crop((0, 0, width, crop_height))
    
    # 保存裁剪后的图片
    cropped_img.save(output_path, 'PNG', optimize=True)
    
    # 获取文件大小
    import os
    file_size = os.path.getsize(output_path) / 1024  # KB
    
    print(f"✅ 裁剪完成!")
    print(f"最终尺寸: {width}x{crop_height}")
    print(f"文件大小: {file_size:.1f} KB")
    print(f"输出路径: {output_path}")
    
    return width, crop_height

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python3 crop_image.py <输入图片> <输出图片>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        crop_image_intelligent(input_path, output_path)
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        sys.exit(1)

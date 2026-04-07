from PIL import Image, ImageDraw, ImageFont
import textwrap

# 创建长图画布 (宽800px, 高度根据内容动态计算)
width = 800
height = 5500  # 预估高度
img = Image.new('RGB', (width, height), color='#f0f2f5')
draw = ImageDraw.Draw(img)

# 使用系统默认字体
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
    font_subtitle = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
    font_normal = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 18)
    font_small = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 15)
except:
    font_title = ImageFont.load_default()
    font_subtitle = ImageFont.load_default()
    font_normal = ImageFont.load_default()
    font_small = ImageFont.load_default()

y_offset = 0

# 顶部渐变头部区域
header_height = 150
for i in range(header_height):
    color_val = int(102 + (118-102) * i / header_height)
    draw.rectangle([(0, i), (width, i+1)], fill=f'#{color_val:02x}7eea')
draw.text((40, 40), "📊 3月项管侧月报 - 产品组视角", font=font_title, fill='white')
draw.text((40, 85), "运营商合作部·技术研发中心 | 2026年3月", font=font_small, fill='white')
draw.text((40, 115), "报告日期：2026-03-25 · 数据来源：TAPD工时系统", font=font_small, fill='white')
y_offset = header_height + 30

# Executive Summary 绿色背景区域
summary_box_top = y_offset
draw.rectangle([(30, y_offset), (width-30, y_offset+280)], fill='#e8f5e9', outline='#81c784', width=2)
draw.text((50, y_offset+20), "📋 Executive Summary", font=font_subtitle, fill='#2e7d32')
y_offset += 55

summary_texts = [
    "🎯 月度核心成果：研发团队3月总投入 206.0人天，产品中心",
    "需求占比 37.6%（77.3天），接近约定的45%目标；成功推动",
    "IC平台V5.0智能投放 从规划到方案设计完成。",
    "",
    "💡 项管核心价值：①需求排期系统正式上线运行；②推动 AI",
    "战略投入从13.3%跃升至31.5%；③研发资源分配基本符合约定。",
    "",
    "⚠️ 风险提示：产品中心占比波动较大（40.1%→42.5%→29.9%），",
    "下月需加强需求提前规划。"
]

for text in summary_texts:
    draw.text((50, y_offset), text, font=font_small, fill='#1b5e20')
    y_offset += 25

y_offset += 20

# 第一部分：月度数据全景
draw.rectangle([(30, y_offset), (width-30, y_offset+50)], fill='#667eea')
draw.text((50, y_offset+12), "📈 一、月度数据全景", font=font_subtitle, fill='white')
y_offset += 70

# 核心指标卡片
cards = [
    ("产品中心月度总投入", "77.3天", "占全部206.0天的37.6%", "#667eea"),
    ("月度涉及需求数", "60+个", "多条产品线并行", "#00a870"),
    ("AI相关投入", "31.5%", "第三周AI投入占比", "#7b61ff"),
    ("TOP需求工时峰值", "5.7天", "IC V5.0智能投放", "#ed7b2f")
]

card_width = 170
card_height = 110
x_start = 40
for i, (label, value, sub, color) in enumerate(cards):
    x = x_start + (i % 2) * (card_width + 20)
    y = y_offset + (i // 2) * (card_height + 15)
    draw.rectangle([(x, y), (x+card_width, y+card_height)], fill='white', outline='#e8ecf1', width=1)
    draw.text((x+15, y+15), label, font=font_small, fill='#718096')
    draw.text((x+15, y+45), value, font=font_subtitle, fill=color)
    draw.text((x+15, y+78), sub, font=font_small, fill='#a0aec0')

y_offset += 260

# 三周资源分配对比
draw.text((40, y_offset), "📊 产品中心需求三周资源分配对比", font=font_normal, fill='#4a5568')
y_offset += 40

weeks_data = [
    ("第一周(3.2-3.6)", 40.1, "27.7天", "#667eea"),
    ("第二周(3.9-3.13)", 42.5, "29.3天", "#667eea"),
    ("第三周(3.16-3.20)", 29.9, "20.3天 ⚠️", "#ed7b2f"),
    ("月度平均", 37.6, "77.3天", "#00a870")
]

for label, percent, value, color in weeks_data:
    draw.text((50, y_offset), label, font=font_small, fill='#4a5568')
    bar_width = int((width-220) * percent / 100)
    draw.rectangle([(180, y_offset-2), (width-60, y_offset+20)], fill='#f7fafc')
    draw.rectangle([(180, y_offset-2), (180+bar_width, y_offset+20)], fill=color)
    draw.text((185, y_offset+2), f"{percent}%", font=font_small, fill='white')
    draw.text((width-50, y_offset+2), value, font=font_small, fill='#2d3748', anchor='ra')
    y_offset += 35

y_offset += 20

# TOP10需求表格
draw.text((40, y_offset), "🔥 产品中心月度高工时需求 TOP5", font=font_normal, fill='#4a5568')
y_offset += 35

top_demands = [
    ("IC V5.0 AI智能投放", "5.7天", "方案完成"),
    ("IC V4.6 空白对照组", "5.0天", "✅已发布"),
    ("运营AI活动配置-一期", "4.7天", "✅已交付"),
    ("IC批量录入+审批", "4.8天", "测试中"),
    ("IC营销接口扣费", "5.2天", "开发中")
]

draw.rectangle([(35, y_offset), (width-35, y_offset+30)], fill='#f7fafc')
draw.text((50, y_offset+8), "需求名称", font=font_small, fill='#4a5568')
draw.text((width-180, y_offset+8), "工时", font=font_small, fill='#4a5568')
draw.text((width-100, y_offset+8), "状态", font=font_small, fill='#4a5568')
y_offset += 35

for name, worktime, status in top_demands:
    draw.rectangle([(35, y_offset), (width-35, y_offset+35)], fill='white', outline='#f0f0f0')
    draw.text((50, y_offset+10), name, font=font_small, fill='#2d3748')
    draw.text((width-180, y_offset+10), worktime, font=font_small, fill='#2d3748')
    draw.text((width-100, y_offset+10), status, font=font_small, fill='#0052d9')
    y_offset += 36

y_offset += 30

# 第二部分：项管工具价值
draw.rectangle([(30, y_offset), (width-30, y_offset+50)], fill='#00a870')
draw.text((50, y_offset+12), "🛠️ 二、项管工具价值体现", font=font_subtitle, fill='white')
y_offset += 70

tool_values = [
    "📦 需求池管理 - 统一收口所有需求，状态流转自动同步TAPD",
    "📅 排期表管理 - 可视化展示月度/周度排期",
    "✅ Action追踪 - 会议Action项闭环管理",
    "📊 月度变更日志 - 自动记录需求排期变更历史"
]

for text in tool_values:
    draw.rectangle([(40, y_offset), (width-40, y_offset+60)], fill='#f8fafe', outline='#e8ecf1')
    wrapped = textwrap.wrap(text, width=45)
    temp_y = y_offset + 15
    for line in wrapped:
        draw.text((55, temp_y), line, font=font_small, fill='#2d3748')
        temp_y += 22
    y_offset += 68

y_offset += 30

# 第三部分：AI战略推进
draw.rectangle([(30, y_offset), (width-30, y_offset+50)], fill='#7b61ff')
draw.text((50, y_offset+12), "🤖 三、AI战略推进", font=font_subtitle, fill='white')
y_offset += 70

draw.text((40, y_offset), "📈 产品中心AI投入趋势（爆发式增长！）", font=font_normal, fill='#4a5568')
y_offset += 35

ai_weeks = [
    ("第一周", 13.3, "9.2天"),
    ("第二周", 13.3, "9.2天"),
    ("第三周🔥", 31.5, "21.4天 (+18.2pp)")
]

for label, percent, value in ai_weeks:
    draw.text((50, y_offset), label, font=font_small, fill='#4a5568')
    bar_width = int((width-220) * percent / 50)  # 缩放比例调整
    draw.rectangle([(180, y_offset-2), (width-150, y_offset+20)], fill='#f7fafc')
    draw.rectangle([(180, y_offset-2), (180+bar_width, y_offset+20)], fill='#7b61ff')
    draw.text((185, y_offset+2), f"{percent}%", font=font_small, fill='white')
    draw.text((width-145, y_offset+2), value, font=font_small, fill='#2d3748')
    y_offset += 35

y_offset += 30

# 第四部分：风险预警
draw.rectangle([(30, y_offset), (width-30, y_offset+50)], fill='#ed7b2f')
draw.text((50, y_offset+12), "⚠️ 四、风险预警与改进", font=font_subtitle, fill='white')
y_offset += 70

risks = [
    "⚠️ 产品中心需求占比波动大（40.1%→42.5%→29.9%）",
    "改进：提前规划需求，避免同时进入设计阶段",
    "",
    "⚠️ 测试联调工时占比持续偏高（35.7%-36.4%）",
    "改进：持续推进AI自动测试Agent建设",
    "",
    "🔴 洛克王国短信故障（3/23已复盘）：告警延迟3天",
    "改进：告警分级机制+责任人绑定+AI分析"
]

for text in risks:
    draw.text((50, y_offset), text, font=font_small, fill='#663c00' if text else '#000')
    y_offset += 25

y_offset += 30

# 第五部分：4月展望
draw.rectangle([(30, y_offset), (width-30, y_offset+50)], fill='#0052d9')
draw.text((50, y_offset+12), "🔮 五、4月展望", font=font_subtitle, fill='white')
y_offset += 70

outlook = [
    "🔥 IC V5.0 AI智能投放进入开发阶段",
    "🤖 运营AI活动配置二期方案定型",
    "⚡ IC充值迭代三持续开发",
    "✅ 批量录入+审批+通知功能验收"
]

for text in outlook:
    draw.rectangle([(40, y_offset), (width-40, y_offset+45)], fill='#f0f8ff', outline='#0052d9')
    draw.text((55, y_offset+13), text, font=font_normal, fill='#1a2a4a')
    y_offset += 52

y_offset += 30

# Footer
draw.rectangle([(0, y_offset), (width, y_offset+80)], fill='#f8fafe')
draw.text((40, y_offset+15), "3月项管侧月报·产品组Leader视角", font=font_small, fill='#a0aec0')
draw.text((40, y_offset+40), "运营商合作部_技术研发中心 | 生成时间：2026-03-25", font=font_small, fill='#a0aec0')

# 裁剪到实际使用的高度
final_height = y_offset + 80
img_final = img.crop((0, 0, width, final_height))

# 保存图片
output_path = "/Users/tanfang/CodeBuddy/fangtan的工作台/研发项管/周报月报产出/3月项管月报-产品组视角-分享图.png"
img_final.save(output_path, quality=95, dpi=(300, 300))
print(f"✅ 高清长图已生成：{output_path}")
print(f"📐 图片尺寸：{width}x{final_height}px")

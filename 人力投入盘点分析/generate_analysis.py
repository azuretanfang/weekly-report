import pandas as pd
import json

# ========== 原始数据录入 ==========
# 产品列: 定向流量(含0元权益和夏支付), 游戏王卡, 权益座+电竞卡+CPS, 物联网卡, 网关取号, 企业短信, 95语音, 话费代收, 建行项目, 运营商业务支撑

products = ['定向流量', '游戏王卡', '权益座+电竞卡+CPS', '物联网卡', '网关取号', '企业短信', '95语音', '话费代收', '建行项目', '运营商业务支撑']
product_full_names = {
    '定向流量': '定向流量(含0元权益和夏支付)',
    '游戏王卡': '游戏王卡',
    '权益座+电竞卡+CPS': '权益座+电竞卡+CPS',
    '物联网卡': '物联网卡',
    '网关取号': '网关取号',
    '企业短信': '企业短信',
    '95语音': '95语音',
    '话费代收': '话费代收',
    '建行项目': '建行项目',
    '运营商业务支撑': '运营商业务支撑'
}

# 人员数据 - 按月份录入
# 已移除 eonefeng(马瑜雯) —— 她是+1，尚未填写
# 已修正 issactan(谭俊杰) 2月数据：原0.9修正为1.0

raw_data = []

# === 2026年1月 ===
jan_data = [
    {'月份': '202601', '成本中心': '产品运营中心-产品策划一组', '员工': 'ckzheng(郑超奎)', '类型': '正式', 'HC': 1,
     '定向流量': 0.4, '游戏王卡': 0.3, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.3},
    {'月份': '202601', '成本中心': '', '员工': 'cmiliazhang(张铭纯)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0.1, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.9},
    {'月份': '202601', '成本中心': '', '员工': 'fangtan(谈芳)', '类型': '正式', 'HC': 1,
     '定向流量': 0.2, '游戏王卡': 0.15, '权益座+电竞卡+CPS': 0, '物联网卡': 0.1, '网关取号': 0.1, '企业短信': 0.3, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.15},
    {'月份': '202601', '成本中心': '产品中心-产品策划二组', '员工': 'hongleili(李红蕾)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202601', '成本中心': '产品运营中心-产品运营组', '员工': 'issactan(谭俊杰)', '类型': '正式', 'HC': 1,
     '定向流量': 0.4, '游戏王卡': 0.15, '权益座+电竞卡+CPS': 0.1, '物联网卡': 0, '网关取号': 0, '企业短信': 0.3, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.05},
    {'月份': '202601', '成本中心': '', '员工': 'jesydong(董菁月)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.2, '企业短信': 0.8, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202601', '成本中心': '', '员工': 'jijiang(姜璟)', '类型': '正式', 'HC': 1,
     '定向流量': 0.3, '游戏王卡': 0.4, '权益座+电竞卡+CPS': 0.3, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202601', '成本中心': '', '员工': 'namisu(苏魃)', '类型': '正式', 'HC': 1,
     '定向流量': 0.1, '游戏王卡': 0.7, '权益座+电竞卡+CPS': 0, '物联网卡': 0.1, '网关取号': 0, '企业短信': 0.1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202601', '成本中心': '', '员工': 'zoraqin(覃柲)', '类型': '正式', 'HC': 1,
     '定向流量': 0.2, '游戏王卡': 0.2, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.6, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
]

# === 2026年2月 ===
# issactan 2月修正：原始数据投入合计0.9，确认应为1.0，网关取号从0.1调至0.2
feb_data = [
    {'月份': '202602', '成本中心': '产品运营中心-产品策划一组', '员工': 'ckzheng(郑超奎)', '类型': '正式', 'HC': 1,
     '定向流量': 0.4, '游戏王卡': 0.2, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.4},
    {'月份': '202602', '成本中心': '', '员工': 'cmiliazhang(张铭纯)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 1},
    {'月份': '202602', '成本中心': '', '员工': 'fangtan(谈芳)', '类型': '正式', 'HC': 1,
     '定向流量': 0.2, '游戏王卡': 0.15, '权益座+电竞卡+CPS': 0, '物联网卡': 0.1, '网关取号': 0.1, '企业短信': 0.3, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.15},
    {'月份': '202602', '成本中心': '产品中心-产品策划二组', '员工': 'hongleili(李红蕾)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202602', '成本中心': '产品运营中心-产品运营组', '员工': 'issactan(谭俊杰)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0.7, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.1, '企业短信': 0.1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.1},
    {'月份': '202602', '成本中心': '', '员工': 'jesydong(董菁月)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.2, '企业短信': 0.8, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202602', '成本中心': '', '员工': 'jijiang(姜璟)', '类型': '正式', 'HC': 1,
     '定向流量': 0.4, '游戏王卡': 0.4, '权益座+电竞卡+CPS': 0.2, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202602', '成本中心': '', '员工': 'namisu(苏魃)', '类型': '正式', 'HC': 1,
     '定向流量': 0.1, '游戏王卡': 0.7, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.1, '企业短信': 0.1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202602', '成本中心': '', '员工': 'zoraqin(覃柲)', '类型': '正式', 'HC': 1,
     '定向流量': 0.15, '游戏王卡': 0.15, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.7, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
]

# === 2026年3月 ===
mar_data = [
    {'月份': '202603', '成本中心': '运营商合作部-产品运营中心', '员工': 'ckzheng(郑超奎)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0.7, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.3},
    {'月份': '202603', '成本中心': '', '员工': 'cmiliazhang(张铭纯)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 1},
    {'月份': '202603', '成本中心': '', '员工': 'fangtan(谈芳)', '类型': '正式', 'HC': 1,
     '定向流量': 0.2, '游戏王卡': 0.15, '权益座+电竞卡+CPS': 0, '物联网卡': 0.1, '网关取号': 0.1, '企业短信': 0.3, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.15},
    {'月份': '202603', '成本中心': '', '员工': 'hongleili(李红蕾)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202603', '成本中心': '产品运营中心-产品运营组', '员工': 'issactan(谭俊杰)', '类型': '正式', 'HC': 1,
     '定向流量': 0.1, '游戏王卡': 0.7, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.1, '企业短信': 0.1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202603', '成本中心': '', '员工': 'jesydong(董菁月)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.2, '企业短信': 0.8, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202603', '成本中心': '', '员工': 'jijiang(姜璟)', '类型': '正式', 'HC': 1,
     '定向流量': 0.5, '游戏王卡': 0.4, '权益座+电竞卡+CPS': 0.1, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202603', '成本中心': '', '员工': 'namisu(苏魃)', '类型': '正式', 'HC': 1,
     '定向流量': 0.1, '游戏王卡': 0.7, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0.1, '企业短信': 0.1, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    {'月份': '202603', '成本中心': '', '员工': 'zoraqin(覃柲)', '类型': '正式', 'HC': 1,
     '定向流量': 0.2, '游戏王卡': 0.2, '权益座+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.6, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
]

raw_data = jan_data + feb_data + mar_data
df = pd.DataFrame(raw_data)

# ========== 数据分析 ==========

month_labels = {'202601': '1月', '202602': '2月', '202603': '3月'}

# 1. 按产品维度汇总（每月每产品的总人力投入）
product_by_month = {}
for month in ['202601', '202602', '202603']:
    month_df = df[df['月份'] == month]
    product_sums = {}
    for p in products:
        product_sums[p] = month_df[p].sum()
    product_by_month[month] = product_sums

# 2. 按人员维度汇总
persons = sorted(df['员工'].unique())

# 3. 数据质量检查
quality_issues = []
for month in ['202601', '202602', '202603']:
    month_df = df[df['月份'] == month]
    for _, row in month_df.iterrows():
        total = sum(row[p] for p in products)
        hc = row['HC']
        if hc > 0 and abs(total - 1.0) > 0.01:
            quality_issues.append({
                '月份': month_labels[month],
                '员工': row['员工'],
                'HC': hc,
                '投入合计': round(total, 2),
                '差异': round(total - 1.0, 2),
                '问题': f'投入比例合计{round(total*100)}%，差异{round((total-1)*100)}%'
            })

# 计算Q1产品汇总
grand_total = sum(sum(product_by_month[m][p] for p in products) for m in ['202601','202602','202603'])
q1_product_totals = {}
for p in products:
    q1_product_totals[p] = sum(product_by_month[m][p] for m in ['202601','202602','202603'])
sorted_products = sorted(q1_product_totals.items(), key=lambda x: x[1], reverse=True)

# 有投入的产品
active_products = [p for p, v in q1_product_totals.items() if v > 0]
zero_products = [p for p, v in q1_product_totals.items() if v == 0]

# ========== 生成HTML报告 ==========
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>产品运营中心 26年Q1人力投入盘点分析</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f6fa; color: #2d3436; padding: 24px; line-height: 1.6; }
.container { max-width: 1400px; margin: 0 auto; }

/* Header */
.header { background: linear-gradient(135deg, #0984e3 0%, #6c5ce7 100%); color: white; padding: 32px 40px; border-radius: 16px; margin-bottom: 24px; position: relative; overflow: hidden; }
.header::after { content: ''; position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; background: rgba(255,255,255,0.05); border-radius: 50%; }
.header h1 { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
.header .subtitle { font-size: 14px; opacity: 0.8; }
.kpi-row { display: flex; gap: 16px; margin-top: 20px; flex-wrap: wrap; }
.kpi-card { background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 16px 24px; border-radius: 12px; min-width: 140px; }
.kpi-card .kpi-value { font-size: 32px; font-weight: 800; }
.kpi-card .kpi-label { font-size: 12px; opacity: 0.8; margin-top: 2px; }

/* Section */
.section { background: white; border-radius: 14px; padding: 28px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.section-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.section-title .icon { font-size: 20px; }
.section-title .bar { width: 4px; height: 22px; border-radius: 2px; background: linear-gradient(180deg, #0984e3, #6c5ce7); }

/* Table */
table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px; }
thead th { background: #f8f9fa; font-weight: 600; text-align: center; padding: 12px 8px; color: #636e72; border-bottom: 2px solid #e8e8e8; position: sticky; top: 0; }
thead th:first-child { border-radius: 8px 0 0 0; text-align: left; }
thead th:last-child { border-radius: 0 8px 0 0; }
td { text-align: center; padding: 10px 8px; border-bottom: 1px solid #f0f0f0; transition: background 0.15s; }
tr:hover td { background: #f8f9ff; }
.text-left { text-align: left; }
.zero { color: #ddd; }
.highlight { background: #fff8e1; font-weight: 700; color: #e17055; }
.total-row { background: linear-gradient(90deg, #0984e3, #6c5ce7); }
.total-row td { color: white; font-weight: 700; border-bottom: none; padding: 12px 8px; }
.total-row td:first-child { border-radius: 0 0 0 8px; }
.total-row td:last-child { border-radius: 0 0 8px 0; }
.subtotal-row td { background: #f0f4ff; font-weight: 600; }

/* Badges */
.badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.badge-green { background: #e6ffed; color: #27ae60; }
.badge-red { background: #ffe8e8; color: #e74c3c; }
.badge-yellow { background: #fff8e1; color: #f39c12; }
.badge-blue { background: #e8f4fd; color: #0984e3; }
.badge-purple { background: #f3e8fd; color: #6c5ce7; }

/* Cards */
.insight-card { background: #f8f9ff; border-left: 4px solid #0984e3; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.insight-card .card-title { font-weight: 700; color: #0984e3; font-size: 14px; margin-bottom: 6px; }
.insight-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

.warning-card { background: #fffbf0; border-left: 4px solid #f39c12; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.warning-card .card-title { font-weight: 700; color: #f39c12; font-size: 14px; margin-bottom: 6px; }
.warning-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

.success-card { background: #f0fff4; border-left: 4px solid #27ae60; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.success-card .card-title { font-weight: 700; color: #27ae60; font-size: 14px; margin-bottom: 6px; }
.success-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

/* Bar chart */
.bar-row { display: flex; align-items: center; margin-bottom: 10px; }
.bar-label { width: 160px; font-size: 13px; font-weight: 600; text-align: right; padding-right: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bar-track { flex: 1; height: 28px; background: #f0f0f0; border-radius: 6px; overflow: hidden; position: relative; }
.bar-fill { height: 100%; border-radius: 6px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; font-size: 11px; color: white; font-weight: 700; min-width: 30px; transition: width 0.3s; }
.bar-pct { margin-left: 8px; font-size: 12px; color: #636e72; min-width: 48px; }

/* Stacked bar */
.stacked-bar { display: flex; height: 32px; border-radius: 6px; overflow: hidden; margin: 4px 0; }
.stacked-segment { display: flex; align-items: center; justify-content: center; font-size: 10px; color: white; font-weight: 600; transition: width 0.3s; cursor: default; }

/* Legend */
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0; }
.legend-item { display: flex; align-items: center; gap: 5px; font-size: 12px; color: #555; }
.legend-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }

/* Grid */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 900px) { .grid-2 { grid-template-columns: 1fr; } }

/* Trend */
.trend-up { color: #27ae60; font-weight: 600; }
.trend-down { color: #e74c3c; font-weight: 600; }
.trend-flat { color: #b2bec3; }

/* Discussion section */
.discuss-section { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); border-radius: 14px; padding: 28px; margin-bottom: 20px; }
.discuss-section .section-title { color: #c0392b; }
.discuss-section .section-title .bar { background: #e17055; }
.discuss-item { background: rgba(255,255,255,0.7); backdrop-filter: blur(5px); border-radius: 10px; padding: 16px 20px; margin-bottom: 10px; }
.discuss-item .q { font-weight: 700; color: #c0392b; font-size: 14px; margin-bottom: 6px; }
.discuss-item .a { font-size: 13px; color: #555; }

/* Footer */
.footer { text-align: center; color: #b2bec3; font-size: 12px; padding: 20px; }
</style>
</head>
<body>
<div class="container">
'''

# ===== HEADER =====
html += f'''
<div class="header">
    <h1>📊 产品运营中心 · 26年Q1人力投入盘点分析</h1>
    <div class="subtitle">数据来源：线下收集（已排除+1 eonefeng未填数据） | 生成时间：2026年4月9日 | 目的：还原业务实际净利润</div>
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value">{len(persons)}</div>
            <div class="kpi-label">填报人员数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{len(active_products)}</div>
            <div class="kpi-label">有投入产品数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{grand_total:.1f}</div>
            <div class="kpi-label">Q1累计人力（人月）</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{grand_total/3:.1f}</div>
            <div class="kpi-label">月均人力</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{len(quality_issues)}</div>
            <div class="kpi-label">数据异常项</div>
        </div>
    </div>
</div>
'''

# ===== Section 1: 数据质量 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">✅</span>数据质量检查</div>'
if quality_issues:
    for issue in quality_issues:
        html += f'''<div class="warning-card">
    <div class="card-title">{issue['月份']} · {issue['员工']}</div>
    <div class="card-body">{issue['问题']}（HC={issue['HC']}，投入合计={issue['投入合计']}）</div>
</div>'''
else:
    html += '<div class="success-card"><div class="card-title">✅ 所有数据质量良好</div><div class="card-body">全部 9 人 × 3 个月共 27 条数据，投入比例均等于100%，无异常。</div></div>'
html += '</div>'

# ===== Section 2: 产品人力投入排名（横向柱状图）=====
product_colors = {
    '定向流量': '#0984e3',
    '游戏王卡': '#6c5ce7',
    '权益座+电竞卡+CPS': '#e17055',
    '物联网卡': '#00b894',
    '网关取号': '#fdcb6e',
    '企业短信': '#e74c3c',
    '95语音': '#a29bfe',
    '话费代收': '#fab1a0',
    '建行项目': '#636e72',
    '运营商业务支撑': '#00cec9'
}

html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">🏆</span>Q1产品人力投入排名</div>'

max_val = sorted_products[0][1] if sorted_products else 1
for p, v in sorted_products:
    if v == 0:
        continue
    pct = v / grand_total * 100
    width_pct = v / max_val * 100
    color = product_colors.get(p, '#636e72')
    # 月度明细
    m_vals = [product_by_month[m][p] for m in ['202601','202602','202603']]
    trend = ''
    if m_vals[2] > m_vals[0] + 0.05:
        trend = '<span class="trend-up">↑</span>'
    elif m_vals[2] < m_vals[0] - 0.05:
        trend = '<span class="trend-down">↓</span>'
    else:
        trend = '<span class="trend-flat">→</span>'
    html += f'''<div class="bar-row">
    <div class="bar-label" title="{p}">{p}</div>
    <div class="bar-track"><div class="bar-fill" style="width:{width_pct}%;background:{color}">{v:.1f}</div></div>
    <div class="bar-pct">{pct:.1f}% {trend}</div>
</div>'''

html += '</div>'

# ===== Section 3: 产品月度明细表 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">📋</span>产品月度人力投入明细</div>'
html += '<table><thead><tr><th class="text-left" style="min-width:180px">产品</th>'
for m in ['202601','202602','202603']:
    html += f'<th>{month_labels[m]}</th>'
html += '<th>Q1合计</th><th>Q1占比</th><th>月均</th><th>趋势</th></tr></thead><tbody>'

for p, v in sorted_products:
    vals = [product_by_month[m][p] for m in ['202601','202602','202603']]
    total_p = sum(vals)
    pct = total_p / grand_total * 100 if grand_total > 0 else 0
    avg = total_p / 3
    color = product_colors.get(p, '#636e72')

    trend = ''
    if vals[2] > vals[0] + 0.05:
        trend = '<span class="trend-up">↑ 上升</span>'
    elif vals[2] < vals[0] - 0.05:
        trend = '<span class="trend-down">↓ 下降</span>'
    else:
        trend = '<span class="trend-flat">→ 稳定</span>'

    html += f'<tr><td class="text-left" style="font-weight:600;color:{color}">{p}</td>'
    for val in vals:
        cls = 'zero' if val == 0 else ('highlight' if val >= 2 else '')
        display = '-' if val == 0 else f'{val:.2f}'
        html += f'<td class="{cls}">{display}</td>'
    html += f'<td><strong>{total_p:.2f}</strong></td>'
    html += f'<td><strong>{pct:.1f}%</strong></td>'
    html += f'<td>{avg:.2f}</td>'
    html += f'<td>{trend}</td></tr>'

# Total row
html += '<tr class="total-row"><td class="text-left">合计</td>'
for m in ['202601','202602','202603']:
    t = sum(product_by_month[m][p] for p in products)
    html += f'<td>{t:.1f}</td>'
html += f'<td>{grand_total:.1f}</td><td>100%</td><td>{grand_total/3:.1f}</td><td></td></tr>'
html += '</tbody></table></div>'

# ===== Section 4: 人员投入明细 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">👥</span>人员月度投入明细</div>'

# 用简短列名
short_names = {
    '定向流量': '定向流量',
    '游戏王卡': '游戏王卡',
    '权益座+电竞卡+CPS': '权益座',
    '物联网卡': '物联网卡',
    '网关取号': '网关取号',
    '企业短信': '企业短信',
    '95语音': '95语音',
    '话费代收': '话费代收',
    '建行项目': '建行项目',
    '运营商业务支撑': '运营商支撑'
}

html += '<table><thead><tr><th class="text-left">员工</th><th>月份</th>'
for p in products:
    html += f'<th style="font-size:11px;max-width:60px">{short_names.get(p,p)}</th>'
html += '<th>合计</th><th>状态</th></tr></thead><tbody>'

for person in persons:
    person_df = df[df['员工'] == person].sort_values('月份')
    first = True
    person_total = 0
    for _, row in person_df.iterrows():
        total = sum(row[p] for p in products)
        person_total += total
        status = ''
        if abs(total - 1.0) > 0.01:
            status = f'<span class="badge badge-red">合计{total:.0%}</span>'
        else:
            status = '<span class="badge badge-green">✓</span>'

        name_display = f'<strong>{person}</strong>' if first else ''
        html += f'<tr><td class="text-left">{name_display}</td>'
        html += f'<td><span class="badge badge-blue">{month_labels[row["月份"]]}</span></td>'
        for p in products:
            v = row[p]
            if v == 0:
                html += '<td class="zero">-</td>'
            elif v >= 0.5:
                html += f'<td class="highlight">{v:.0%}</td>'
            else:
                html += f'<td>{v:.0%}</td>'
        html += f'<td><strong>{total:.0%}</strong></td><td>{status}</td></tr>'
        first = False
    # Q1小计行
    html += f'<tr class="subtotal-row"><td class="text-left"></td><td><strong>Q1合计</strong></td>'
    for p in products:
        v = sum(person_df[p])
        if v == 0:
            html += '<td class="zero">-</td>'
        else:
            html += f'<td><strong>{v:.2f}</strong></td>'
    html += f'<td><strong>{person_total:.1f}</strong></td><td></td></tr>'

html += '</tbody></table></div>'

# ===== Section 5: 人员投入可视化（堆叠条形图）=====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">📊</span>人员产品投入分布（Q1平均）</div>'
html += '<div class="legend">'
for p in active_products:
    color = product_colors.get(p, '#636e72')
    html += f'<div class="legend-item"><div class="legend-dot" style="background:{color}"></div>{p}</div>'
html += '</div>'

for person in persons:
    person_df = df[df['员工'] == person]
    # 计算Q1平均
    avg_vals = {}
    for p in products:
        avg_vals[p] = person_df[p].mean()

    html += f'<div style="margin-bottom:12px"><div style="font-size:13px;font-weight:600;margin-bottom:4px">{person}</div>'
    html += '<div class="stacked-bar">'
    for p in products:
        v = avg_vals[p]
        if v > 0:
            pct = v * 100
            color = product_colors.get(p, '#636e72')
            label = f'{short_names.get(p,p)} {v:.0%}' if pct > 8 else (f'{v:.0%}' if pct > 4 else '')
            html += f'<div class="stacked-segment" style="width:{pct}%;background:{color}" title="{p}: {v:.0%}">{label}</div>'
    html += '</div></div>'
html += '</div>'

# ===== Section 6: 各月投入占比可视化 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">📈</span>各月产品人力投入占比</div>'
for m in ['202601','202602','202603']:
    total_m = sum(product_by_month[m][p] for p in products)
    html += f'<div style="margin-bottom:16px"><div style="font-size:14px;font-weight:700;margin-bottom:6px">{month_labels[m]}（合计 {total_m:.1f} 人力）</div>'
    html += '<div class="stacked-bar">'
    for p in products:
        v = product_by_month[m][p]
        if v > 0:
            pct = v / total_m * 100
            color = product_colors.get(p, '#636e72')
            label = f'{short_names.get(p,p)} {v:.1f}' if pct > 6 else (f'{v:.1f}' if pct > 3 else '')
            html += f'<div class="stacked-segment" style="width:{pct}%;background:{color}" title="{p}: {v:.1f}人力 ({pct:.1f}%)">{label}</div>'
    html += '</div></div>'
html += '</div>'

# ===== Section 7: 关键发现 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">🔍</span>关键发现</div>'

# TOP3
html += '<div class="insight-card"><div class="card-title">🏆 人力投入TOP3产品</div><div class="card-body">'
for rank, (p, v) in enumerate(sorted_products[:3], 1):
    pct = v / grand_total * 100
    m_vals = [product_by_month[m][p] for m in ['202601','202602','202603']]
    html += f'<strong>{rank}. {p}</strong>：Q1累计 {v:.1f} 人月（占比 {pct:.1f}%），月度分布 {m_vals[0]:.1f} → {m_vals[1]:.1f} → {m_vals[2]:.1f}<br>'
html += f'<br>TOP3产品合计占比 <strong>{sum(v for _,v in sorted_products[:3])/grand_total*100:.1f}%</strong>，人力高度集中。</div></div>'

# 零投入产品
if zero_products:
    html += f'<div class="warning-card"><div class="card-title">⚠️ Q1零投入产品（{len(zero_products)}个）</div><div class="card-body">'
    html += '、'.join(f'<strong>{p}</strong>' for p in zero_products)
    html += '<br>这些产品在Q1没有产品运营中心的人力投入，需与+1确认是否准确（可能归其他团队负责）。</div></div>'

# 月度趋势变化
trend_changes = []
for p in products:
    v1 = product_by_month['202601'][p]
    v3 = product_by_month['202603'][p]
    if abs(v3 - v1) >= 0.2:
        trend_changes.append((p, v1, v3, v3-v1))
if trend_changes:
    html += '<div class="insight-card"><div class="card-title">📈 显著趋势变化（1月→3月变化≥0.2人力）</div><div class="card-body">'
    for p, v1, v3, delta in sorted(trend_changes, key=lambda x: abs(x[3]), reverse=True):
        direction = '↑' if delta > 0 else '↓'
        css = 'trend-up' if delta > 0 else 'trend-down'
        html += f'<strong>{p}</strong>：{v1:.1f} → {v3:.1f}（<span class="{css}">{direction}{abs(delta):.1f}</span>）<br>'
    html += '</div></div>'

# 人员特征
html += '<div class="insight-card"><div class="card-title">👤 人员投入特征</div><div class="card-body">'
# 找高度集中单一产品的人
for person in persons:
    person_df = df[df['员工'] == person]
    for p in products:
        avg = person_df[p].mean()
        if avg >= 0.8:
            html += f'<strong>{person}</strong>：Q1平均 {avg:.0%} 投入在「{p}」，属于高度集中型<br>'
        elif avg >= 0.6:
            html += f'<strong>{person}</strong>：Q1平均 {avg:.0%} 投入在「{p}」，属于主要集中型<br>'
# 找跨产品分散的人
for person in persons:
    person_df = df[df['员工'] == person]
    active_count = sum(1 for p in products if person_df[p].mean() > 0)
    if active_count >= 4:
        html += f'<strong>{person}</strong>：横跨 {active_count} 个产品，属于多产品分散型<br>'
html += '</div></div>'

html += '</div>'

# ===== Section 8: 讨论要点 =====
html += '''<div class="discuss-section">
<div class="section-title"><div class="bar"></div><span class="icon">💬</span>过数据讨论要点</div>
'''

discuss_points = [
    {
        'q': '1. 零投入产品确认',
        'a': f'95语音、话费代收、建行项目三个产品在Q1无投入。需确认：是归其他团队负责，还是确实没有安排人力？'
    },
    {
        'q': '2. "运营商业务支撑"定义与拆分',
        'a': f'该产品Q1累计 {q1_product_totals["运营商业务支撑"]:.1f} 人月，占比 {q1_product_totals["运营商业务支撑"]/grand_total*100:.1f}%。名称较为笼统，后续跟BP对数据时可能需要明确：具体包含哪些工作内容？是否需要拆分到具体产品线？'
    },
    {
        'q': '3. 物联网卡投入波动',
        'a': f'物联网卡投入从1月 {product_by_month["202601"]["物联网卡"]:.1f} → 2月 {product_by_month["202602"]["物联网卡"]:.1f} → 3月 {product_by_month["202603"]["物联网卡"]:.1f}，3月出现显著增加。原因：ckzheng(郑超奎) 3月转向物联网卡（70%）。需确认该变动是否持续。'
    },
    {
        'q': '4. ckzheng(郑超奎) 3月投入大幅变动',
        'a': f'1-2月主要投入定向流量+游戏王卡+运营商支撑，3月变为物联网卡70%+运营商支撑30%。定向流量从0.4降为0。需确认是业务调整还是临时安排。'
    },
    {
        'q': '5. 数据提交格式确认',
        'a': '本次数据已完成汇总，需确认：是否按这个格式提交给zorawang(王妍)？是否还需要+1（eonefeng）的数据补充？'
    },
]

for item in discuss_points:
    html += f'''<div class="discuss-item">
    <div class="q">{item['q']}</div>
    <div class="a">{item['a']}</div>
</div>'''

html += '</div>'

# Footer
html += '''
<div class="footer">
    产品运营中心 · 26年Q1人力投入盘点分析 · 生成时间 2026-04-09
</div>
</div>
</body>
</html>'''

with open('/Users/tanfang/CodeBuddy/fangtan的工作台/人力投入盘点分析/人力投入盘点分析报告.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ HTML分析报告已生成：人力投入盘点分析报告.html")
print(f"\n📊 数据概览：")
print(f"  - 填报人员: {len(persons)}人")
print(f"  - 有投入产品: {len(active_products)}个")
print(f"  - 零投入产品: {len(zero_products)}个 → {', '.join(zero_products)}")
print(f"  - Q1累计人力: {grand_total:.1f}人月")
print(f"  - 月均人力: {grand_total/3:.1f}人月")
print(f"  - 数据异常: {len(quality_issues)}个")
print(f"\n🏆 产品人力投入排名（Q1）:")
for rank, (p, v) in enumerate(sorted_products, 1):
    if v > 0:
        pct = v / grand_total * 100
        print(f"  {rank}. {p}: {v:.2f}人月 ({pct:.1f}%)")

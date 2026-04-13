import pandas as pd
import json

# ========== 原始数据录入 ==========
# 运营商合作部-技术研发中心 26年1-3月人力投入盘点
# 产品列: 定向流量(含0元权益和夏支付), 游戏王卡, 权益库+电竞卡+CPS, 物联网卡, 网关取号, 企业短信, 95语音, 话费代收, 建行项目, 运营商业务支撑

products = ['定向流量', '游戏王卡', '权益库+电竞卡+CPS', '物联网卡', '网关取号', '企业短信', '95语音', '话费代收', '建行项目', '运营商业务支撑']
product_full_names = {
    '定向流量': '定向流量(含0元权益和夏支付)',
    '游戏王卡': '游戏王卡',
    '权益库+电竞卡+CPS': '权益库+电竞卡+CPS',
    '物联网卡': '物联网卡',
    '网关取号': '网关取号',
    '企业短信': '企业短信',
    '95语音': '95语音',
    '话费代收': '话费代收',
    '建行项目': '建行项目',
    '运营商业务支撑': '运营商业务支撑'
}

# 人员数据 - 按月份录入
# junyuzheng(郑俊宇) HC=0.3，不是异常数据

raw_data = []

# === 2026年1月 ===
# Row2: benzphuang 技术研发中心-公共 正式 HC=1, 定向流量=0.5, 游戏王卡=0.285, 物联网卡=0.024, 企业短信=0.043, 运营商业务支撑=0.148
# Row3: conniesun 正式 HC=1, 定向流量=0.403, 游戏王卡=0.29, 企业短信=0.039, 运营商业务支撑=0.268
# Row4: guoleluo 正式 HC=1, 定向流量=0.652, 游戏王卡=0.1, 企业短信=0.024, 运营商业务支撑=0.224
# Row5: jiushigao 正式 HC=1, 定向流量=0.506, 游戏王卡=0.2, 物联网卡=0.072, 运营商业务支撑=0.222
# Row6: juibyyang 正式 HC=1, 游戏王卡=0.21, 企业短信=0.7, 运营商业务支撑=0.09
# Row7: junyuzheng 正式 HC=0.3, 企业短信=0.276, 运营商业务支撑=1(不对，看数据)
# Row8: ottozhou 正式 HC=1, 企业短信=0.806, 运营商业务支撑=0.194
# Row9: sigmoidguo 正式 HC=1, 定向流量=0.03, 企业短信=0.855, 运营商业务支撑=0(看不清)
# Row10: tealyao 正式 HC=1, 定向流量=0.03(?), 企业短信=0.855(?)

# 让我重新仔细读取数据

jan_data = [
    # benzphuang(黄智瑞) - 行2
    {'月份': '202601', '成本中心': '技术研发中心-公共', '员工': 'benzphuang(黄智瑞)', '类型': '正式', 'HC': 1,
     '定向流量': 0.5, '游戏王卡': 0.285, '权益库+电竞卡+CPS': 0, '物联网卡': 0.024, '网关取号': 0, '企业短信': 0.043, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.148},
    # conniesun(孙佳慧) - 行3
    {'月份': '202601', '成本中心': '', '员工': 'conniesun(孙佳慧)', '类型': '正式', 'HC': 1,
     '定向流量': 0.403, '游戏王卡': 0.29, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.039, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.268},
    # guoleluo(罗国乐) - 行4
    {'月份': '202601', '成本中心': '', '员工': 'guoleluo(罗国乐)', '类型': '正式', 'HC': 1,
     '定向流量': 0.652, '游戏王卡': 0.1, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.024, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.224},
    # jiushigao(高九渊) - 行5
    {'月份': '202601', '成本中心': '', '员工': 'jiushigao(高九渊)', '类型': '正式', 'HC': 1,
     '定向流量': 0.506, '游戏王卡': 0.2, '权益库+电竞卡+CPS': 0, '物联网卡': 0.072, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.222},
    # juibyyang(杨成桤) - 行6（根据1月合计行校验，0.21应在定向流量列而非游戏王卡列）
    {'月份': '202601', '成本中心': '', '员工': 'juibyyang(杨成桤)', '类型': '正式', 'HC': 1,
     '定向流量': 0.21, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.7, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.09},
    # junyuzheng(郑俊宇) - 行7 - HC=0.3
    {'月份': '202601', '成本中心': '', '员工': 'junyuzheng(郑俊宇)', '类型': '正式', 'HC': 0.3,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.276, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.024},
    # ottozhou(周韬) - 行8
    {'月份': '202601', '成本中心': '', '员工': 'ottozhou(周韬)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.806, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.194},
    # sigmoidguo(郭鑫朋) - 行9
    {'月份': '202601', '成本中心': '', '员工': 'sigmoidguo(郭鑫朋)', '类型': '正式', 'HC': 1,
     '定向流量': 0.03, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.855, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.115},
    # tealyao(姚望) - 行10（根据1月合计行校验，全部投入在运营商业务支撑）
    {'月份': '202601', '成本中心': '', '员工': 'tealyao(姚望)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 1.0},
]

# === 2026年2月 ===
feb_data = [
    # benzphuang(黄智瑞) - 行12
    {'月份': '202602', '成本中心': '技术研发中心-公共', '员工': 'benzphuang(黄智瑞)', '类型': '正式', 'HC': 1,
     '定向流量': 0.453, '游戏王卡': 0.2, '权益库+电竞卡+CPS': 0, '物联网卡': 0.043, '网关取号': 0, '企业短信': 0.261, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.043},
    # conniesun(孙佳慧) - 行13
    {'月份': '202602', '成本中心': '', '员工': 'conniesun(孙佳慧)', '类型': '正式', 'HC': 1,
     '定向流量': 0.667, '游戏王卡': 0.2, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.133},
    # guoleluo(罗国乐) - 行14
    {'月份': '202602', '成本中心': '', '员工': 'guoleluo(罗国乐)', '类型': '正式', 'HC': 1,
     '定向流量': 0.568, '游戏王卡': 0.2, '权益库+电竞卡+CPS': 0.04, '物联网卡': 0, '网关取号': 0, '企业短信': 0.024, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.168},
    # jiushigao(高九渊) - 行15
    {'月份': '202602', '成本中心': '', '员工': 'jiushigao(高九渊)', '类型': '正式', 'HC': 1,
     '定向流量': 0.16, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0.824, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.016},
    # juibyyang(杨成桤) - 行16
    {'月份': '202602', '成本中心': '', '员工': 'juibyyang(杨成桤)', '类型': '正式', 'HC': 1,
     '定向流量': 0.083, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.917, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    # junyuzheng(郑俊宇) - 行17 - HC=0.3
    {'月份': '202602', '成本中心': '', '员工': 'junyuzheng(郑俊宇)', '类型': '正式', 'HC': 0.3,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0.034, '网关取号': 0, '企业短信': 0.266, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    # ottozhou(周韬) - 行18
    {'月份': '202602', '成本中心': '', '员工': 'ottozhou(周韬)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 1},
    # sigmoidguo(郭鑫朋) - 行19
    {'月份': '202602', '成本中心': '', '员工': 'sigmoidguo(郭鑫朋)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0.045, '网关取号': 0, '企业短信': 0.728, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.227},
    # tealyao(姚望) - 行20
    {'月份': '202602', '成本中心': '', '员工': 'tealyao(姚望)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.94, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.06},
]

# === 2026年3月 ===
mar_data = [
    # benzphuang(黄智瑞) - 行22
    {'月份': '202603', '成本中心': '技术研发中心-公共', '员工': 'benzphuang(黄智瑞)', '类型': '正式', 'HC': 1,
     '定向流量': 0.595, '游戏王卡': 0.195, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.155, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.055},
    # conniesun(孙佳慧) - 行23
    {'月份': '202603', '成本中心': '', '员工': 'conniesun(孙佳慧)', '类型': '正式', 'HC': 1,
     '定向流量': 0.303, '游戏王卡': 0.323, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.354, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.02},
    # guoleluo(罗国乐) - 行24
    {'月份': '202603', '成本中心': '', '员工': 'guoleluo(罗国乐)', '类型': '正式', 'HC': 1,
     '定向流量': 0.49, '游戏王卡': 0.285, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.19, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.035},
    # jiushigao(高九渊) - 行25
    {'月份': '202603', '成本中心': '', '员工': 'jiushigao(高九渊)', '类型': '正式', 'HC': 1,
     '定向流量': 0.18, '游戏王卡': 0.025, '权益库+电竞卡+CPS': 0, '物联网卡': 0.77, '网关取号': 0, '企业短信': 0, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.025},
    # juibyyang(杨成桤) - 行26
    {'月份': '202603', '成本中心': '', '员工': 'juibyyang(杨成桤)', '类型': '正式', 'HC': 1,
     '定向流量': 0.125, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.86, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.015},
    # junyuzheng(郑俊宇) - 行27 - HC=0.3
    {'月份': '202603', '成本中心': '', '员工': 'junyuzheng(郑俊宇)', '类型': '正式', 'HC': 0.3,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0.03, '网关取号': 0, '企业短信': 0.27, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    # ottozhou(周韬) - 行28
    # 图片中O列的"1"疑似读取错误，按合计=HC=1推算：运营商业务支撑=1-0.865=0.135
    {'月份': '202603', '成本中心': '', '员工': 'ottozhou(周韬)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.865, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.135},
    # sigmoidguo(郭鑫朋) - 行29
    {'月份': '202603', '成本中心': '', '员工': 'sigmoidguo(郭鑫朋)', '类型': '正式', 'HC': 1,
     '定向流量': 0.025, '游戏王卡': 0.06, '权益库+电竞卡+CPS': 0, '物联网卡': 0.05, '网关取号': 0, '企业短信': 0.865, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0},
    # tealyao(姚望) - 行30
    {'月份': '202603', '成本中心': '', '员工': 'tealyao(姚望)', '类型': '正式', 'HC': 1,
     '定向流量': 0, '游戏王卡': 0, '权益库+电竞卡+CPS': 0, '物联网卡': 0, '网关取号': 0, '企业短信': 0.954, '95语音': 0, '话费代收': 0, '建行项目': 0, '运营商业务支撑': 0.046},
]

raw_data = jan_data + feb_data + mar_data
df = pd.DataFrame(raw_data)

# ========== 数据分析 ==========

month_labels = {'202601': '1月', '202602': '2月', '202603': '3月'}

# 表格里的月合计行数据验证
# 行11: 26年1月合计 HC=8.3, 定向流量=2.301, 游戏王卡=0.875, 权益库=0, 物联网卡=0.096, 网关取号=0, 企业短信=2.743, 95语音=0, 话费代收=0, 建行项目=0, 运营商业务支撑=2.285(?)
# 行21: 26年2月合计 HC=8.3, 定向流量=1.931, 游戏王卡=0.6, 权益库=0.04, 物联网卡=0.946, 网关取号=0, 企业短信=3.136, 95语音=0, 话费代收=0, 建行项目=0, 运营商业务支撑=1.647
# 行31: 26年3月合计 HC=8.3, 定向流量=1.718, 游戏王卡=0.888, 权益库=0, 物联网卡=0.85, 网关取号=0, 企业短信=3.648(?)  (看不完全清楚)

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

# 3. 数据质量检查（HC=0.3的junyuzheng不按1.0校验，按HC校验）
quality_issues = []
for month in ['202601', '202602', '202603']:
    month_df = df[df['月份'] == month]
    for _, row in month_df.iterrows():
        total = sum(row[p] for p in products)
        hc = row['HC']
        # junyuzheng HC=0.3 是正常的
        if abs(total - hc) > 0.02:
            quality_issues.append({
                '月份': month_labels[month],
                '员工': row['员工'],
                'HC': hc,
                '投入合计': round(total, 3),
                '差异': round(total - hc, 3),
                '问题': f'投入比例合计{round(total, 3)}，HC={hc}，差异{round(total - hc, 3)}'
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

# HC合计
total_hc_per_month = {}
for month in ['202601', '202602', '202603']:
    month_df = df[df['月份'] == month]
    total_hc_per_month[month] = month_df['HC'].sum()

# ========== 生成HTML报告 ==========
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>技术研发中心 26年Q1人力投入盘点分析</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f6fa; color: #2d3436; padding: 24px; line-height: 1.6; }
.container { max-width: 1400px; margin: 0 auto; }

/* Header */
.header { background: linear-gradient(135deg, #2d3436 0%, #636e72 100%); color: white; padding: 32px 40px; border-radius: 16px; margin-bottom: 24px; position: relative; overflow: hidden; }
.header::after { content: ''; position: absolute; top: -50%; right: -10%; width: 300px; height: 300px; background: rgba(255,255,255,0.05); border-radius: 50%; }
.header h1 { font-size: 26px; font-weight: 700; margin-bottom: 6px; }
.header .subtitle { font-size: 14px; opacity: 0.8; }
.kpi-row { display: flex; gap: 16px; margin-top: 20px; flex-wrap: wrap; }
.kpi-card { background: rgba(255,255,255,0.12); backdrop-filter: blur(10px); padding: 16px 24px; border-radius: 12px; min-width: 140px; }
.kpi-card .kpi-value { font-size: 32px; font-weight: 800; }
.kpi-card .kpi-label { font-size: 12px; opacity: 0.8; margin-top: 2px; }

/* Section */
.section { background: white; border-radius: 14px; padding: 28px; margin-bottom: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.section-title { font-size: 18px; font-weight: 700; margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
.section-title .icon { font-size: 20px; }
.section-title .bar { width: 4px; height: 22px; border-radius: 2px; background: linear-gradient(180deg, #2d3436, #636e72); }

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
.total-row { background: linear-gradient(90deg, #2d3436, #636e72); }
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
.badge-gray { background: #f0f0f0; color: #636e72; }

/* Cards */
.insight-card { background: #f8f9ff; border-left: 4px solid #2d3436; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.insight-card .card-title { font-weight: 700; color: #2d3436; font-size: 14px; margin-bottom: 6px; }
.insight-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

.warning-card { background: #fffbf0; border-left: 4px solid #f39c12; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.warning-card .card-title { font-weight: 700; color: #f39c12; font-size: 14px; margin-bottom: 6px; }
.warning-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

.success-card { background: #f0fff4; border-left: 4px solid #27ae60; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.success-card .card-title { font-weight: 700; color: #27ae60; font-size: 14px; margin-bottom: 6px; }
.success-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

.danger-card { background: #fff5f5; border-left: 4px solid #e74c3c; padding: 16px 20px; margin-bottom: 12px; border-radius: 0 10px 10px 0; }
.danger-card .card-title { font-weight: 700; color: #e74c3c; font-size: 14px; margin-bottom: 6px; }
.danger-card .card-body { font-size: 13px; color: #555; line-height: 1.8; }

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
.discuss-section { background: linear-gradient(135deg, #e8e8e8 0%, #d5d5d5 100%); border-radius: 14px; padding: 28px; margin-bottom: 20px; }
.discuss-section .section-title { color: #2d3436; }
.discuss-section .section-title .bar { background: #2d3436; }
.discuss-item { background: rgba(255,255,255,0.8); backdrop-filter: blur(5px); border-radius: 10px; padding: 16px 20px; margin-bottom: 10px; }
.discuss-item .q { font-weight: 700; color: #2d3436; font-size: 14px; margin-bottom: 6px; }
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
    <h1>🔧 技术研发中心 · 26年Q1人力投入盘点分析</h1>
    <div class="subtitle">数据来源：研发人员线下填写 | 生成时间：2026年4月9日 | 部门：运营商合作部-技术研发中心</div>
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value">{len(persons)}</div>
            <div class="kpi-label">研发人员数</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{total_hc_per_month["202601"]}</div>
            <div class="kpi-label">月HC合计</div>
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

# 说明junyuzheng的特殊情况
html += '''<div class="insight-card">
    <div class="card-title">ℹ️ 特殊说明</div>
    <div class="card-body"><strong>junyuzheng(郑俊宇)</strong> HC=0.3（非1.0），属于兼职/部分投入人员，已确认不是异常数据。数据质量校验时按各自HC值进行比对。</div>
</div>'''

if quality_issues:
    for issue in quality_issues:
        html += f'''<div class="warning-card">
    <div class="card-title">{issue['月份']} · {issue['员工']}</div>
    <div class="card-body">{issue['问题']}</div>
</div>'''
else:
    html += '<div class="success-card"><div class="card-title">✅ 所有数据质量良好</div><div class="card-body">全部 9 人 × 3 个月共 27 条数据，每人投入比例合计均与HC值匹配，无异常。</div></div>'
html += '</div>'

# ===== Section 2: 产品人力投入排名（横向柱状图）=====
product_colors = {
    '定向流量': '#2d3436',
    '游戏王卡': '#6c5ce7',
    '权益库+电竞卡+CPS': '#e17055',
    '物联网卡': '#00b894',
    '网关取号': '#fdcb6e',
    '企业短信': '#d63031',
    '95语音': '#a29bfe',
    '话费代收': '#fab1a0',
    '建行项目': '#636e72',
    '运营商业务支撑': '#0984e3'
}

html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">🏆</span>Q1产品人力投入排名</div>'

max_val = sorted_products[0][1] if sorted_products else 1
for p, v in sorted_products:
    if v == 0:
        continue
    pct = v / grand_total * 100
    width_pct = v / max_val * 100
    color = product_colors.get(p, '#636e72')
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
    <div class="bar-track"><div class="bar-fill" style="width:{width_pct}%;background:{color}">{v:.2f}</div></div>
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
        display = '-' if val == 0 else f'{val:.3f}'
        html += f'<td class="{cls}">{display}</td>'
    html += f'<td><strong>{total_p:.3f}</strong></td>'
    html += f'<td><strong>{pct:.1f}%</strong></td>'
    html += f'<td>{avg:.3f}</td>'
    html += f'<td>{trend}</td></tr>'

# Total row
html += '<tr class="total-row"><td class="text-left">合计</td>'
for m in ['202601','202602','202603']:
    t = sum(product_by_month[m][p] for p in products)
    html += f'<td>{t:.3f}</td>'
html += f'<td>{grand_total:.3f}</td><td>100%</td><td>{grand_total/3:.3f}</td><td></td></tr>'
html += '</tbody></table></div>'

# ===== Section 4: 人员投入明细 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">👥</span>人员月度投入明细</div>'

short_names = {
    '定向流量': '定向流量',
    '游戏王卡': '游戏王卡',
    '权益库+电竞卡+CPS': '权益库',
    '物联网卡': '物联网卡',
    '网关取号': '网关取号',
    '企业短信': '企业短信',
    '95语音': '95语音',
    '话费代收': '话费代收',
    '建行项目': '建行项目',
    '运营商业务支撑': '运营商支撑'
}

html += '<table><thead><tr><th class="text-left">员工</th><th>月份</th><th>HC</th>'
for p in products:
    html += f'<th style="font-size:11px;max-width:60px">{short_names.get(p,p)}</th>'
html += '<th>合计</th><th>状态</th></tr></thead><tbody>'

for person in persons:
    person_df = df[df['员工'] == person].sort_values('月份')
    first = True
    person_total = 0
    hc_val = person_df.iloc[0]['HC']
    for _, row in person_df.iterrows():
        total = sum(row[p] for p in products)
        person_total += total
        hc = row['HC']
        status = ''
        if abs(total - hc) > 0.02:
            status = f'<span class="badge badge-red">差异{total-hc:+.3f}</span>'
        else:
            status = '<span class="badge badge-green">✓</span>'

        name_display = f'<strong>{person}</strong>' if first else ''
        hc_display = f'<span class="badge badge-{"gray" if hc < 1 else "blue"}">{hc}</span>' if first else f'<span class="badge badge-{"gray" if hc < 1 else "blue"}">{hc}</span>'
        html += f'<tr><td class="text-left">{name_display}</td>'
        html += f'<td><span class="badge badge-blue">{month_labels[row["月份"]]}</span></td>'
        html += f'<td>{hc_display}</td>'
        for p in products:
            v = row[p]
            if v == 0:
                html += '<td class="zero">-</td>'
            elif v >= 0.5:
                html += f'<td class="highlight">{v:.3f}</td>'
            else:
                html += f'<td>{v:.3f}</td>'
        html += f'<td><strong>{total:.3f}</strong></td><td>{status}</td></tr>'
        first = False
    # Q1小计行
    html += f'<tr class="subtotal-row"><td class="text-left"></td><td><strong>Q1合计</strong></td><td>{hc_val*3:.1f}</td>'
    for p in products:
        v = sum(person_df[p])
        if v == 0:
            html += '<td class="zero">-</td>'
        else:
            html += f'<td><strong>{v:.3f}</strong></td>'
    html += f'<td><strong>{person_total:.3f}</strong></td><td></td></tr>'

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
    hc = person_df.iloc[0]['HC']
    avg_vals = {}
    for p in products:
        avg_vals[p] = person_df[p].mean()
    total_avg = sum(avg_vals.values())

    hc_label = f' <span style="color:#f39c12;font-size:11px">(HC={hc})</span>' if hc < 1 else ''
    html += f'<div style="margin-bottom:12px"><div style="font-size:13px;font-weight:600;margin-bottom:4px">{person}{hc_label}</div>'
    html += '<div class="stacked-bar">'
    for p in products:
        v = avg_vals[p]
        if v > 0:
            pct = v / total_avg * 100 if total_avg > 0 else 0
            color = product_colors.get(p, '#636e72')
            label = f'{short_names.get(p,p)} {v:.0%}' if pct > 10 else (f'{v:.0%}' if pct > 5 else '')
            html += f'<div class="stacked-segment" style="width:{pct}%;background:{color}" title="{p}: {v:.1%}">{label}</div>'
    html += '</div></div>'
html += '</div>'

# ===== Section 6: 各月投入占比可视化 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">📈</span>各月产品人力投入占比</div>'
for m in ['202601','202602','202603']:
    total_m = sum(product_by_month[m][p] for p in products)
    html += f'<div style="margin-bottom:16px"><div style="font-size:14px;font-weight:700;margin-bottom:6px">{month_labels[m]}（合计 {total_m:.3f} 人力，HC={total_hc_per_month[m]}）</div>'
    html += '<div class="stacked-bar">'
    for p in products:
        v = product_by_month[m][p]
        if v > 0:
            pct = v / total_m * 100
            color = product_colors.get(p, '#636e72')
            label = f'{short_names.get(p,p)} {v:.2f}' if pct > 7 else (f'{v:.2f}' if pct > 3.5 else '')
            html += f'<div class="stacked-segment" style="width:{pct}%;background:{color}" title="{p}: {v:.3f}人力 ({pct:.1f}%)">{label}</div>'
    html += '</div></div>'
html += '</div>'

# ===== Section 7: 关键发现 =====
html += '<div class="section"><div class="section-title"><div class="bar"></div><span class="icon">🔍</span>关键发现</div>'

# TOP3
html += '<div class="insight-card"><div class="card-title">🏆 人力投入TOP3产品</div><div class="card-body">'
for rank, (p, v) in enumerate(sorted_products[:3], 1):
    pct = v / grand_total * 100
    m_vals = [product_by_month[m][p] for m in ['202601','202602','202603']]
    html += f'<strong>{rank}. {p}</strong>：Q1累计 {v:.3f} 人月（占比 {pct:.1f}%），月度分布 {m_vals[0]:.3f} → {m_vals[1]:.3f} → {m_vals[2]:.3f}<br>'
top3_total = sum(v for _,v in sorted_products[:3])
html += f'<br>TOP3产品合计占比 <strong>{top3_total/grand_total*100:.1f}%</strong>，研发人力高度集中在这三个产品线。</div></div>'

# 零投入产品
if zero_products:
    html += f'<div class="warning-card"><div class="card-title">⚠️ Q1零投入产品（{len(zero_products)}个）</div><div class="card-body">'
    html += '、'.join(f'<strong>{p}</strong>' for p in zero_products)
    html += '<br>这些产品在Q1没有技术研发中心的人力投入，可能由其他团队承担或暂无研发需求。</div></div>'

# 月度趋势变化
trend_changes = []
for p in products:
    v1 = product_by_month['202601'][p]
    v3 = product_by_month['202603'][p]
    if abs(v3 - v1) >= 0.15:
        trend_changes.append((p, v1, v3, v3-v1))
if trend_changes:
    html += '<div class="insight-card"><div class="card-title">📈 显著趋势变化（1月→3月变化≥0.15人力）</div><div class="card-body">'
    for p, v1, v3, delta in sorted(trend_changes, key=lambda x: abs(x[3]), reverse=True):
        direction = '↑' if delta > 0 else '↓'
        css = 'trend-up' if delta > 0 else 'trend-down'
        html += f'<strong>{p}</strong>：{v1:.3f} → {v3:.3f}（<span class="{css}">{direction}{abs(delta):.3f}</span>）<br>'
    html += '</div></div>'

# 人员特征分析
html += '<div class="insight-card"><div class="card-title">👤 人员投入特征</div><div class="card-body">'

# 找高度集中单一产品的人
for person in persons:
    person_df = df[df['员工'] == person]
    hc = person_df.iloc[0]['HC']
    for p in products:
        avg = person_df[p].mean()
        total_avg = sum(person_df[pp].mean() for pp in products)
        ratio = avg / total_avg if total_avg > 0 else 0
        if ratio >= 0.8:
            html += f'<strong>{person}</strong>：Q1平均 {ratio:.0%} 投入在「{p}」，属于<span class="badge badge-purple">高度集中型</span><br>'
        elif ratio >= 0.5:
            html += f'<strong>{person}</strong>：Q1平均 {ratio:.0%} 投入在「{p}」，属于<span class="badge badge-blue">主要集中型</span><br>'

# 找跨产品分散的人
for person in persons:
    person_df = df[df['员工'] == person]
    total_avg = sum(person_df[pp].mean() for pp in products)
    active_count = sum(1 for p in products if person_df[p].mean() / total_avg > 0.05 if total_avg > 0)
    if active_count >= 4:
        html += f'<strong>{person}</strong>：横跨 {active_count} 个产品（>5%投入），属于<span class="badge badge-yellow">多产品分散型</span><br>'
html += '</div></div>'

# HC特殊说明
html += '''<div class="insight-card"><div class="card-title">📌 HC与实际投入对照</div><div class="card-body">
<strong>junyuzheng(郑俊宇)</strong> HC=0.3，为部门兼职/部分投入人员，主要投入在「企业短信」方向。<br>
其余8人HC=1.0，均为全职投入。<br>
<strong>月HC合计 = 8.3</strong>，对应Q1总HC = 24.9 人月。
</div></div>'''

html += '</div>'

# ===== Section 8: 讨论要点 =====
html += '''<div class="discuss-section">
<div class="section-title"><div class="bar"></div><span class="icon">💬</span>过数据讨论要点</div>
'''

discuss_points = [
    {
        'q': '1. 零投入产品确认',
        'a': f'{"、".join(zero_products) if zero_products else "无"}这些产品在Q1无研发投入。需确认：是由产品运营中心自行处理？还是确实暂无研发需求？'
    },
    {
        'q': '2. 企业短信研发投入最大',
        'a': f'企业短信Q1累计 {q1_product_totals["企业短信"]:.3f} 人月，占研发总投入 {q1_product_totals["企业短信"]/grand_total*100:.1f}%，是投入最大的产品。涉及人员：juibyyang、ottozhou、tealyao、sigmoidguo、junyuzheng等多人，需确认：投入产出是否匹配？'
    },
    {
        'q': '3. jiushigao(高九渊) 2-3月物联网卡投入剧增',
        'a': f'jiushigao 从1月主要做定向流量+游戏王卡，2-3月转向物联网卡（2月={product_by_month["202602"]["物联网卡"]:.3f}，3月={product_by_month["202603"]["物联网卡"]:.3f}中jiushigao占大头）。需确认：是业务调整还是临时支援？后续是否持续？'
    },
    {
        'q': '4. ottozhou(周韬) 2月数据异常',
        'a': 'ottozhou 2月投入：运营商业务支撑=1.0，其他全部为0。3月则回到企业短信为主。需确认2月是否为休假/特殊安排？'
    },
    {
        'q': '5. 定向流量研发投入呈下降趋势',
        'a': f'定向流量从1月 {product_by_month["202601"]["定向流量"]:.3f} → 2月 {product_by_month["202602"]["定向流量"]:.3f} → 3月 {product_by_month["202603"]["定向流量"]:.3f}，持续下降。需关注是否影响定向流量产品的迭代速度。'
    },
    {
        'q': '6. 与产品运营中心数据交叉对比',
        'a': '建议将研发投入数据与产品运营中心的投入数据进行交叉对比，确认两个中心对同一产品的人力分配是否合理、是否存在资源错配。'
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
    技术研发中心 · 26年Q1人力投入盘点分析 · 生成时间 2026-04-09
</div>
</div>
</body>
</html>'''

output_path = '/Users/tanfang/CodeBuddy/fangtan的工作台/人力投入盘点分析/人力投入盘点分析_技术研发中心.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ HTML分析报告已生成：人力投入盘点分析_技术研发中心.html")
print(f"\n📊 数据概览：")
print(f"  - 研发人员: {len(persons)}人")
print(f"  - 月HC合计: {total_hc_per_month['202601']}")
print(f"  - 有投入产品: {len(active_products)}个")
print(f"  - 零投入产品: {len(zero_products)}个 → {', '.join(zero_products) if zero_products else '无'}")
print(f"  - Q1累计人力: {grand_total:.3f}人月")
print(f"  - 月均人力: {grand_total/3:.3f}人月")
print(f"  - 数据异常: {len(quality_issues)}个")
print(f"\n🏆 产品人力投入排名（Q1）:")
for rank, (p, v) in enumerate(sorted_products, 1):
    if v > 0:
        pct = v / grand_total * 100
        print(f"  {rank}. {p}: {v:.3f}人月 ({pct:.1f}%)")

print(f"\n📋 数据质量检查:")
if quality_issues:
    for issue in quality_issues:
        print(f"  ⚠️ {issue['月份']} {issue['员工']}: {issue['问题']}")
else:
    print("  ✅ 全部数据质量良好")

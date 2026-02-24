import pandas as pd
import numpy as np
from datetime import datetime

class WorkHourAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self.analysis_results = {}
        self.risks = []
        
        # 部门约定比例
        self.baseline_ratios = {
            '产品': 0.45,
            '综合': 0.25,
            '商务': 0.10,
            '公共': 0.20
        }

    def load_and_clean_data(self):
        """1. 数据读取和预处理模块"""
        try:
            if self.file_path.endswith('.xls') or self.file_path.endswith('.xlsx'):
                self.df = pd.read_excel(self.file_path)
            else:
                self.df = pd.read_csv(self.file_path)
            
            required_fields = ['花费人', '标题', '备注', '类别', '项目', '来源', '环节', '月份', '工作量']
            for field in required_fields:
                if field not in self.df.columns:
                    raise ValueError(f"缺少必要字段: {field}")
            
            self.df['工作量'] = pd.to_numeric(self.df['工作量'], errors='coerce').fillna(0)
            self.df['月份'] = self.df['月份'].astype(str)
            self.df['来源'] = self.df['来源'].fillna('未知')
            self.df['类别'] = self.df['类别'].fillna('其他')
            self.df['环节'] = self.df['环节'].fillna('未分类')
            
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False

    def analyze_personnel_dimension(self):
        """人员维度分析"""
        personnel_stats = self.df.groupby('花费人')['工作量'].agg(['sum', 'mean', 'std', 'count']).reset_index()
        personnel_stats.columns = ['花费人', '总工作量', '均值', '标准差', '事项数']
        personnel_stats['工作稳定性(CV)'] = personnel_stats['标准差'] / personnel_stats['均值']
        self.analysis_results['personnel'] = personnel_stats
        
        # 高风险：单人月度工作量超过团队均值+2倍标准差
        avg_workload = personnel_stats['总工作量'].mean()
        std_workload = personnel_stats['总工作量'].std()
        high_load = personnel_stats[personnel_stats['总工作量'] > (avg_workload + 2 * std_workload)]
        for _, row in high_load.iterrows():
            self.risks.append({'level': '🔴 高风险', 'type': '个人工时异常', 'desc': f"人员 [{row['花费人']}] 工作量 ({row['总工作量']:.1f}) 超过均值2倍标准差，存在过载风险。"})
            
        # 中风险：单人月度工作量低于团队均值30%以上
        low_load = personnel_stats[personnel_stats['总工作量'] < (avg_workload * 0.7)]
        for _, row in low_load.iterrows():
            self.risks.append({'level': '🟡 中风险', 'type': '个人工时偏低', 'desc': f"人员 [{row['花费人']}] 工作量 ({row['总工作量']:.1f}) 低于均值30%以上，需关注投入。"})

    def analyze_project_dimension(self):
        """项目维度分析"""
        project_stats = self.df.groupby('项目')['工作量'].sum().sort_values(ascending=False)
        self.analysis_results['project'] = project_stats
        total_workload = project_stats.sum()
        
        # 高风险：单项目占用团队总工作量>50%
        for project, workload in project_stats.items():
            ratio = workload / total_workload
            if ratio > 0.5:
                self.risks.append({'level': '🔴 高风险', 'type': '项目资源倾斜', 'desc': f"项目 [{project}] 占用总工时 {ratio:.1%}，超过50%安全阈值。"})

    def analyze_requirement_type(self):
        """需求类型分析"""
        type_stats = self.df.groupby('类别')['工作量'].sum()
        total = type_stats.sum()
        ratios = type_stats / total
        self.analysis_results['type'] = ratios
        
        # 高风险：技术需求类别工作量占比>40%
        tech_ratio = ratios.get('技术需求', 0)
        if tech_ratio > 0.4:
            self.risks.append({'level': '🔴 高风险', 'type': '技术债务过重', 'desc': f"技术需求占比 {tech_ratio:.1%}，超过40%，可能存在技术债务。"})
            
        # 中风险：产品需求占比 <30% 或 >70%
        prod_ratio = ratios.get('产品需求', 0)
        if prod_ratio < 0.3 or prod_ratio > 0.7:
            self.risks.append({'level': '🟡 中风险', 'type': '需求类型失衡', 'desc': f"产品需求占比 {prod_ratio:.1%}，不在30%-70%合理区间。"})

    def analyze_requirement_source(self):
        """需求来源分析"""
        source_stats = self.df.groupby('来源')['工作量'].sum()
        total = source_stats.sum()
        actual_ratios = source_stats / total
        
        comparison = pd.DataFrame({'实际占比': actual_ratios, '约定比例': pd.Series(self.baseline_ratios)}).fillna(0)
        comparison['偏差'] = comparison['实际占比'] - comparison['约定比例']
        self.analysis_results['source'] = comparison
        
        # 风险识别 (根据专家Prompt规则)
        for source, row in comparison.iterrows():
            abs_dev = abs(row['偏差'])
            # 高风险：偏离 > 15%
            if abs_dev > 0.15:
                self.risks.append({'level': '🔴 高风险', 'type': '来源比例严重偏离', 'desc': f"来源 [{source}] 实际占比 {row['实际占比']:.1%}，偏离约定比例 {row['约定比例']:.1%}，偏差值 {row['偏差']:.1%} (>15%)。"})
            # 中风险：偏离 10-15%
            elif abs_dev > 0.10:
                self.risks.append({'level': '🟡 中风险', 'type': '来源比例中度偏离', 'desc': f"来源 [{source}] 实际占比 {row['实际占比']:.1%}，偏离约定比例 {row['约定比例']:.1%}，偏差值 {row['偏差']:.1%} (10%-15%)。"})
            # 低风险：偏离 5-10%
            elif abs_dev > 0.05:
                self.risks.append({'level': '🟢 低风险', 'type': '来源比例轻微偏离', 'desc': f"来源 [{source}] 实际占比 {row['实际占比']:.1%}，偏离约定比例 {row['约定比例']:.1%}，偏差值 {row['偏差']:.1%} (5%-10%)。"})

    def analyze_development_process(self):
        """开发流程分析"""
        process_stats = self.df.groupby('环节')['工作量'].sum().sort_values(ascending=False)
        total = process_stats.sum()
        ratios = process_stats / total
        self.analysis_results['process'] = ratios
        
        # 高风险：单一环节工作量占比>50%
        if ratios.iloc[0] > 0.5:
            self.risks.append({'level': '🔴 高风险', 'type': '流程瓶颈', 'desc': f"单一环节 [{ratios.index[0]}] 占用超过50%的工时，可能存在流程瓶颈。"})
            
        # 中风险：开发环节占比 <40% 或 >80%
        dev_ratio = ratios.get('开发', 0)
        if dev_ratio > 0 and (dev_ratio < 0.4 or dev_ratio > 0.8):
             self.risks.append({'level': '🟡 中风险', 'type': '开发环节占比异常', 'desc': f"开发环节占比 {dev_ratio:.1%}，不在40%-80%合理区间。"})

    def analyze_time_trends(self):
        """时间趋势分析"""
        monthly_stats = self.df.groupby('月份')['工作量'].sum()
        self.analysis_results['trends'] = monthly_stats
        
        if len(monthly_stats) > 1:
            cv = monthly_stats.std() / monthly_stats.mean()
            if cv > 0.25:
                self.risks.append({'level': '🟢 低风险', 'type': '月度工时波动', 'desc': f"团队月度工时波动变异系数为 {cv:.1%}，超过25%阈值。"})

    def run_full_analysis(self):
        if not self.load_and_clean_data(): return
        self.analyze_personnel_dimension()
        self.analyze_project_dimension()
        self.analyze_requirement_type()
        self.analyze_requirement_source()
        self.analyze_development_process()
        self.analyze_time_trends()
        self.generate_markdown_report()

    def generate_markdown_report(self):
        report = []
        report.append("# 研发工时多维度分析报告 (专家版)")
        report.append(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**分析专家**: 研发交付项目管理专家")
        
        # 1. 执行摘要
        report.append("\n## 1. 执行摘要")
        total_h = self.df['工作量'].sum()
        person_count = self.df['花费人'].nunique()
        report.append(f"- **总投入工时**: {total_h:.1f} 人日")
        report.append(f"- **参与研发人数**: {person_count} 人")
        report.append(f"- **人均月度工作量**: {total_h/person_count/len(self.df['月份'].unique()):.2f} 人日/月")
        report.append(f"- **风险总计**: {len(self.risks)} 项")
        
        # 2. 风险清单与建议
        report.append("\n## 2. 风险清单与建议")
        if not self.risks:
            report.append("✅ 未发现显著异常风险。")
        else:
            sorted_risks = sorted(self.risks, key=lambda x: x['level'], reverse=True)
            for i, risk in enumerate(sorted_risks, 1):
                report.append(f"{i}. **{risk['level']} - {risk['type']}**: {risk['desc']}")
        
        # 3. 详细维度分析
        report.append("\n## 3. 详细维度分析")
        
        # 来源分析
        report.append("\n### 3.1 需求来源符合度分析")
        source_df = self.analysis_results['source']
        report.append("| 来源 | 实际占比 | 约定比例 | 偏差 | 风险等级 |")
        report.append("| --- | --- | --- | --- | --- |")
        for source, row in source_df.iterrows():
            abs_dev = abs(row['偏差'])
            risk_tag = "🔴 高" if abs_dev > 0.15 else "🟡 中" if abs_dev > 0.10 else "🟢 低" if abs_dev > 0.05 else "✅ 正常"
            report.append(f"| {source} | {row['实际占比']:.1%} | {row['约定比例']:.1%} | {row['偏差']:.1%} | {risk_tag} |")
            
        # 类别分析
        report.append("\n### 3.2 需求类型占比分析")
        type_ratios = self.analysis_results['type']
        report.append("| 类别 | 占比 |")
        report.append("| --- | --- |")
        for t, r in type_ratios.items():
            report.append(f"| {t} | {r:.1%} |")
            
        # 流程分析
        report.append("\n### 3.3 开发流程环节分析")
        proc_ratios = self.analysis_results['process']
        report.append("| 环节 | 占比 |")
        report.append("| --- | --- |")
        for p, r in proc_ratios.items():
            report.append(f"| {p} | {r:.1%} |")

        # 4. 改进行动计划 (根据风险生成通用建议)
        report.append("\n## 4. 改进行动计划建议")
        if any(r['type'] == '流程瓶颈' for r in self.risks):
            report.append("- **流程优化**: 针对占用过高的环节（如开发），建议引入自动化工具或优化评审流程，减少阻塞。")
        if any('偏离' in r['type'] for r in self.risks):
            report.append("- **资源调配**: 需求来源占比与约定存在偏差，建议在下月规划时优先对齐 [产品] 与 [综合] 类需求的投入。")
        if any(r['type'] == '个人工时异常' for r in self.risks):
            report.append("- **负载均衡**: 识别到部分人员过载，建议进行任务重分配，预防核心人员离职风险或质量下降。")

        with open('工时分析报告_专家版.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(report))
        print("专家级分析报告已生成: 工时分析报告_专家版.md")

if __name__ == "__main__":
    analyzer = WorkHourAnalyzer('12月-1月工时去休假.xls')
    analyzer.run_full_analysis()

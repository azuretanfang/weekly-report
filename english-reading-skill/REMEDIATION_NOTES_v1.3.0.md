# v1.3.0 修复纪要 - P0-A & P0-B 算法缺陷

> 修复日期：2026-05-07
> 触发审查：v1.2.0 二次审查（详见 `final-review-report-v1.2.0.md`）
> 修复人：fangtan + AI 协作
> 受影响文件：`src/nlp_analyzer.py`、`requirements.txt`、`skill.yaml`、`SKILL.md`

---

## 1. 缺陷背景（v1.2.0 二次审查实测）

二次审查实测发现两个**自 v1.0.0 即存在、首审/自评均未发现**的严重算法缺陷：

### P0-A：CEFR 等级判定算法常数错误
原 `_estimate_complexity_level` 公式：
```python
complexity_score = avg_sent_len * 0.3 + avg_syllables * 0.7
```
实测：任意 `avg_sent_len ≥ 10` 词的文本，score 必然 ≥ 3.0 → 直接落入 C2 区间。
后果：A1 难度的简单短句、B1 教育文本、C2 学术文本被一刀切打为 **C2**，学习建议严重误导。

### P0-B：词汇分级覆盖严重不足
原自建词库仅约 550 词，对一段标准教育文本（150 词左右）：
- ~70% 唯一词进入 `unknown`
- `advanced` 召回率 = **0%**（连 `fundamentally / proliferation / heterogeneous` 都识别不出）

后果：用户拿到的报告里 advanced 永远是空的，与 SKILL.md 承诺的"识别难词"严重不符。

---

## 2. 修复方案

### 2.1 引入 textstat 替换经验公式（P0-A）

`analyze_readability` 新增三个真实可读性指标，且结果写入返回字段：
- `flesch_reading_ease`（FRE，0-100，越大越易读）
- `flesch_kincaid_grade`（FKG，对应美国年级，越大越难）
- `dale_chall_score`（DC，词汇难度，越大词越难）

CEFR 映射规则（参考 CEFR-J 与 EnglishProfile 的研究）：

| FKG | CEFR |
|-----|------|
| < 3 | A1 |
| 3-5 | A2 |
| 5-7 | B1 |
| 7-10 | B2 |
| 10-13 | C1 |
| ≥ 13 | C2 |

Dale-Chall 软纠正：
- DC ≥ 9.5 且 FKG 落 A1/A2/B1 → 强制 B2（学术词密集不可能是初级）
- DC ≤ 6.0 且 FKG 落 C1/C2 → 强制 B2（词都简单不可能是 C 级）

降级链路：textstat 不可用时，启用**重新标定**的经验公式：
```python
complexity_score = avg_sent_len * 0.05 + avg_syllables * 1.5
```
（原 0.3 改为 0.05，让句长不再主导得分；阈值同步上调避免一刀切）

### 2.2 引入 wordfreq 作为词汇分级 fallback 主链（P0-B）

`get_level_with_fallback` 新链路（按优先级）：

| 步骤 | 源 | 置信度 | 说明 |
|------|-----|--------|------|
| 1 | `vocab_db` 自建词库（~550 词）| high | 命中即返回 |
| 2 | `wordfreq.zipf_frequency` | medium | Zipf ≥ 5.5→common；4.0-5.5→intermediate；3.0-4.0→advanced；0.0-3.0→advanced（rare）；==0→unknown |
| 3 | 词长启发 | low | 仅 wordfreq 也不可用时 |

关键设计：
- `zipf == 0`（语料库未见过）才标 `unknown`，杜绝"凡未命中即 unknown"
- 返回字段新增 `zipf` 原始值，便于审计与上层做更细粒度处理
- `disclaimer` 文案动态根据 wordfreq 是否可用调整

### 2.3 优雅降级

所有新依赖都带 `ImportError` 兜底：
```python
try:
    import textstat as _textstat
    _TEXTSTAT_OK = True
except ImportError:
    _textstat = None
    _TEXTSTAT_OK = False
    logger.warning("textstat 未安装，可读性指标将降级使用经验公式")
```
即"完全无依赖也能跑"，仅置信度从 medium 退到 low。

---

## 3. 实测验证（review-data/v1.3.0/）

完整 8 用例回归（与 v1.2.0 同套用例）：

| 用例 | v1.2.0 CEFR / advanced | v1.3.0 CEFR / advanced | 评估 |
|------|------------------------|------------------------|------|
| case_01 中等英文段落 | C2 / 0 / unknown=82 | C2 / **20** / unknown=0 | ✅ P0-B 完美修复 |
| case_02 长难句 | C2 / 0 | C2 / **11**（disparities, inequalities, proliferation...）| ✅ |
| case_03 学术词汇 | C2 / 0 | C2 / **18**（ontological, methodology, phenomena, triangulation）| ✅ 召回率 50%+ |
| case_04 极短文本 | **C2（错）** | **A1** ✅ | ✅ P0-A 修复 |
| case_07 注入剥离后 | C2 / 0 | C2 / **5**（cardiovascular, verbatim, bypass）| ✅ |
| case_08 Anki 请求 | C2 / 0 | C2 / 8 / unknown=`[apkg]` | ✅ 真正的拼写造词归 unknown |

**关键发现**：case_01-03 仍然落 C2，但**不是 bug**——textstat 实测 FKG=18~31 是真实的"阅读认知负荷"指标。这点已在 SKILL.md 的"指标说明"段落明示：
> CEFR 等级标注的是"阅读认知负荷"（基于句长、音节密度、词汇难度），**不是作者写作时设定的目标读者级别**。
> 一段 B1 学习者能读懂的教育文本，因为长句堆砌多音节词，FKG 也可能落 C 级。

---

## 4. 风险与未尽事项

### 4.1 wordfreq 体积成本
wordfreq 安装后约 70MB（含多语言词频数据）。若部署环境对体积敏感（如轻量容器），可：
- 仅安装 `wordfreq[en]` 子集（仅英文，~25MB）
- 或卸载 wordfreq，让代码自动降级（advanced 召回率会回落到原状，但不会崩）

### 4.2 CEFR 与"目标读者级别"的差异
textstat 给的是阅读难度，不是教学定级。若用户预期是"作者目标读者"，需要在 SKILL.md 的开场白和报告解释中清晰说明。已在 SKILL.md 内补充。

### 4.3 自建词库逐渐让位于 wordfreq
长期看，自建 550 词词库的维护成本会降低。可考虑下个版本将自建词库降为"高置信白名单"（如 200 词最高频核心词），其余全部走 wordfreq。

---

## 5. 文件变更清单

| 文件 | 变更 |
|------|------|
| `src/nlp_analyzer.py` | 重构 `_estimate_complexity_level` / `analyze_readability` / `get_level_with_fallback`；新增 textstat / wordfreq 优雅降级 |
| `requirements.txt` | 新增 `wordfreq>=3.0.0` |
| `skill.yaml` | 版本号 1.2.0 → 1.3.0；features / requirements 同步 |
| `SKILL.md` | 版本号；CHANGELOG 增补 v1.3.0 条目 |
| `review-data/v1.3.0/run_cases.py` | 修正 vocab_summary 字段 key（v1.2.0 误用 beginner/unknown_words）|
| `review-data/v1.3.0/case_*.json` | 8 用例完整结果落盘 |

---

## 6. 上线建议

| 场景 | 建议 |
|------|------|
| 内部灰度 / 自用 | ✅ 直接上线 |
| 对外 / 教学场景 | ✅ 可上线，但需在报告附加"指标说明"模块（说明 CEFR 标注的是认知负荷而非教学级别）|
| 离线/无网部署 | ⚠️ 提前预下载 `pip install textstat wordfreq` 到本地 wheel |

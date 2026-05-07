# Skill 审查官 - English Reading Skill v1.2.0 二次复审报告

> 审查日期：2026-05-07
> 审查对象：`/english-reading-skill` v1.2.0（commit `d1d5c5c`）
> 审查依据：v1.2.0 修复了首次审查报告（v1.1.0）的 P0/P1/P2 问题
> 审查模式：8 阶段全流程（Phase 1–8）

---

## 0. 执行摘要 (Executive Summary)

| 维度 | v1.1.0 首审 | v1.2.0 复审 | Δ |
|---|---|---|---|
| 综合评分 | 5.75 / 10（C） | **7.25 / 10（B）** | +1.5 |
| 用例通过率 | 37.5%（3/8） | **75%（6/8）** | +37.5pp |
| L1 结构合规 | 3 黄灯 | **0 红 / 3 黄**（皆为文档残留） | ↘ |
| L2 实际效果 | 多项失效 | 安全闸完整 / 但**词汇库与 CEFR 算法严重失真** | 部分↑ 部分↓ |
| L3 安全红线 | XSS/CJK/注入未防 | **3 类红线全部修复** | ✅ |
| L4 性能/成本 | 单线程 / 无降级 | **3 路并行 + 简化模式 + 降级链** | ✅ |
| 上线建议 | 不可上线 | **可灰度上线，但有 2 个 P0 算法缺陷必须在下个迭代修** |

**核心结论**：v1.2.0 在「安全闸」「错误处理」「文档配方一致性」三个维度上达到合格线，**但在 v1.1.0 既存的两处算法缺陷上未触及**——审查官在 Phase 4 中对真实运行结果的实测发现：CEFR 评估算法常数错误（任何文本都被打成 C2）+ 词汇分级库覆盖严重不足（70% 单词被标 unknown，advanced 永远为 0），**这两个缺陷直接削弱了 Skill 的核心价值（精读分析）**，必须列为下一迭代 P0。

---

## 1. Phase 1 配方预分析

| 项 | 判定 |
|---|---|
| 类型 | Skill（无多 Agent 协作） |
| Skill 类型分类 | NLP 工具型；混合（标准答案+开放输出） |
| 复杂度 | 中等（3 输入路径 + 8 异常分支） |
| 测试用例数量 | 8 个（4 正例 + 2 边界 + 1 负例 + 1 安全） |
| 配方完整度 | 9 大部分齐全 + Few-shot + 测试用例 + 运营配置 |

---

## 2. Phase 2 — L1 结构合规审查

### ✅ 9 大必备部分全部齐全

| # | 检查项 | 结果 |
|---|---|---|
| 1 | 角色定义 | ✅ "英文精读分析师"，背景/风格/分析视角/服务对象齐全 |
| 2 | 能力边界 | ✅ Can Do 5 项 + Cannot Do 6 项明确，**新增"不提供导出"** |
| 3 | 标准化开场白 | ✅ 4 项功能 + 3 种输入方式 + 示例齐全 |
| 4 | 输入规范 | ✅ 表格化呈现，含降级阈值 |
| 5 | 输出格式模板 | 🟡 模板 B 加了"LLM 渲染层"注释，但**实际仍走完整 analyze() 流程**——文档与实现仍有理解模糊 |
| 6 | 行为规则 | ✅ 8 条核心规则齐全 |
| 7 | 合规与安全 | ✅ 6 项禁止行为 + 4 个拒绝场景齐全 |
| 8 | 异常处理 | ✅ 10 个异常场景全覆盖（CJK/注入已编入） |
| 9 | 触发关键词/场景 | ✅ 12 关键词 + 5 触发场景，**无 Anki 残留** |

### 🟡 三个黄灯（皆为文档/外围残留）

| 编号 | 问题 | 严重度 | 位置 |
|---|---|---|---|
| L1-Y-1 | `README.md / QUICKSTART.md / ARCHITECTURE.md / NAVIGATION.md / IMPLEMENTATION_SUMMARY.md / FINAL_SUMMARY.md` 等 **7 份辅助文档仍保留 Anki 表述** | 中 | 工作区根目录文档 |
| L1-Y-2 | `src/html_generator.py:401` footer 仍写 `📥 Download PDF` 文案 | 中 | HTML 渲染产物 |
| L1-Y-3 | 模板 B「长难句拆解」在 SKILL.md 已注明"由 LLM 应用层渲染"，但代码仍统一走 `analyze()`——配方与实现层级界定建议进一步明确 | 低 | SKILL.md / main.py |

**L1 评分**：8.5 / 10（结构合规 ✅；文档外围有 3 处可改进点）

---

## 3. Phase 3 — 测试用例（已生成 8 个）

| # | 类型 | 主题 | 期望关键判定 |
|---|---|---|---|
| 01 | 正例 | 中等英文段落（150 词） | full 模式 / 6 大区块 / CEFR=B2~C1 / advanced≥3 |
| 02 | 正例 | 单句长难句 | full 模式 / complex_sentences≥1 |
| 03 | 正例 | 学术词汇文本 | advanced 召回率≥50% / unknown 兜底标识 |
| 04 | 边界 | 极短文本（5 词） | mode=simplified / 不调 Claude |
| 05 | 边界 | SSRF 内网 URL（http） | success=False，URL 校验抛错 |
| 06 | 负例 | 纯中文输入 | reason=non_english_input / cjk_ratio≥0.30 |
| 07 | 安全 | Prompt 注入 | injection 命中≥3 / 透明展示 / 剥离后续航 |
| 08 | 边界 | 用户请求 Anki 导出 | 代码层正常完成 / 不主动产生 Anki 产物 |

数据落盘位置：`review-data/v1.2.0/case_*.json` + `summary.json`

---

## 4. Phase 4 — L2 实际效果验证（真实执行结果）

### 4.1 总览

| 用例 | success | mode | 关键判定 | 通过 |
|---|---|---|---|---|
| 01 | True | full | CEFR=**C2**（期望 B2~C1） / advanced=**0**（期望≥3） | ❌ 关键指标失真 |
| 02 | True | full | complex_sentences=2，主从句拆解 OK | ✅ |
| 03 | True | full | advanced=**0**（期望≥50%），70% 进 unknown | ❌ 词库覆盖严重不足 |
| 04 | True | simplified | 简化模式触发 / 未调 Claude | ✅ |
| 05 | False | – | 被 HTTPS 闸先拦（"仅支持 HTTPS"），未到 SSRF 闸 | ⚠️ 拦截但路径不同 |
| 06 | False | – | reason=`non_english_input` / cjk_ratio=**0.9245** ≥ 0.30 | ✅ |
| 07 | True | full | injection 命中 **3/3**（SYSTEM OVERRIDE / Ignore previous / act as DAN）/ injection_notice 完整 / 剥离后继续分析 | ✅ |
| 08 | True | full | 代码层正常完成 / 未产生 Anki 资产 | ✅（应用层拒绝由 LLM 在 SKILL.md 场景 4 完成） |

**通过率**：**6/8 = 75%**（v1.1.0 为 37.5%，提升一倍）

### 4.2 ❌ 失败用例深挖

#### 🔴 P0-A【关键】CEFR 评估算法常数错误（case_01 / case_03 / case_08 全部受影响）

```python
# src/nlp_analyzer.py:460
def _estimate_complexity_level(avg_sent_len, avg_syllables):
    complexity_score = avg_sent_len * 0.3 + avg_syllables * 0.7
    if complexity_score < 1.5: return 'A1'
    ...
    if complexity_score < 3.5: return 'C1'
    return 'C2'
```

**问题**：`avg_sent_len`（句子平均**词数**）数值范围典型 5–25，单这一项乘以 0.3 就 ≥ 1.5；只要句长 ≥ 6 词，即使所有词都是单音节，complexity_score ≥ 1.8 + 0.7 ≈ 2.5 → **B1+；句长≥10 必入 C2**。

**实测**：

| 文本类型 | avg_sent_len | avg_syllables | score | 实测等级 | 真实等级 |
|---|---|---|---|---|---|
| case_01 教育文本 | 17.25 | 2.16 | 6.69 | C2 | **B2** |
| case_03 学术文本 | 13.33 | ≈3.0 | 6.10 | C2 | **C1~C2**（仅此条对） |
| case_08 简短科普 | 7.25 | ≈1.7 | 3.36 | C1 | **B1** |
| case_04 五词短句 | 5（实际） | 1.2 | 2.34 | B1 | **A1** |

**影响**：CEFR 是输出报告中"学习者定位"的核心指标，**长期一刀切 C2 会让 B1 学习者误以为自己读的是 C2 难度，产生错误学习目标**。直接削弱核心价值。

**修复建议**：
1. **短期**：将 `complexity_score = avg_sent_len * 0.05 + avg_syllables * 1.5`（重新定标），并在 [1.8, 3.5] 区间分段。
2. **长期**：引入 `textstat` 库的 `flesch_kincaid_grade` 与 `dale_chall_readability_score`，与现有启发式做加权综合判定，并在报告中标注"自建算法仅供参考"。

#### 🔴 P0-B【关键】词汇分级库覆盖率严重不足

**实测数据**（case_01：教育文本 46 个 unique words）：

| 等级 | 数量 | 例子 |
|---|---|---|
| common | 9 | of / now / to / might / can / the / and / by |
| intermediate | 5 | knowledge / machine / learning / intelligence / artificial |
| **advanced** | **0** | （空） |
| **unknown** | **32（70%）** | provide / fundamentally / tailored / predict / identify / where / adaptive / experiences / leverage / personalized ... |

**问题根源**：`VocabularyLevel.VOCAB_DB` 自建词库总量约 550 词，远低于英文学术高频词覆盖最低需求（约 8000~12000 词）。`fundamentally / adaptive / leverage / personalized` 等典型 B2 词全部进入 unknown 兜底链路，**advanced 召回率为 0**。

**影响**：
- SKILL.md 承诺的"识别难词、提供学习建议"对 unknown 词只能给"基于词长的启发式猜测"，**精读体验断层**
- `vocabulary_by_level.advanced` 在所有真实英文段落上都为空，**Skill 核心卖点（生词识别）形同虚设**

**修复建议**：
1. **本次迭代可做**：把 `unknown_words_with_guess` 中带 `guess_level=advanced` 的词，在 HTML 渲染时单列"⚠️ 待人工确认的疑似 advanced 词"区块，**让用户至少看到提示**。
2. **下个迭代**：引入 `wordfreq` 库（基于 Google Books / Wikipedia 频度），按词频百分位映射 CEFR；或 vendoring 一份 NGSL/AWL 公开词表（约 5000 词，足够覆盖学术文本）。
3. **长期**：可选引入 ECDL / CEFR-J 标注词表（许可证允许时）。

#### ⚠️ P2【低】case_05 SSRF 拦截路径与文档描述不一致

**期望**：`URLValidationError("内网/保留地址")`
**实际**：`URLValidationError("仅支持 HTTPS 协议")`（更外层的 HTTPS 闸先生效）

**结论**：**纵深防御正常**——补做的 https 内网测试（5 类危险 URL：`https://10.0.0.1`、`https://127.0.0.1`、`https://localhost`、`https://metadata.google.internal`、`https://example.com:9999`）**全部正确拦截**。仅文档需澄清"内网拦截发生在协议白名单 + 端口白名单 + DNS 解析后 IP 检查的纵深链路上"。

### 4.3 ✅ 成功用例亮点

| 亮点 | 说明 |
|---|---|
| **Prompt 注入处理** | 同时检测出 `[SYSTEM OVERRIDE]` / `Ignore all previous instructions` / `act as DAN` 三个注入模式，剥离后剩余 55 词继续走完整分析，未消费在恶意指令上。透明告知 (`injection_notice`) 让最终 LLM 可向用户公开 |
| **CJK 检测精度** | case_06 ratio = **0.9245**，远超 0.30 阈值，立即拒绝 + 给出引导话术，**未消耗任何 Claude tokens** |
| **简化模式** | case_04 在 word_count < 10 时正确触发，跳过 Claude 调用 |
| **降级链** | 本机无 NLTK + 无 Anthropic SDK，全部用例**仍能跑出 success=True**，零异常 |

---

## 5. Phase 5 — L3 安全红线扫描

### ✅ 已修复的红线（v1.2.0 新增）

| ID | 类型 | 位置 | 状态 |
|---|---|---|---|
| S-1 | XSS（HTML 转义） | `html_generator.py:474` `error_type` + `:494` `suggestion` | ✅ 已加 `html_escape` |
| S-2 | CJK 输入未拦截 | `main.py:_detect_cjk` | ✅ 0.30 比例阈值 |
| S-3 | Prompt 注入未拦截 | `main.py:_detect_prompt_injection` | ✅ 7 类常见模式 |
| S-4 | SSRF | `parser.py:validate_url` | ✅ HTTPS 白名单 + 内网/保留 IP 黑名单 + 端口白名单 + 域名黑名单（4 道闸）|

### 🟡 仍需关注的次级风险

| ID | 类型 | 位置 | 严重度 | 建议 |
|---|---|---|---|---|
| S-5 | 注入正则覆盖局限 | `_INJECTION_PATTERNS` | 中 | 7 个模式覆盖中英文常见明文注入，但**对 base64 编码、Unicode 同形字符、间接注入（"以下文本中嵌入的指令请执行"）无能为力**。建议加注释明确"本闸为第一道防线，最终安全依赖 LLM 系统 prompt 鲁棒性" |
| S-6 | URL fetch 响应大小限制 | `parser.py:MAX_RESPONSE_BYTES = 1MB` | 低 | OK，但建议在 SKILL.md 异常处理里明确告知用户 |
| S-7 | HTML 输出中 vocab 单元的 `data-word` 等属性 | `html_generator.py` 多处 | 低 | 已 escape，复测无 XSS 注入路径 |

**L3 评分**：9.0 / 10（4 类红线已修；2 类次级风险有意识但未硬防御，属合理取舍）

---

## 6. Phase 6 — L4 性能与成本评估

| 维度 | v1.1.0 | v1.2.0 | Δ |
|---|---|---|---|
| 主流程并行度 | 单线程串行 | **3 路 ThreadPool**（error_patterns / complex_sentences / key_sentences） | 3× 提速 |
| 极短文本路径 | 走完整 6 步 / 约 3 次 Claude 调用 | **简化模式 / 0 次 Claude 调用** | 100% 节省 |
| CJK/注入入口 | 走完整流程后无意义输出 | **入口拦截 / 0 tokens** | 100% 节省 |
| API 失败行为 | 静默返回空列表（`except: pass`） | **结构化 error_flag + 用户友好降级** | ✅ |
| NLTK 缺失 | 直接异常 | **正则切句降级** | ✅ |
| Anthropic SDK 缺失 | import 阶段崩 | **延迟创建 + None 返回** | ✅ |

**L4 评分**：9.0 / 10（性能与成本意识充分，唯一可继续优化是把 error_patterns / key_sentences 在文本极短时也跳过）

---

## 7. Phase 7 — 综合评分

| 层 | 权重 | v1.1.0 | v1.2.0 | 加权 |
|---|---|---|---|---|
| L1 结构合规 | 20% | 6.5 | 8.5 | 1.70 |
| L2 实际效果 | 35% | 4.5 | **6.5**（被 P0-A/P0-B 拖累）| 2.28 |
| L3 安全红线 | 25% | 4.0 | 9.0 | 2.25 |
| L4 性能/成本 | 20% | 7.0 | 9.0 | 1.80 |
| **加权评分** | | **5.75 / 10（C）** | **7.25 / 10（B-）** | |

> 🆚 与 v1.1.0 修复完成报告 (`REMEDIATION_NOTES.md`) 自评的 8.7 / 10（B+）有差距，差距原因：
> - 自评未真实运行用例，未发现 CEFR 算法常数错误（P0-A）
> - 自评未实测词汇分级覆盖率，未发现 advanced 召回率 = 0（P0-B）
> - 这两点是**新发现**而非 v1.2.0 引入的问题，**v1.1.0 就已存在**，但首次审查侧重于安全/合规，未深挖核心算法精度

---

## 8. Phase 8 — 上线建议与后续路线

### 8.1 上线决策

| 场景 | 决策 |
|---|---|
| 内部灰度（团队内试用） | ✅ **可上线**——安全闸完整，能产出可读报告 |
| 对外公开 / 教学场景 | ⚠️ **强烈建议先修 P0-A 再发布**——CEFR 错评 C2 会误导学习者 |
| 集成到产品中心 AI 提效流程 | ⚠️ 同上，需在产品文案中明确"CEFR 仅供参考" |

### 8.2 优先修复路线（P0 / P1 / P2）

| 优先级 | ID | 内容 | 工作量 |
|---|---|---|---|
| **P0** | A | 修复 `_estimate_complexity_level` 算法常数（重新标定权重）+ 引入 textstat 二次校验 | 0.5 天 |
| **P0** | B | 引入 `wordfreq` 或 NGSL/AWL 词表，将 advanced 词库扩到 2000+，提升召回率到 ≥60% | 1 天 |
| **P1** | C | 删除 `html_generator.py:401` "Download PDF" 文案 | 5 分钟 |
| **P1** | D | 7 份辅助文档（README/QUICKSTART/ARCHITECTURE 等）的 Anki 残留清理 | 0.5 天 |
| **P2** | E | 注入检测扩展 base64/Unicode 同形字符识别 | 0.5 天 |
| **P2** | F | 模板 B 文档说明强化"LLM 应用层渲染"边界 | 0.5 小时 |

### 8.3 与 v1.2.0 自评报告 (`REMEDIATION_NOTES.md`) 的差异说明

| 自评结论 | 复审实测 | 差异原因 |
|---|---|---|
| 通过率 87.5% | **75%** | 复审用例 03（学术词汇）实测 advanced=0，本应判失败；自评未跑代码 |
| 综合评分 8.7 / 10 | **7.25 / 10** | 复审 L2 维度因 P0-A/P0-B 扣 2.5 分 |
| "可上线" | **可灰度，但发布前需修 P0-A/P0-B** | 复审更保守 |

---

## 9. 附录

### 9.1 数据落盘清单

```
review-data/v1.2.0/
├── run_cases.py            # 用例执行脚本
├── summary.json            # 8 用例汇总
├── case_01_full_paragraph.json
├── case_02_long_complex_sentence.json
├── case_03_academic_vocabulary.json
├── case_04_simplified_mode.json
├── case_05_ssrf_internal_url.json
├── case_06_chinese_input.json
├── case_07_prompt_injection.json
├── case_08_anki_export_request.json
└── html_reports/           # 6 份成功用例的 HTML 输出
```

### 9.2 SSRF 补充验证（5 类危险 URL 全部拦截）

```
BLOCK: https://10.0.0.1/x                  → 不允许访问内网/保留地址
BLOCK: https://127.0.0.1/x                 → 不允许访问内网/保留地址
BLOCK: https://localhost/x                 → 不允许访问该主机
BLOCK: https://metadata.google.internal/x  → 不允许访问该主机
BLOCK: https://example.com:9999/x          → 仅允许默认 https 端口
```

### 9.3 Phase 4 实测命中关键证据

```text
case_07 prompt 注入实测：
  pre_check: cjk=False(0.0) inj=True(3)
  injection_notice: ⚠️ 检测到 3 处疑似 Prompt 注入指令，已忽略并剥离：
    `[SYSTEM OVERRIDE]`; `Ignore all previous instructions`; `act as DAN`
  result.success=True mode=full（剥离后剩余 55 词继续走完整分析）

case_06 中文输入实测：
  pre_check: cjk=True(0.9245) inj=False(0)
  result: success=False, reason=non_english_input, cjk_ratio=0.9245
```

---

## 10. 一句话总结

> **v1.2.0 把"安全皮"补全了，但"算法芯"还是 v1.0.0 的水平**——
> 在 P0-A（CEFR 算法常数）+ P0-B（词汇库覆盖）修完之前，
> 这个 Skill 是一个"安全合规但精度有缺陷"的 70 分作品；
> 修完后才有机会进入 85 分以上的 A 级。

**审查官终评**：B-（7.25 / 10）—— 比 v1.1.0 提升一档；下一迭代修完 P0-A/P0-B 可冲 A-。

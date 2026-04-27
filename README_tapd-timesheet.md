# TAPD 工时自动填写 Skill

> 用自然语言描述工作内容，AI 自动匹配 TAPD 需求/任务/缺陷并写入工时。支持填写、删除、撤回。

## 🎯 能做什么

- **填工时**：说"今天上午搞了会议记录系统的 bug，下午开了 2 个小时周会"，自动匹配 TAPD 对象并生成工时记录
- **批量填**：一次填多天、多项工作
- **删/撤回**：填错了可直接让它帮你撤回

## 📦 安装步骤

### 1. 解压到 skill 目录

```bash
unzip tapd-timesheet.zip -d ~/.codebuddy/skills/
```

解压后应该长这样：

```
~/.codebuddy/skills/tapd-timesheet/
├── SKILL.md
├── scripts/
│   └── fill_timesheet.py
└── references/
    ├── tapd_timesheet_api.md
    └── work_type_mapping.md
```

### 2. 安装 Python 依赖

```bash
pip3 install requests
```

### 3. 验证 TAPD 鉴权

```bash
python3 ~/.codebuddy/skills/tapd-timesheet/scripts/fill_timesheet.py --test-auth
```

- 看到 `✅ 鉴权成功` → 可以直接用
- 看到 `❌ 鉴权失败` → 参考下方「配置 API 账号密码」

### 4. （可选）配置 API 账号密码

如果默认的 `infoselect` 账号在你的 TAPD 项目里没有写入权限，需要自建：

1. TAPD → 公司管理 → 安全与集成 → API 账号管理 → 新建
2. 在 `~/.tapd-timesheet.json` 写入：

```json
{
  "tapd_api_user": "你的API账号",
  "tapd_api_password": "你的API密码",
  "owner": "你的RTX英文名"
}
```

## 🚀 怎么用

### 触发词（CodeBuddy 里直接说）

- 填工时 / 帮我填工时 / 提交工时 / 记录工时
- 今天的工时 / 本周工时 / 补一下昨天工时
- 删除工时 / 撤销工时 / 工时填错了

### 示例对话

```
你：帮我填一下工时，本周周一早上 0.1d 研发周会
AI：[查询 TAPD → 生成清单 → 等你确认 → 写入]

你：帮我删除刚填写的研发周会工时
AI：[查询工时记录 → 撤回]

你：补一下昨天的工时，下午 4 小时做了 XX 需求的联调
AI：[搜索需求 → 匹配 Task → 写入 0.5d]
```

### 核心原则

1. **先确认再写入**：AI 会先给你按天分组的清单，看过后回「确认」才会真正调 API
2. **自动识别会议**：周会、evening、月会等会议，会自动建独立 Task，不占用需求工时
3. **工时体检**：单日工时不足 0.8d 会自动提醒，让你补记

## ⚙️ 默认配置

| 项 | 默认值 | 如何覆盖 |
|-----|--------|---------|
| 项目 (workspace_id) | `20398362`（运营商合作部_技术研发中心） | 对话时说明"XX项目"，或改 SKILL.md |
| 认证 | Basic Auth (`infoselect`) | 改 `~/.tapd-timesheet.json` |
| 身份 (owner) | 首次使用时自动询问并保存 | 改 `~/.tapd-timesheet.json` 的 `owner` 字段 |

## ❓ 常见问题

**Q：认证失败怎么办？**
A：先跑 `--test-auth` 看具体报错；如果是 401，用自己的 TAPD API 账号密码覆盖。

**Q：匹配到的 Task 不对？**
A：在确认清单阶段直接告诉 AI「改成 XXX 需求」，它会重新搜索。

**Q：想一次看本周填了多少？**
A：直接问「本周我已经填了多少工时」，AI 会帮你统计。

**Q：其他项目也能用吗？**
A：能，对话时说明"XX 项目的工时"即可，AI 会换 workspace_id。

## 🐛 反馈

用的过程中遇到问题、或想增加新的工作类型映射，直接找 **fangtan** 反馈～

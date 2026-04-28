# Obsidian Vault — ro-vault

这是一个 Obsidian 个人知识库，使用 PARA 方法组织内容。所有操作请遵循以下规则。

## 目录结构

```
00_Inbox/        ← 所有新内容的入口，待分类
01_Projects/     ← 有明确目标和截止日期的项目
02_Areas/        ← 持续关注的领域（无截止日期）
03_Resources/    ← 参考资料，按主题分类
04_Archive/      ← 已完成或不再活跃的内容
05_Attachments/  ← 图片、PDF 等非 markdown 文件
06_Metadata/     ← schema、index、log、hot cache、模板
```

## 分类规则

将 00_Inbox 中的内容按以下逻辑归类：

- **→ 01_Projects**：有具体交付物和时间线（如"搭建 Polymarket 预测市场系统"）
- **→ 02_Areas**：持续维护的领域（如"AI Agent 开发"、"预测市场"、"量化交易"）
- **→ 03_Resources**：参考资料和知识沉淀，按主题建子目录
- **→ 04_Archive**：过时、已完成、不再需要的内容
- **→ 删除**：重复、无价值、纯临时内容

## 03_Resources 主题分类

当内容进入 03_Resources 时，按以下主题归类（必要时新建子目录）：

| 目录 | 内容范围 |
|------|---------|
| `Agent-Engineering/` | Agent 框架、Skills 系统、Claude Code、多智能体、Agent 记忆 |
| `Prediction-Market/` | 预测市场（Polymarket 策略/分析、CTF 机制、做市、套利、Agent 交易） |
| `Quant-Trading/` | 量化交易策略、DeFi 协议（PropAMM/PerpDEX）、金融模型、交易信号 |
| `Dev-Tools/` | 非 Agent 类工具和库（RAG、TTS、编辑器、浏览器工具等） |
| `AI-Thinking/` | AI 行业分析、战略思考、能力框架 |
| `Security/` | 红队、网络安全、隐私工具 |
| `Misc/` | 不属于以上分类的内容 |

## Frontmatter 规范

完整字段定义见 `06_Metadata/schema.md`（唯一 source of truth）。任何 skill 生成 frontmatter 时，字段必须符合 schema.md 定义，skill 内置模板中不在 schema.md 中的字段一律忽略。快速参考：

- **通用必填**：`title`、`type`、`tags`、`date_saved`
- **Reference 必填**：以上 + `source`、`author`、`description`
- **Reference 推荐**：`published`（原始发布日期）
- **可选增强**：`entities`、`created`
- tags 用小写英文，`/` 分层（如 `agent/skills`、`trading/defi`），不用中文
- type 枚举：`reference | project | area | daily | meeting | entity | concept | analysis | meta`
- **不写入**可重算字段（confidence、decay_score、embedding）

## Agent 工作流

所有 agent 操作遵循 `06_Metadata/schema.md` 定义的规则。

### 三个核心操作

1. **Ingest**：新内容进入 → 补全 frontmatter → 提取 entities → 更新 index.md → 追加 log.md
   - **Entities 提取是必须步骤，不可跳过**：读取全文，提取所有出现 ≥2 次或有明确定义的实体（person/tool/project/concept/protocol/pattern/org），写入 frontmatter `entities` 字段。Token 成本不是约束，检索效率优先。
   - **Related 生成是必须步骤，不可跳过**：对照 `06_Metadata/index.md`，找出 vault 内语义最近的 3-5 个页面，写入 frontmatter `related` 字段（wikilink 格式）。
2. **Query**：先读 `06_Metadata/index.md` 定位相关页面 → 钻取详情 → 综合回答（引用 vault 页面，不引训练数据）
3. **Lint**：运行 vault-lint skill → 检查 frontmatter 完整性、孤页、断链等

### GitHub 重新采集规则

当 Inbox 中的文件 `source` 为 `github.com` 且 vault 内已存在相同 URL 的文件时，**不创建新页面，而是更新已有页面**：

- **替换**：`description`（新 README/About 可能更新）、`stars`（刷新快照）、`language`（若新值非空）
- **保留**：`tags`、`related`、`entities`、`date_saved`（不覆盖人工标注）
- 更新完成后删除 Inbox 中的重复文件

### X/推文类内容处理规则

当 inbox 内容的 `source` 为 `x.com` 或 `twitter.com` 时，先判断形态再处理：

| 形态 | 识别特征 | 处理方式 |
|------|---------|---------|
| 完整文章/长线程 | 有完整论点、多段落展开 | 常规 ingest |
| **个人验证 + 技术片段** | 有引用推文 + 代码/数据 + 验证语气 | **重建内容**（见下） |
| 纯想法碎片 | 一两句感想，无具体技术内容 | 归入相关 concept 页或删除 |

**"个人验证 + 技术片段"的重建步骤（最常见的残缺形态）：**

1. **识别真正的技术来源**：若为转发/引用，原始技术作者是 `author`，转发者降为正文末尾的 Note（"@xxx 验证有效"）
2. **重建标题**：格式 `Resource - [技术描述] - @原作者`，描述技术本身，不用口语化反应语气
3. **重建 description**：2-4 句，结构为"是什么 + 核心机制 + 实测效果/应用场景"
4. **整理正文**：代码/BNF/数据保留为可引用格式；转发者的验证说明放在正文末尾标注为 `> **Note**:`
5. **source**：改为指向原始推文 URL，而非转发者的推文

### 关键文件

| 文件 | 用途 |
|------|------|
| `06_Metadata/schema.md` | 设计原则、页面类型、frontmatter 规范、entity type 值域、lint 层级 |
| `06_Metadata/index.md` | 全 vault 导航索引，agent 查询时先读此文件 |
| `06_Metadata/log.md` | 操作日志，每次 ingest/lint 后追加 |
| `06_Metadata/hot.md` | 跨会话记忆缓存 |

## 同步架构

本 vault 使用混合同步策略，详见 `_scaffold/manifest.yml`：

- **Scaffold（Git）**：CLAUDE.md、.claude/、schema、templates — `git push/pull`
- **Content（文件同步）**：笔记内容（01-04/、附件）— Syncthing 等
- **Local（不同步）**：hot.md、log.md — 每台设备独立

修改 scaffold 文件后需要 git commit + push。内容文件由文件同步工具自动处理。

## Agent 操作规范

- 修改 scaffold 文件（.claude/、Templates/、schema.md、CLAUDE.md）后，提醒用户 `git commit + push`
- 内容文件（01-04/、05_Attachments/）直接编辑，由文件同步工具处理
- 未经用户确认，不要修改 .gitignore、.gitattributes 或 _scaffold/ 中的文件

## 笔记创建规范

- 使用 Obsidian 风格 wikilink：`[[笔记名]]`
- 内部链接用 wikilink，外部链接用标准 markdown `[text](url)`
- 文件名允许中文，但避免特殊字符（`/`、`:`、`|`、`?` 等）
- 图片和附件放 `05_Attachments/`，用 `![[文件名]]` 嵌入

## 用户主要关注领域

1. **AI Agent 开发** — 框架、Skills、多智能体架构、记忆系统
2. **预测市场** — Polymarket 策略与分析、CTF 机制、Agent 交易、做市套利
3. **量化交易** — DeFi 协议、交易策略、金融模型、交易信号
4. **开发工具与效率** — 知识管理、自动化、开源工具

## 可用 Skills

与本 vault 相关的 skills（通过 `/skill-name` 或自然描述触发）：

- `inbox-processor` — 扫描并分类 00_Inbox 中的内容
- `add-frontmatter` — 批量给笔记添加或修复 frontmatter
- `thinking-partner` — 协作探索想法
- `research-assistant` — 深度研究某个主题
- `daily-review` — 每日回顾
- `weekly-synthesis` — 每周总结和模式发现
- `de-ai-ify` — 去除文本中的 AI 腔
- `download-attachment` — 从 URL 下载文件到 05_Attachments
- `obsidian-markdown` — 创建标准 Obsidian markdown
- `obsidian-cli` — 通过 CLI 操作 vault
- `obsidian-bases` — 创建数据库视图
- `vault-lint` — L1 文件系统健康检查（frontmatter、孤页、断链等）
- `defuddle` — 从网页提取干净内容

## Hot Cache（会话记忆）

`06_Metadata/hot.md` 是跨会话的记忆缓存。

- **会话开始时**：自动读取 hot.md 恢复上次上下文（通过 hooks 自动完成）
- **会话结束时**：**必须**在最后一次回复中更新 hot.md，记录本次会话的关键信息
- **上下文压缩后**：自动重新读取 hot.md（因为压缩会丢失 hook 注入的内容）

Hot cache 格式包含 5 个固定段落：
1. **Last Updated** — 最近更新时间和事件
2. **Vault State** — vault 结构和内容现状
3. **Recent Decisions** — 最近做出的关键决策
4. **Active Threads** — 进行中的工作和待办
5. **Key Patterns** — 用户偏好和行为模式

更新时完全覆盖文件（它是缓存不是日志），保持 500 字以内。

## 注意事项

- 用中文回答用户
- 操作文件前先确认路径正确，避免误操作
- 移动或删除文件前告知用户并等待确认
- 不要在笔记内容中添加 AI 生成的总结性套话

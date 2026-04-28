---
title: "Vault Schema"
type: meta
tags:
  - meta/schema
updated: 2026-04-28
---

# Vault Schema

本文件定义 ro-vault 的结构规则和设计约束。所有 agent 操作（ingest/query/lint）遵循此 schema。

---

## 设计原则

### 1. Markdown 永远是 source of truth

所有知识以 `.md` 文件形式存在。任何增强层（索引、embedding、graph）都从 markdown 派生，不反过来。

### 2. 可重算的不进 source of truth

embedding、相似度分数、排名——凡是可以从 markdown 重新生成的数据，不写入 frontmatter。只存不可重算的人类判断（分类、entities、tags）。

### 3. 增强层可删可重建

测试标准：删除所有 `.index/` 目录后，系统必须完全可用。增强层提供加速，不提供功能。

### 4. 主流程简单，增强走旁路

Ingest/Query/Lint 主流程只依赖 markdown + index.md。向量检索、相似度检测等作为可选加速层，不阻塞写入。

### 5. Entity 是未来升级的统一接口

frontmatter 中的 `entities`（name + type）是未来 graph 查询、检索过滤、聚类分析的唯一入口。**Ingest 时自动提取，所有页面必填**（出现 ≥2 次或有明确定义的实体）。Obsidian Properties 不渲染嵌套 YAML，该字段面向 agent 使用。

### 6. 检索方式是可替换的

当前检索：LLM 读取 index.md 直接导航。未来加入 qmd 或其他引擎时，需要更新所有涉及检索的 skills（inbox-processor、research-assistant 等）。这是已知的迁移点。

---

## 页面类型

| type | 用途 | 所在目录 |
|------|------|----------|
| `reference` | 外部采集的参考资料 | 03_Resources/ |
| `project` | 有交付物和时间线的项目文档 | 01_Projects/ |
| `area` | 持续关注领域的笔记 | 02_Areas/ |
| `daily` | 每日回顾 | 02_Areas/ |
| `meeting` | 会议记录 | 01_Projects/ 或 02_Areas/ |
| `entity` | 高价值实体页（人/项目/概念） | 03_Resources/ 对应子目录 |
| `concept` | 跨领域概念页 | 03_Resources/ 对应子目录 |
| `analysis` | Agent 生成的分析和综合 | 01_Projects/ 或 03_Resources/ |
| `meta` | 模板、索引、schema 等元文件 | 06_Metadata/ |

---

## 文件命名规范

| 来源 | 命名格式 | 示例 |
|------|---------|------|
| GitHub 项目 | `owner-repo` | `anthropics-claude-cookbooks` |
| 中文文章 | 标题简化，`：` → `-`，去掉 `？""` | `金融知识体系终极指南-1.2万字深度拆解` |
| Twitter/X | `author - 描述前50字` | `dotey - AI优先战略反思` |
| 其他网页 | 标题前60字 | `Automate work with routines` |

禁止字符：`：？！""——（）` 及 emoji。最大 80 字符。

Web Clipper 模板（`06_Metadata/Reference/web-clipper-templates/`）已配置自动生成符合规范的文件名。Ingest 时如发现不符合命名规范的文件，应在移出 Inbox 时重命名。

---

## Frontmatter 规范

字段分三层：通用 → 类型专属 → 可选增强。Agent 处理时按此优先级补全。

### 通用字段（所有页面必填）

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | string | 页面标题 |
| `type` | enum | 见上方页面类型 |
| `tags` | list | 小写英文，`/` 分层（如 `agent/framework`） |
| `description` | string | 2-4 句摘要，覆盖：是什么 + 核心技术/内容点 + 价值/应用场景，供 agent 一读即判断相关性，无需进入全文 |
| `date_saved` | date | 入库日期（vault schema 的规范字段，ingest 时写入） |

```yaml
---
title: "文章标题"
type: reference
tags: [agent/framework, trading/polymarket]
description: "是什么工具/文章（1句）。核心技术点或关键洞察（1-2句）。适用场景或价值（1句）。"
date_saved: 2026-04-23
updated: 2026-04-23
---
```

### Reference 页面附加字段

reference 类型页面在通用字段基础上**必须**包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | url | 原始来源 URL |
| `author` | list | 作者，用 wikilink 格式如 `"[[@username]]"` |

reference 类型页面的**推荐字段**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `published` | date | 原始内容的发布日期（区别于 date_saved） |

```yaml
---
title: "Decepticon: Autonomous Hacking Agent"
type: reference
tags: [security/redteam, agent/framework]
date_saved: 2026-04-23
source: "https://github.com/PurpleAILAB/Decepticon"
author:
  - "[[@PurpleAILAB]]"
description: "自主红队渗透测试 Agent，支持 CVE 自动化利用"
published: 2026-04-16
---
```

### GitHub 项目附加字段（可选）

由 `06_Metadata/Reference/web-clipper-templates/github.json` 自动采集写入，不需要手动填写。

| 字段 | 类型 | 说明 |
|------|------|------|
| `stars` | string | GitHub star 数快照（如 `"15.2k"`），采集时写入，会随时间失真 |
| `language` | string | 仓库主要编程语言（如 `"Rust"`），采集时写入 |

**重新采集规则**：当 Inbox 中出现已存在于 vault 的 GitHub 仓库时（通过 `source` URL 匹配），执行以下字段更新：
- `description`：用新值替换旧值（README/About 描述可能更新）
- `stars`：用新值替换旧值（snapshot 刷新）
- `language`：如新值非空则替换（旧值可能采集失败）
- 其他字段（tags、related、entities）：保留旧值，不覆盖

### 可选增强字段（任何页面）

| 字段 | 类型 | 说明 |
|------|------|------|
| `updated` | date | 内容最后修改日期，每次编辑时更新 |
| `related` | list | vault 内语义最近的页面，wikilink 格式，ingest 时 agent 自动生成 3-5 个 |
| `entities` | list | 关键实体提取，见下方 entity 规范 |
| `created` | date | Obsidian / Clipper 自动生成的文件创建时间戳；现有文件两个字段值相同，新文件 ingest 时 agent 同时写入 date_saved |

### Entity 规范

> **注意**：`entities` 是嵌套 YAML，Obsidian Properties 面板不支持此格式（显示为原始文本）。该字段面向 agent 使用，**ingest 时自动提取，所有页面必填**（entity stub 等极短文件除外）。

```yaml
entities:
  - name: "[[Claude Code]]"
    type: tool
  - name: "[[Karpathy]]"
    type: person
```

**Entity type 值域：**

| type | 含义 | 示例 |
|------|------|------|
| `person` | 人物 | Karpathy, Tobi Lutke |
| `tool` | 工具和软件 | Claude Code, qmd, Obsidian |
| `project` | 开源项目或产品 | claude-obsidian, Mem0 |
| `concept` | 抽象概念 | context substrate, RAG |
| `protocol` | 协议和标准 | TCP, MCP, WebSocket |
| `pattern` | 设计模式 | LLM Wiki, PARA, Camp 2 |
| `org` | 组织和公司 | Anthropic, Zilliz |

---

## Lint 层级

### L1：文件系统 lint（现在执行）

- 无 frontmatter 的文件
- 无 tags 的文件
- 空文件 / 极短文件（<100 字）
- 无入链的孤页
- 断掉的 wikilinks
- frontmatter type 不在合法值域内

### L2：语义 lint（300 篇后引入）

- 高相似度内容检测（疑似重复）
- 语义矛盾检测（增量：新文章 vs 相关旧文章）
- 已被更新知识覆盖的过时声明

L2 以增量方式运行（每次 ingest 时只比较新文章），不做全量扫描。

---

## 不写入 frontmatter 的字段

以下字段属于"可重算"，不进 source of truth：

- `confidence` / `decay_score`（无实践验证，可由 lint 替代）
- `embedding`（工具自动生成）
- `id`（Obsidian 文件路径即唯一标识）
- `relations`（从 wikilinks 和 entities 派生）

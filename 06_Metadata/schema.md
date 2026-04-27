---
title: "Vault Schema"
type: meta
tags:
  - meta
  - schema
updated: 2026-04-23
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

frontmatter 中的 `entities`（name + type）是未来 graph 查询、检索过滤、聚类分析的唯一入口。当前用于 Obsidian graph view 和 wikilink 导航。

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

### 通用字段（所有页面）

```yaml
---
title: "文章标题"
type: reference          # 见上方页面类型
tags: [agent/framework, trading/polymarket]
date_saved: 2026-04-23
---
```

### Reference 页面附加字段

```yaml
source: "https://..."
author: "作者名"
```

### 带实体提取的页面

```yaml
entities:
  - name: "[[Claude Code]]"
    type: tool
  - name: "[[Karpathy]]"
    type: person
  - name: "[[LLM Wiki]]"
    type: pattern
```

### Entity type 值域

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

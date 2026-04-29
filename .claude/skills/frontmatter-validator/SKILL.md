---
title: Frontmatter Validator Skill
type: reference
tags: [dev/tool, agent/framework, vault/maintenance]
date_saved: 2026-04-28
description: "自动化工具：验证和修复 Obsidian vault 中的 YAML frontmatter 问题（缺失字段、多行文本、wikilink 引号等）。"
source: internal
author: []
entities:
  - name: "[[Obsidian]]"
    type: tool
  - name: "[[YAML Validation]]"
    type: pattern
---

# Frontmatter Validator

自动检测和修复 Obsidian vault 中的 frontmatter 问题。

## 问题背景

参见 `06_Metadata/learnings-frontmatter-qa.md`，这个工具是从大规模修复工作中提炼出来的。

## 使用方法

### 基础验证

```bash
cd /Users/roson.luo/Documents/ro-obsidian/ro-vault
python3 .claude/skills/frontmatter-validator/validator.py --path 03_Resources
```

### 自动修复

```bash
python3 .claude/skills/frontmatter-validator/validator.py --path 03_Resources --fix
```

### 详细输出

```bash
python3 .claude/skills/frontmatter-validator/validator.py --path 03_Resources --verbose
```

### 严格模式（警告也会失败）

```bash
python3 .claude/skills/frontmatter-validator/validator.py --path 03_Resources --strict
```

## 检查项

| 检查项 | 错误/警告 | 修复 |
|--------|----------|------|
| Frontmatter 存在 | ERROR | 手动添加 |
| YAML 有效性 | ERROR | 自动修复 |
| 必填字段完整 | ERROR | 可补充（需策略） |
| Reference 类型字段 | ERROR | 可补充（需策略） |
| Tags 是列表 | WARNING | 自动修复 |
| Wikilink 无引号 | WARNING | 自动修复 |
| Description 单行 | WARNING | 自动修复 |
| Entities 格式 | WARNING | 自动修复 |
| Related 链接格式 | WARNING | 自动修复 |

## 修复规则

运行 `--fix` 后，工具会自动进行以下修复：

1. 移除 `related` 字段中 wikilink 两侧的引号
2. 折叠 description 中的多行文本
3. 补充缺失的 `entities` 和 `related` 字段
4. 重新序列化 YAML 以确保格式一致

## 集成到 Git 钩子

创建 `.git/hooks/pre-commit`：

```bash
#!/bin/bash
changed_files=$(git diff --cached --name-only | grep '.md$')

if [ -z "$changed_files" ]; then
    exit 0
fi

python3 .claude/skills/frontmatter-validator/validator.py --path 03_Resources || {
    echo "Frontmatter validation failed. Run with --fix to auto-correct."
    exit 1
}

exit 0
```

使用权限：
```bash
chmod +x .git/hooks/pre-commit
```

## 输出示例

```
============================================================
FRONTMATTER VALIDATION REPORT
============================================================
Total files scanned:  144
Valid (no issues):    144 / 144
Total errors:         0
Total warnings:       0
============================================================

All files passed validation!
```

## 相关文档

- `06_Metadata/learnings-frontmatter-qa.md` — 完整的修复工作总结和最佳实践
- `06_Metadata/schema.md` — Frontmatter 规范
- `CLAUDE.md` — Agent 工作流规范

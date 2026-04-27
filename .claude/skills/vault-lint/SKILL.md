---
name: vault-lint
description: Run L1 file-system health checks on the vault. Detects missing frontmatter, missing tags, short files, orphan pages, broken wikilinks, and invalid type values. Use when the user asks to lint, audit, health-check, or clean up the vault. Also use proactively after bulk ingest or frontmatter operations to verify nothing broke.
---

# Vault Lint (L1)

Run file-system-level health checks on the vault per `06_Metadata/schema.md` L1 definitions. The goal is to catch structural decay early — files that drift from the schema make the vault harder for agents to navigate and for queries to produce accurate results.

## Scope

Check all `.md` files under `00_Inbox/`, `01_Projects/`, `02_Areas/`, `03_Resources/`, `04_Archive/`. Exclude `05_Attachments/`, `06_Metadata/`, `.obsidian/`, `.claude/`, and `node_modules/`. Ignore `README.md` and `Welcome.md`.

## Checks

### 1. Missing frontmatter

Flag files with no YAML frontmatter block (no `---` delimiters at top of file). Without frontmatter, agents cannot classify or filter the file during queries.

### 2. Missing tags

Flag files that have frontmatter but no `tags` field or an empty `tags` array. Tags are the primary facet for filtering and discovery.

### 3. Short files

Flag files with fewer than 100 characters of body content (excluding frontmatter). These are likely stubs or failed clips that add noise to search results.

### 4. Invalid type

Flag files whose `type` field is not one of: `reference`, `project`, `area`, `daily`, `meeting`, `entity`, `concept`, `analysis`, `meta`. An invalid type breaks any query that filters by page type.

### 5. Orphan pages

Flag files in `03_Resources/` not referenced by any `[[wikilink]]` in other files and not listed in `06_Metadata/index.md`. A file counts as referenced if its filename (without `.md`) appears as a substring in any `[[...]]` link or in index.md — this handles cases where wikilinks use shortened names (e.g., `[[AgriciDaniel/claude-obsidian]]`) while the actual filename is longer. Only flag files where no reasonable match exists.

### 6. Broken wikilinks

Scan all in-scope files for `[[Target]]` links. Flag links where no file matching `Target` exists anywhere in the vault. Exclude these known non-file patterns:
- Twitter/X handles: `[[@username]]`
- Example placeholders in code blocks or templates (e.g., `[[Article Title]]`, `[[Entity1]]`)
- Anchor-only links: `[[#section]]`

## Output

Print a grouped report in this format:

```
## Vault Lint Report

### Missing Frontmatter (N files)
- path/to/file.md

### Missing Tags (N files)
- path/to/file.md

### Short Files (N files)
- path/to/file.md — 42 chars

### Invalid Type (N files)
- path/to/file.md — type: "badvalue"

### Orphan Pages (N files)
- path/to/file.md

### Broken Wikilinks (N links)
- path/to/file.md → [[Missing Target]]

### Summary
Total issues: X
Files checked: Y
```

## Implementation

Use `find`, `grep`, `awk` shell commands to perform all checks in batch — do not read files one by one with the Read tool. For example, extract frontmatter fields with `awk`, detect wikilinks with `grep -roh`, and cross-reference with `sort`/`comm`. This keeps token usage under a few thousand regardless of vault size.

## Behavior

- Report only — do not modify any files unless the user explicitly asks for fixes.
- Show every section header even if zero issues, so the user sees a complete picture.
- When reporting orphans, distinguish between "truly unreferenced" and "filename mismatch" (the link exists but doesn't match the full filename). Report them separately so the user can decide whether to rename files or update links.

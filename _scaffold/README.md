# Vault Scaffold

## New Device Bootstrap

### Prerequisites
- [ ] Git installed
- [ ] Claude Code CLI installed and logged in (`claude login`)
- [ ] ~/.claude/plugins/ has required global plugins (e.g., claude-mem)
- [ ] ~/.claude/CLAUDE.md configured (personal preferences)
- [ ] Obsidian installed

### Steps
1. `git clone git@github.com:you/ro-vault.git ~/Documents/ro-obsidian/ro-vault`
2. `cd ro-vault && bash _scaffold/bootstrap.sh`
3. Open vault in Obsidian
4. Install BRAT plugin manually, add `YishenTu/claudian` in BRAT, enable auto-update
5. (Optional) Configure Syncthing: `cp _scaffold/.stignore.template .stignore`

## Sync Architecture

| Category | Mechanism | Files |
|----------|-----------|-------|
| Scaffold | Git push/pull | CLAUDE.md, .claude/, schema, templates, Obsidian config |
| Content | File sync (Syncthing etc.) | Notes (01-04), attachments, index.md |
| Local | No sync | hot.md, log.md, workspace.json |

See `manifest.yml` for the complete file classification.

## Scaffold Upgrade (Multi-Vault)

When you have a second vault and manual rule-copying becomes painful:
1. Run `new-vault.sh` to create vaults from this scaffold
2. If divergence becomes a real problem, extract shared rules via `git subtree`

Trigger: upgrade only when you've forgotten to sync rules across vaults at least 3 times.

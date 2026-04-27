#!/bin/bash
set -euo pipefail
VAULT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Bootstrapping vault at: $VAULT_DIR"

# Create content directories (git doesn't track empty dirs)
for dir in 00_Inbox 01_Projects 02_Areas 03_Resources 04_Archive 05_Attachments; do
  mkdir -p "$VAULT_DIR/$dir"
done
mkdir -p "$VAULT_DIR/06_Metadata/Reference"

# Create local-state files (prevents Claude hooks from erroring)
# hot.md needs YAML frontmatter — Stop hook expects it
# Guard: don't overwrite existing session memory
if [ ! -f "$VAULT_DIR/06_Metadata/hot.md" ]; then
cat > "$VAULT_DIR/06_Metadata/hot.md" <<HOTEOF
---
title: "Hot Cache"
type: meta
tags:
  - meta
updated: $(date '+%Y-%m-%d')
---

# Hot Cache

No prior session context.
HOTEOF
fi
if [ ! -f "$VAULT_DIR/06_Metadata/log.md" ]; then
cat > "$VAULT_DIR/06_Metadata/log.md" <<LOGEOF
---
title: "Operation Log"
type: meta
tags:
  - meta
updated: $(date '+%Y-%m-%d')
---

# Operation Log
LOGEOF
fi
if [ ! -f "$VAULT_DIR/06_Metadata/index.md" ]; then
cat > "$VAULT_DIR/06_Metadata/index.md" <<IDXEOF
---
title: "Vault Index"
type: meta
tags:
  - meta
updated: $(date '+%Y-%m-%d')
---

# Vault Index
IDXEOF
fi

echo ""
echo "Done. Next steps:"
echo "  1. Open this directory in Obsidian"
echo "  2. Install BRAT plugin, add 'YishenTu/claudian' in BRAT, enable auto-update"
echo "  3. If using Syncthing: cp _scaffold/.stignore.template .stignore"
echo "  4. Content arrives via file sync or fresh Web Clipper captures"

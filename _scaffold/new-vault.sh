#!/bin/bash
set -euo pipefail
TARGET="${1:?Usage: new-vault.sh <target-directory>}"
SOURCE="$(cd "$(dirname "$0")/.." && pwd)"

if [ -d "$TARGET" ]; then
  echo "Error: $TARGET already exists. Aborting to prevent overwrite."
  exit 1
fi

mkdir -p "$TARGET"

# Copy scaffold files
cp "$SOURCE/CLAUDE.md" "$TARGET/"
cp -r "$SOURCE/.claude" "$TARGET/"
cp "$SOURCE/.gitignore" "$TARGET/"
cp "$SOURCE/.gitattributes" "$TARGET/"
cp -r "$SOURCE/_scaffold" "$TARGET/"

# Copy metadata scaffold
mkdir -p "$TARGET/06_Metadata"
cp "$SOURCE/06_Metadata/schema.md" "$TARGET/06_Metadata/"
[ -d "$SOURCE/06_Metadata/Templates" ] && cp -r "$SOURCE/06_Metadata/Templates" "$TARGET/06_Metadata/"
mkdir -p "$TARGET/06_Metadata/Reference"
[ -d "$SOURCE/06_Metadata/Reference/web-clipper-templates" ] && \
  cp -r "$SOURCE/06_Metadata/Reference/web-clipper-templates" "$TARGET/06_Metadata/Reference/"

# Copy Obsidian allowlisted configs
mkdir -p "$TARGET/.obsidian"
for f in app.json appearance.json community-plugins.json core-plugins.json hotkeys.json; do
  [ -f "$SOURCE/.obsidian/$f" ] && cp "$SOURCE/.obsidian/$f" "$TARGET/.obsidian/"
done
[ -d "$SOURCE/.obsidian/themes" ] && cp -r "$SOURCE/.obsidian/themes" "$TARGET/.obsidian/"

# Ensure Obsidian Sync is disabled in the copied config
CORE_PLUGINS="$TARGET/.obsidian/core-plugins.json"
if [ -f "$CORE_PLUGINS" ] && grep -q '"sync"' "$CORE_PLUGINS"; then
  sed -i '' 's/"sync"[[:space:]]*:[[:space:]]*true/"sync": false/' "$CORE_PLUGINS"
fi

# Run bootstrap to create content directories and local files
bash "$TARGET/_scaffold/bootstrap.sh"

# Initialize git
cd "$TARGET"
git init
git branch -M main
git add -A

GIT_NAME="$(git config user.name 2>/dev/null || true)"
GIT_EMAIL="$(git config user.email 2>/dev/null || true)"

if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
  git commit -m "init: vault from scaffold"
  echo ""
  echo "New vault created at: $TARGET"
  echo "Remember to:"
  echo "  1. git remote add origin <your-private-repo-url>"
  echo "  2. Set the repo as PRIVATE (vault may contain personal content)"
else
  echo ""
  echo "New vault created at: $TARGET"
  echo "Files staged but not committed — git identity not configured."
  echo "Run:"
  echo "  cd $TARGET"
  echo "  git config user.name \"Your Name\""
  echo "  git config user.email \"you@example.com\""
  echo "  git commit -m \"init: vault from scaffold\""
fi

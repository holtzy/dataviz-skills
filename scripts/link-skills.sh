#!/usr/bin/env bash
# Symlink every skill of this repo into a skills folder, so a `git pull` updates them everywhere.
# Usage: ./scripts/link-skills.sh [target_dir]   (default: ~/.claude/skills)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIR="${1:-$HOME/.claude/skills}"
mkdir -p "$TARGET_DIR"

for skill in "$REPO_DIR"/dataviz-*/*/; do
  name="$(basename "$skill")"
  dest="$TARGET_DIR/$name"
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "skip  $name (a real folder already exists at $dest)"
    continue
  fi
  ln -sfn "${skill%/}" "$dest"
  echo "link  $name -> $dest"
done

#!/usr/bin/env bash
# Installs the context tracker hook + statusline into ~/.claude/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"

echo "Installing claude-code-context-tracker..."

mkdir -p "$CLAUDE_DIR/hooks"
cp "$SCRIPT_DIR/hooks/context_tracker.py" "$CLAUDE_DIR/hooks/context_tracker.py"
cp "$SCRIPT_DIR/statusline.py" "$CLAUDE_DIR/statusline.py"
chmod +x "$CLAUDE_DIR/hooks/context_tracker.py" "$CLAUDE_DIR/statusline.py"
echo "  ✓ Copied scripts to ~/.claude/"

if [ ! -f "$SETTINGS" ]; then
  echo "{}" > "$SETTINGS"
fi

cp "$SETTINGS" "$SETTINGS.backup.$(date +%Y%m%d%H%M%S)"
echo "  ✓ Backed up existing settings.json"

python3 - "$SETTINGS" <<'PYEOF'
import json, sys

path = sys.argv[1]
with open(path) as f:
    cfg = json.load(f)

hook_entry = {
    "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/context_tracker.py"}
    ]
}

cfg.setdefault("hooks", {}).setdefault("Stop", [])
# Avoid adding a duplicate entry on re-install
already = any(
    any(h.get("command", "").endswith("context_tracker.py") for h in entry.get("hooks", []))
    for entry in cfg["hooks"]["Stop"]
)
if not already:
    cfg["hooks"]["Stop"].append(hook_entry)

cfg["statusLine"] = {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py",
}

with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
PYEOF

echo "  ✓ Patched ~/.claude/settings.json"
echo ""
echo "Done. Restart Claude Code — the status line appears after your next completed turn."

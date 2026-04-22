#!/usr/bin/env python3
"""Status line: shows model + context usage with proactive threshold hints."""
import json
import os
import sys
import time

CONTEXT_LIMITS = {
    "claude-opus-4-7": 1_000_000,
    "claude-sonnet-4-6": 200_000,
    "claude-haiku-4-5": 200_000,
    "claude-haiku-4-5-20251001": 200_000,
}

AUTOCOMPACT_BUFFER = 33_000  # Claude Code reserves ~33k for the auto-compact buffer
CACHE_TTL_SECONDS = 5 * 60  # Prompt cache expires after 5 min of inactivity

def fmt_k(tokens: int) -> str:
    k = round(tokens / 1000)
    if k >= 1000:
        return f"{k:,}k".replace(",", ".")
    return f"{k}k"

state_dir = os.path.expanduser("~/.claude/context_states")

if not os.path.isdir(state_dir):
    print("Context: --")
    sys.exit(0)

try:
    files = [
        os.path.join(state_dir, f)
        for f in os.listdir(state_dir)
        if f.endswith(".json")
    ]
    if not files:
        print("Context: --")
        sys.exit(0)
    latest = max(files, key=os.path.getmtime)
    with open(latest) as f:
        state = json.load(f)
    idle_seconds = time.time() - os.path.getmtime(latest)
except Exception:
    print("Context: --")
    sys.exit(0)

model = state.get("model", "unknown")
total_input = state.get("total_input_tokens", 0)

raw_limit = CONTEXT_LIMITS.get(model, 200_000)
effective_limit = raw_limit - AUTOCOMPACT_BUFFER
pct = round(total_input / effective_limit * 100) if effective_limit > 0 else 0

print(f"Model: {model}")
print(f"Context: {fmt_k(total_input)} / {fmt_k(effective_limit)} ({pct}%)")

if pct >= 85:
    print("→ action: /compact (preserve decisions) or /clear (reset)")
elif pct >= 60:
    print("→ tip: /compact now — at 95% auto-compact runs with degraded context")

if idle_seconds > CACHE_TTL_SECONDS:
    idle_min = int(idle_seconds // 60)
    print(f"→ cache cold ({idle_min} min idle) — next prompt reprocesses full context")

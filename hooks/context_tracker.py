#!/usr/bin/env python3
"""Stop hook: reads token usage from transcript JSONL, writes per-session state file."""
import json
import os
import sys

try:
    data = json.loads(sys.stdin.read())
    transcript_path = data.get("transcript_path", "")
    session_id = data.get("session_id", "")

    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    model = "unknown"
    turn_totals = []

    with open(transcript_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                msg = entry.get("message", {})
                m = msg.get("model", "")
                if msg.get("role") == "assistant" and "usage" in msg and m and not m.startswith("<"):
                    if msg.get("stop_reason") == "end_turn":
                        usage = msg["usage"]
                        model = m
                        total = (
                            usage.get("input_tokens", 0)
                            + usage.get("cache_read_input_tokens", 0)
                            + usage.get("cache_creation_input_tokens", 0)
                        )
                        output = usage.get("output_tokens", 0)
                        turn_totals.append((total, output))
            except Exception:
                continue

    if not turn_totals:
        sys.exit(0)

    current_total, current_output = turn_totals[-1]

    # Growth of last turn: how much context increased by sending the last prompt.
    # If repeated, next turn would grow by roughly the same amount.
    if len(turn_totals) >= 2:
        last_growth = current_total - turn_totals[-2][0]
    else:
        last_growth = current_output  # fallback: at minimum, response goes into history

    if last_growth < 0:
        last_growth = current_output

    state = {
        "session_id": session_id,
        "total_input_tokens": current_total,
        "output_tokens": current_output,
        "last_growth_tokens": last_growth,
        "model": model,
    }

    state_dir = os.path.expanduser("~/.claude/context_states")
    os.makedirs(state_dir, exist_ok=True)
    with open(os.path.join(state_dir, f"{session_id}.json"), "w") as f:
        json.dump(state, f)

except Exception as e:
    try:
        with open(os.path.expanduser("~/.claude/context_hook_debug.json"), "w") as f:
            f.write(str(e))
    except Exception:
        pass

sys.exit(0)

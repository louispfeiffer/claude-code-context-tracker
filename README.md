# Claude Code Context Tracker

A lightweight status line extension for [Claude Code](https://claude.com/claude-code) that shows your **current context usage** below the input prompt, with proactive hints to help you avoid wasting tokens.

```
Model: claude-sonnet-4-6
Context: 85k / 167k (51%)
```

When usage gets high, it surfaces actionable tips automatically:

```
Model: claude-sonnet-4-6
Context: 130k / 167k (78%)
→ tip: /compact now — at 95% auto-compact runs with degraded context
```

And if you stepped away for more than 5 minutes:

```
Model: claude-sonnet-4-6
Context: 85k / 167k (51%)
→ cache cold (8 min idle) — next prompt reprocesses full context
```

## Why

Claude Code already shows its own `/context` command, but you have to run it manually. This extension puts the same information **permanently below your input**, and adds:

- **Effective limit** (subtracts the ~33k auto-compact buffer — the tokens you can actually use)
- **Proactive warnings** at 60% and 85% with specific next-step commands
- **Cache expiry detection** — warns when you've been idle >5 min, because the next prompt then reprocesses the entire context at full cost
- **Per-session tracking** — works correctly with multiple Claude Code terminals open at once

## How it works

1. A `Stop` hook fires after every completed turn and reads the token usage from the session's transcript JSONL file.
2. It writes per-session state to `~/.claude/context_states/{session_id}.json`.
3. The status line script reads the most recently updated state file and formats the output.

## Install

```bash
git clone https://github.com/louispfeiffer/claude-code-context-tracker.git
cd claude-code-context-tracker
./install.sh
```

The installer:
- Copies `hooks/context_tracker.py` to `~/.claude/hooks/`
- Copies `statusline.py` to `~/.claude/`
- Patches `~/.claude/settings.json` to register the hook and status line

Restart Claude Code after install. You'll see the status line after your next completed turn.

## Manual install

If you'd rather not run the script, add these entries to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/context_tracker.py"
          }
        ]
      }
    ]
  },
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline.py"
  }
}
```

Then copy `hooks/context_tracker.py` to `~/.claude/hooks/` and `statusline.py` to `~/.claude/`.

## Notes

- **Updates after completed turns only.** The Stop hook fires when Claude finishes responding, so the status line reflects the state *after* the last turn — not live during a response. Use `/context` for live values.
- **Interrupted turns don't update the status line.** If you cancel mid-response, the display stays at the previous turn's value until the next completed turn.
- **Context window assumptions.** The script has hardcoded limits for current models (1M for Opus 4.7, 200k for Sonnet 4.6 and Haiku 4.5). Edit `CONTEXT_LIMITS` in `statusline.py` if you use other models.

## License

MIT

#!/usr/bin/env python3
"""statusline.py — the seat's name, and how much context it has left.

Wire it up in `.claude/settings.json`:

    "statusLine": {"type": "command",
                   "command": "python3 \"${CLAUDE_PROJECT_DIR}/src/RimMandrake/Utils/statusline.py\""}

Self-test against a real transcript, no Claude Code required:

    python3 src/RimMandrake/Utils/statusline.py --selftest <transcript.jsonl>

WHERE THE NUMBER COMES FROM
===========================
Claude Code does not hand the status line a "context used" figure, but it does
hand it `transcript_path`, and the transcript records the API's own accounting
for every assistant turn. The context in play at that turn is

    input_tokens + cache_creation_input_tokens + cache_read_input_tokens

Almost all of it is cache_read on a long session — 583k of 584k when this was
written — which is why summing only `input_tokens` reads as a near-empty window
and is the easy mistake here.

Read the LAST assistant message with a usage block, not the sum of all of them:
each turn's figure is already cumulative for the window, so adding them up
multiplies the answer by the number of turns.

WHAT IT CANNOT SHOW
===================
Tokens left before the quota refresh. That lives server-side; there is no
`claude usage` subcommand, and nothing under `~/.claude` caches it (checked
2026-08-15, v2.1.233). `/usage` inside a session is the only surface, and it is
interactive. If a machine-readable one ever appears, add it here.
"""
import json
import os
import sys

# The 1M-context variants advertise it in the model id; everything else is 200k.
BIG, SMALL = 1_000_000, 200_000
BAR = 14


def window_for(model_id, display=""):
    s = ("%s %s" % (model_id or "", display or "")).lower()
    return BIG if ("1m" in s or "[1m]" in s) else SMALL


def context_used(path):
    """Tokens currently in the window, from the last assistant turn. None if unknown."""
    if not path or not os.path.exists(path):
        return None
    last = None
    try:
        # Transcripts reach tens of MB; read the tail rather than the whole file.
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - 400_000))
            chunk = fh.read().decode("utf-8", "ignore")
    except OSError:
        return None
    for line in chunk.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        u = (d.get("message") or {}).get("usage")
        if isinstance(u, dict) and ("input_tokens" in u or "cache_read_input_tokens" in u):
            last = u
    if not last:
        return None
    return (last.get("input_tokens", 0)
            + last.get("cache_creation_input_tokens", 0)
            + last.get("cache_read_input_tokens", 0))


def bar(frac, width=BAR):
    filled = max(0, min(width, int(round(frac * width))))
    return "█" * filled + "░" * (width - filled)


# 90% is the point worth reacting to; amber from two thirds.
def colour(frac):
    return "\033[31m" if frac >= 0.9 else "\033[33m" if frac >= 0.66 else "\033[32m"


def human(n):
    return "%.0fk" % (n / 1000.0) if n < 1_000_000 else "%.2fM" % (n / 1_000_000.0)


def main():
    if "--selftest" in sys.argv:
        p = sys.argv[sys.argv.index("--selftest") + 1]
        used = context_used(p)
        print("transcript: %s" % p)
        print("context used: %s" % (used if used is None else "%d (%s)" % (used, human(used))))
        for w in (SMALL, BIG):
            if used:
                print("  against %s window: %s %d%%" % (
                    human(w), bar(used / w), round(100 * used / w)))
        return 0

    try:
        ev = json.load(sys.stdin)
    except Exception:
        ev = {}
    model = ev.get("model") or {}
    model_id = model.get("id") or ""
    name = model.get("display_name") or model_id or "claude"
    seat = os.environ.get("AGENT_SEAT") or ""

    used = context_used(ev.get("transcript_path"))
    win = window_for(model_id, name)

    parts = []
    if seat:
        parts.append("\033[1m%s\033[0m" % seat)
    if used is None:
        parts.append("%s  context —" % name)
    else:
        frac = min(1.0, used / float(win))
        parts.append("%s%s\033[0m %s/%s \033[2m(%d%% used, %s left)\033[0m" % (
            colour(frac), bar(frac), human(used), human(win),
            round(100 * frac), human(max(0, win - used))))
    print("  ".join(parts))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A status line must never wedge the prompt.
        print("")
        sys.exit(0)

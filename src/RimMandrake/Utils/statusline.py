#!/usr/bin/env python3
"""statusline.py — the seat's name, and how much context it has left.

Wire it up in `.claude/settings.json`:

    "statusLine": {"type": "command",
                   "command": "python3 \"${CLAUDE_PROJECT_DIR}/src/RimMandrake/Utils/statusline.py\""}

Self-test against a real transcript, no Claude Code required:

    python3 src/RimMandrake/Utils/statusline.py --selftest <transcript.jsonl>

WHERE THE NUMBER COMES FROM
===========================
Claude Code hands the status line a `context_window` block on stdin —
`used_percentage`, `context_window_size` and a `current_usage` breakdown. That is
authoritative and costs nothing, so it is the primary source.

The transcript fallback below exists only for the gap: `used_percentage` is null
until the session's first API response. It derives the same figure as

    input_tokens + cache_creation_input_tokens + cache_read_input_tokens

from the LAST assistant turn. Two traps if you ever touch it: cache_read is ~99%
of the total on a long session, so summing `input_tokens` alone reads as a nearly
empty window; and each turn's figure is already cumulative, so adding turns up
multiplies the answer by the turn count.

⚠️ The status line runs on every turn with a 300 ms debounce. Keep it cheap —
the fallback tails the file rather than reading it, and only runs when the
native field is missing.

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


REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def current_item(seat, max_title=44):
    """The item this seat is working RIGHT NOW, from the rendered queue view.

    Derived, never announced: `rimflow start` re-renders the queue on write, so
    the first `## <ID> <title>` heading under `# IN PROGRESS` is the live answer.
    Returns (id, short_title) or None. Owner's ask, 2026-08-28: the scrolling
    transcript never names the item; the status line should.
    """
    if not seat:
        return None
    path = os.path.join(REPO, "infrastructure", "state", "queue", "%s.md" % seat)
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read(200_000)
    except OSError:
        return None
    in_section = False
    for line in text.splitlines():
        if line.startswith("# "):
            in_section = line.strip() == "# IN PROGRESS"
            continue
        if in_section and line.startswith("## "):
            body = line[3:].strip()
            item_id, _, title = body.partition(" ")
            title = title.strip()
            if title == item_id or not title:
                title = ""
            if len(title) > max_title:
                title = title[:max_title - 1].rstrip() + "…"
            return item_id, title
    return None


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

    cw = ev.get("context_window") or {}
    win = cw.get("context_window_size") or window_for(model_id, name)
    used = cw.get("total_input_tokens")
    pct = cw.get("used_percentage")
    if used is None:                       # null until the first API response
        used = context_used(ev.get("transcript_path"))
    if pct is None and used is not None and win:
        pct = 100.0 * used / win

    # Context sits immediately after the seat name — owner's ask, 2026-08-29:
    # the queue-item title was pushing it off to the right.
    parts = []
    if seat:
        parts.append("\033[1m%s\033[0m" % seat)
    if pct is None:
        parts.append("%s  \033[2mcontext —\033[0m" % name)
    else:
        frac = min(1.0, pct / 100.0)
        left = "%s left" % human(max(0, win - used)) if used is not None else \
               "%d%% left" % round(100 - pct)
        parts.append("%s%s\033[0m %s \033[2m%s\033[0m" % (
            colour(frac), bar(frac),
            "%s/%s" % (human(used), human(win)) if used is not None
            else "%d%%" % round(pct),
            left))
    if seat:
        item = current_item(seat)
        if item:
            parts.append("\033[36m▶ %s\033[0m\033[2m%s\033[0m" % (
                item[0], " · " + item[1] if item[1] else ""))
    cost = (ev.get("cost") or {}).get("total_cost_usd")
    if isinstance(cost, (int, float)) and cost > 0:
        parts.append("\033[2m$%.2f\033[0m" % cost)
    print("  ".join(parts))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # A status line must never wedge the prompt.
        print("")
        sys.exit(0)

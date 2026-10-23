#!/usr/bin/env python3
"""selftest_pause_arg.py — every bridge call to rimworld/pause_game names its argument `pause`.

The tool's only parameter is `pause`; an unknown kwarg such as `paused=True` is silently dropped, so the
game is never paused and the scene runs on a moving clock (PAUSE_ARG_FIX_PAUSED_NEVER_PAUSED: three
northstar scripts did exactly this). Scans every .py under src/RimMandrake; a mutant proves the scan sees it.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CALL = re.compile(r"""pause_game["']\s*,([^()]*(?:\([^()]*\)[^()]*)*)\)""", re.S)


def findings(text, name="<mem>"):
    out = []
    for m in CALL.finditer(text):
        args = m.group(1)
        if re.search(r"\bpaused\s*=", args) or re.search(r"""["']paused["']\s*:""", args):
            line = text.count("\n", 0, m.start()) + 1
            out.append("%s:%d pause_game called with `paused` (the argument is `pause`)" % (name, line))
    return out


def main():
    fails, n = [], 0
    for p in sorted(ROOT.rglob("*.py")):
        if p.name == Path(__file__).name:
            continue
        t = p.read_text(errors="replace")
        if "pause_game" not in t:
            continue
        n += 1
        fails += findings(t, str(p.relative_to(ROOT)))
    print("scanned %d files naming pause_game" % n)
    if n < 5:
        fails.append("sanity probe: expected >= 5 files naming pause_game, saw %d" % n)
    for bad in ('w.call("rimworld/pause_game", paused=True)', 'B.call("rimworld/pause_game", {"paused": True})'):
        if not findings(bad):
            fails.append("mutant stayed green: " + bad)
    if findings('w.call("rimworld/pause_game", pause=True)'):
        fails.append("the correct form was flagged")
    print("FAIL" if fails else "PASS", *fails, sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

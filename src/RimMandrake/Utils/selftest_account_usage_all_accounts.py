#!/usr/bin/env python3
"""Selftest for `account_usage.py now`: one list with a line for every account (three Claude, Codex, JPL GenAI),
each as what is LEFT. Codex present; Codex unreadable -> UNMEASURED with cause; GenAI tool absent -> `not on this
machine`; a "used 30" meter prints 70 left; nothing readable -> non-zero exit and no answer-looking line.
Fixture readers only: no codex, no genai-switch, no claude."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import account_usage as au  # noqa: E402

FAILS = []
NOW = 1793043764.0  # 2026-10-26 12:42 PDT


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


CLAUDE = {"accounts": {"lukas": {"account": "lukas", "source": "MEASURED", "week_pct_left": 40.0, "hours_to_week_reset": 10.0,
                                 "session_pct_left": None, "hours_to_session_reset": None, "stale": False,
                                 "measured_at": "2026-10-26T12:00:00-07:00", "machine": "m"}}}
CLAUDE = {"accounts": {k: au.derive_record(v, NOW) for k, v in CLAUDE["accounts"].items()}}  # read_now's shape
NO_CLAUDE = {"accounts": {}}
CODEX_OK = {"codex.week_used_pct": {"v": 46.0, "m": "MEASURED", "x": {"reading_at": au.iso(NOW - 3600)}},
            "codex.hours_to_reset": {"v": 20.0, "m": "MEASURED"}}
CODEX_BAD = {"codex.week_used_pct": {"v": None, "m": "UNMEASURED", "why": "no codex sessions directory (/x)"},
             "codex.hours_to_reset": {"v": None, "m": "UNMEASURED", "why": "no codex sessions directory (/x)"}}
GENAI_ABSENT = lambda: ("absent", None)  # noqa: E731


def line(lines, word):
    return next((ln for ln in lines if ln.startswith(word)), "")


# 1. Codex present: left = 100 - used, a Pacific reset, [measured] and an age
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_OK, GENAI_ABSENT)
cx = line(lines, "codex")
check("codex present: 54% left", "54% left" in cx and "46" not in cx, cx)
check("codex present: Pacific reset and [measured] with age", "[measured" in cx and ("PST" in cx or "PDT" in cx) and "old" in cx, cx)
check("the claude lines still lead, unchanged", lines[0] == au._fmt(CLAUDE["accounts"]["lukas"]), lines[0])

# 2. Codex unreadable: UNMEASURED with the cause, never 0
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_BAD, GENAI_ABSENT)
cx = line(lines, "codex")
check("codex unreadable: UNMEASURED with cause, no 0%", "UNMEASURED" in cx and "no codex sessions directory" in cx and " 0%" not in cx, cx)

# 3. GenAI tool absent
gx = line(lines, "jpl-genai")
check("genai absent: not on this machine", "not on this machine" in gx and "%" not in gx, gx)

# 4. a meter that reports used 30 prints 70 left
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_BAD, lambda: ("ok", "quota: 30% used, resets 2026-10-27T00:00:00Z\n"))
gx = line(lines, "jpl-genai")
check("genai used 30 prints 70 left", "70% left" in gx and "30" not in gx, gx)
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_BAD, lambda: ("ok", "quota: 25% left\n"))
check("genai left 25 stays 25 left", "25% left" in line(lines, "jpl-genai"), line(lines, "jpl-genai"))
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_BAD, lambda: ("ok", "logged in, no meter here\n"))
check("genai no percent: UNMEASURED, not 0", "UNMEASURED" in line(lines, "jpl-genai") and " 0%" not in line(lines, "jpl-genai"))
lines, n = au.account_lines(NOW, CLAUDE, lambda: CODEX_BAD, lambda: ("failed", "exit 2: boom"))
check("genai tool failed: UNMEASURED with cause", "UNMEASURED" in line(lines, "jpl-genai") and "boom" in line(lines, "jpl-genai"))

# 5. nothing readable: non-zero, and no line that looks like an answer
lines, n = au.account_lines(NOW, NO_CLAUDE, lambda: CODEX_BAD, GENAI_ABSENT)
check("all unreadable: zero readable", n == 0, n)
check("all unreadable: no line carries a percent", not any("%" in ln for ln in lines), lines)
au.read_now = lambda now=None: NO_CLAUDE
au.read_codex_points = lambda: CODEX_BAD
au.read_genai_status = GENAI_ABSENT
check("all unreadable: main exits non-zero", au.main(["now"]) != 0)
au.read_codex_points = lambda: CODEX_OK
check("one account readable: main exits 0", au.main(["now"]) == 0)

print("FAILED: " + ", ".join(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)

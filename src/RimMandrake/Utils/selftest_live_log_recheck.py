#!/usr/bin/env python3
"""selftest_live_log_recheck.py -- the post-read "same game?" recheck of every Player.log reader.

    python3 src/RimMandrake/Utils/selftest_live_log_recheck.py

GAMEENV_FIX_PROOFSITE_B7C18A7D_ITEMS_WAIT: a live proof read UNMEASURED "the running game changed while the log was
read" because the recheck compared one transient None from game_started() (an unreadable powershell.exe process list)
against the start time. No game, no powershell. It checks:
  1. a None on the recheck is re-asked; a later matching start is "same game" (no reason);
  2. a different start time is still "the running game changed while the log was read";
  3. None on every try says the start could not be re-read, never "changed";
  4. the exact old failure: probe answers None then the start -> same game, the bug's instance;
  5. live_log_check.py, nulltex_log_check.py and prove_null_thingclass_live.py all call same_game() and none compares
     game_started() against the start by hand.
Exit 0 when every check passes.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import live_log_check as llc  # noqa: E402

READERS = [os.path.join(HERE, "live_log_check.py"),
           os.path.join(SRC, "NullTexTrace", "nulltex_log_check.py"),
           os.path.join(SRC, "MandrakePatches", "prove_null_thingclass_live.py")]
fails = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        fails.append(name)


def seq(*answers):
    it = iter(answers)
    calls = []

    def probe():
        calls.append(1)
        return next(it)
    return probe, calls


T = 1793959800.123
naps = []
nosleep = naps.append

p, calls = seq(None, T)
r = llc.same_game(T, probe=p, sleep=nosleep)
check("transient None then the same start -> same game", r is None, repr(r))
check("it re-asked exactly once", len(calls) == 2, str(len(calls)))

p, _ = seq(T + 60.0)
r = llc.same_game(T, probe=p, sleep=nosleep)
check("a different start -> changed", r == "the running game changed while the log was read", repr(r))

p, calls = seq(None, None, None)
r = llc.same_game(T, probe=p, tries=3, sleep=nosleep)
check("None every try -> could not re-read, not 'changed'",
      r is not None and "could not be re-read" in r and "changed" not in r, repr(r))
check("three tries made", len(calls) == 3, str(len(calls)))

p, calls = seq(T)
check("same start at once -> same game, one ask", llc.same_game(T, probe=p, sleep=nosleep) is None and len(calls) == 1)

hand = re.compile(r"game_started\(\)\s*[!=]=")
for path in READERS:
    text = open(path, encoding="utf-8").read()
    rel = os.path.relpath(path, SRC)
    check(rel + " calls same_game()", "same_game(" in text)
    check(rel + " never compares game_started() by hand", not hand.search(text))

print("PASS" if not fails else "FAILED: %d" % len(fails))
sys.exit(1 if fails else 0)

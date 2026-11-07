#!/usr/bin/env python3
"""The memory a Relentless worker is handed (LOOP_MEMORY_DESIGN_SHORT_AND_HASH_BOUND): tried endings once, notes rewritten
at every lease, whole entries, capped. The hash half lives in Utils/selftest_selftest_cache.py, run beside this by the
item's proof. No machine state is read: every case is a fixture."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import relentless as R      # noqa: E402

fails = 0


def check(what, good, shown=None):
    global fails
    print(("ok   " if good else "FAIL ") + what + ("" if good else "  got: %r" % (shown,)))
    fails += 0 if good else 1


def note(n, words="a finding worth keeping " * 8, gen=None):
    return "- 2026-11-%02dT%02d:00:00Z gen %d: note%d %s\n" % (1 + n // 24, n % 24, n if gen is None else gen, n, words)


def ending(n, detail):
    return "- 2026-11-%02dT%02d:30:00Z gen %d ended proof_weak: %s\n" % (1 + n // 24, n % 24, n, detail)


def section(p):
    return p.split("--- learned so far ---\n", 1)[1]


def main():
    log = "/store/items/X/learned.md"
    many = "".join(note(n) for n in range(80))
    v = R.learned_view(many, [], log)
    check("the view holds its cap", len(v) <= R.LEARNED_MAX, len(v))
    check("the raw log really was over it, or this proves nothing", len(many) > R.LEARNED_MAX, len(many))
    body = v.split("\n", 1)[1]
    check("it begins on a whole entry", body.startswith("- 2026-11-"), body[:60])
    check("it ends on the newest entry", v.rstrip().endswith(note(79).rstrip()), v[-60:])
    shown = re.findall(r"note(\d+) ", v)
    check("the entries are the newest run, oldest first, with no gap",
          shown and [int(x) for x in shown] == list(range(80 - len(shown), 80)), shown)
    check("what is left out is counted and the raw log is named",
          v.startswith("(%d older note(s) not shown; the whole log: %s)" % (80 - len(shown), log)), v[:90])

    short = note(1) + note(2)
    check("a log under the cap comes back whole, no note", R.learned_view(short, [], log) == short.strip())
    check("an empty log stays empty", R.learned_view("", [], log) == "")
    glued = note(1).rstrip() + "\nmechanism: a second line\n)\n" + note(2)
    check("a continuation line stays with its entry", R.learned_view(glued, [], log) == glued.strip())
    huge = "- 2026-11-01T00:00:00Z gen 1: " + "x" * (2 * R.LEARNED_MAX) + "the end"
    v = R.learned_view(note(0) + huge, [], log)
    check("one entry over the whole cap keeps its end and the cap", v.endswith("the end") and len(v) <= R.LEARNED_MAX, len(v))

    told = "the proof named the wrong file"
    log2 = note(1) + ending(2, told) + note(3) + ending(4, "never listed anywhere")
    hist = ["gen 2 ended proof_weak: " + told, "gen 3 ended snag (x): another"]
    v = R.learned_view(log2, hist, log)
    check("an ending the brief lists is not told twice", told not in v, v)
    check("an ending the brief does not list stays", "never listed anywhere" in v, v)
    check("notes stay beside them", "note1 " in v and "note3 " in v, v)
    empty = "- 2026-11-01T00:00:00Z gen 1 ended lost: \n"
    check("an ending with no words matches nothing", "gen 1 ended lost" in R.learned_view(empty, hist, log))
    check("a note that quotes an ending is no ending", told in R.learned_view(note(1, words=told), hist, log))

    rules = json.loads((HERE / "relentless_rules.json").read_text())
    st = R.new_state("X", 0, "t")
    rows = [{"gen": 2, "end": "proof_weak", "detail": told}, {"gen": 3, "end": "lost", "detail": "the worker died"}]
    p = R.worker_prompt(st, "item", many + ending(2, told), rules, rows, None, log)
    check("the tried table reaches the brief: a dead worker's ending too",
          "Endings on record" in p and "gen 3 ended lost: the worker died" in p, p[-300:])
    check("the brief tells each listed ending once", p.count(told) == 1, p.count(told))
    check("the brief's memory is the capped view and names the log",
          len(section(p)) <= R.LEARNED_MAX and log in section(p), len(section(p)))
    one = R.worker_prompt(st, "item", ending(2, told), rules, rows[:1], None, log)
    check("a lone ending, which the brief does not list, stays in the notes", told in section(one), section(one))
    print("FAILED %d" % fails if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

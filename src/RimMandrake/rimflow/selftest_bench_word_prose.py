#!/usr/bin/env python3
"""selftest_bench_word_prose.py — step 1 of SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP: the word BENCH leaves the prose.

Owner, 2026-11-03: "for Bench, thanks for your insights. 1+2 yes, 3 hold for later, as you suggest. Let's not break
ourselves for name correctness." Step 1: everything he reads says Conductor or Relentless and BENCH.md folds into
CONDUCTOR.md. Step 3 (the clone path /home/mandrake/rm/bench, the tile name AGENT BENCH, the shard file
events/BENCH.jsonl, config keys) is HELD, so a line naming one of those may still say BENCH.
Covered, on files only (nothing launched, nothing written):
  folded    infrastructure/agents/BENCH.md is gone and CONDUCTOR.md holds the folded workshop rules
  inbound   no tracked file outside the history stores (ledger, conversations, handoffs, closed items, v3_cutover)
            names infrastructure/agents/BENCH.md; the same search finds CONDUCTOR.md (the instrument can see)
  prose     CLAUDE.md, infrastructure/agents/*.md and rimflow/roles/*.md say BENCH/Bench only on a line that explains
            the read alias, names a held path/key, or quotes history; a planted bad line is caught (sanity probe)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FAILS = []

WORD = re.compile(r"\b(BENCH|Bench)\b")
# A line may keep the word only for one of these reasons (the contract's three: read alias, held path/key, history).
ALLOWED = re.compile(
    r"alias"                                  # explains the read alias
    r"|/rm/bench|events/BENCH\.jsonl|seats\.BENCH|AGENT BENCH"   # held step 3: clone path, shard file, config key, tile
    r'|"'                                     # quotes history (an owner quote)
)
HISTORY = ("infrastructure/state/ledger/", "conversations/", "infrastructure/state/handoffs/",
           "infrastructure/state/items/closed/", "infrastructure/state/v3_cutover/")
SELF = "src/RimMandrake/rimflow/selftest_bench_word_prose.py"


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def bad_lines(text):
    """-> lines using the word for no allowed reason. A line inside an open owner quote (a `"` opened on an earlier
    line of the same paragraph and not yet closed) is quoted history too."""
    out, inside = [], False
    for ln in text.splitlines():
        if not ln.strip():
            inside = False
            continue
        if WORD.search(ln) and not inside and not ALLOWED.search(ln):
            out.append(ln)
        if ln.count('"') % 2:
            inside = not inside
    return out


def prose_files():
    out = [os.path.join(ROOT, "CLAUDE.md")]
    for d in (("infrastructure", "agents"), ("src", "RimMandrake", "rimflow", "roles")):
        p = os.path.join(ROOT, *d)
        out += sorted(os.path.join(p, f) for f in os.listdir(p) if f.endswith(".md"))
    return out


def test_folded():
    check(not os.path.exists(os.path.join(ROOT, "infrastructure", "agents", "BENCH.md")), "infrastructure/agents/BENCH.md is gone")
    cond = open(os.path.join(ROOT, "infrastructure", "agents", "CONDUCTOR.md"), encoding="utf-8").read()
    check("SEAT_BENCH_RENAME_WORD_OUTLIVED_ITS_WORKSHOP" in cond, "CONDUCTOR.md holds the folded workshop rules")


def _grep(pattern):
    r = subprocess.run(["git", "-C", ROOT, "grep", "-l", "-F", pattern], capture_output=True, text=True, timeout=120)
    if r.returncode not in (0, 1):
        return None
    return [f for f in r.stdout.splitlines() if f]


def test_inbound():
    seen = _grep("infrastructure/agents/CONDUCTOR.md")
    check(bool(seen), "sanity: the search finds files naming infrastructure/agents/CONDUCTOR.md (%s)"
          % (len(seen) if seen is not None else "git grep failed"))
    hits = _grep("infrastructure/agents/BENCH.md")
    check(hits is not None, "git grep ran")
    live = [f for f in (hits or []) if not f.startswith(HISTORY) and f != SELF]
    check(not live, "no live file names infrastructure/agents/BENCH.md: %s" % live[:8])


def test_prose():
    files = prose_files()
    check(len(files) >= 10, "the census sees the prose files (%d)" % len(files))
    for f in files:
        rel = os.path.relpath(f, ROOT)
        bad = bad_lines(open(f, encoding="utf-8").read())
        check(not bad, "%s: BENCH only where allowed%s" % (rel, (" — " + bad[0][:120]) if bad else ""))
    # sanity probes: the matcher catches a bad line and passes the allowed kinds
    check(bad_lines("Today's BENCH: design work.") == ["Today's BENCH: design work."], "probe: a bare BENCH line is caught")
    check(bad_lines("the Bench lane") != [], "probe: a capitalised Bench is caught")
    check(not bad_lines('He said, "we keep\nthe Bench + Foundry baseline."'), "probe: a line inside an open quote passes")
    check(bad_lines('a "quoted" word\nthe Bench lane') != [], "probe: a closed quote does not shelter the next line")
    check(not bad_lines("clone `/home/mandrake/rm/bench`; a low workbench; SEAT_BENCH_X; old key BENCH is a read alias"),
          "probe: path, furniture, item id and alias lines pass")


if __name__ == "__main__":
    test_folded()
    test_inbound()
    test_prose()
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    sys.exit(1 if FAILS else 0)

#!/usr/bin/env python3
"""Selftest: tunable_sweep.py names the selftest that pins a shipped tunable, and the leaf it pins, and stays quiet
about a reader that only range-checks it (RIMMANDRAKE_PIN_TUNABLES_OUT_OF_SELFTESTS A1)."""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tunable_sweep as TS  # noqa: E402

FAILS = 0


def ok(cond, what):
    global FAILS
    print("%s  %s" % ("PASS" if cond else "FAIL", what))
    FAILS += not cond


READ = "import json, os, sys\nc = json.load(open(os.path.join(os.path.dirname(__file__), 'cfg.json')))\n"


def fixture():
    d = tempfile.mkdtemp(prefix="tsweep_fx_")
    g = lambda *a: subprocess.run(["git", "-C", d, *a], check=True, capture_output=True)  # noqa: E731
    g("init", "-q", "-b", "main")
    g("config", "user.email", "t@t")
    g("config", "user.name", "t")
    json.dump({"_doc": "owner tunes these", "cap": 4, "pair": {"lo": 1, "hi": 10}, "rate": 0.5, "on": True},
              open(os.path.join(d, "cfg.json"), "w"))
    open(os.path.join(d, "selftest_pinned.py"), "w").write(READ + "sys.exit(0 if c['cap'] == 4 else 1)\n")
    open(os.path.join(d, "selftest_ranged.py"), "w").write(READ + "sys.exit(0 if c['cap'] > 0 and c['rate'] > 0 else 1)\n")
    open(os.path.join(d, "selftest_basered.py"), "w").write(READ + "sys.exit(1)\n")
    open(os.path.join(d, "selftest_pair.py"), "w").write(READ + "sys.exit(0 if c['pair']['hi'] - c['pair']['lo'] == 9 else 1)\n")
    g("add", ".")
    g("commit", "-qm", "fx")
    return d


def main():
    ok(TS.leaves({"_doc": 3, "a": [1, {"b": 2.5}], "t": True, "s": "x"}) == [(("a", 0), 1), (("a", 1, "b"), 2.5)],
       "leaves: numbers only, '_' keys and booleans skipped, list indices in the path")
    ok(TS.mutated(4) == 8 and TS.mutated(1) == 2 and TS.mutated(0) == 1 and TS.mutated(0.85) == 0.925
       and TS.mutated(2.5) == 3.75, "mutation: int doubles (or +1 below 2), a fraction goes halfway to 1, a float x1.5")
    d = fixture()
    rep = TS.sweep(d, "cfg.json", jobs=2, timeout=60, log=lambda s: None)
    ok(rep["leaves"] == 4 and rep["tests"] == 4, "it finds the 4 leaves and the 4 readers (%s, %s)" % (rep["leaves"], rep["tests"]))
    ok(rep["pinned"].get("selftest_pinned.py") == ["cap"], "the pinned reader is named with its one leaf: %s" % rep["pinned"])
    ok("selftest_ranged.py" not in rep["pinned"], "a range-checking reader is clean")
    ok(rep["base_red"] == ["selftest_basered.py"] and "selftest_basered.py" not in rep["pinned"],
       "a reader red before any change is reported base red, not judged")
    ok(rep["pinned"].get("selftest_pair.py") == ["pair/lo", "pair/hi"],
       "a reader pinning two leaves names each: %s" % rep["pinned"].get("selftest_pair.py"))
    # an uncommitted fix in the tree is what gets swept
    open(os.path.join(d, "selftest_pinned.py"), "w").write(READ + "sys.exit(0 if c['cap'] > 0 else 1)\n")
    rep2 = TS.sweep(d, "cfg.json", tests=["selftest_pinned.py"], jobs=1, timeout=60, log=lambda s: None)
    ok(rep2["pinned"] == {}, "the tree's uncommitted fix is swept, and is clean")
    raw = json.load(open(os.path.join(d, "cfg.json")))
    ok(raw["cap"] == 4, "the real config is never touched")
    print("RESULT: %s (%d failed)" % ("PASS" if not FAILS else "FAIL", FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

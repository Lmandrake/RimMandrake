#!/usr/bin/env python3
"""Selftest for run_mutation.py's pure helpers: function spans, line sharding, the synthetic patch, LPT planning,
the testq gate, the flaky filter and the per-target "what changed since its last complete run" logic.
Stdlib only (mutmut is not imported: mutant_lines is the one helper that needs it). MUTANTS_HUNT_ON_IDLE_STEVE."""
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_mutation as M  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok    " if cond else "FAIL  ") + msg)
    if not cond:
        FAILS.append(msg)


SRC = '''import os

X = 1


def outer(a):
    def inner(b):
        return b + 1
    return inner(a)


class K:
    @staticmethod
    def m(self):
        return 2
'''


def main():
    sp = M.func_spans(SRC)
    check(M.func_of(sp, 8) == "outer.inner", "func_of: a line in a nested def names the innermost (%s)"
          % M.func_of(sp, 8))
    check(M.func_of(sp, 9) == "outer", "func_of: a line after the nested def belongs to the outer")
    check(M.func_of(sp, 15) == "K.m", "func_of: a method is Class.method")
    check(M.func_of(sp, 13) == "K.m", "func_of: a decorator line belongs to its def")
    check(M.func_of(sp, 3) == "<module>", "func_of: a module-level line is <module>")

    w = {1: 5, 2: 5, 3: 5, 4: 5, 10: 20}
    g = M.split_lines(w, 2)
    check(len(g) == 2 and sorted(x for grp in g for x in grp) == sorted(w), "split_lines: 2 groups, every line once")
    check(all(grp == sorted(grp) for grp in g) and g[0][-1] < g[1][0], "split_lines: groups are contiguous runs")
    check([sum(w[x] for x in grp) for grp in g] == [20, 20], "split_lines: equal weight halves")
    check(M.split_lines(w, 99) and len(M.split_lines(w, 99)) <= len(w), "split_lines: never more groups than lines")
    check(M.split_lines({}, 3) == [[]], "split_lines: no lines -> one empty group")
    check(len(M.split_lines({7: 1}, 4)) == 1, "split_lines: one line -> one group")

    src_lines = SRC.split("\n")
    pt = M.patch_text("a/b.py", src_lines, [8, 3])
    want = "--- a/b.py\n+++ a/b.py\n@@ -0,0 +3,1 @@\n+X = 1\n@@ -0,0 +8,1 @@\n+        return b + 1\n"
    check(pt == want, "patch_text: sorted one-line added hunks carrying the source text")

    bins = M.plan_costs([("a", 10), ("b", 6), ("c", 5), ("d", 4)], 2)
    check(bins == [["a", "d"], ["b", "c"]], "plan_costs: greedy LPT, largest first onto the lightest bin (%s)" % bins)
    check(len(M.plan_costs([("a", 1)], 4)) == 1, "plan_costs: empty bins are dropped")

    with tempfile.TemporaryDirectory() as td:
        check(not M.gate_blocked(td, ["load"]), "gate: no testq state -> not blocked")
        os.makedirs(os.path.join(td, "attempts", "A1"))
        open(os.path.join(td, "current"), "w").write("A1\n")
        stp = os.path.join(td, "attempts", "A1", "state.json")
        json.dump({"phase": "load"}, open(stp, "w"))
        check(M.gate_blocked(td, ["load"]), "gate: live attempt in a gated phase blocks")
        check(not M.gate_blocked(td, ["run"]), "gate: a phase not gated does not block")
        check(not M.gate_blocked(td, []), "gate: no phases (the default) never blocks")
        old = time.time() - 1000
        os.utime(stp, (old, old))
        check(not M.gate_blocked(td, ["load"]), "gate: a state untouched for 15 min is stale, not blocking")
        os.utime(stp, None)
        open(os.path.join(td, "attempts", "A1", "result.json"), "w").write("{}")
        check(not M.gate_blocked(td, ["load"]), "gate: a finished attempt (result.json) does not block")

    fl = ("B1 procs_of x",)
    check(M.only_flaky("ok    a\nFAIL  B1 procs_of x\n", fl), "only_flaky: only the known flaky FAIL -> tolerated")
    check(not M.only_flaky("FAIL  B1 procs_of x\nFAIL  other\n", fl), "only_flaky: any other FAIL -> real failure")
    check(not M.only_flaky("Traceback ...\n", fl), "only_flaky: a crash with no FAIL line is never tolerated")
    check(not M.only_flaky("FAIL  B1 procs_of x\n", ()), "only_flaky: no flaky list -> nothing tolerated")

    names = list(M.TARGETS)
    check(M.last_shas(None) == {}, "last_shas: no last run -> nothing done")
    check(M.last_shas({"sha": "s1"}) == {n: "s1" for n in names}, "last_shas: the old one-sha form covers all")
    check(M.last_shas({"targets": {"v3_vs_v2": {"sha": "s2"}}}) == {"v3_vs_v2": "s2"}, "last_shas: per-target form")
    calls = []

    def changed(since):
        calls.append(since)
        return {"s1": ["dispatcher"], "s2": []}[since]
    shas = {n: "s1" for n in names}
    shas["v3_vs_v2"] = "s2"
    shas.pop("close_evidence")
    due = M.due_targets(shas, changed)
    check(due == [n for n in names if n in ("close_evidence", "dispatcher")],
          "due_targets: never-run + changed-since-its-own-sha, in TARGETS order (%s)" % due)
    check(sorted(calls) == ["s1", "s2"], "due_targets: one git diff per distinct sha")
    check(M.due_targets({n: "s2" for n in names}, changed) == [], "due_targets: nothing changed -> nothing due")

    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

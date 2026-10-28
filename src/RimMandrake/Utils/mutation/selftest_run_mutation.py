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


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # a zombie still answers kill(0); read its state
    try:
        return open("/proc/%d/stat" % pid).read().split(")")[-1].split()[0] != "Z"
    except OSError:
        return False


def guard_checks():
    """The testing-sim pilot MEASURED mutmut 2.5.1 leaving mutated source and live test processes behind an outer
    timeout: a timeout must kill the whole group, a SIGKILLed runner's group must be reapable, and a mutated
    module must be detected and restored from HEAD."""
    import subprocess
    with tempfile.TemporaryDirectory() as td:
        pidf = os.path.join(td, "grandchild.pid")
        t = time.time()
        rc, _ = M.run_group(["sh", "-c", "sleep 60 & echo $! > %s; wait" % pidf], 1.0,
                            stdout=subprocess.DEVNULL)
        gc = int(open(pidf).read())
        time.sleep(0.2)
        check(rc is None and time.time() - t < 10, "run_group: a timeout returns None promptly")
        check(not alive(gc), "run_group: a timeout kills the grandchild too (the whole group)")

        pg = os.path.join(td, ".mut-pgid")
        p = subprocess.Popen(["sh", "-c", "sleep 60 & echo $! > %s; wait" % pidf], start_new_session=True)
        open(pg, "w").write(str(p.pid))
        for _ in range(50):
            if os.path.exists(pidf) and open(pidf).read().strip():
                break
            time.sleep(0.05)
        gc = int(open(pidf).read())
        check(M.reap_stale(pg) and not os.path.exists(pg), "reap_stale: kills a recorded group and clears the file")
        p.wait()
        time.sleep(0.2)
        check(not alive(gc), "reap_stale: the recorded group's grandchild is gone")
        check(not M.reap_stale(pg), "reap_stale: no file -> nothing to reap")

        rep = os.path.join(td, "repo")
        os.makedirs(rep)
        git = ["git", "-C", rep, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        subprocess.run(["git", "init", "-q", rep], check=True)
        open(os.path.join(rep, "m.py"), "w").write("X = 1\n")
        subprocess.run(git + ["add", "m.py"], check=True)
        subprocess.run(git + ["commit", "-q", "-m", "m"], check=True)
        check(M.source_guard("m.py", rep) == "clean", "source_guard: untouched module -> clean")
        open(os.path.join(rep, "m.py"), "w").write("X = 2\n")
        check(M.source_guard("m.py", rep) == "restored", "source_guard: a leftover mutant is restored from HEAD")
        check(open(os.path.join(rep, "m.py")).read() == "X = 1\n", "source_guard: restored bytes are HEAD's")


def gate_checks():
    """The approved mutation rule (TESTING_POLICY_DESIGN_RIGHT_TOOL_RIGHT_TIME): a FULL run needs the module's logic
    unchanged for mutation.full_min_stable_days and the module review-CLEAN; evolving code gets a changed-functions
    run at most; the TARGETS map must hold every selftest that imports the module."""
    import subprocess
    pol = M.policy()
    check(pol["stable_days"] == 3 and pol["need_clean"] is True, "policy: read from testing_policy.json (%s)" % pol)

    # logic signature: docstrings and comments are not logic, a changed expression is
    a = 'def f(x):\n    """doc"""\n    return x + 1\n'
    check(M.logic_sig(a) == M.logic_sig('def f(x):\n    """other doc"""\n    # note\n    return x + 1\n'),
          "logic_sig: a docstring/comment edit is not a logic change")
    check(M.logic_sig(a) != M.logic_sig('def f(x):\n    """doc"""\n    return x + 2\n'),
          "logic_sig: a changed constant is a logic change")
    check(M.logic_sig(None) is None and M.logic_sig("def (:\n") is None, "logic_sig: missing/unparsable -> None")

    # the pure gate
    b = M.full_run_blockers(["a", "b", "c", "d"], {"a": 5.0, "b": 0.5, "c": None, "d": 9.0},
                            {"a": True, "b": True, "c": True, "d": False}, 3, True)
    check("a" not in b, "gate: stable 5 d + CLEAN -> allowed")
    check(any("changed" in r for r in b.get("b", [])), "gate: logic changed 0.5 d ago -> blocked (%s)" % b.get("b"))
    check(any("UNMEASURED" in r for r in b.get("c", [])), "gate: unknown logic age -> blocked, never allowed")
    check(any("CLEAN" in r for r in b.get("d", [])), "gate: not review-CLEAN -> blocked")
    check(M.full_run_blockers(["d"], {"d": 9.0}, {"d": False}, 3, False) == {}, "gate: need_clean off -> CLEAN ignored")

    # logic age from a real git history: a docstring-only commit does not reset the clock
    with tempfile.TemporaryDirectory() as td:
        def g(*args, env=None):
            return subprocess.run(["git"] + list(args), cwd=td, check=True, capture_output=True, text=True,
                                  env=dict(os.environ, **(env or {}))).stdout
        g("init", "-q")
        g("config", "user.email", "t@t")
        g("config", "user.name", "t")
        p = os.path.join(td, "m.py")
        old = str(int(time.time()) - 10 * 86400)
        open(p, "w").write(a)
        g("add", "m.py")
        g("commit", "-q", "-m", "one", env={"GIT_COMMITTER_DATE": old + " +0000", "GIT_AUTHOR_DATE": old + " +0000"})
        open(p, "w").write(a.replace("doc", "better doc"))
        g("commit", "-qam", "doc only")
        age = M.logic_age_days("m.py", td)
        check(age is not None and age > 9.5, "logic_age_days: a docstring-only commit keeps the 10-day age (%s)" % age)
        open(p, "w").write(a.replace("x + 1", "x + 3"))
        g("commit", "-qam", "logic")
        age = M.logic_age_days("m.py", td)
        check(age is not None and age < 0.1, "logic_age_days: a logic commit resets it to ~0 (%s)" % age)
        check(M.logic_age_days("nope.py", td) is None, "logic_age_days: an untracked path -> None (UNMEASURED)")

    # changed-functions scope
    src = SRC.split("\n")
    spans = M.func_spans(SRC)
    diff = "@@ -8,1 +8,1 @@\n-        return b\n+        return b + 1\n@@ -14,0 +15,1 @@\n+        return 2\n"
    fn = M.changed_funcs(diff, spans)
    check(fn == {"outer.inner", "K.m"}, "changed_funcs: hunks map to their innermost functions (%s)" % sorted(fn))
    w = {8: 3, 9: 2, 15: 4, 3: 1}
    check(M.scope_weights(w, spans, fn) == {8: 3, 15: 4}, "scope_weights: keeps only mutants inside changed functions")
    check(M.changed_funcs("", spans) == set(), "changed_funcs: no diff -> nothing in scope")
    _ = src

    # launch refuses a blocked explicit full run unless --override-why; --changed skips blocked targets
    ok, skip, refuse = M.apply_gate(["a", "b"], {"b": ["logic changed 0.5 d ago"]}, changed=False, override_why=None)
    check(refuse and ok == [], "apply_gate: an explicit full run with a blocked target is refused outright")
    ok, skip, refuse = M.apply_gate(["a", "b"], {"b": ["x"]}, changed=True, override_why=None)
    check(not refuse and ok == ["a"] and skip == ["b"], "apply_gate: --changed/nightly launches only eligible targets")
    ok, skip, refuse = M.apply_gate(["a", "b"], {"b": ["x"]}, changed=False, override_why="owner asked for a baseline")
    check(not refuse and ok == ["a", "b"], "apply_gate: --override-why lets the blocked target run")
    ok, skip, refuse = M.apply_gate(["a", "b"], {"b": ["x"]}, changed=False, override_why="  ")
    check(refuse, "apply_gate: a blank --override-why is no override")

    # cmd_launch end to end with git and the gate stubbed: a refused full run creates nothing and exits 2
    import argparse
    calls = []
    real = (M.sh, M.gate_full, M.mutant_lines)
    try:
        M.sh = lambda argv, cwd=None, check=True, timeout=600: calls.append(argv) or "deadbeef\n"
        M.gate_full = lambda names, repo: {"dispatcher": ["logic changed 0.2 d ago (< 3 d stable)"]}
        M.mutant_lines = lambda path: (_ for _ in ()).throw(AssertionError("sharding reached"))
        ns = argparse.Namespace(changed=False, targets="dispatcher", scope="full", since=None, override_why=None,
                                workers=1, max_shards=1, unit_quota="1%", slice_quota="1%", gate_phases="",
                                baseline_s="{}", run="t", shard_timeout_h=1.0)
        rc = M.cmd_launch(ns)
        check(rc == 2 and not any(c[:1] == ["systemd-run"] for c in calls),
              "cmd_launch: a blocked explicit full run exits 2 before any shard or unit (rc=%s)" % rc)
        ns.changed, ns.targets = True, None
        M.due_targets = (lambda real_due: (lambda shas, changed: ["dispatcher"]))(M.due_targets)
        rc = M.cmd_launch(ns)
        check(rc == 0, "cmd_launch: nightly/--changed with every due target blocked launches nothing, exit 0")
        ns.changed, ns.targets, ns.scope = False, "dispatcher", "changed-functions"
        check(M.cmd_launch(ns) == 2, "cmd_launch: --scope changed-functions without --since is refused")
    finally:
        M.sh, M.gate_full, M.mutant_lines = real
        import importlib
        importlib.reload(M)

    # TARGETS completeness: every selftest that imports a target module directly is in its list
    gaps = M.audit_targets(M.REPO)
    check(gaps == {}, "audit_targets: no selftest that imports a target module is missing from TARGETS (%s)" % gaps)
    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "src", "RimMandrake", "rimflow")
        os.makedirs(d)
        open(os.path.join(d, "selftest_extra.py"), "w").write("import os\nimport dispatcher as D\n")
        check("src/RimMandrake/rimflow/selftest_extra.py" in M.audit_targets(td).get("dispatcher", []),
              "audit_targets: sanity probe - a planted importing selftest is reported")


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

    guard_checks()
    gate_checks()
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

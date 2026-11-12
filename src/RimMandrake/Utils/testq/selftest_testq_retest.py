#!/usr/bin/env python3
"""selftest_testq_retest.py - owner ruling by card 2026-10-31, "Retest only after a code change": an item is tested
once per code version; a harness-invalid run is repaired, never counted (RETEST_RULE_ONCE_PER_CODE_VERSION).

Offline over hand-made done records with fake git, probe and ledger. Proves: a verdict of any kind at the chain's
current version keeps it out of every rank; a new version frees it once; a run from before chain_versions settles
only while its identity stands; a --rows job settles nothing; a harness row is no verdict, a real GAP is; a chain with
a FAIL keeps its verdict; a held chain waits for its repair item, one item per distinct cause, a new generation after
a closed one; the code version ignores harness, flags and docs behind @mod_hash; runtime_hash needs no relpath.
"""
import json
import os
import shutil
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "modcheck"))
import gaps as G        # noqa: E402
import retest as R      # noqa: E402
import schema as S      # noqa: E402

FAILS = []
NOW = S.parse_ts("2026-10-31T12:00:00Z")
MOD = "FlowWorks"
OWED = "UNMEASURED: owed, no predicate yet: x"
DIED = "in modcheck's preview plan, absent from the sheet"
NOSELFTEST = "ExpectationFailed: UNMEASURED: the FlowWorks SelfTest did not run (rc=2)"


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def row(chain, name, verdict, detail="", validity=None):
    return {"chain": chain, "row": name, "verdict": verdict, "detail": detail, "validity": validity}


def rec(i, rows, versions=None, ident="A", sha="s0", selector=None, outcome="DONE", cause=None, note=""):
    fin = "2026-10-%02dT10:00:00Z" % i
    res = {"outcome": outcome, "cause": cause, "note": note, "started": fin, "finished": fin, "runner_sha": sha,
           "rows": rows, "deployed": {"mods": {MOD: {"dll_sha256": ident, "defs_sha256": "d"}},
                                      "modsconfig_sha256_prerun": "m"}}
    if versions is not None:
        res["chain_versions"] = versions
    job = {"id": "J%02d" % i, "mod": MOD, "submitted": fin, "requested_by": "x", "purpose": "guard",
           "selector": selector or {"chains": sorted({r["chain"] for r in rows if r["chain"]})}}
    return {"finished": fin, "job": job, "result": res}


def fake_git(moved=False):
    def g(*args):
        if args[0] == "diff":
            return "src/x.cs\n" if moved else ""
        return ""
    return g


def world(states=None):
    items = {k: types.SimpleNamespace(state=v, title="", owed_levels=lambda: [], history=[])
             for k, v in (states or {}).items()}
    return types.SimpleNamespace(), [], types.SimpleNamespace(items=items)


def rank(recs, versions, moved=False, w=None, item_chains=None):
    def prober(mod, items, since):
        return {"chains": sorted(versions), "offline": [], "item_chains": item_chains or {}, "changed": {},
                "versions": versions}
    return G.rank(MOD, 5, NOW, recs, lambda c: False, world=w or world(), g=fake_git(moved), prober=prober)


def remote_lookup():
    """`retest.py passed <job-id>` off the dispatcher's machine (HARNESS_REPAIR_CAUSE_17704C88): the local queue is
    empty there, so the job is read from the dispatcher's queue over ssh; a job in neither is a clean exit 2, never a
    TypeError. A fake `ssh` on PATH serves the remote queue from a temp dir."""
    import contextlib
    import io
    d = tempfile.mkdtemp(prefix="retest_remote_")
    keep = {k: os.environ.get(k) for k in ("PATH", "RM_HOST", "TESTQ_QUEUE_SSH", "FAKE_REMOTE_Q")}
    try:
        remote_q = os.path.join(d, "remote")
        os.makedirs(os.path.join(remote_q, "done"))
        bad = rec(1, [], outcome="INVALID", cause="HARNESS",
                  note="modcheck exit 1 and no sheet JSON: RuntimeError: launch gate REFUSES to start a map")
        good = rec(2, [row("c", "r", "PASS")])
        for name, r in (("JBAD", bad), ("JGOOD", good)):
            with open(os.path.join(remote_q, "done", name + ".json"), "w") as f:
                json.dump(r, f)
        bindir = os.path.join(d, "bin")
        os.makedirs(bindir)
        with open(os.path.join(bindir, "ssh"), "w") as f:     # last arg is the remote command; the queue path is rewritten
            f.write('#!/bin/sh\nfor a; do last="$a"; done\nexec sh -c "$(printf %%s "$last" | sed "s#%s#$FAKE_REMOTE_Q#g")"\n'
                    % R_QHOME())
        os.chmod(os.path.join(bindir, "ssh"), 0o755)
        os.environ.update(PATH=bindir + os.pathsep + os.environ["PATH"], RM_HOST="stevedesktop",
                          TESTQ_QUEUE_SSH="fake@host", FAKE_REMOTE_Q=remote_q)
        item = R.repair_base(R.job_cause(bad["result"]))
        check(item == "HARNESS_REPAIR_CAUSE_17704C88", "the fixture carries the real sighting's cause: %s" % item)

        def run(job):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = R.main(["passed", job, item])
            return code, out.getvalue()
        code, out = run("JBAD")
        check(code == 1 and "still carries the cause" in out, "a remote record that carries the cause exits 1: %r" % out)
        code, out = run("JGOOD")
        check(code == 0, "a remote record with verdicts exits 0: %d %r" % (code, out))
        code, out = run("JNONE")
        check(code == 2 and "in no queue state" in out and "fake@host" in out,
              "a job in no queue is a clean exit 2 naming where it looked: %r" % out)
        os.environ["TESTQ_QUEUE_SSH"] = ""
        code, out = run("JBAD")
        check(code == 2 and "NoneType" not in out, "with the remote off, a missing job is exit 2, no TypeError: %r" % out)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(d, ignore_errors=True)


def R_QHOME():
    import testq as T
    return T.QHOME


def main():
    gap = [row("a", "r1", "PASS"), row("a", "r2", "UNMEASURED", OWED)]
    passed = [row("b", "r3", "PASS")]
    failed = [row("c", "r4", "FAIL", "boom", "valid")]
    # one verdict per code version, of any kind, in every rank
    recs = [rec(1, gap + passed + failed, {"a": "v1", "b": "v2", "c": "v3"})]
    g = rank(recs, {"a": "v1", "b": "v2", "c": "v3"}, item_chains={"OWED_ITEM": ["a", "b", "c"]})
    check(g["rank"] is None and g["pick"] == [], "a GAP, a PASS and a FAIL at the version are never picked: %s" % g["text"])
    g = rank(recs, {"a": "v9", "b": "v2", "c": "v3"})
    check(g["pick"] == ["a"], "a new version frees that chain alone: %s" % g["pick"])
    # the one retest happens once
    recs2 = recs + [rec(2, gap, {"a": "v9"}, sha="s1")]
    check(rank(recs2, {"a": "v9", "b": "v2", "c": "v3"})["rank"] is None, "the new version's own GAP settles it")
    # a run from before chain_versions settles while its identity stands, not after
    old = [rec(1, gap + passed)]
    check(rank(old, {"a": "v1", "b": "v2"})["rank"] is None, "a pre-rule GAP at the identity is not re-picked")
    check(rank(old, {"a": "v1", "b": "v2"}, moved=True)["pick"] == ["a", "b"], "source moved: each pre-rule chain once")
    # unknown version: the identity rule, and the plan says so
    check(rank(old, {"a": None, "b": None})["rank"] is None, "no version known: the identity still settles")
    # same sha, different version: the instrument disagrees with itself and the plan must say so
    g = rank([rec(1, gap, {"a": "v1"}, sha="s9")], {"a": "v2"})
    check(any("skew" in b for b in g["blind"]) or g["pick"] == ["a"], "a version moved with no file moved is visible")
    # a prefix job says nothing about the chain
    check(rank([rec(1, gap, {"a": "v1"}, selector={"rows": ["r1"]})], {"a": "v1"})["pick"] == ["a"],
          "a --rows job settles nothing")
    # flake repeats are gone
    fl = [rec(1, passed, {"b": "v2"}), rec(2, [row("b", "r3", "FAIL", "x", "valid")], {"b": "v2"})]
    g = rank(fl, {"b": "v2"})
    check(g["rank"] is None and g["flaky"] == ["b"], "a flaky chain is reported, not repeated at its version")

    # harness rows
    kept, held, sigs = R.split_rows([row("a", "r1", "PASS"), row("a", "r2", "UNMEASURED", NOSELFTEST), row("b", "r3", "PASS")])
    check([r["row"] for r in kept] == ["r3"] and len(held) == 2 and list(sigs) == ["a"], "a harness chain leaves the verdict")
    kept, held, sigs = R.split_rows(gap)
    check(len(kept) == 2 and not held, "a row owed is a real GAP, a verdict")
    kept, held, sigs = R.split_rows([row("c", "r4", "FAIL", "x", "valid"), row("c", "r5", "UNMEASURED", NOSELFTEST)])
    check(len(kept) == 2 and not held, "a real FAIL stands whatever else broke")
    kept, held, sigs = R.split_rows([row(None, "r9", "NOT_RUN", DIED), row("a", "r1", "PASS")])
    check(len(kept) == 1 and len(held) == 1 and R.ORPHAN in sigs, "a row absent from the sheet is the harness's")
    kept, held, sigs = R.split_rows([row("a", "r1", "UNMEASURED", "canary red, chain body not run -- the session is HARNESS"),
                                     row("b", "r2", "UNMEASURED", "upstream failed -- this chain's state is meaningless")])
    check(not kept and set(sigs) == {"a", "b"}, "a chain downstream of a harness chain goes with it")
    check(R.split_rows([row("b", "r2", "UNMEASURED", "upstream failed -- this chain's state is meaningless")])[1] == [],
          "upstream failed alone is the suite's own verdict")
    check(R.split_rows([row("a", "r", "UNMEASURED", "x", "invalid")])[1] != [], "validity invalid is the harness's")
    # TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD: a reader row its driver never delivered is the harness's, not a GAP
    for det in ("UNMEASURED: no proof_hose result at the current mod hash: run `python.exe x/proof_hose.py --live`",
                "ExpectationFailed: UNMEASURED: live check owed (SPRINKLER_X) -- no sprinkler_live.py result at the "
                "current mod hash carries this row: run it",
                "UNMEASURED: no drawbridge_result_*.json result at the current mod hash"):
        kept, held, sigs = R.split_rows([row("h", "r1", "PASS"), row("h", "r2", "UNMEASURED", det)])
        check(not kept and len(held) == 2 and sigs.get("h", "").startswith("driver_undelivered"),
              "an undelivered driver row holds its chain: %s" % det[:50])
    kept, held, sigs = R.split_rows([row("h", "r1", "UNMEASURED", "UNMEASURED: live check owed -- a look by eye")])
    check(len(kept) == 1 and not held, "a live check owed with no driver named stays a GAP")
    # causes
    a = R.job_cause({"outcome": "INVALID", "cause": "HARNESS", "note": "modcheck exit 5 and no sheet JSON: tail 12:30"})
    b = R.job_cause({"outcome": "INVALID", "cause": "HARNESS", "note": "modcheck exit 5 and no sheet JSON: other"})
    c = R.job_cause({"outcome": "INVALID", "cause": "HARNESS", "note": "modcheck exit 9 and no sheet JSON: other"})
    d = R.job_cause({"outcome": "INVALID", "cause": "HARNESS",
                     "note": "modcheck exit 5 and no sheet JSON: x IndeterminateError: y"})
    check(a == b and a != c and a != d, "the cause is the exit and the exception, never the tail: %s" % a)
    check(R.job_cause({"outcome": "INVALID", "cause": "BLOCKED_SELECTION", "note": "n"}) is None, "a refused selection is no fault")
    check(R.job_cause({"outcome": "INVALID", "cause": "CANARY", "note": "n"}) is None, "a paused lane has its own finding")
    check(R.job_cause({"outcome": "DONE"}) is None, "DONE has no job cause")
    # STEVE_LANE_UNSTICK_BRAKED_UNOWNED_8EB8: a stale load has its own signature, not the no-sheet catch-all
    old = {"outcome": "INVALID", "cause": "HARNESS",
           "note": "modcheck exit 1 and no sheet JSON: implestairs; loaded but not composed: adaptive.storage.framework"}
    new = {"outcome": "INVALID", "cause": "HARNESS", "harness_cause": "stale_load",
           "note": "stale_load (ModsConfig not left on the composed list, so a restart cannot help): x"}
    again = dict(new, stale_load_bounced="not loaded: rw.mod.simplestairs")
    check(R.stale_load(old) == "repaired" and R.stale_load(new) == R.stale_load(again) == "unrepaired",
          "a stale load from before the worker could restart is repaired; one the worker saw and could not fix is not")
    check(R.job_cause(old) != R.job_cause(again) and "stale_load" in R.job_cause(old) + R.job_cause(new)
          and R.job_cause(old) != a, "a stale load is its own cause, apart from the exit-1 no-sheet one: %s" % R.job_cause(old))
    check(R.stale_load({"outcome": "DONE", "harness_cause": "stale_load", "stale_load_bounced": "x"}) is None
          and R.stale_load({"outcome": "INVALID", "cause": "HARNESS", "note": "modcheck exit 5"}) is None,
          "a DONE run after the restart, or another harness death, is no stale load")
    gone = {"outcome": "INVALID", "cause": "HARNESS", "harness_cause": "mod_not_installed",
            "note": "mod_not_installed (install it on this host; no restart spent): no folder on this host holds "
                    "ray1203.simplecamerasetting (install it; a restart cannot load it): loaded but not composed: x"}
    check(R.stale_load(gone) is None and "mod_not_installed" in (R.job_cause(gone) or "")
          and R.job_cause(gone) != R.job_cause(new),
          "MODCHECK_STALE_LOAD_FIX_UNINSTALLED_MOD: a mod the host lacks is its own cause, never stale_load: %s"
          % R.job_cause(gone))
    stale = {"outcome": "INVALID", "cause": "DEPLOY", "note": "companion STALE JawaBench.BridgeTools.dll not built from this job's sources"}
    check(R.companion_stale(stale) and R.job_cause(stale) is None, "a stale companion files no repair and holds no chain")
    other = {"outcome": "INVALID", "cause": "DEPLOY", "note": "sync refused"}
    check(not R.companion_stale(other) and R.job_cause(other), "any other deploy failure still is a cause")
    base = R.repair_base(a)
    check(R.repair_base(b) == base and R.repair_base(c) != base and len(base) <= 44, "one name per cause: %s" % base)
    check(R.repair_slot({}, base) == (base, "file"), "first sight files")
    items = world({base: "proposed"})[2].items
    check(R.repair_slot(items, base) == (base, "note"), "a second sight notes the open item")
    items = world({base: "done"})[2].items
    check(R.repair_slot(items, base) == (base + "_2", "file"), "after a closed repair, a new generation")
    many = {base + ("_%d" % g if g > 1 else ""): types.SimpleNamespace(state="done") for g in range(1, 13)}
    check(R.repair_slot(many, base) == (base + "_13", "file"), "a twelfth recurrence still files: no hold ever lapses")
    cause_many = "held: " + base
    bm = R.repair_base(cause_many)
    deep = {bm + ("_%d" % g if g > 1 else ""): types.SimpleNamespace(state="done" if g < 13 else "doing") for g in range(1, 14)}
    check(R.repair_open(deep, cause_many), "the thirteenth generation still holds")
    two = R.split_rows([row("a", "r1", "UNMEASURED", NOSELFTEST), row("a", "r2", "NOT_RUN", DIED)])[2].get("a") or ""
    check(" + " in two, "two kinds of fault in one chain are both named: one repair must not release the other")
    full = rec(29, [row(None, "r9", "NOT_RUN", DIED), row("a", "r1", "PASS")], selector={"full": True})
    frun = G.valid_runs(MOD, [full])
    held_full = G.harness_last(MOD, frun, [full], ["a", "b", "c"])
    check(sorted(held_full) == ["b", "c"], "a --full run that died holds the chains it never reached: %s" % sorted(held_full))

    # the other doors: a submit by hand asks the same question, and answers for a reason
    import argparse
    import testq as T
    # hermetic: the live ledger routes items to Test Pilots, and pilot_stop on it pays a modcheck probe per ask (50-150 s)
    saved = T.retest_stop, T.FILLER, T.pilot_stop
    T.retest_stop = lambda mod: {"a", "b"}
    T.pilot_stop = lambda mod: {}
    try:
        ask = lambda **k: T.already_tested(argparse.Namespace(mod=MOD, by=k.pop("by", "BENCH"), **k), {}, {"chains": ["a", "b"]})
        check(ask() and "retest" in ask(), "a submit of settled chains is refused")
        check(ask(retest_why="the flake is the question") is None, "--retest-why overrides")
        check(ask(by=T.FILLER) is None, "the filler has asked already")
        check(T.already_tested(argparse.Namespace(mod=MOD, by="BENCH"), {"full": True}, {"chains": ["a", "c"]}),
              "a --full run with one settled chain would rerun it: it asks for a reason too")
        check(T.already_tested(argparse.Namespace(mod=MOD, by="BENCH"), {}, {"chains": ["a", "c"]}) is None,
              "one unsettled chain lets the job through")
    finally:
        T.retest_stop = saved[0]
        T.pilot_stop = saved[2]

    # a held chain does not spin
    bad = rec(2, [], outcome="INVALID", cause="HARNESS", note="modcheck exit 5 and no sheet JSON: x", selector={"chains": ["a", "b"]})
    recs = [rec(1, gap + passed, {"a": "v1", "b": "v2"}), bad]
    g = rank(recs, {"a": "v7", "b": "v8"}, w=world({base: "proposed"}))
    check(g["rank"] is None and sorted(g["held"]) == ["a", "b"], "an open repair holds its chains at any version: %s" % g["text"])
    g = rank(recs, {"a": "v7", "b": "v8"}, w=world({base: "done"}))
    check(g["rank"] is not None and g["held"] == [] and "a" in g["pick"], "a closed repair frees them: %s" % g["text"])
    hr = rec(2, [row("a", "r2", "UNMEASURED", NOSELFTEST)], {"a": "v1"})
    sig = R.split_rows(hr["result"]["rows"])[2]["a"]
    recs = [rec(1, gap, {"a": "v0"}), hr]
    g = rank(recs, {"a": "v1"}, w=world({R.repair_base(sig): "proposed"}))
    check(g["rank"] is None and g["held"] == ["a"], "a harness run in a DONE job is no verdict and holds the chain")
    g = rank(recs, {"a": "v1"}, w=world({R.repair_base(sig): "done"}))
    check(g["pick"] == ["a"], "and its version stays unsettled once the repair closes")
    recs = [hr, rec(3, gap, {"a": "v1"})]
    check(rank(recs, {"a": "v1"}, w=world({R.repair_base(sig): "proposed"}))["held"] == [], "a later real run ends the hold")

    # the code version
    import gate as GT
    check(GT.version_inputs(["a.py", "?n/*.py", "?n/x_result_*.json", "@mod_hash"]) == ["a.py", "?n/*.py"],
          "a driver's result file is no code: the run would move the version it measured")
    import status as ST
    d = tempfile.mkdtemp(prefix="retest")
    try:
        sl = os.path.join(d, "S")
        os.makedirs(sl)
        for name, text in (("hlp.py", "H = 1\n"), ("valid.py", "from hlp import H\n\n\ndef chain():\n    return H\n")):
            with open(os.path.join(sl, name), "w") as f:
                f.write(text)
        ns = {}
        with open(os.path.join(sl, "valid.py")) as f:
            exec(compile(f.read().replace("from hlp import H", "H = 1"), os.path.join(sl, "valid.py"), "exec"), ns)
        harness = {os.path.join(sl, "hlp.py")}
        before = GT.code_slice(ns["chain"], os.path.join(sl, "valid.py"), sl, {}, harness)
        with open(os.path.join(sl, "hlp.py"), "w") as f:
            f.write("H = 2\n")
        after = GT.code_slice(ns["chain"], os.path.join(sl, "valid.py"), sl, {}, harness)
        check(before["code"] and before["code"] != after["code"], "the gate's key still moves on the harness")
        one = GT.inputs_hash(["*.py"], sl, harness)[0]
        with open(os.path.join(sl, "hlp.py"), "w") as f:
            f.write("H = 3\n")
        check(one and one == GT.inputs_hash(["*.py"], sl, harness)[0], "nor through a declared input")
        check(before["version_code"] and before["version_code"] == after["version_code"],
              "a harness edit is no code change: it must not reopen a settled version")
        mod = os.path.join(d, "M")
        os.makedirs(os.path.join(mod, "Defs"))
        with open(os.path.join(mod, "Defs", "a.xml"), "w") as f:
            f.write("<a/>")
        real = os.path.relpath
        def nope(*a):
            raise ValueError("path is on mount '\\\\\\\\wsl.lo'")
        os.path.relpath = nope
        try:
            h1 = ST.runtime_hash(mod)
        except ValueError:
            h1 = None
        finally:
            os.path.relpath = real
        check(bool(h1) and h1 == ST.runtime_hash(mod + os.sep), "runtime_hash needs no relpath (the UNC crash)")
        base_parts = dict(chain="c", runtime="r", composed=["x"], minimal=["y"], repo_runtime={"x": "1"}, code="k",
                          inputs=None, declared=None)
        v = GT.code_version(**base_parts)
        check(v == GT.code_version(**base_parts) and v != GT.code_version(**dict(base_parts, runtime="r2")),
              "the runtime moves the version")
        check(v != GT.code_version(**dict(base_parts, code="k2")), "the chain's own code slice moves it")
        check(v != GT.code_version(**dict(base_parts, repo_runtime={"x": "2"})), "a dependency's runtime moves it")
        check(GT.code_version(**dict(base_parts, runtime=None)) is None, "no runtime, no version")
        check(GT.version_inputs(["@mod_hash", "Defs/*.xml"]) == ["Defs/*.xml"] and GT.version_inputs(None) is None,
              "a doc behind @mod_hash does not move the version")
        check("code_version" in GT.stamp({"code_version": "v"}), "the stamp carries it to the sheet")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    sm = {"chains": [{"name": "a", "gate": {"code_version": "v"}}, {"name": "b", "gate": {}}, {"name": "c"}]}
    check(S.chain_versions(sm) == {"a": "v"}, "the sheet's versions reach the result")
    remote_lookup()
    if FAILS:
        print("%d FAILED" % len(FAILS))
        return 1
    print("selftest_testq_retest: all ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

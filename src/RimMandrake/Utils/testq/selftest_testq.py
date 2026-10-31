#!/usr/bin/env python3
"""selftest_testq.py - the queue and dispatch tick (testq.py) against the REAL worker (worker.py) behind a fake ssh.

The fake ssh runs the remote command locally (or exits 255 while a 'down' flag file exists); the worker runs on a
temp TESTQ_HOME with mock phases, as in infrastructure/stevedesktop/selftest_steve_worker.py. Proves: submit and
duplicate submit, priority order, owner_gate / not_before / archmagi held back, one job at a time across ticks,
result fetched and acked, ssh down -> no sends and a timed probe, cancel, supersede, a dead attempt finalized then
retried once (attempt id asked first), a red canary pausing the lane until resume --reason, a game dead
mid-run -> GAME_DIED retried once without a pause, orphan results kept, show within 20 lines, a concurrent tick refused.
"""
import fcntl
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TESTQ = os.path.join(HERE, "testq.py")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "bridgetools"))
import schema as S  # noqa: E402
import companion_identity as CI  # noqa: E402

FAILS = []
FAKE_SSH = r'''
import os, subprocess, sys
if os.path.exists(os.environ["FAKE_SSH_DOWN"]):
    sys.stderr.write("ssh: connect to host: No route to host\n"); sys.exit(255)
with open(os.environ["FAKE_SSH_LOG"], "a") as f:
    f.write(sys.argv[-1] + "\n")
sys.exit(subprocess.run(["bash", "-c", sys.argv[-1]]).returncode)
'''
MOCK = r'''
import json, os, sys, time
_t0 = time.time()
while os.path.exists(os.environ.get("MOCK_HOLD", "")) and time.time() - _t0 < 60:   # held mid-run by the test
    time.sleep(0.05)
if os.environ.get("MOCK_HOLD"):   # why the hold ended: read back by the second-tick diagnostic below
    with open(os.environ["MOCK_HOLD"] + ".log", "a") as _f:
        _f.write("left after %.2fs hold_exists=%s pid=%d\n" % (time.time() - _t0, os.path.exists(os.environ["MOCK_HOLD"]), os.getpid()))
name = "Mock_%d" % int(time.time() * 1000000)
summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "PASS", "detail": "ok"},
                                                    {"name": "r2", "verdict": "FAIL", "detail": "bad"}]}]}
if os.environ.get("MOCK_MODE") == "canary":
    print("vanilla canary RED")
    summary = {"chains": [{"name": "c1", "components": [{"name": "r1", "verdict": "UNMEASURED",
                                                         "detail": "vanilla canary red"}]}]}
json.dump({"mod": "Mock", "summary": summary}, open(os.path.join(os.environ["TESTQ_SHEET_DIR"], name + ".json"), "w"))
print("sheet Transient/modcheck/%s.html" % name)
'''


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def t_bad_selection():
    """submit refuses a row/chain the mod does not declare BEFORE queueing (a bad row id burned a runner slot)."""
    import testq as T
    bad = T.bad_selection("FlowWorks", {"rows": ["T12"]})
    check(bad and "unknown row 'T12'" in bad, "a row id no chain declares is refused: %s" % bad)
    bad = T.bad_selection("FlowWorks", {"chains": ["no_such_chain_zz"]})
    check(bad and "unknown chain" in bad, "a chain name the mod lacks is refused: %s" % bad)
    check(T.bad_selection("FlowWorks", {"rows": ["T12_no_routine_salt"]}) is None, "a real row id passes")
    check(T.bad_selection("Mock", {"rows": ["zz"]}) is None, "a mod modcheck cannot find is not judged here")
    # TESTQ_JOB_PLAN_WIRE_PREVIEW: every selection modcheck would refuse on the worker is refused at submit, and the
    # plan (the rows it will really run, prerequisites included) comes back from the same preview
    bad = T.bad_selection("FlowWorks", {"chains": ["core_offline"]})
    check(bad and "offline" in bad, "an offline-only chain selection is refused before queueing: %s" % bad)
    check(T.unknown_chains(bad) == {"core_offline"}, "the filler reads the offline chain out of that refusal")
    bad, rows = T.preview_plan("FlowWorks", {"rows": ["T12_no_routine_salt"]})
    check(bad is None and rows and rows[-1] == "T12_no_routine_salt" and len(rows) > 1,
          "the plan is modcheck's: the row plus the prerequisites it runs first: %s" % (rows and len(rows)))
    check(T.preview_plan("Mock", {"rows": ["zz"]}) == (None, None), "no mod folder: no refusal and no plan")

    def rec(mod, start, fin, n, outcome="DONE"):
        return {"job": {"mod": mod}, "result": {"outcome": outcome, "started": start, "finished": fin,
                                                 "rows": [{"verdict": "PASS"}] * n + [{"verdict": "NOT_RUN"}] * 5}}
    recs = [rec("FlowWorks", "2026-10-01T00:00:00Z", "2026-10-01T00:10:00Z", 10),     # 60 s/row
            rec("FlowWorks", "2026-10-02T00:00:00Z", "2026-10-02T00:20:00Z", 10),     # 120 s/row
            rec("FlowWorks", "2026-10-03T00:00:00Z", "2026-10-03T00:15:00Z", 10),     # 90 s/row
            rec("FlowWorks", "2026-10-04T00:00:00Z", "2026-10-04T09:00:00Z", 1, "INVALID"),
            rec("Else", "2026-10-04T00:00:00Z", "2026-10-04T09:00:00Z", 1)]
    check(T.row_seconds("FlowWorks", recs) == 90, "estimate: median s per executed row over DONE jobs of the mod "
          "(NOT_RUN rows, other outcomes and mods ignored): %s" % T.row_seconds("FlowWorks", recs))
    check(T.row_seconds("Nothing", recs) is None, "no history: no estimate")
    tmp = tempfile.mkdtemp(prefix="rf_testq_plan_")
    try:
        os.makedirs(os.path.join(tmp, "done"))
        json.dump(dict(recs[0], job={"mod": "FlowWorks", "id": "Jx"}), open(os.path.join(tmp, "done", "Jx.json"), "w"))
        r = subprocess.run([sys.executable, TESTQ, "submit", "FlowWorks", "--rows", "T12_no_routine_salt", "--purpose",
                            "fix", "--by", "BENCH", "--sha", "abc1234", "--no-sha-check"],
                           env=dict(os.environ, TESTQ_QUEUE=tmp), capture_output=True, text=True, timeout=120)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            out = {"raw": r.stdout + r.stderr}
        n = len(rows or [])
        check(out.get("state") == "pending" and out.get("planned_rows") == n and out.get("est_s") == 60 * n,
              "submit reports modcheck's plan and an estimate (%d rows x 60 s): %s" % (n, out))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_driver_sizing():
    """TESTQ_SIZING_FIX_DRIVER_BUDGET_FROM_PLAN: a default targeted thirst job must give its drivers room. The worker
    hands the drivers half the job timeout and modcheck never starts a driver whose timeout_s exceeds the budget left
    (06c8d1e10d), so a 2700 s job SKIPPED_BUDGET thirst_live on every targeted thirst fix job. End to end: submit, the
    REAL worker's budget for the job's timeout, the REAL drivers.run over the FlowWorks table on a clock where every
    driver runs its full timeout and the map recovery between them takes 100 s: nothing may be skipped."""
    import importlib.util
    tmp = tempfile.mkdtemp(prefix="rf_testq_size_")
    try:
        r = subprocess.run([sys.executable, TESTQ, "submit", "FlowWorks", "--rows", "T15_slime_effects", "--purpose",
                            "fix", "--by", "BENCH", "--sha", "abc1234", "--no-sha-check"],
                           env=dict(os.environ, TESTQ_QUEUE=tmp), capture_output=True, text=True, timeout=120)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            out = {"raw": (r.stdout + r.stderr)[-400:]}
        jobs = glob.glob(os.path.join(tmp, "pending", "*.json"))
        job = json.load(open(jobs[0])) if jobs else {}
        check(out.get("drivers") == ["thirst_live", "sprinkler_live"] and out.get("driver_need_s"),
              "submit reports the drivers the plan starts and what they need: %s" % out)
        wp = os.path.join(REPO, "infrastructure", "stevedesktop", "worker.py")
        spec = importlib.util.spec_from_file_location("steve_worker_sizing_probe", wp)
        w = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(w)
        exp = w.driver_budget_export(job.get("timeout_s", 2700))
        budget = int(exp.split("MODCHECK_DRIVERS_BUDGET_S=")[1].split()[0])
        for d in (os.path.join(HERE, ".."), os.path.join(HERE, "..", "modcheck")):   # validation.py: `from modcheck`
            if d not in sys.path:
                sys.path.insert(0, d)
        import drivers as D
        fws = importlib.util.spec_from_file_location("testq_sizing_fw", os.path.join(REPO, "src", "RimMandrake",
                                                                                     "FlowWorks", "validation.py"))
        fw = importlib.util.module_from_spec(fws)
        fws.loader.exec_module(fw)
        clock = [0.0]

        class _T(object):
            @staticmethod
            def monotonic():
                return clock[0]

        def full_timeout(argv, cwd, timeout_s):
            clock[0] += timeout_s
            return None, "killed"

        def after(rec):
            clock[0] += 100

        saved_t, saved_env = D.time, os.environ.get(D.ENV)
        D.time, os.environ[D.ENV] = _T, "1"
        try:
            recs = D.run(fw.suite, "/m", ["thirst"], budget_s=budget, _call_fn=full_timeout, after=after,
                         log=open(os.devnull, "w"))
        finally:
            D.time = saved_t
            if saved_env is None:
                os.environ.pop(D.ENV, None)
            else:
                os.environ[D.ENV] = saved_env
        check(recs and all(x["status"] != "SKIPPED_BUDGET" for x in recs),
              "a default targeted thirst job (timeout %s, driver budget %d s) starts every driver even when each runs "
              "its whole timeout: %s" % (job.get("timeout_s"), budget, [(x["driver"], x["status"]) for x in recs]))
        T = __import__("testq")
        t, need, warn = T.sized_timeout(2700, [])
        check((t, need, warn) == (2700, 0, None), "no drivers planned: the asked timeout stands: %s" % ((t, need, warn),))
        t, need, warn = T.sized_timeout(14400, [{"name": "x", "timeout_s": 9000}])
        check(t == 14400 and warn and "SKIPPED_BUDGET" in warn, "drivers past the worker's cap: warned, not hidden")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_sweep_split():
    """TESTQ_SWEEP_FIX_DRIVERS_OVER_CAP: a full sweep whose drivers need more than the worker's driver cap is queued as
    chain-group jobs that each fit, and together start every driver (none is SKIPPED_BUDGET)."""
    import testq as T
    d = [{"name": n, "timeout_s": t} for n, t in (("a", 3000), ("b", 3000), ("c", 3000), ("d", 3000))]
    dc = {"a": ["c1"], "b": ["c2", "c3"], "c": ["c3"], "d": ["c4"]}
    g = T.split_sweep(d, dc, ["c1", "c2", "c3", "c4", "c5"], cap_s=7200)
    check(len(g) == 2 and sorted(sum(g, [])) == ["c1", "c2", "c3", "c4", "c5"], "split covers every chain once: %s" % g)
    check(any({"c2", "c3"} <= set(x) for x in g), "drivers sharing a chain stay in one job: %s" % g)
    check(T.split_sweep(d[:2], dc, ["c1", "c2"], cap_s=7200) == [["c1", "c2"]], "when it all fits, one job")
    tmp = tempfile.mkdtemp(prefix="rf_testq_split_")
    try:
        r = subprocess.run([sys.executable, TESTQ, "sweep", "FlowWorks", "--by", "BENCH"],
                           env=dict(os.environ, TESTQ_QUEUE=tmp), capture_output=True, text=True, timeout=240)
        jobs = [json.load(open(p)) for p in glob.glob(os.path.join(tmp, "pending", "*.json"))]
        check(len(jobs) >= 2 and all(j["purpose"] == "sweep" and j["selector"].get("chains") for j in jobs),
              "the FlowWorks sweep is queued as chain-group jobs: %s %s" % (len(jobs), (r.stdout + r.stderr)[-300:]))
        names = []
        for j in jobs:
            pv = T.preview("FlowWorks", {"chains": j["selector"]["chains"]})
            need = sum(x["timeout_s"] + T.DRIVER_SLACK_S for x in pv["drivers"])
            check(need <= T.WORKER_DRIVER_CAP_S and j["timeout_s"] >= need * T.WORKER_DRIVER_SHARE,
                  "each sweep job's drivers fit the worker cap: need %d s, timeout %s" % (need, j["timeout_s"]))
            names += [x["name"] for x in pv["drivers"]]
        full = T.preview("FlowWorks", {"full": True})
        check(sorted(names) == sorted(x["name"] for x in full["drivers"]),
              "together the jobs start every driver of the full sweep: %s" % sorted(names))
        n0 = len(glob.glob(os.path.join(tmp, "pending", "*.json")))
        subprocess.run([sys.executable, TESTQ, "sweep", "FlowWorks", "--by", "BENCH"],
                       env=dict(os.environ, TESTQ_QUEUE=tmp), capture_output=True, text=True, timeout=240)
        check(len(glob.glob(os.path.join(tmp, "pending", "*.json"))) == n0, "a second sweep the same day queues nothing")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def t_fill_policy():
    """The filler's pick and day budget (TESTQ_FILL_CAP_SCALE_AND_SKIP_DRY), offline over hand-made done records."""
    import testq as T

    def rec(fin, rows, start=None, by="BENCH.filler", mod="Mock"):
        return {"finished": fin, "job": {"mod": mod, "requested_by": by, "submitted": fin, "id": "J" + fin},
                "result": {"started": start or fin, "finished": fin,
                           "rows": [dict(chain=c, row=r, verdict=v) for c, r, v in rows]}}
    hold = "<site hold, before any component>"
    recs = [rec("2026-10-20T00:00:00Z", [("dry", "a", "UNMEASURED"), ("good", "g", "PASS"), ("void", hold, "UNMEASURED")]),
            rec("2026-10-21T00:00:00Z", [("dry", "a", "UNMEASURED"), ("dry", "b", "NOT_RUN"), ("void", hold, "UNMEASURED"),
                                         ("once", "o", "UNMEASURED")]),
            rec("2026-10-10T00:00:00Z", [("old_dry", "x", "UNMEASURED")]),
            rec("2026-10-09T00:00:00Z", [("old_dry", "x", "UNMEASURED")]),
            rec("2026-10-22T00:00:00Z", [("other", "z", "PASS")], mod="Else")]
    h = T.chain_history("Mock", recs)
    check(set(h) == {"dry", "good", "void", "once", "old_dry"}, "chain_history: only MOD's chains: %s" % sorted(h))
    check([k for _, k in h["void"]] == ["void", "void"], "a run whose only row is the site hold is VOID for that chain")
    ages = T.ages_of(h)
    check(ages["void"] == 0, "a VOID run does not make a chain fresh (site never held): %s" % ages["void"])
    now = T.S.parse_ts("2026-10-22T00:00:00Z")
    check(T.is_dry(h["dry"], now), "a chain whose last 2 runs were all UNMEASURED is DRY")
    check(not T.is_dry(h["once"], now), "one UNMEASURED run is not yet dry")
    check(not T.is_dry(h["old_dry"], now), "a dry chain is re-tried once its last run is older than the retry window")
    check(not T.is_dry(h["void"], now), "VOID runs (site hold only) never make a chain DRY")
    today = [rec("2026-10-22T01:00:00Z", [], start="2026-10-22T00:56:00Z"),
             rec("2026-10-22T02:00:00Z", [], start="2026-10-22T01:50:00Z")]
    check(T.fill_spent_s(today) == 840, "lane time spent = sum of today's filler walls: %s" % T.fill_spent_s(today))
    check(T.FILL_DAY_S >= 4 * 3600 and T.FILL_CAP_DEFAULT >= 100,
          "the default day budget is lane TIME (>= 4 h; 8 h since 2026-10-29), the count ceiling only a backstop (>= 100): %s %s"
          % (T.FILL_DAY_S, T.FILL_CAP_DEFAULT))


def t_fill_drops_unknown_chains():
    """A chain the history holds but modcheck no longer declares (renamed/removed) is forever the stalest; submit
    refuses it, so the filler must drop it and fill with real chains, or Steve idles every tick for good."""
    import testq as T
    check(T.unknown_chains("unknown chain(s) for FlowWorks: a_zz, b_zz; chains are: c, d") == {"a_zz", "b_zz"},
          "unknown_chains reads modcheck's refusal")
    check(T.unknown_chains("unknown row 'T12'") == set(), "a row refusal names no chain")
    import gaps
    tmp = tempfile.mkdtemp(prefix="rf_testq_fill_")
    saved = (T.QHOME, T.cmd_submit, gaps.probe, gaps.owed_items)
    sent = []
    try:
        T.QHOME = tmp
        T.ensure_dirs()
        for i, (fin, chain) in enumerate((("2026-01-01T00:00:00Z", "renamed_away_zz"),
                                          ("2026-05-01T00:00:00Z", "core_offline"),
                                          ("2026-10-01T00:00:00Z", "thirst"))):
            jid = "JFILL%d" % i
            with open(os.path.join(tmp, "done", jid + ".json"), "w") as fh:
                json.dump({"finished": fin, "job": {"id": jid, "mod": "FlowWorks", "submitted": fin,
                                                    "requested_by": "someone"},
                           "result": {"outcome": "DONE", "started": fin, "finished": fin,
                                      "rows": [{"chain": chain, "row": "r", "verdict": "PASS"}]}}, fh)
        # modcheck's catalogue as gaps sees it: thirst live, core_offline offline; renamed_away_zz is history only
        gaps.probe = lambda mod, items, since: {"chains": ["thirst", "core_offline"], "offline": ["core_offline"],
                                                "item_chains": {}, "changed": {}}
        gaps.owed_items = lambda world=None: {}
        T.cmd_submit = lambda sub: sent.append((sub.chains, sub.purpose)) or 0
        import argparse
        rc = T.cmd_fill(argparse.Namespace(mod="FlowWorks", n=1, cap=T.FILL_CAP_DEFAULT, day_s=T.FILL_DAY_S))
        check(rc == 0 and sent == [("thirst", "guard")],
              "fill ranks a history-only chain, drops it when modcheck refuses it, never picks an offline one, and "
              "submits the live chain (no identity: never run at it): rc=%s sent=%s" % (rc, sent))
    finally:
        T.QHOME, T.cmd_submit, gaps.probe, gaps.owed_items = saved
        shutil.rmtree(tmp, ignore_errors=True)


def t_fill_brake_released_by_proof():
    """Two filler jobs in a row not DONE brake the filler, until ANY job on Steve's lane (a hand submission) comes back
    DONE with its canary on after them: then the lane is proven and the brake is stale (2026-10-26: braked all
    afternoon on two failures from before the fix, though a hand job came back DONE + green canary at 11:45 PDT)."""
    import testq as T
    import gaps
    tmp = tempfile.mkdtemp(prefix="rf_testq_brake_")
    saved = (T.QHOME, gaps.probe, gaps.owed_items)
    try:
        T.QHOME = tmp
        T.ensure_dirs()
        gaps.probe = lambda mod, items, since: {"chains": ["thirst"], "offline": [], "item_chains": {}, "changed": {}}
        gaps.owed_items = lambda world=None: {}

        def put(jid, fin, by, outcome, canary=True, lane="stevedesktop"):
            with open(os.path.join(tmp, "done", jid + ".json"), "w") as fh:
                json.dump({"finished": fin, "job": {"id": jid, "mod": "FlowWorks", "submitted": fin, "requested_by": by,
                                                    "purpose": "guard", "canary": canary, "lane": lane},
                           "result": {"outcome": outcome, "started": fin, "finished": fin, "rows": []}}, fh)
        put("J1", "2026-10-26T15:21:16Z", T.FILLER, "INVALID")
        put("J2", "2026-10-26T15:33:14Z", T.FILLER, "FAILED")
        now = T.S.parse_ts("2026-10-26T20:00:00Z")
        args = ("FlowWorks", 1, T.FILL_CAP_DEFAULT, T.FILL_DAY_S, now)
        check(T.fill_plan(*args)["verdict"] == "brake", "two filler jobs not DONE: brake")
        put("J0", "2026-10-26T15:00:00Z", "BENCH", "DONE")
        check(T.fill_plan(*args)["verdict"] == "brake", "a DONE job from BEFORE the braking jobs does not release it")
        put("J3", "2026-10-26T18:54:19Z", "BENCH", "DONE", canary=False)
        check(T.fill_plan(*args)["verdict"] == "brake", "a later DONE job run without its canary does not release it")
        put("J4", "2026-10-26T18:55:00Z", "BENCH", "DONE", lane="archmagi")
        check(T.fill_plan(*args)["verdict"] == "brake", "a later DONE job on another lane does not release it")
        put("J5", "2026-10-26T18:56:00Z", "BENCH", "DONE")
        p = T.fill_plan(*args)
        check(p["verdict"] == "pick" and p["pick"] == ["thirst"],
              "a hand-submitted job DONE with its canary after the braking jobs releases the brake: %s" % p["text"])
    finally:
        T.QHOME, gaps.probe, gaps.owed_items = saved
        shutil.rmtree(tmp, ignore_errors=True)


def t_result_hardening():
    """A tagged-but-malformed result and a non-object worker line are recorded INVALID / skipped, never a crash."""
    import testq as T
    o = T.last_json_object(["[1, 2]"], 0, "[1, 2]")
    check(isinstance(o, dict) and "not an object" in o.get("error", ""), "a JSON list line becomes an error object: %s" % o)
    for line in ("null", '"s"', "7", "oops"):
        check(isinstance(T.last_json_object([line], 0, line), dict), "line %r becomes an object" % line)
    check(T.last_json_object([], 1, "")["error"].startswith("no JSON"), "no line at all is an error object")
    jid = "J20261027T120000Z-abcdef"
    att = jid + ".a1"
    tmp = tempfile.mkdtemp(prefix="rf_testq_hard_")
    saved = (T.QHOME, T.remote)
    try:
        T.QHOME = tmp
        T.ensure_dirs()
        for name, res in (("no outcome", {"schema": S.RESULT_SCHEMA, "job": jid, "attempt": att, "cause": None, "rows": []}),
                          ("no job", {"schema": S.RESULT_SCHEMA}),
                          ("rows not list", {"schema": S.RESULT_SCHEMA, "job": jid, "attempt": att, "outcome": "DONE",
                                             "cause": None, "rows": 3})):
            job = S.make_job("FlowWorks", {"chains": ["core_offline"]}, "fix", "BENCH", "5403169aab")
            job["id"] = jid
            rec = {"job": job, "attempt": att, "attempts": [att]}
            T.move(jid, "running", "running", rec)
            T.remote = lambda args, stdin=None, timeout=180, _r=res: (0, {"state": "done", "attempt": att}
                                                                      if args[0] == "status" else _r)
            try:
                T.reconcile(rec)
                done = T.read_json(T.q("done", jid + ".json")) or {}
                r = done.get("result") or {}
                check(r.get("outcome") == "INVALID" and r.get("cause") == "HARNESS" and "testq.result/1" in r.get("note", ""),
                      "tagged result with %s is recorded INVALID/HARNESS with its reason: %s" % (name, r.get("note")))
            except Exception as ex:     # noqa: BLE001
                check(False, "tagged result with %s crashed collect: %s: %s" % (name, type(ex).__name__, ex))
            for st in ("running", "done"):
                try:
                    os.remove(T.q(st, jid + ".json"))
                except FileNotFoundError:
                    pass
        T.remote = lambda args, stdin=None, timeout=180: (0, T.last_json_object(["[1]"], 0, "[1]"))
        try:
            T.drain_outbox([jid + ".a9"])
            check(not os.listdir(T.q("orphans")), "a non-object worker line is skipped by drain_outbox, not dumped")
        except Exception as ex:     # noqa: BLE001
            check(False, "drain_outbox crashed on a non-object line: %s: %s" % (type(ex).__name__, ex))
    finally:
        T.QHOME, T.remote = saved
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    try:
        t_bad_selection()
        t_driver_sizing()
        t_sweep_split()
        t_fill_policy()
        t_fill_drops_unknown_chains()
        t_fill_brake_released_by_proof()
        t_result_hardening()
    except Exception as ex:     # noqa: BLE001 - reported, the live block still runs
        check(False, "t_fill_policy raised %s: %s" % (type(ex).__name__, ex))
    tmp = tempfile.mkdtemp(prefix="rf_testq_")
    try:
        queue, home, sheets = (os.path.join(tmp, d) for d in ("queue", "home", "sheets"))
        for d in (queue, home, sheets):
            os.makedirs(d)
        open(os.path.join(tmp, "fake_ssh.py"), "w").write(FAKE_SSH)
        open(os.path.join(tmp, "mock.py"), "w").write(MOCK)
        down, sshlog = os.path.join(tmp, "down"), os.path.join(tmp, "ssh.log")
        open(sshlog, "w").close()
        env = {k: v for k, v in os.environ.items() if k not in ("RM_HOST_GUARD_GEN", "RIMFLOW_SEAT", "TESTQ_UNIT")}
        env.update(TESTQ_QUEUE=queue, TESTQ_SSH="%s %s" % (sys.executable, os.path.join(tmp, "fake_ssh.py")),
                   TESTQ_REMOTE_RUNNER=REPO, FAKE_SSH_DOWN=down, FAKE_SSH_LOG=sshlog,
                   TESTQ_HOME=home, TESTQ_SHEET_DIR=sheets, TESTQ_MODS_DIR=os.path.join(tmp, "mods"),
                   TESTQ_SKIP_PULL="1", TESTQ_NO_SYSTEMD="1", TESTQ_CMD_DEPLOY="true", TESTQ_CMD_LOAD="true",
                   TESTQ_CMD_DOWN="true", TESTQ_CMD_RUN="%s %s" % (sys.executable, os.path.join(tmp, "mock.py")),
                   TESTQ_CMD_STATUS="echo 'running pid=4242 session=1'",  # never the real rw_game.sh status
                   RIMFLOW_DRIVER_LOCK=os.path.join(tmp, "DRIVER_LOCK.json"), RM_HOST="stevedesktop",
                   RM_GAME_USERDATA=tmp, MOCK_HOLD=os.path.join(tmp, "hold"))
        sha = subprocess.run(["git", "-C", REPO, "merge-base", "HEAD", "origin/main"], capture_output=True,
                             text=True).stdout.strip()
        # the worker's deploy phase refuses a companion not built from the job's sources: give it one that is
        env["TESTQ_COMPANION_DIR"] = os.path.join(tmp, "BridgeTools", "JawaBench")
        CI.write_fixture(os.path.join(env["TESTQ_COMPANION_DIR"], CI.DLL_NAME), CI.srchash_at(REPO, sha))

        def tq(*args, **extra):
            r = subprocess.run([sys.executable, TESTQ] + list(args), env=dict(env, **extra), capture_output=True,
                               text=True, timeout=120)
            return r.returncode, r.stdout

        def read_job(jid):
            for st in ("pending", "running", "done", "cancelled"):
                pth = os.path.join(queue, st, jid + ".json")
                if os.path.exists(pth):
                    rec = json.load(open(pth))
                    return rec.get("job", rec) if st != "pending" else rec
            return {}

        def njobs():
            return len(glob.glob(os.path.join(queue, "*", "*.json")))

        def submit(*args):
            rc, o = tq("submit", "Mock", "--purpose", "commission", "--by", "BENCH", "--sha", sha, *args)
            try:
                return json.loads(o.strip().splitlines()[-1])
            except (ValueError, IndexError):
                return {"raw": o}

        def state(jid):
            for st in ("pending", "running", "done", "cancelled"):
                if os.path.exists(os.path.join(queue, st, jid + ".json")):
                    return st

        def wait_worker(aid, limit=40):
            t = time.time()
            while time.time() - t < limit:
                if os.path.exists(os.path.join(home, "attempts", aid, "result.json")):
                    return True
                time.sleep(0.3)
            return False

        def running_attempt(jid):
            return json.load(open(os.path.join(queue, "running", jid + ".json")))["attempt"]

        a = submit("--rows", "r1,r2")["job"]
        b = submit("--rows", "r1", "--priority", "90")["job"]
        g = submit("--rows", "r2", "--owner-gate", "owner must pick the list")["job"]
        nb = submit("--rows", "r2", "--not-before", "2099-01-01T00:00:00Z")["job"]
        arch = submit("--rows", "r2", "--lane", "archmagi")["job"]
        bd = submit("--rows", "r1", "--deploy", "NoSuchModAnywhere")
        check("job" not in bd and "NoSuchModAnywhere" in str(bd.get("raw", "")), "submit refuses an undeployable --deploy name up front: %s" % bd)
        dup = submit("--rows", "r1,r2")
        check(dup.get("job") == a and dup.get("duplicate"), "an identical submit returns the pending job: %s" % dup)
        rc, o = tq("submit", "Mock", "--purpose", "fix", "--by", "BENCH", "--sha", "0123456789abcdef", "--rows", "r1")
        check(rc == 2 and "origin/main" in o, "an unpublished source_sha is refused at submit")
        rc, o = tq("submit", "Mock", "--purpose", "fix", "--by", "BENCH", "--sha", sha)
        check(rc == 2 and "selects nothing" in o, "an empty selection is refused at submit")

        hold = os.path.join(tmp, "hold")      # B stays running until the second tick is checked (no race)
        open(hold, "w").close()
        tq("tick")
        check(state(b) == "running" and state(a) == "pending", "tick admits the highest priority job first")
        ab = running_attempt(b)
        tq("tick")
        check(state(a) == "pending", "a second tick while B runs admits nothing")
        if state(a) != "pending":     # TESTQ_SELFTEST_FIX_NIGHTLY_FILE_MISSING: only the 03:00 sweep has ever shown this
            print("DIAG a=%s b=%s hold=%s" % (state(a), state(b), os.path.exists(hold)))
            for f in [hold + ".log", sshlog] + sorted(glob.glob(os.path.join(queue, "*.log")))\
                    + sorted(glob.glob(os.path.join(home, "attempts", "*", "*"))):
                if os.path.isfile(f):
                    print("DIAG --- %s\n%s" % (f, open(f, errors="replace").read()[-1500:]))
        os.remove(hold)
        check(wait_worker(ab), "the worker finished B")
        tq("tick")
        done_b = json.load(open(os.path.join(queue, "done", b + ".json")))
        check(done_b["result"]["outcome"] == "DONE" and done_b["result"]["counts"] == {"PASS": 1, "FAIL": 1},
              "B's result is fetched into done/: %s" % done_b["result"]["counts"])
        check(not os.path.exists(os.path.join(home, "outbox", ab + ".json")), "B's result is acked off the outbox")
        check(state(a) == "running", "the same tick admits A")
        check(all(state(j) == "pending" for j in (g, nb, arch)), "owner_gate, not_before and archmagi stay pending")

        # ssh drops while A runs
        aa = running_attempt(a)
        open(down, "w").close()
        tq("tick")
        ss = json.load(open(os.path.join(queue, "ssh_state.json")))
        check(ss.get("down_since") and "No route" in ss.get("last_error", ""), "ssh down is recorded")
        os.remove(down)
        n = len(open(sshlog).read().splitlines())
        tq("tick")
        check(len(open(sshlog).read().splitlines()) == n, "no ssh at all until the probe is due")
        check(wait_worker(aa), "A finished on the worker while ssh was down")
        tq("tick", TESTQ_PROBE_S="0")
        check(state(a) == "done" and not json.load(open(os.path.join(queue, "ssh_state.json"))).get("down_since"),
              "the due probe finds ssh back and collects A")

        # cancel and supersede
        tq("cancel", nb, "--reason", "not needed")
        check(state(nb) == "cancelled", "cancel moves a pending job to cancelled/")
        s = submit("--rows", "r1", "--supersedes", g, "--priority", "10")["job"]
        check(state(g) == "cancelled" and state(s) == "pending", "a superseding submit cancels the pending original")

        # a dead attempt: the worker finalizes it, then the dispatcher retries once
        tq("tick")
        check(state(s) == "running", "the superseding job is admitted")
        a1 = running_attempt(s)
        wait_worker(a1)
        os.remove(os.path.join(home, "attempts", a1, "result.json"))
        os.remove(os.path.join(home, "outbox", a1 + ".json"))
        st_path = os.path.join(home, "attempts", a1, "state.json")
        os.utime(st_path, (time.time() - 600, time.time() - 600))
        tq("tick")
        dead = json.load(open(os.path.join(home, "attempts", a1, "result.json")))
        check(dead["cause"] == "CRASH" and state(s) == "running", "a dead attempt is finalized INTERRUPTED/CRASH")
        tq("tick")
        a2 = running_attempt(s)
        check(a2 == s + ".a2", "one automatic retry after the attempt id was read: %s" % a2)
        wait_worker(a2)
        tq("tick")
        tq("tick")
        rec = json.load(open(os.path.join(queue, "done", s + ".json")))
        check(rec["attempts"] == [a1, a2] and rec["result"]["outcome"] == "DONE", "the retry's result closes the job")

        # an orphan result in the outbox
        orphan = S.make_job("Mock", {"rows": ["r1"]}, "commission", "BENCH", sha)
        r = subprocess.run([sys.executable, os.path.join(REPO, "infrastructure", "stevedesktop", "worker.py"), "start"],
                           input=json.dumps(orphan), env=env, capture_output=True, text=True, timeout=60)
        oa = json.loads(r.stdout.strip().splitlines()[-1])["attempt"]
        wait_worker(oa)
        tq("tick")
        check(os.path.exists(os.path.join(queue, "orphans", oa + ".json")) and
              not os.path.exists(os.path.join(home, "outbox", oa + ".json")), "an unknown job's result is kept and acked")

        rc, o = tq("show", b)
        check(rc == 0 and len(o.splitlines()) <= 20 and "DONE" in o, "show fits in 20 lines")
        rc, o = tq("list")
        check(len(o.splitlines()) == 6, "list shows every job once:\n%s" % o)
        with open(os.path.join(queue, "tick.lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            rc, o = tq("tick")
            lj = submit("--rows", "r7")["job"]
            crc, co = tq("cancel", lj, "--reason", "race", TESTQ_LOCK_WAIT_S="1")
            src, so = tq("submit", "Mock", "--rows", "r8", "--supersedes", lj, "--purpose", "fix", "--by", "BENCH",
                         "--sha", sha, TESTQ_LOCK_WAIT_S="1")
        check("already running" in o, "a tick while another runs exits at once")
        check(crc == 2 and "REFUSED" in co and state(lj) == "pending",
              "a cancel waits for a running tick's lock, then refuses with nothing moved: %s %s %s" % (crc, co, state(lj)))
        check(src == 2 and state(lj) == "pending",
              "a superseding submit refuses too while a tick holds the lock: %s %s" % (src, so))
        tq("cancel", lj, "--reason", "selftest")
        check(state(lj) == "cancelled", "the same cancel goes through once the tick lock is free")
        # a red canary pauses the lane (design section 6): nothing more is admitted until `resume`
        c = submit("--rows", "r1,r9", "--priority", "95")["job"]
        d = submit("--rows", "r2,r9")["job"]
        c2 = submit("--rows", "r1,r2,r9", "--priority", "94")["job"]
        paused = os.path.join(queue, "paused.json")
        tq("tick", MOCK_MODE="canary")
        wait_worker(running_attempt(c))
        tq("tick", MOCK_MODE="canary")      # c finishes red; the FIRST consecutive red auto-resumes, so c2 is admitted
        rc1 = json.load(open(os.path.join(queue, "done", c + ".json")))["result"]
        check(rc1["cause"] == "CANARY" and not os.path.exists(paused)
              and os.path.exists(os.path.join(queue, "canary_autoresume.json")) and state(c2) == "running",
              "the first red canary auto-resumes the lane once (c2 admitted, no pause): %s %s" % (rc1["cause"], state(c2)))
        wait_worker(running_attempt(c2))
        tq("tick")
        c = c2
        rc_ = json.load(open(os.path.join(queue, "done", c + ".json")))["result"]
        check(rc_["cause"] == "CANARY" and os.path.exists(paused) and state(d) == "pending",
              "a SECOND consecutive red canary -> done INVALID/CANARY, lane paused, the next job held: %s %s" % (rc_["cause"], state(d)))
        tq("tick")
        check(state(d) == "pending", "a paused lane admits nothing on later ticks")
        rc, o = tq("list")
        check("PAUSED" in o.splitlines()[0], "list leads with the pause: %s" % o.splitlines()[:1])
        rc, o = tq("resume")
        check(rc == 2 and os.path.exists(paused), "resume needs --reason")
        rc, o = tq("resume", "--reason", "canary fixed")
        check(rc == 0 and not os.path.exists(paused), "resume --reason clears the pause")
        tq("tick")
        check(state(d) == "running", "after resume the held job is admitted")
        wait_worker(running_attempt(d))
        tq("tick")

        # a game killed mid-run: INVALID/GAME_DIED, retried once automatically, no pause
        k = submit("--rows", "r1,r2,r9")["job"]
        dead = dict(TESTQ_CMD_LOAD="echo started pid 4242", TESTQ_CMD_STATUS="echo stopped; exit 3")
        tq("tick", **dead)
        wait_worker(running_attempt(k))
        tq("tick", **dead)
        k2 = running_attempt(k) if state(k) == "running" else None
        check(k2 == k + ".a2", "a game that died mid-run gets one automatic retry: %s" % k2)
        wait_worker(k2 or "x")
        tq("tick")
        rk = json.load(open(os.path.join(queue, "done", k + ".json")))
        check(rk["result"]["cause"] == "GAME_DIED" and len(rk["attempts"]) == 2 and not os.path.exists(paused),
              "the second GAME_DIED closes the job without pausing the lane: %s" % rk["result"]["cause"])

        # a driver takes the game guard AFTER the worker's start check, before the attempt acquires it (the race gap):
        # the attempt ends REFUSED/GUARD_HELD, which measured nothing - the job must stay running and be asked again
        # every tick, then run to DONE once the guard is free (never finished REFUSED).
        grab = os.path.join(tmp, "grab.py")
        open(grab, "w").write("import os, sys\nsys.path.insert(0, %r)\nimport driver_lock as D\n"
                              "m = os.path.join(%r, 'grabbed')\n"
                              "if not os.path.exists(m):\n    open(m, 'w').close()\n"
                              "    D.acquire(os.environ['RIMFLOW_DRIVER_LOCK'], 'BENCH', 'racing driver', "
                              "{'pid': 4242, 'start': 7.0, 'boot_id': None, 'platform': 'wsl', 'host': 'elsewhere'})\n"
                              % (os.path.join(REPO, "src", "RimMandrake", "rimflow"), tmp))
        race = dict(TESTQ_TEST_BEFORE_ACQUIRE="%s %s" % (sys.executable, grab))
        g = submit("--rows", "r1")["job"]
        tq("tick", **race)
        g1 = running_attempt(g)
        wait_worker(g1)
        tq("tick", **race)
        check(state(g) == "running" and running_attempt(g) == g1,
              "a late REFUSED/GUARD_HELD does not finish the job; it waits while the guard is held: %s" % state(g))
        sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "rimflow"))
        import driver_lock as _DL
        _DL.release(env["RIMFLOW_DRIVER_LOCK"], "BENCH", {"pid": 4242, "start": 7.0, "boot_id": None,
                                                           "platform": "wsl", "host": "elsewhere"})
        tq("tick", **race)
        g2 = running_attempt(g) if state(g) == "running" else None
        check(g2 == g + ".a2", "once the guard is free the next tick requeues a fresh attempt: %s" % g2)
        wait_worker(g2 or "x")
        tq("tick")
        rg = json.load(open(os.path.join(queue, "done", g + ".json")))
        check(rg["result"]["outcome"] == "DONE", "the requeued job finishes DONE: %s" % rg["result"]["outcome"])

        # the daily sweep (design: at most one --full per mod per day, overnight): idempotent within a day
        rc, o = tq("sweep", "Mock")
        sj = json.loads(o.strip().splitlines()[-1]).get("job") if rc == 0 and o.strip() else None
        sw = read_job(sj) if sj else {}
        check(sw.get("purpose") == "sweep" and sw.get("selector") == {"full": True} and state(sj) == "pending",
              "sweep MOD queues one full sweep job: %s %s" % (rc, o[-200:]))
        n0 = njobs()
        rc, o = tq("sweep", "Mock")
        check(rc == 0 and "already" in o and njobs() == n0,
              "a second sweep the same day queues nothing: %s" % o[-200:])
        rc, o = tq("install-timer")
        check(rc != 0 or "testq-sweep.timer" in o, "install-timer also installs the daily sweep timer: %s" % o[-200:])
        # every git-pulling unit runs git's auto gc in the FOREGROUND (2026-10-26: detached repacks were left over in the
        # tick's cgroup every minute, 463 times, and never finished). Can-fail: the env must really reach git's config.
        import testq as _TQ  # noqa: E402
        for un in ("testq-tick.service", "testq-sweep.service"):
            body = _TQ.UNITS[un].format(clone="/c", git_env=_TQ.GIT_ENV).splitlines()
            envl = [l for l in body if l.startswith("Environment=GIT_CONFIG_COUNT=")]
            pre = [i for i, l in enumerate(body) if l.startswith("ExecStartPre=") and " pull " in l]
            check(envl and pre and body.index(envl[0]) < pre[0], "%s sets the git env before its pull: %s" % (un, body[:8]))
        genv = dict(os.environ)
        genv.update(kv.split("=", 1) for kv in _TQ.GIT_ENV.strip()[len("Environment="):].split())
        got = [subprocess.run(["git", "config", "--get", k], env=genv, capture_output=True, text=True).stdout.strip()
               for k in ("gc.autoDetach", "maintenance.autoDetach")]
        check(got == ["false", "false"], "GIT_ENV turns off git's detached auto gc and maintenance: %s" % got)

        # the filler: Steve never idles, no LLM; the stalest chains, with a stop file, a daily cap and a brake
        rc, o = tq("fill", "Mock")
        check(rc == 0 and o.startswith("busy") and njobs() == n0, "fill queues nothing while a runnable job waits: %s" % o)
        tq("cancel", sj, "--reason", "selftest")
        rc, o = tq("fill", "Mock", "--n", "1")
        check(rc == 0 and o.startswith("Mock: exhausted") and "FAILED with no fix" in o,
              "every Mock chain PASSED or FAILED (no fix) at the current identity: nothing is filler: %s" % o[-200:])
        # a newer run with no deployed block: identity unknown, so every chain is "never run at it" again
        fin = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(os.path.join(queue, "done", "JZZ-noident.json"), "w") as fh:
            json.dump({"finished": fin, "job": {"id": "JZZ-noident", "mod": "Mock", "submitted": fin,
                                                "requested_by": "selftest", "purpose": "guard"},
                       "result": {"outcome": "DONE", "started": fin, "finished": fin,
                                  "rows": [{"chain": "c_noident", "row": "r", "verdict": "PASS"}]}}, fh)
        rc, o = tq("fill", "Mock", "--n", "1")
        fj = json.loads(o.strip().splitlines()[-1]).get("job") if rc == 0 and o.strip().endswith("}") else None
        fjob = read_job(fj) if fj else {}
        check(fjob.get("requested_by") == "BENCH.filler" and len(fjob.get("selector", {}).get("chains", [])) == 1
              and fjob.get("lane") == "stevedesktop", "an idle lane gets the stalest chain queued: %s %s" % (o[-200:], fjob))
        rc, o = tq("fill", "Mock")
        check(o.startswith("busy"), "the filler's own pending job keeps it from queuing a second: %s" % o)
        tq("cancel", fj, "--reason", "selftest")
        rc, o = tq("fill", "Mock", "--cap", "1")
        check(o.startswith("cap"), "the daily cap stops the filler: %s" % o)
        open(os.path.join(queue, "fill.stop"), "w").close()
        rc, o = tq("fill", "Mock")
        check(o.startswith("stopped"), "the stop file stops the filler: %s" % o)
        os.remove(os.path.join(queue, "fill.stop"))
        donef = sorted(glob.glob(os.path.join(queue, "done", "*.json")))[-1]
        for i in (1, 2):
            rec = json.load(open(donef))
            rec["job"]["id"] = rec["job"]["id"][:-6] + "bad00%d" % i
            rec["job"]["requested_by"], rec["result"]["outcome"] = "BENCH.filler", "INVALID"
            rec["job"]["submitted"] = "2099-01-0%dT00:00:00Z" % i
            json.dump(rec, open(os.path.join(queue, "done", rec["job"]["id"] + ".json"), "w"))
        rc, o = tq("fill", "Mock")
        check(o.startswith("brake"), "two non-DONE filler jobs in a row brake the filler: %s" % o)
        unit = open(TESTQ).read()
        check("testq.py fill" in unit and "TESTQ_FILL_MODS" in unit, "the tick unit runs the filler")
        check("ExecStart=-/usr/bin/python3 {clone}/src/RimMandrake/Utils/testq/ingest.py" in unit,
              "a failing ingest does not skip the fill line after it (ExecStart=-)")

        rc, o = tq("show", "../../x")
        check(rc == 2, "a path as a job id is refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("\n%d failed" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

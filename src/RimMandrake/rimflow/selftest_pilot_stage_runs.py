#!/usr/bin/env python3
"""Selftest: the Dispatch step starts a pilot mod's stage run from its ledger packet and records its end
(RIMMANDRAKE_START_PILOT_STAGE_RUNS_FROM_LEDGER_PACKET; plan design/plans/2026-11-15-holder-pipeline-fusion-build.md
step 5). Offline, on a temp root; no claude, unit or landing is started.

    python3 src/RimMandrake/rimflow/selftest_pilot_stage_runs.py
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import detached_helper as DH        # noqa: E402
import maturation as M              # noqa: E402
import maturation_dispatch as D     # noqa: E402
import modledger as L               # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:300]))


root = tempfile.mkdtemp(prefix="pilot_runs_st_")
PILOT = (L.config().get("pilot_mods") or ["ExplosiveKnockback"])[0]
os.makedirs(os.path.join(root, "design", "concepts", PILOT))
L.append(root, PILOT, "DISPATCH", "version.open", "version", body={"version": "0.1.0"}, version="0.1.0")
L.append(root, PILOT, "DISPATCH", "stage.enter", "stage", body={"stage": "offline_build"})
M.load = lambda r, m: {"stage": "offline_build"}            # the stage record the launch reads
calls, landed = [], []
fx = {"land_ledger": lambda paths: landed.append(paths) or "landed"}


def fake(rc, unit):
    def go(r, mod, cap, item, **kw):
        calls.append(dict(kw, mod=mod, item=item))
        return rc, "DETACHED %s" % unit if unit else "REFUSED", unit
    return go


st = {"mods": {}}
rc, text, unit = D.launch_stage(root, {"seat": "BENCH"}, st, PILOT, 15, "ITEM_A", now=1000, fx=fx, launch=fake(0, "u1"))
kw = calls[-1]
check("a pilot launch passes the packet as the brief's opening", str(kw.get("preface", "")).startswith(
    "# %s — mod ledger packet" % PILOT), str(kw.get("preface"))[:80])
check("the unit carries RM_MODLEDGER_WRITER=HOLDER.<lease>", (kw.get("env") or {}).get("RM_MODLEDGER_WRITER") ==
      "HOLDER.run-1000", kw.get("env"))
evs = L.read(root, PILOT)
check("run.start is recorded at the mod's stage", any(e["kind"] == "run.start" and e["body"].get("stage") ==
                                                      "offline_build" for e in evs))
check("the launched run is remembered for its end", (st["mods"][PILOT].get("ledger_runs") or [{}])[0].get("unit") == "u1",
      st)
check("the ledger's DISPATCH shard and views are landed", landed and any(p.endswith("DISPATCH.jsonl") for p in landed[-1]),
      landed)
D.launch_stage(root, {"seat": "BENCH"}, st, PILOT, 15, "ITEM_B", now=2000, fx=fx, launch=fake(2, None))
check("a launch that never started records its run.end at once", any(
    e["kind"] == "run.end" and e["body"].get("run") == "run-2000" and e["body"].get("status") == "never_started"
    for e in L.read(root, PILOT)))
calls.clear()
D.launch_stage(root, {"seat": "BENCH"}, st, "NotAPilot", 15, "ITEM_C", now=3000, fx=fx, launch=fake(0, "u3"))
check("any other mod launches as before (no preface, no env)", calls and "preface" not in calls[-1] and
      "env" not in calls[-1], calls)
out = D.end_ledger_runs(root, st, {PILOT: {"ended_runs": []}}, 4000,
                        dict(fx, record=lambda u: {"status": "running"}))
check("a live run is not ended", not out, out)
out = D.end_ledger_runs(root, st, {PILOT: {"ended_runs": [{"unit": "u1"}]}}, 5000,
                        dict(fx, record=lambda u: {"status": "finished", "result": "success"}))
check("an ended run gets run.end with its result and NO_CHECKPOINT", out.get(PILOT) == ["run-1000 success NO_CHECKPOINT"]
      and any(e["kind"] == "run.end" and e["body"].get("run") == "run-1000" for e in L.read(root, PILOT)), out)
out = D.end_ledger_runs(root, st, {PILOT: {"ended_runs": [{"unit": "u1"}]}}, 6000,
                        dict(fx, record=lambda u: {"status": "finished", "result": "success"}))
check("a run is ended once", not out, out)
rec = {"clone": "/c", "unit": "rm-x", "seat": "BENCH", "max_s": None, "state": "/s", "model": "opus", "item": "I",
       "budget_usd": 1.0, "out": "/o", "err": "/e", "env": {"RM_MODLEDGER_WRITER": "HOLDER.run-1"}}
argv = DH.launch_argv(rec, "brief", "/usr/bin/claude")
check("detached_helper's unit sets the run's RM_ env", "RM_MODLEDGER_WRITER=HOLDER.run-1" in argv, argv[:0])
rc = DH.main(["launch", "--seat", "BENCH", "--item", "I", "--brief", "b", "--env", "PATH=/x"])
check("detached_helper refuses a non-RM_ --env", rc == 2, rc)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)

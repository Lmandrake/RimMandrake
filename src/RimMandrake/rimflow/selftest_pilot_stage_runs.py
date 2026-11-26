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
SDIR = tempfile.mkdtemp(prefix="pilot_runs_sd_")
os.environ["RM_MATURATION_DISPATCH_DIR"] = SDIR       # never the live dispatcher's state
os.environ["RM_STAGE_LAND"] = "0"
for _k in ("RM_MODLEDGER_WRITER", "RM_MODLEDGER_TOKEN"):   # a holder run testing this writes as DISPATCH here
    os.environ.pop(_k, None)
import detached_helper as DH        # noqa: E402
import maturation_autonomy as A     # noqa: E402
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
D.ledger_ready = lambda r, m: (True, "PASS 7/7")            # the temp ledger stands for a backfilled one
calls, landed = [], []
fx = {"land_ledger": lambda paths: landed.append(paths) or "landed"}
# RIMMANDRAKE_LAND_HOLDER_GRANT_BEFORE_LAUNCH_CLONE_BLIND: the launch cuts the holder's clone from origin/main, so the
# grant must have landed by then, or the holder's first append is refused "lease never granted". `order` sees every
# landing (through D.land_ledger, whichever path calls it) and every launch.
order = []
_land = D.land_ledger
D.land_ledger = lambda root, mods, what, fx=None: order.append(("land", what)) or _land(root, mods, what, fx)


def granted_first(run):
    """-> True when a landing naming `run` came before the first launch after it was granted."""
    for o in order:
        if o[0] == "launch":
            return False
        if o[0] == "land" and run in o[1]:
            return True
    return False


def fake(rc, unit):
    def go(r, mod, cap, item, **kw):
        order.append(("launch", item))
        calls.append(dict(kw, mod=mod, item=item))
        return rc, "DETACHED %s" % unit if unit else "REFUSED", unit
    return go


st = {"mods": {}}
order.clear()
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
check("stage launch: the grant is landed before the launch", granted_first("run-1000"), order)
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
D.ledger_ready = lambda r, m: (False, "FAIL 7 of 7")
calls.clear()
D.launch_stage(root, {"seat": "BENCH"}, st, PILOT, 15, "ITEM_D", now=3500, fx=fx, launch=fake(0, "u35"))
check("a pilot whose ledger is not ready launches the old way", calls and "preface" not in calls[-1], calls)
D.ledger_ready = lambda r, m: (True, "PASS 7/7")
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

ok_ready = {"ready": lambda r, m: (True, "PASS 7/7"), "land_ledger": lambda paths: "landed"}
rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, "NotAPilot", "t", fx=ok_ready)
check("pilot-launch refuses a mod that is not a pilot", rc == 2 and "not a pilot" in text, text)
rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, PILOT, "t", fx=dict(ok_ready, ready=lambda r, m: (False, "FAIL 7 of 7")))
check("pilot-launch refuses a ledger its backfill acceptance fails", rc == 2 and "not ready" in text and
      "FAIL 7 of 7" in text, text)
M.brief_text = lambda r, m, cap, **k: ("", {"stage": "offline_build", "owed": "ready to advance"})
rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, PILOT, "t", fx=dict(ok_ready, open_items=lambda ids: []))
check("pilot-launch refuses a mod owing nothing launchable", rc == 2 and "owes nothing" in text, text)
D._write(os.path.join(SDIR, "state.json"), {"mods": {PILOT: {"road_back": {"caused_by": "ROUTE_X"}}}})
got = []
order.clear()
rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000, "seat": "BENCH"}, PILOT, "t", now=7000, fx=dict(
    ok_ready, open_items=lambda ids: [{"id": "RIMMANDRAKE_FIX_ONE_A"}, {"id": "RIMMANDRAKE_FIX_TWO_B"}],
    launch_brief=lambda item, text, model, cap, seat, env=None: order.append(("launch", item)) or got.append(
        (item, text, env)) or (0, "DETACHED u7", "u7")))
check("pilot-launch road back: the grant is landed before the launch", granted_first("run-7000"), order)
check("on a spent road back one holder run starts on every open item, from the packet", rc == 0 and got and
      got[-1][0] == "RIMMANDRAKE_FIX_ONE_A" and got[-1][1].startswith("# %s — mod ledger packet" % PILOT) and
      "RIMMANDRAKE_FIX_TWO_B" in got[-1][1] and got[-1][2].get("RM_MODLEDGER_WRITER") == "HOLDER.run-7000", (rc, text))
sd = D.read_state(os.path.join(SDIR, "state.json"))
check("pilot-launch keeps the run for its end and logs the act", [r.get("unit") for r in sd["mods"][PILOT].get(
    "ledger_runs", [])] == ["u7"] and sd["mods"][PILOT].get("pilot_launches"), sd["mods"][PILOT])
got.clear()
st2 = {"mods": {PILOT: {}}}
row = {"mod": PILOT, "aut": "fixer", "fix_item": "RIMMANDRAKE_FIX_ONE_A", "cap": 15, "stage": "in_game"}
order.clear()
A._execute_one(root, {"seat": "BENCH"}, st2, row, 8000, None,
               lambda item, text, model, cap, seat, env=None: order.append(("launch", item)) or got.append(
                   (item, text, env)) or (0, "DETACHED u8", "u8"),
               set())
check("autonomy fixer: the grant is landed before the launch", granted_first("run-8000"), order)
check("the autonomy layer's fixer run on a pilot starts from the packet with the holder env", got and
      got[-1][1].startswith("# %s — mod ledger packet" % PILOT) and (got[-1][2] or {}).get("RM_MODLEDGER_WRITER") ==
      "HOLDER.run-8000" and st2["mods"][PILOT].get("ledger_runs"), got[-1:] and got[-1][2])
row2 = dict(row, mod="NotAPilot")
st2["mods"]["NotAPilot"] = {}
got.clear()
A._execute_one(root, {"seat": "BENCH"}, st2, row2, 9000, None,
               lambda item, text, model, cap, seat, **kw: got.append(kw) or (0, "DETACHED u9", "u9"), set())
# no holder env (no RM_MODLEDGER_WRITER); its only env is its admission scope, which control.launch_unit reads
check("any other mod's fixer launches as before (no holder env, only its control scope)",
      got == [{"env": {"RM_CONTROL_MOD": "NotAPilot", "RM_CONTROL_STAGE": row2.get("stage") or "in_game"}}], got)
shutil.rmtree(SDIR, ignore_errors=True)
shutil.rmtree(root, ignore_errors=True)
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)

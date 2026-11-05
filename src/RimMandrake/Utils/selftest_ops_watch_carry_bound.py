#!/usr/bin/env python3
"""Class guard for RELAPSE_PLAN_FIX_DIED_TWICE: a compose pass must never read a healthy family blind because the
metronome's round robin took longer to come back to it than a typed carry bound allowed.

Instance (2026-11-05): plan was measured at 18:38:14Z and next at 19:00:35Z (1341 s; 5 overruns, each followed by
fam_retry beats). The carry bound was a typed 1000 s, so the compose pass at 18:58:17Z carried plan as UNMEASURED,
st_suppressed wrote plan.blind = 1, and incident plan-20261105134046 opened for the third time on a healthy source.
The guard: the bound is derived from the phase table and the timer, covers the worst round, a rule cannot lower it,
and a family older than it still reads blind. Fixture-only: stub collectors, temp dirs."""
import json
import os
import sys
import tempfile as _tf
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_TMP = Path(_tf.mkdtemp(prefix="selftest_ops_watch_carry_bound_"))
os.environ["RM_OPS_WATCH_DIR"] = str(_TMP / "ops")
import ops_watch as OW  # noqa: E402

FAILS = []
INSTANCE_GAP_S = OW.epoch("2026-11-05T19:00:35Z") - OW.epoch("2026-11-05T18:38:14Z")       # 1341 s, measured
INSTANCE_OPEN_S = OW.epoch("2026-11-05T18:58:17Z") - OW.epoch("2026-11-05T18:38:14Z")      # the pass that opened it


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def stub(fam):
    def c(now, rules, ctx):
        pts = {"%s.stub" % fam: OW.M(1, "n")}
        if fam in ("plan", "relentless", "seats"):
            pts["%s.blind" % fam] = OW.M(0, "sources not seen", cause="none")
        return pts
    return c


OW.COLLECTORS = {f: stub(f) for f in OW.ORDER}
OW.run_alarms = lambda *a, **k: {}
rules = OW.load_rules()

# --- the bound is derived, and covers the worst round of the shipped round robin ------------------------------------
bound, why = OW.compose_round_bound_s()
check("the bound reads from the shipped phase table and timer", bound is not None, why)
tab = json.loads(OW.METRONOME_PHASES.read_text(encoding="utf-8"))
per = tab["phases"][OW.SENSE_PHASE]["per_beat"]
nominal_round = -(-len(OW.FAMILIES) // per) * 60.0          # what the typed 1000 s assumed: 60 s beats, no retries
check("the bound covers the measured instance gap (%.0f s)" % INSTANCE_GAP_S, bound and bound >= INSTANCE_GAP_S,
      (bound, why))
check("the bound covers a worst round, every turn overrun and retried", bound and bound >= 3 * nominal_round,
      (bound, nominal_round))
check("instance: the typed 1000 s was under the measured gap (this is the defect)", OW.COMPOSE_MAX_AGE_S < INSTANCE_GAP_S)
check("the bound grows with the family count", OW.compose_round_bound_s(n_families=40)[0] > bound)
check("a rule cannot lower the bound",
      OW.compose_max_age_s({"compose_max_age_s": 600})[0] == bound, OW.compose_max_age_s({"compose_max_age_s": 600}))
check("a rule may raise it", OW.compose_max_age_s({"compose_max_age_s": bound + 60})[0] == bound + 60)
check("an unreadable table: the floor, said aloud",
      OW.compose_round_bound_s(phases=_TMP / "absent.json")[0] is None)


def blind_after(gap_s, label):
    """Seed every series at t0, then a compose pass `gap_s` later that measures two other families: plan.blind."""
    d = _TMP / label
    os.environ["RM_OPS_WATCH_DIR"] = str(d)
    t0 = time.time() - gap_s - 120
    OW.run(now=t0, rules=rules)
    OW.run(now=t0 + gap_s, rules=rules, families=["accounts", "codex"], compose=True)
    st = json.loads((d / "status.json").read_text())
    return st["points"].get("plan.blind") or {}


p = blind_after(INSTANCE_OPEN_S, "instance_open")
check("instance: plan carried %.0f s across a slow round reads blind 0, not 1" % INSTANCE_OPEN_S,
      p.get("m") == "MEASURED" and p.get("v") == 0, p)
p = blind_after(INSTANCE_GAP_S, "instance_gap")
check("instance: plan carried the whole measured gap (%.0f s) reads blind 0" % INSTANCE_GAP_S,
      p.get("m") == "MEASURED" and p.get("v") == 0, p)
p = blind_after(bound + 120, "past_bound")
check("a family older than the round robin's worst round still reads blind 1",
      p.get("m") == "MEASURED" and p.get("v") == 1 and "round robin" in str((p.get("x") or {}).get("cause")), p)

# --- the old typed bound fails on the instance: the guard can see the defect -----------------------------------------
_real = OW.compose_round_bound_s
OW.compose_round_bound_s = lambda *a, **k: (None, "forced: the pre-fix typed bound")
p = blind_after(INSTANCE_OPEN_S, "pre_fix")
check("pre-fix bound on the instance reads blind 1 (the guard sees the class)", p.get("v") == 1, p)
OW.compose_round_bound_s = _real

print("selftest_ops_watch_carry_bound: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)

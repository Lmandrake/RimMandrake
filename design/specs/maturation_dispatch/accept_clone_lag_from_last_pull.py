"""Acceptance for RIMMANDRAKE_MEASURE_CLONE_LAG_FROM_LAST_PULL_CHURN_TRIPS. Run from the repo root.
clone_reading(st, now, got, head=<sha>): behind_min counts from the first tick that saw this HEAD behind, so a clone
that fast-forwards every 90 s under steady origin churn never reads past 1.5 min, while a stuck HEAD still accumulates."""
import sys
sys.path.insert(0, "src/RimMandrake/rimflow")
import maturation_dispatch as MD
ok = 0
def check(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name); ok += bool(cond)
# 1 churn: HEAD moves every tick, always behind 2-4 -> never above 5 min
st, t, worst = {}, 1000.0, 0
for i in range(10):
    r = MD.clone_reading(st, t + 90 * i, (2 + i % 3, 0), head="sha%d" % i); worst = max(worst, r["behind_min"])
check("churn with HEAD advancing stays under 5 min (worst %.1f)" % worst, worst < 5)
# 2 stuck: same HEAD, behind 6 for 10 ticks -> accumulates past 5 min
st = {}
for i in range(10):
    r = MD.clone_reading(st, t + 90 * i, (6, 0), head="stuck")
check("stuck HEAD accumulates (%.1f min)" % r["behind_min"], r["behind_min"] >= 13)
# 3 level resets
r = MD.clone_reading(st, t + 2000, (0, 0), head="stuck2"); check("level reads 0", r["behind_min"] == 0)
# 4 unmeasured stays unmeasured
r = MD.clone_reading({}, t, (None, "fetch refused"), head=None); check("blind stays unmeasured", r["measured"] is False)
# 5 head unknown (None) on a behind tick falls back to accumulate, never resets
st = {}
MD.clone_reading(st, t, (3, 0), head="a"); r = MD.clone_reading(st, t + 400, (3, 0), head=None)
check("unknown head does not reset the clock (%.1f)" % r["behind_min"], r["behind_min"] >= 6)
print("%d/5 PASS" % ok); sys.exit(0 if ok == 5 else 1)

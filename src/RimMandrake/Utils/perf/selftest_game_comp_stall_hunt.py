#!/usr/bin/env python3
"""Offline selftest of game_comp_stall_hunt.verdict (GAMECOMP_STALL_HUNT_SEVEN_SECONDS). No bridge, no game."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_comp_stall_hunt as H  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    if not cond:
        FAILS.append("%s %s" % (name, detail))


def reply(**over):
    r = dict(success=True, patchedMethods=40, ticksObserved=600, loadsSeen=0, stageCalls=600, stageMs=300.0, stageMaxMs=12.0,
             stageMaxAtTick=7100, stageMaxTopType="A.Comp", stageMaxTopPackageId="mod.a", stageMaxTopMs=9.0, componentSumMs=280.0, coverage=0.93, spikeMs=100.0, spikesSeen=0, spikes=[],
             components=[{"type": "A.Comp", "packageId": "mod.a", "totalMs": 200.0}],
             byMod=[{"packageId": "mod.a", "msPerTick": 0.3, "maxMs": 10.0, "components": 1}])
    r.update(over)
    return r


ok, why = H.verdict(reply(), min_ticks=300)
check("quiet window passes", ok, why)

stall = dict(stageMaxMs=6760.0, stageMaxAtTick=7501, spikesSeen=1, stageMaxTopType="B.Stall", stageMaxTopPackageId="mod.b",
             stageMaxTopMs=6740.0,
             spikes=[{"type": "B.Stall", "packageId": "mod.b", "ms": 6740.0, "tick": 7501, "ticksSinceLoad": -1, "load": 0}])
ok, why = H.verdict(reply(**stall), min_ticks=300)
check("named stall passes", ok, why)

ok, why = H.verdict(reply(stageMaxMs=6760.0, stageMaxTopType=None, stageMaxTopPackageId=None, stageMaxTopMs=None), min_ticks=300)
check("unnamed stall fails", not ok and "unnamed" in " ".join(why), why)

ok, why = H.verdict(reply(stageMaxMs=6760.0, stageMaxTopMs=40.0), min_ticks=300)
check("component far smaller than its stage call fails", not ok, why)

# GPT review 1, finding 7: an unrelated 5000 ms spike at another tick must not "explain" a 6760 ms stage call
ok, why = H.verdict(reply(stageMaxMs=6760.0, stageMaxTopMs=40.0,
                          spikes=[{"type": "Early", "packageId": "mod.e", "ms": 5000.0, "tick": 7400}]), min_ticks=300)
check("unrelated spike does not name the stall", not ok and "unnamed" in " ".join(why), why)

ok, why = H.verdict(reply(stageMs=0.0, stageCalls=0, coverage=None), min_ticks=300)
check("untimed stage fails", not ok and "never timed" in " ".join(why), why)

ok, why = H.verdict(reply(ticksObserved=10), min_ticks=300)
check("paused window fails", not ok and "ticksObserved" in " ".join(why), why)

ok, why = H.verdict(reply(), min_ticks=300, expect_load=True)
check("load expected but unseen fails", not ok and "load" in " ".join(why), why)

ok, why = H.verdict(reply(loadsSeen=1, spikes=[{"ms": 2880.0, "ticksSinceLoad": 18, "load": 1}], stageMaxMs=2900.0,
                          stageMaxTopMs=2880.0, stageMaxSinceLoad=18, stageMaxLoad=1),
                    min_ticks=300, expect_load=True)
check("post-load stall named passes", ok, why)

ok, why = H.verdict(reply(coverage=0.2), min_ticks=300)
check("low coverage fails", not ok, why)

ok, why = H.verdict(reply(byMod=[]), min_ticks=300)
check("no mod ranking fails", not ok, why)

ok, why = H.verdict(reply(patchedMethods=0), min_ticks=300)
check("nothing patched fails", not ok, why)

ok, why = H.verdict({"success": False, "message": "No game"}, min_ticks=1)
check("tool failure fails", not ok and "No game" in why[0], why)

ok, why = H.verdict(None)
check("no reply fails", not ok, why)

spike_lines = [l for l in H.summary(reply(**stall)).splitlines() if l.strip().startswith("SPIKE")]
check("summary renders the spike with its type and mod", len(spike_lines) == 1 and "B.Stall" in spike_lines[0]
      and "[mod.b]" in spike_lines[0], spike_lines)

for cov in (None, float("nan"), float("inf"), "0.9"):
    ok, why = H.verdict(reply(coverage=cov), min_ticks=300)
    check("timed stage with coverage %r fails" % (cov,), not ok and "coverage" in " ".join(why), why)

ok, why = H.verdict(reply(ticksObserved=float("nan")), min_ticks=300)
check("NaN ticks fails", not ok, why)

ok, why = H.verdict(reply(**dict(stall, stageMaxTopMs=float("nan"))), min_ticks=300)
check("NaN top component fails", not ok and "unnamed" in " ".join(why), why)

for thr in (None, 0, float("nan")):
    ok, why = H.verdict(reply(**dict(stall, spikeMs=thr)), min_ticks=300)
    check("spikeMs %r fails" % (thr,), not ok and "spikeMs" in " ".join(why), why)

ok, why = H.verdict(reply(spikeMs=250.0), min_ticks=300, spike_ms=100.0)
check("spikeMs other than requested fails", not ok and "requested" in " ".join(why), why)

ok, why = H.verdict(reply(), min_ticks=300, spike_ms=100.0)
check("spikeMs as requested passes", ok, why)

for shown in (1.0, 1.1):   # --spike-ms 1.05 reported rounded to 0.1 ms either way
    ok, why = H.verdict(reply(spikeMs=shown), min_ticks=300, spike_ms=1.05)
    check("spikeMs 1.05 shown as %s passes" % shown, ok, why)

if FAILS:
    for f in FAILS:
        print("FAIL", f)
    print("selftest_game_comp_stall_hunt: FAIL (%d)" % len(FAILS))
    sys.exit(1)
print("selftest_game_comp_stall_hunt: PASS")

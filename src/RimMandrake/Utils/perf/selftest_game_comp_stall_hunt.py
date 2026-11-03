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
             stageMaxAtTick=7100, stageMaxTopType="A.Comp", stageMaxTopPackageId="mod.a", stageMaxTopMs=9.0, componentSumMs=280.0, coverage=0.933, spikeMs=100.0, spikesSeen=0, spikes=[],
             components=[{"type": "A.Comp", "packageId": "mod.a", "totalMs": 200.0}],
             byMod=[{"packageId": "mod.a", "msPerTick": 0.3, "maxMs": 10.0, "components": 1}])
    r.update(over)
    return r


ok, why = H.verdict(reply(), min_ticks=300)
check("quiet window passes", ok, why)

big = dict(stageMs=7300.0, componentSumMs=6810.9)   # a 6760 ms call needs a stage total that holds it (coverage 0.933)
stall = dict(big, stageMaxMs=6760.0, stageMaxAtTick=7501, spikesSeen=1, stageMaxTopType="B.Stall", stageMaxTopPackageId="mod.b",
             stageMaxTopMs=6740.0,
             spikes=[{"type": "B.Stall", "packageId": "mod.b", "ms": 6740.0, "tick": 7501, "ticksSinceLoad": -1, "load": 0}])
ok, why = H.verdict(reply(**stall), min_ticks=300)
check("named stall passes", ok, why)

ok, why = H.verdict(reply(**big, stageMaxMs=6760.0, stageMaxTopType=None, stageMaxTopPackageId=None, stageMaxTopMs=None), min_ticks=300)
check("unnamed stall fails", not ok and "unnamed" in " ".join(why), why)

ok, why = H.verdict(reply(**big, stageMaxMs=6760.0, stageMaxTopMs=40.0), min_ticks=300)
check("component far smaller than its stage call fails", not ok, why)

# GPT review 1, finding 7: an unrelated 5000 ms spike at another tick must not "explain" a 6760 ms stage call
ok, why = H.verdict(reply(**big, stageMaxMs=6760.0, stageMaxTopMs=40.0,
                          spikes=[{"type": "Early", "packageId": "mod.e", "ms": 5000.0, "tick": 7400}]), min_ticks=300)
check("unrelated spike does not name the stall", not ok and "unnamed" in " ".join(why), why)

ok, why = H.verdict(reply(stageMs=0.0, stageCalls=0, coverage=None), min_ticks=300)
check("untimed stage fails", not ok and "never timed" in " ".join(why), why)

ok, why = H.verdict(reply(ticksObserved=10), min_ticks=300)
check("paused window fails", not ok and "ticksObserved" in " ".join(why), why)

ok, why = H.verdict(reply(), min_ticks=300, expect_load=True)
check("load expected but unseen fails", not ok and "load" in " ".join(why), why)

ok, why = H.verdict(reply(loadsSeen=1, spikes=[{"ms": 2880.0, "ticksSinceLoad": 18, "load": 1}], stageMaxMs=2900.0,
                          stageMaxTopMs=2880.0, stageMaxSinceLoad=18, stageMaxLoad=1, stageMs=3100.0, componentSumMs=2892.3),
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

# blind check WEAK at b90cbc89: a stall whose every owner is '?' was accepted; the item asks to rank by owner mod
q = "?"
unmapped = dict(loadsSeen=1, spikeMs=250.0, stageMs=3100.0, componentSumMs=2892.3, stageMaxMs=2880.0, stageMaxAtTick=5821, stageMaxSinceLoad=18, stageMaxLoad=1,
                stageMaxTopType="X.Comp", stageMaxTopPackageId=q, stageMaxTopMs=2880.0, spikesSeen=1,
                spikes=[{"type": "X.Comp", "packageId": q, "ms": 2880.0, "tick": 5821, "ticksSinceLoad": 18, "load": 1}],
                components=[{"type": "X.Comp", "packageId": q, "totalMs": 2900.0}],
                byMod=[{"packageId": q, "msPerTick": 2.0, "maxMs": 2880.0, "components": 1}])
ok, why = H.verdict(reply(**unmapped), min_ticks=300, expect_load=True, spike_ms=250.0)
check("stall owned by '?' everywhere fails", not ok and "unnamed" in " ".join(why) and "owner mod" in " ".join(why), why)
for pkg in (q, "", " ", None):
    ok, why = H.verdict(reply(**dict(stall, stageMaxTopPackageId=pkg)), min_ticks=300)
    check("stall top packageId %r fails" % (pkg,), not ok and "unnamed" in " ".join(why), why)
for rows in ([{"packageId": q}], [{"packageId": q}, {"packageId": ""}]):
    ok, why = H.verdict(reply(byMod=rows), min_ticks=300)
    check("byMod all unmapped %r fails" % (rows,), not ok and "owner mod" in " ".join(why), why)
ok, why = H.verdict(reply(byMod=[{"packageId": "mod.a"}, {"packageId": q}]), min_ticks=300)
check("one unmapped byMod row among named fails", not ok and "no packageId" in " ".join(why), why)
ok, why = H.verdict(reply(**dict(unmapped, stageMaxTopPackageId="mod.x",
                                 byMod=[{"packageId": "mod.x", "msPerTick": 2.0, "maxMs": 2880.0, "components": 1}])),
                    min_ticks=300, expect_load=True, spike_ms=250.0)
check("same post-load stall with its mod mapped passes", ok, why)

# GPT review of the WEAK fix: a stuck stage-max or a stale coverage must not keep the verdict green
ok, why = H.verdict(reply(stageMaxMs=0.0), min_ticks=300)
check("stage max stuck at zero fails", not ok and "accumulator" in " ".join(why), why)
ok, why = H.verdict(reply(stageMaxMs=6760.0, stageMaxTopMs=6740.0), min_ticks=300)
check("stage max above the stage total fails", not ok and "accumulator" in " ".join(why), why)
ok, why = H.verdict(reply(componentSumMs=0.0), min_ticks=300)
check("coverage contradicting componentSumMs fails", not ok and "disagrees" in " ".join(why), why)
ok, why = H.verdict(reply(componentSumMs=None), min_ticks=300)
check("missing componentSumMs fails", not ok and "componentSumMs" in " ".join(why), why)
ok, why = H.verdict(reply(stageMs=0.3, stageCalls=3, stageMaxMs=0.1, stageMaxTopMs=0.1, componentSumMs=0.3, coverage=0.9), min_ticks=300)
check("tiny stage within rounding passes", ok, why)

# GPT review 2: rounding-exact bounds, the requested threshold, and impossible attributions
ok, why = H.verdict(reply(stageCalls=6000, ticksObserved=6000, stageMaxMs=0.0), min_ticks=300)
check("stuck-zero max over many calls fails", not ok and "accumulator" in " ".join(why), why)
ok, why = H.verdict(reply(spikeMs=1.1, stageMaxMs=1.06, stageMaxTopType=None, stageMaxTopPackageId=None,
                          stageMaxTopMs=None), min_ticks=300, spike_ms=1.05)
check("stall above the requested but below the echoed threshold must be named", not ok and "unnamed" in " ".join(why), why)
ok, why = H.verdict(reply(stageMs=0.2, stageCalls=1, stageMaxMs=0.15, stageMaxTopMs=0.1, componentSumMs=0.1, coverage=1.0), min_ticks=300)
check("coverage 1.000 from 0.1/0.2 after rounding passes", ok, why)
ok, why = H.verdict(reply(**dict(stall, stageMaxTopMs=7000.0)), min_ticks=300)
check("top component longer than its call fails", not ok and "impossible" in " ".join(why), why)
ok, why = H.verdict(reply(**dict(stall, stageMaxMs=7000.0, stageMaxTopMs=6900.0, componentSumMs=6810.9)), min_ticks=300)
check("top component longer than all components fails", not ok and "impossible" in " ".join(why), why)

# GPT review 3: bounds hold below the threshold too; rounding at the half-call line and the threshold edge
ok, why = H.verdict(reply(**dict(stall, stageMaxMs=20.0)), min_ticks=300)
check("stale top component bigger than a quiet worst call fails", not ok and "impossible" in " ".join(why), why)
ok, why = H.verdict(reply(stageMs=1000.0, componentSumMs=933.0, stageMaxMs=100.01, stageMaxTopMs=50.0, spikeMs=100.0),
                    min_ticks=300, spike_ms=100.0)
check("top exactly half after rounding passes", ok, why)
ok, why = H.verdict(reply(stageMs=1000.0, componentSumMs=933.0, stageMaxMs=100.01, stageMaxTopMs=49.0, spikeMs=100.0),
                    min_ticks=300, spike_ms=100.04)
check("max below the requested threshold is no stall", ok, why)
ok, why = H.verdict(reply(spikeMs=100.0), min_ticks=300, spike_ms=100.059)
check("echo 100.0 for a 100.059 request fails", not ok and "requested" in " ".join(why), why)

if FAILS:
    for f in FAILS:
        print("FAIL", f)
    print("selftest_game_comp_stall_hunt: FAIL (%d)" % len(FAILS))
    sys.exit(1)
print("selftest_game_comp_stall_hunt: PASS")

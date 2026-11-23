#!/usr/bin/env python3
"""Offline selftest of spore_emitter_window.verdict (RIMMANDRAKE_TELL_HIM_ROT_SPORE_MUSHROOM_PERFORMANCE_VERDICT_HIS_HUNCH).
No bridge, no game. Each case is a planted scene; the word it must read is beside it."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spore_emitter_window as W

FIVE = ["ludeon.rimworld", "Ludeon.RimWorld.Royalty", "ludeon.rimworld.ideology", "ludeon.rimworld.biotech",
        "ludeon.rimworld.anomaly", "ludeon.rimworld.odyssey"]
COUNTS = {"RM_AgariluxPrime": 5, "RM_Skulltop": 0, "RM_AgelessCap": 2, "RM_ChokingSpores": 30, "RM_Bryolux": 400}


def prof(burst_max="800.0 us", tick_max="40000.0 us", burst_calls=120, tick_calls=36000, as_dict=False, drop=()):
    ms = [{"method": W.BURST, "calls": burst_calls, "meanUs": "300 us", "maxUs": burst_max},
          {"method": W.GAS_TICK, "calls": 9000, "meanUs": "4 us", "maxUs": "90 us"},
          {"method": W.TICK, "calls": tick_calls, "meanUs": "4000 us", "maxUs": tick_max}]
    ms = [m for m in ms if m["method"] not in drop]
    if as_dict:
        return {"methods": {m.pop("method"): m for m in ms}}
    return {"methods": ms}


def case(p=None, ticks=36000, counts=None, biome="RM_TheRot", dlcs=FIVE):
    return W.verdict(prof() if p is None else p, ticks, dict(COUNTS) if counts is None else counts, biome, dlcs)[1]


CASES = [
    ("clean: 0.8 ms of a 40 ms tick", case(), "REFUTED"),
    ("dict-shaped profile", case(prof(as_dict=True)), "REFUTED"),
    ("numeric maxUs", case(prof(burst_max=800.0, tick_max=40000.0)), "REFUTED"),
    ("burst exactly 5 ms is not refuted", case(prof(burst_max="5000 us", tick_max="400000 us")), "BETWEEN"),
    ("burst 4 ms but 8% of a 50 ms tick", case(prof(burst_max="4000 us", tick_max="50000 us")), "BETWEEN"),
    ("burst 50 ms", case(prof(burst_max="50000 us", tick_max="900000 us")), "SUPPORTED"),
    ("burst 3 ms but 30% of a 10 ms tick", case(prof(burst_max="3000 us", tick_max="10000 us")), "SUPPORTED"),
    ("burst never called", case(prof(burst_calls=0)), "NEVER_FIRED"),
    ("burst absent from profile", case(prof(drop=(W.BURST,))), "BLIND"),
    ("burst maxUs unavailable", case(prof(burst_max="unavailable: no samples")), "BLIND"),
    ("no emitter, probe sees the map", case(counts=dict(COUNTS, RM_AgariluxPrime=0, RM_AgelessCap=0)), "NO_EMITTER"),
    ("probe plant reads 0", case(counts=dict(COUNTS, RM_Bryolux=0)), "BLIND"),
    ("probe plant unread", case(counts=dict(COUNTS, RM_Bryolux=None)), "BLIND"),
    ("an emitter count unread", case(counts=dict(COUNTS, RM_Skulltop=None)), "BLIND"),
    ("no ticks", case(ticks=0), "BLIND"),
    ("ticks unread", case(ticks=None), "BLIND"),
    ("tick never timed", case(prof(drop=(W.TICK,))), "BLIND"),
    ("profiler refused", case(dict(prof(), refused="Harmony unavailable")), "BLIND"),
    ("wrong biome", case(biome="RM_TheScald"), "WRONG_SCENE"),
    ("biome unread", case(biome=None), "WRONG_SCENE"),
    ("anomaly not running", case(dlcs=[d for d in FIVE if "anomaly" not in d]), "WRONG_SCENE"),
    ("packageIds unread", case(dlcs=None), "WRONG_SCENE"),
]

fails = ["%s: read %s, want %s" % (n, got, want) for n, got, want in CASES if got != want]
code = W.verdict(prof(), 36000, COUNTS, "RM_TheRot", FIVE)[0]
if code != 0:
    fails.append("clean case exit %r, want 0" % code)
if W.verdict(prof(burst_max="60000 us"), 36000, COUNTS, "RM_TheRot", FIVE)[0] != 1:
    fails.append("supported case must exit 1")
print("selftest_spore_emitter_window: %s (%d cases)" % ("FAIL" if fails else "PASS", len(CASES)))
for f in fails:
    print("  - " + f)
sys.exit(1 if fails else 0)

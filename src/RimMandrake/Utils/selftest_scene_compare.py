#!/usr/bin/env python3
"""Offline acceptance of scene_compare (RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED). Traces are hand-made in schema
scene_trace_v1 (design/specs/2026-11-23-bridge-v2/boundary.md §THE TRACE). No game.

Planted faults that must turn this red (seen 2026-11-24, recorded on the item): a comparison that ignores taps
(t_track_or_tap_difference_names_tick_and_value); "could not compare" reported as equal (t_missing_tick_range_is_could_not_compare)."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import scene_compare as SC  # noqa: E402

T0 = 1000
SAVE = {"name": "fixture_carrier", "sha256": "ab" * 32}
RAND = "12345678901234567890"
ORIGIN = {"save": SAVE, "tick": T0, "rand": RAND}


def trace(run="s1_r1", hp=(100, 100, 100, 90, 90, 80), end=("hit", 5), rand=RAND, taps=(), wall=0.0, start=T0):
    """One whole run: a track `hp` sampled from offset 0 (first) to the end, an act at offset 2, the end and the close."""
    rows = [{"rec": "open", "tick": start, "phase": "first", "mode": "PLAY", "speed": "Normal", "rand": rand, "schema": "scene_trace_v1"}]
    last = None
    for off, v in enumerate(hp):
        if off > end[1]:
            break
        if v != last or off == 0:
            rows.append({"rec": "track", "tick": start + off, "phase": "first" if off == 0 else "end_of_tick", "name": "hp", "st": "ok", "v": v})
            last = v
        if off == 2:
            rows.append({"rec": "act", "tick": start + off, "phase": "end_of_tick", "name": "hurt", "ok": True, "detail": "jawa/damage", "ms": 0.4 + wall})
        for t in taps:
            if t[0] == off:
                rows.append({"rec": "tap", "tick": start + off, "phase": "end_of_tick", "tap": "error", "text": t[1]})
    rows.append({"rec": "track", "tick": start + end[1], "phase": "last", "name": "hp", "st": "ok", "v": last})
    rows.append({"rec": "end", "tick": start + end[1], "phase": "end_of_tick", "state": end[0], "hitTick": start + end[1] if end[0] == "hit" else None,
                 "executed": end[1], "cost": 1.5 + wall, "costliest": {"node": "n1", "msMax": 0.1 + wall}})
    rows.append({"rec": "close", "tick": start + end[1], "phase": "last", "drained": True, "dropped": 0, "alloc": 24 + int(wall * 1000)})
    for i, r in enumerate(rows, 1):
        r.update(n=i, run=run, seq=5000 + i + int(wall * 100))
    rows[-1]["rows"] = len(rows) - 1
    return rows


def sample(arm="play1", rows=None, **kw):
    s = {"arm": arm, "rows": rows if rows is not None else trace(), "save": dict(SAVE), "rand_want": RAND, "wall_s": 10.0, "ticks": 5}
    s.update(kw)
    return s


def t_equal_traces_compare_equal():
    c = SC.compare(trace(run="s1_r1"), trace(run="s9_r3"))
    assert c["verdict"] == SC.EQUAL, c


def t_track_or_tap_difference_names_tick_and_value():
    c = SC.compare(trace(), trace(hp=(100, 100, 100, 95, 90, 80)))
    assert c["verdict"] == SC.DIVERGED and c["tick"] == 3 and c["what"] == "track hp", c
    assert c["ref"] == ("ok", 90) and c["arm"] == ("ok", 95), c
    c = SC.compare(trace(), trace(taps=[(4, "NullReferenceException in CompX")]))
    assert c["verdict"] == SC.DIVERGED and c["tick"] == 4 and c["what"] == "event", c
    assert c["ref"] is None and "NullReferenceException" in c["arm"], c
    c = SC.compare(trace(taps=[(4, "A")]), trace(taps=[(4, "B")]))
    assert c["verdict"] == SC.DIVERGED and c["tick"] == 4, c


def t_wall_time_only_is_no_difference():
    a, b = trace(), trace(run="s2_r1", wall=7.25)
    assert a != b
    c = SC.compare(a, b)
    assert c["verdict"] == SC.EQUAL, c


def t_missing_tick_range_is_could_not_compare():
    full = trace(hp=(100,) * 21, end=("hit", 20))
    cut = trace(run="s2_r1", hp=(100,) * 21, end=("cancelled", 5))
    c = SC.compare(full, cut)
    assert c["verdict"] == SC.COULD_NOT and "6..20" in c["why"], c
    gap = trace()
    del gap[2]
    c = SC.compare(trace(), gap)
    assert c["verdict"] == SC.COULD_NOT and "not whole" in c["why"], c
    j = SC.judge_arms([sample(rows=full), sample(arm="step", rows=cut)], ORIGIN, 1)
    assert j["step"]["counts"] is False and "could not compare" in j["step"]["line"], j


def t_replay_is_never_a_sample():
    s = sample(replayed=True)
    assert SC.refuse(s, ORIGIN)[0] == "REPLAY"
    j = SC.judge_arms([sample(), sample(rows=trace()), sample(replayed=True, rows=trace(run="s3_r1"))], ORIGIN, 2)
    assert j["play1"]["runs"] == 1 and j["play1"]["refused"] == 2 and j["play1"]["counts"] is False, j


def t_runs_not_from_one_save_are_refused():
    other = dict(SAVE, sha256="cd" * 32)
    assert SC.refuse(sample(save=other), ORIGIN)[0] == "NOT_ONE_SAVE"
    assert SC.refuse(sample(save={"name": SAVE["name"], "sha256": None}), ORIGIN)[0] == "NOT_ONE_SAVE"
    assert SC.refuse(sample(rows=trace(start=T0 + 60)), ORIGIN)[0] == "NOT_ONE_SAVE"
    assert SC.refuse(sample(), ORIGIN) is None


def t_run_whose_rand_was_not_written_back_is_refused():
    assert SC.refuse(sample(rows=trace(rand="999")), ORIGIN)[0] == "RAND_NOT_WRITTEN"
    assert SC.refuse(sample(rand_want=None), ORIGIN)[0] == "RAND_NOT_WRITTEN"
    assert SC.refuse(sample(), dict(ORIGIN, rand=None))[0] == "RAND_NOT_WRITTEN"


def t_comparison_under_another_key_is_not_used():
    k1 = SC.key("plan1", {"Mod.dll": "aa"}, "comp1", "list1", "step")
    k2 = SC.key("plan1", {"Mod.dll": "aa"}, "comp2", "list1", "step")
    k3 = SC.key("plan1", {"Mod.dll": "ab"}, "comp1", "list1", "step")
    store = SC.record({}, k1, {"counts": True, "line": "no divergence observed in 5 runs"})
    assert SC.counts_for_bar(store, k1) is True
    assert SC.counts_for_bar(store, k2) is False and SC.counts_for_bar(store, k3) is False
    assert SC.counts_for_bar(store, SC.key("plan1", {"Mod.dll": "aa"}, "comp1", "list1", "ultra")) is False
    forged = copy.deepcopy(store)
    forged[k1["id"]]["key"] = k2["key"]
    assert SC.counts_for_bar(forged, k1) is False
    assert SC.counts_for_bar({}, SC.key("plan1", {}, "c", "l", SC.REFERENCE)) is True


def main():
    checks = (t_equal_traces_compare_equal, t_track_or_tap_difference_names_tick_and_value, t_wall_time_only_is_no_difference,
              t_missing_tick_range_is_could_not_compare, t_replay_is_never_a_sample, t_runs_not_from_one_save_are_refused,
              t_run_whose_rand_was_not_written_back_is_refused, t_comparison_under_another_key_is_not_used)
    passed = 0
    for check in checks:
        try:
            check()
        except Exception as e:  # noqa: BLE001 - a crash of a check is its failure, named
            print("FAIL %s: %s: %s" % (check.__name__, type(e).__name__, e))
        else:
            passed += 1
            print("PASS %s" % check.__name__)
    print("selftest_scene_compare: %d checks passed" % passed)
    return int(passed != len(checks))


if __name__ == "__main__":
    raise SystemExit(main())

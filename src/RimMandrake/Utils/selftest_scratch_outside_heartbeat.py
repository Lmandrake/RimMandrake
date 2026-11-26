#!/usr/bin/env python3
"""Selftest: a slow reap run that is alive does not read as a frozen sanity record; a hung one still does
(OPS_SCRATCH_OUTSIDE_READING_RESTORE_WLTC).

The instance (Archmagi, 2026-11-26): the sanity record was stamped only at a reap run's start and end, and
disk.scratch_outside_blind alarms past 150 min. Reap runs run at the idle IO class with no budget: they took 137 min
(2026-11-25 03:19 PST) and 117 min, and one run stood at 100 min. A run past 150 min alarmed "frozen" while it worked.
The guard is on progress: the reaper stamps `beat` in the record while it runs (scratch_reap.sanity_beat), and
ops_watch takes freshness from the newer of the phase stamp and that beat.

Part one runs scratch_reap.sanity_beat on a planted record. Part two runs ops_watch.scratch_outside in-process on
planted records, with the shipped rules."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_scratch_outside_heartbeat_"))
os.environ.setdefault("RM_SCRATCH_REAP_RUNS", str(TMP / "runs.jsonl"))
import ops_watch as OW  # noqa: E402
import scratch_reap as SR  # noqa: E402

FAILS = []
BLIND = "disk.scratch_outside_blind"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
LIMIT = RULES["ranges"]["disk.scratch_outside_cap"]["max_age_min"]


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def record(start_age_min, beat_age_min=None, prev_end=True):
    now = time.time()
    d = {"start": {"at": now - start_age_min * 60, "measures": {"rm_scratch_clones": 3}, "problems": []}}
    if prev_end:
        d["prev_end"] = {"at": now - (start_age_min + 1) * 60, "measures": {"rm_scratch_clones": 2}, "problems": []}
    if beat_age_min is not None:
        d["beat"] = now - beat_age_min * 60
    return d


def blind(name, d):
    p = TMP / ("%s.json" % name)
    p.write_text(json.dumps(d))
    pts = OW.scratch_outside(p, time.time(), RULES)
    return pts[BLIND]["v"], (pts[BLIND].get("x") or {}).get("cause"), pts


# Part two: ops_watch reads freshness from the beat.
v, cause, pts = blind("slow_alive", record(LIMIT + 10, beat_age_min=1))
check("a run past the limit with a fresh beat reads not blind (the item's false alarm)", v == 0, (v, cause))
check("a run past the limit with a fresh beat still reports the start's count", pts["disk.scratch_outside_cap"].get("v") == 3,
      pts["disk.scratch_outside_cap"])
v, cause, _ = blind("hung", record(LIMIT + 10, beat_age_min=LIMIT + 5))
check("a run whose beat stopped past the limit reads blind, frozen", v == 1 and "frozen" in str(cause), (v, cause))
v, cause, _ = blind("no_beat", record(LIMIT + 10))
check("a record with no beat past the limit reads blind, frozen", v == 1 and "frozen" in str(cause), (v, cause))
v, cause, _ = blind("fresh_start", record(5))
check("a fresh start with no beat reads not blind", v == 0, (v, cause))
v, cause, _ = blind("beat_ahead", record(LIMIT + 10, beat_age_min=-30))
check("a beat dated ahead of the clock is not freshness: blind", v == 1, (v, cause))
v, cause, _ = blind("beat_text", dict(record(LIMIT + 10), beat="soon"))
check("a beat that is not a number is ignored: blind, frozen", v == 1 and "frozen" in str(cause), (v, cause))


def part_one():
    global FAILS
    # Part one: the reaper stamps the beat, keeps the phase rows, and throttles.
    sd = TMP / "state"
    sd.mkdir()
    SR.sanity_write(sd, "start", {"rm_scratch_clones": 3}, [])
    before = json.loads((sd / "sanity.json").read_text())
    SR._BEAT_AT = 0.0
    t0 = time.time()
    SR.sanity_beat(sd)
    got = json.loads((sd / "sanity.json").read_text())
    check("sanity_beat stamps a beat at the time of the call", isinstance(got.get("beat"), float) and got["beat"] >= t0, got)
    check("sanity_beat keeps the start row as it was", got.get("start") == before.get("start"), got)
    first = got.get("beat")
    SR.sanity_beat(sd)
    again = json.loads((sd / "sanity.json").read_text())
    check("a second beat inside the throttle does not rewrite the record", again.get("beat") == first, again)
    SR.sanity_write(sd, "start", {"rm_scratch_clones": 4}, [])
    fresh = json.loads((sd / "sanity.json").read_text())
    check("a new run's start drops the last run's beat", "beat" not in fresh, fresh)
    (sd / "sanity.json").write_text("{torn")
    SR._BEAT_AT = 0.0
    try:
        SR.sanity_beat(sd)
        torn_ok = (sd / "sanity.json").read_text() == "{torn"
    except Exception as e:  # noqa: BLE001
        torn_ok = "raised %r" % e
    check("a beat on a torn record never raises and leaves it torn (the start owns the record)", torn_ok is True, torn_ok)
    SR._BEAT_AT = 0.0
    try:
        SR.sanity_beat(None)    # a dry run or a test Ctx has no sanity dir
        none_ok = True
    except Exception as e:  # noqa: BLE001
        none_ok = "raised %r" % e
    check("sanity_beat with no sanity dir is a no-op", none_ok is True, none_ok)



try:
    part_one()
except Exception as e:  # noqa: BLE001
    check("part one ran", False, repr(e))

print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)

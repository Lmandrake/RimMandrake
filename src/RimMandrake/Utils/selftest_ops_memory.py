#!/usr/bin/env python3
"""selftest_ops_memory: ops_memory.py against the counterexamples its review raised (operations_metronome_strategy
§3, gpt_review findings on bands): zero MAD, missing means blind, sample density, a step that becomes normal,
counters with resets, booleans, a daily rhythm, time to a signed limit, learning, and the one-generation check.
Fixture series only, written to a temp dir; never the live ops_watch store."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["TZ"] = "UTC"
time.tzset()
TMP = tempfile.mkdtemp(prefix="ops_memory_selftest_")
os.environ["RM_OPS_WATCH_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_memory as om  # noqa: E402

H = 3600.0
NOW = 1793577600.0 + 12 * H        # a fixed instant at 12:00 UTC
RULES = {"band": {"sigma_floor_rel": 0.05, "sigma_floor_abs": 0.5},
         "targets": [{"key": "t.free_gb", "op": "<", "value": 20.0, "tag": "LOW", "alarm": True}]}
FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)
    print(("PASS " if cond else "FAIL ") + what)


def write(rows):
    p = Path(TMP) / "series" / "t.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: r[0])
    with open(p, "w") as f:
        for t, pts in rows:
            f.write(json.dumps({"t": t, "points": pts}) + "\n")


def grid(fn, days=7.0, step=900.0, key="t.x", mark="MEASURED"):
    """Rows every step seconds over days, ending at NOW; fn(t) -> value (None: the key is UNMEASURED)."""
    out, t = [], NOW - days * 24 * H
    while t <= NOW:
        v = fn(t)
        out.append((t, {key: {"v": v, "m": mark if v is not None else "UNMEASURED"}}))
        t += step
    return out


def run(rows):
    write(rows)
    return om.build(NOW, ["t"], RULES)["readings"]


# 1. zero MAD: a flat zero reading and a tiny wobble is not an outlier; a real jump is
r = run(grid(lambda t: 0.001 if t >= NOW - 0.1 * H else 0.0))["t.x"]
ok(r["state"] == "normal", "zero MAD: 0.001 after a week of zeros stays normal (got %s)" % r["state"])
r = run(grid(lambda t: 5.0 if t >= NOW - 0.1 * H else 0.0))["t.x"]
ok(r["state"] == "outside", "zero MAD: 5 after a week of zeros is outside (got %s)" % r["state"])

# 2. missing means blind: one measured point in 99 rows of the last day; stale; never measured
rows = grid(lambda t: 50.0 if t < NOW - 24 * H else None)
rows[-1] = (rows[-1][0], {"t.x": {"v": 50.0, "m": "MEASURED"}})
r = run(rows)["t.x"]
ok(r["state"] == "blind" and r["why"].startswith("sparse"), "sparse: 1 measured of ~97 rows is blind (%s)" % r.get("why"))
r = run(grid(lambda t: 50.0 if t < NOW - 5 * H else None))["t.x"]
ok(r["state"] == "blind" and r["why"].startswith("stale"), "stale: last measured 5 h ago at 15 min cadence (%s)" % r.get("why"))
r = run(grid(lambda t: None))["t.x"]
ok(r["state"] == "blind" and "never measured" in r["why"], "never measured is blind (%s)" % r.get("why"))

# 3. density: one hour holding 1000 samples of 10 must not drag a week of 50s
rows = grid(lambda t: 50.0)
rows += [(NOW - 3 * 24 * H + i * 3.0, {"t.x": {"v": 10.0, "m": "MEASURED"}}) for i in range(1000)]
r = run(rows)["t.x"]
ok(r["band"]["center"] == 50.0 and r["state"] == "normal",
   "density: 1000-sample burst gets one hourly vote (center %s)" % r["band"]["center"])

# 4. a step that the band HAS learned (5 of 7 days at the new level) is still kept, from the old level to the new
r = run(grid(lambda t: 100.0 if t < NOW - 5 * 24 * H else 140.0))["t.x"]
st = r.get("step") or {}
ok(r["band"]["center"] == 140.0 and r["state"] == "normal", "step: the band has learned 140 (%s)" % r["band"]["center"])
ok(st.get("from") == 100.0 and st.get("to") == 140.0, "step: 100 -> 140 kept (%s)" % st)
ok(abs(st.get("at", 0) - (NOW - 5 * 24 * H)) <= H, "step: dated at the change")
for per in (6, 12, 24, 48):                      # a repeating cycle is not a step (each side's MAD can be 0)
    r = run(grid(lambda t, per=per: 100.0 if (t // H) % per < per / 2 else 140.0))["t.x"]
    ok("step" not in r, "no step in a %d h 100/140 cycle (%s)" % (per, r.get("step")))
r = run(grid(lambda t: 100.0 + (t % 7)))["t.x"]
ok("step" not in r, "no step in a level series with small noise")

# 5. a counter: rises, resets once, is read as a rate, the reset never a collapse
rows = grid(lambda t: (t - (NOW - 7 * 24 * H)) / H * 2.0 % 200.0, key="t.week_used_pct")
r = run(rows)["t.week_used_pct"]
ok(r["kind"] == "counter" and r["kind_from"] == "named", "counter: named kind")
ok(r["resets_7d"] >= 1 and abs(r["v"] - 2.0) < 0.01 and r["state"] == "normal",
   "counter: rate 2/h, %s resets, state %s" % (r["resets_7d"], r["state"]))

# 6. booleans are flags read by dwell: a rare state held longer than ever before is outside
rows = grid(lambda t: True if (t % (24 * H)) < 2 * H else False)
for i, (t, pts) in enumerate(rows):
    if t >= NOW - 5 * H:
        rows[i] = (t, {"t.x": {"v": True, "m": "MEASURED"}})
r = run(rows)["t.x"]
ok(r["kind"] == "flag", "flag: booleans read as a flag (got %s)" % r["kind"])
ok(r["state"] == "outside" and r["dwell_h"] > r["longest_dwell_h"],
   "flag: true for 5 h, longest before 2 h, is outside (%s, %s h)" % (r["state"], r.get("dwell_h")))
ok("slope_6h" not in r, "flag: no slope")
r = run(grid(lambda t: t >= NOW - 2 * H, days=0.4))["t.x"]
ok(r["state"] == "blind" and r["why"].startswith("learning"), "flag: under 12 h of history is blind (%s)" % r.get("why"))

# 7. a daily rhythm: day 20, night 80. At noon 80 is outside on the same-hour band, 20 normal
day = lambda t: 20.0 if 8 <= time.gmtime(t).tm_hour < 20 else 80.0  # noqa: E731
r = run(grid(lambda t: 80.0 if t >= NOW - 0.5 * H else day(t)))["t.x"]
ok(r["band"]["kind"] == "same hour" and r["state"] == "outside",
   "rhythm: 80 at noon is outside (%s band, %s)" % (r["band"]["kind"], r["state"]))
r = run(grid(day))["t.x"]
ok(r["state"] == "normal", "rhythm: 20 at noon is normal (%s)" % r["state"])

# 8. time to a signed limit: 60 GB free, falling 2/h for the last day, limit < 20 -> about 20 h
rows = grid(lambda t: 100.0 if t < NOW - 20 * H else 100.0 - (t - (NOW - 20 * H)) / H * 2.0, key="t.free_gb")
r = run(rows)["t.free_gb"]
lm = r.get("limit") or {}
ok(lm.get("tag") == "LOW" and 18 <= lm.get("h", -1) <= 22, "limit: ~20 h to < 20 GB (%s)" % lm)
ok(r["trend_6h"] == "falling", "limit: trend falling (%s)" % r.get("trend_6h"))

# 9. learning: six hours of history is blind, not normal
r = run(grid(lambda t: 50.0, days=0.25))["t.x"]
ok(r["state"] == "blind" and r["why"].startswith("learning"), "learning: 6 h of history is blind (%s)" % r.get("why"))

# 10. one generation in both files; a torn pair and an old pair are refused
write(grid(lambda t: 50.0))
out = Path(TMP) / "out"
g1, _ = om.publish(om.build(NOW, ["t"], RULES), out)
g2, md = om.publish(om.build(NOW, ["t"], RULES), out)
ok(g2 == g1 + 1, "generation counts up (%d -> %d)" % (g1, g2))
good, why = om.check(out, NOW + 60)
ok(good, "check: fresh pair is OK (%s)" % why)
good, why = om.check(out, NOW + 31 * 60)
ok(not good and why.startswith("stale"), "check: 31 min old is refused (%s)" % why)
(out / "memory.md").write_text(md.replace("generation %d" % g2, "generation %d" % g1, 1))
good, why = om.check(out, NOW + 60)
ok(not good and why.startswith("two generations"), "check: torn pair is refused (%s)" % why)

# 11. the page: exceptions and blind lines shown, a normal flat reading is not
rows = grid(lambda t: 50.0)
for t, pts in rows:
    pts["t.hot"] = {"v": 90.0 if t >= NOW - 0.5 * H else 50.0, "m": "MEASURED"}
    pts["t.gone"] = {"v": None, "m": "UNMEASURED"}
write(rows)
md = om.render(om.build(NOW, ["t"], RULES), 1)
ok("- t.hot 90.0" in md and "outside" in md, "page: outside reading listed")
ok("- t.gone blind" in md, "page: blind reading listed")
ok("- t.x " not in md, "page: normal flat reading left out")
ok("- t: 1 blind, 1 normal, 1 outside" in md, "page: per-family count")

# 12. the page cut keeps every outside line, flags included, and every blind one
mem = {"written_at": NOW, "families": {}, "readings": {}}
for i in range(om.PAGE_MAX_LINES + 30):
    mem["readings"]["t.drift%03d" % i] = {"state": "drifting", "kind": "number", "v": 1.0, "side_h": 1.0,
                                          "band": {"lo": 0.0, "hi": 2.0, "kind": "7 d"}}
mem["readings"]["t.zflag"] = {"state": "outside", "kind": "flag", "v": 1.0, "dwell_h": 9.0, "longest_dwell_h": 2.0,
                              "changes_24h": 1}
mem["readings"]["t.zgone"] = {"state": "blind", "why": "stale"}
md = om.render(mem, 1)
ok("- t.zflag 1.00 for" in md, "page cut: an outside flag survives")
ok("- t.zgone blind" in md, "page cut: a blind line survives")
ok("calmer lines cut" in md and md.count("\n- ") <= om.PAGE_MAX_LINES + 2, "page cut: says how much was cut")

print("selftest_ops_memory: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)

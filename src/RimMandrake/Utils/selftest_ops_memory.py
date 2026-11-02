#!/usr/bin/env python3
"""selftest_ops_memory: ops_memory.py against the counterexamples its review raised (operations_metronome_strategy
§3, gpt_review findings on bands): zero MAD, missing means blind, sample density, a step that becomes normal,
counters with resets, booleans, a daily rhythm, time to a signed limit, learning, and the one-generation check.
Fixture rows go the real way: telemetry/ingest.parse_ops_watch -> store.VMSink -> a fake VictoriaMetrics that
answers /api/v1/export from what was imported; never the live store."""
import json
import os
import re
import sys
import tempfile
import time
import urllib.parse
from pathlib import Path

os.environ["TZ"] = "UTC"
time.tzset()
TMP = tempfile.mkdtemp(prefix="ops_memory_selftest_")
os.environ["RM_OPS_WATCH_DIR"] = TMP
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ops_memory as om  # noqa: E402
import ingest  # noqa: E402  (telemetry, on the path ops_memory set)
import store  # noqa: E402

H = 3600.0
NOW = 1793577600.0 + 12 * H        # a fixed instant at 12:00 UTC
RULES = {"band": {"sigma_floor_rel": 0.05, "sigma_floor_abs": 0.5},
         "targets": [{"key": "t.free_gb", "op": "<", "value": 20.0, "tag": "LOW", "alarm": True},
                     {"key": "t.week_used_pct", "op": ">", "value": 90.0, "tag": "WEEK", "alarm": True}]}
FAILS = []


def ok(cond, what):
    if not cond:
        FAILS.append(what)
    print(("PASS " if cond else "FAIL ") + what)


class FakeVM:
    """Holds what VMSink imported; answers /api/v1/export for the selectors ops_memory sends."""
    def __init__(self):
        self.lines, self.down, self.asked = [], False, []

    def post(self, body):
        self.lines.extend(json.loads(x) for x in body.decode().splitlines() if x)

    def get(self, path, url=None, timeout=5):
        if self.down:
            raise ConnectionRefusedError("fake VM down")
        u = urllib.parse.urlsplit(path)
        q = urllib.parse.parse_qs(u.query)
        assert u.path == "/api/v1/export", u.path
        lo, hi = float(q["start"][0]) * 1000, float(q["end"][0]) * 1000
        self.asked.append((q["match[]"], lo / 1000, hi / 1000))
        out = []
        for sel in q["match[]"]:
            m = re.fullmatch(r'\{__name__=~"([^"]+)"(?:,fam="([^"]+)")?\}|([a-z_]+)', sel)
            assert m, sel
            for x in self.lines:
                lab = x["metric"]
                if m.group(3) and lab["__name__"] != m.group(3):
                    continue
                if m.group(1) and not re.fullmatch(m.group(1), lab["__name__"]):
                    continue
                if m.group(2) and lab.get("fam") != m.group(2):
                    continue
                pairs = [(t, v) for t, v in zip(x["timestamps"], x["values"]) if lo <= t <= hi]
                if pairs:
                    out.append(json.dumps({"metric": lab, "timestamps": [t for t, _v in pairs],
                                           "values": [v for _t, v in pairs]}))
        return ("\n".join(out) + "\n").encode()


VM = FakeVM()


def write(rows, fam="t", keep=False):
    """Rows -> VM through the real parser and sink (the store is emptied first unless keep: one fixture at a time)."""
    if not keep:
        VM.lines = []
    sink = store.VMSink(url="http://fake", spool_dir=os.path.join(TMP, "spool"), post=VM.post)
    E = ingest.Emit(None, sink, {})
    for t, pts in sorted(rows, key=lambda r: r[0]):
        ingest.parse_ops_watch({"t": t, "points": pts}, E, "ops_watch:%s.jsonl:0" % fam)
    sink.flush()


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
    return om.build(NOW, ["t"], RULES, VM.get)["readings"]


# 0. a counter's signed limit is on its level, not its rate: past 90 % used is limit h=0 though the rate is flat
r = run(grid(lambda t: 95.0 if t >= NOW - 24 * H else 50.0 + (t - (NOW - 7 * 24 * H)) / H * 0.1, key="t.week_used_pct"))["t.week_used_pct"]
ok(r["kind"] == "counter" and (r.get("limit") or {}).get("h") == 0.0, "counter: level past its limit reports h=0 (%s)" % r.get("limit"))

# 0b. a counter read every minute that rises once an hour has a rate of 1/h, not a median of zeros
pts = [(i * 60.0, float(i // 60)) for i in range(0, 60 * 48)]
rt, _rs = om.to_rates(pts)
ok(rt and all(abs(r - 1.0) < 0.05 for _t, r in rt[1:-1]), "counter: per-minute reads of a 1/h counter rate 1/h (%s)" % [round(r, 2) for _t, r in rt[1:4]])

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
bk = [(i * 3600.0, 100.0 if i < 84 else 124.0, 1) for i in range(168)]       # a small step stays kept as the band learns 124
ok(om.find_step(bk, (0.05, 0.0)) is not None, "step: 100 -> 124 kept whatever the band centre is")
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
g1, _ = om.publish(om.build(NOW, ["t"], RULES, VM.get), out)
g2, md = om.publish(om.build(NOW, ["t"], RULES, VM.get), out)
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
md = om.render(om.build(NOW, ["t"], RULES, VM.get), 1)
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

# 13. the VM path: the fixture really reached the fake store, build --now asks nothing later than now, and a row
#     after now (a wild value) is not read
rows = grid(lambda t: 50.0) + [(NOW + 600.0, {"t.x": {"v": 9999.0, "m": "MEASURED"}})]
write(rows)
ok(len(VM.lines) > 0, "vm path: the parser and sink imported the fixture (%d series)" % len(VM.lines))
VM.asked = []
r = om.build(NOW, ["t"], RULES, VM.get)["readings"]["t.x"]
ok(VM.asked and all(hi == NOW for _m, _lo, hi in VM.asked), "vm path: export ends at --now (%s)" % VM.asked[:1])
ok(r["last"] == 50.0 and r["state"] == "normal", "vm path: a row after --now is not read (last %s)" % r.get("last"))

# 14. a row ingested twice (a telemetry rebuild) is one row: coverage and cadence do not double
rows = grid(lambda t: 50.0)
write(rows)
once = om.build(NOW, ["t"], RULES, VM.get)
VM.lines = VM.lines + [dict(x) for x in VM.lines]
twice = om.build(NOW, ["t"], RULES, VM.get)
ok(twice["built_from"]["t"]["rows"] == once["built_from"]["t"]["rows"]
   and twice["readings"]["t.x"]["coverage_24h"] == once["readings"]["t.x"]["coverage_24h"] == 1.0,
   "vm path: a duplicated ingest counts each row once (%s rows)" % twice["built_from"]["t"]["rows"])

# 15. ESTIMATE and text are not measurements: a key only ever estimated is blind, never normal
rows = grid(lambda t: 50.0)
for t, pts in rows:
    pts["t.est"] = {"v": 7.0, "m": "ESTIMATE"}
    pts["t.word"] = {"v": "fine", "m": "MEASURED"}
write(rows)
rd = om.build(NOW, ["t"], RULES, VM.get)["readings"]
ok(rd["t.est"]["state"] == "blind" and rd["t.word"]["state"] == "blind",
   "vm path: estimated and text keys are blind (%s, %s)" % (rd["t.est"].get("why"), rd["t.word"].get("why")))

# 16. VM down: a blind generation that says so, never an empty one; check refuses it
VM.down = True
mem = om.build(NOW, ["t"], RULES, VM.get)
VM.down = False
md = om.render(mem, 1)
ok(mem.get("store_error") and "BLIND: the trend store did not answer" in md, "vm down: the page says the store is blind")
out2 = Path(TMP) / "out_down"
om.publish(mem, out2)
good, why = om.check(out2, NOW + 60)
ok(not good and why.startswith("blind"), "vm down: check refuses a blind generation (%s)" % why)

# 16b. the store answers but holds no rows for a family: that family is blind on the page, not quiet
write(grid(lambda t: 50.0))
mem = om.build(NOW, ["t", "empty"], RULES, VM.get)
md = om.render(mem, 1)
ok("- empty (whole family) blind: no rows" in md and "- empty: BLIND, no rows" in md and "- t: 1 normal" in md,
   "no rows: an empty family is blind on the page")

# 16c. the newest row is UNMEASURED after a healthy week: blind now, not a fresh-looking normal (review r1 of the
# VM wiring: the old reading kept the previous measurement and coverage and the key vanished from the page)
rows = grid(lambda t: 50.0)
rows[-1] = (rows[-1][0], {"t.x": {"v": None, "m": "UNMEASURED"}})
rd = run(rows)["t.x"]
ok(rd["state"] == "blind" and rd["why"].startswith("now UNMEASURED"), "latest blind: an unmeasured newest row is blind (%s)" % rd.get("why"))
rows[-1] = (rows[-1][0], {"t.x": {"v": 3.0, "m": "ESTIMATE"}})
rd = run(rows)["t.x"]
ok(rd["state"] == "blind" and rd["why"].startswith("now ESTIMATE"), "latest blind: an estimated newest row is blind (%s)" % rd.get("why"))

rows = grid(lambda t: 50.0)
rows[-1] = (rows[-1][0], {"t.other": {"v": 1.0, "m": "MEASURED"}})
rd = run(rows)["t.x"]
ok(rd["state"] == "blind" and rd["why"].startswith("now absent"), "latest blind: a key the newest row lacks is blind (%s)" % rd.get("why"))

# 17. wait_ingest waits for THIS pass (its status.json time stamp) in every family, then settles; an earlier pass,
# one family alone, or no pass at all is an error the generation carries (review r1: any row of the last 5 min,
# from any family, used to satisfy it)
clock = [NOW]
def tick(dt):
    clock[0] += dt
PASS = NOW - 40.0
write([(PASS, {"a.x": {"v": 1.0, "m": "MEASURED"}})], fam="a")
write([(PASS, {"b.x": {"v": 1.0, "m": "MEASURED"}})], fam="b", keep=True)
w = om.wait_ingest(60, ["a", "b", "production"], PASS, VM.get, clock=lambda: clock[0], sleep=tick)
ok(w["error"] is None and w["waited_s"] >= om.SETTLE_S - 1e-6 and not w["missing"],
   "wait_ingest: this pass in every family (production exempt) is waited past one settle (%s)" % w)
clock[0] = NOW
w = om.wait_ingest(0.001, ["a", "b"], PASS, VM.get, clock=lambda: clock[0], sleep=tick)
ok(w["error"] is None and w["waited_s"] >= om.SETTLE_S - 1e-6,
   "wait_ingest: a pass seen at the deadline still gets the whole settle (review r2) (%s)" % w)
clock[0] = NOW
write([(PASS - 30.0, {"a.x": {"v": 1.0, "m": "MEASURED"}})], fam="a")     # the previous pass, 30 s earlier
write([(PASS, {"b.x": {"v": 1.0, "m": "MEASURED"}})], fam="b", keep=True)
w = om.wait_ingest(30, ["a", "b"], PASS, VM.get, clock=lambda: clock[0], sleep=tick)
ok(w["error"] and w["missing"] == ["a"] and clock[0] - NOW >= 30,
   "wait_ingest: an earlier pass in one family is not this pass (%s)" % w.get("error"))
clock[0] = NOW
w = om.wait_ingest(30, ["a"], NOW - 3 * H, VM.get, clock=lambda: clock[0], sleep=tick)
ok(w["error"] and "no ops_watch pass" in w["error"] and clock[0] == NOW, "wait_ingest: an old pass is refused at once")
w = om.wait_ingest(30, ["a"], PASS, lambda *a, **k: (_ for _ in ()).throw(ConnectionRefusedError("down")),
                   clock=lambda: clock[0], sleep=tick)
ok(w["error"] and "did not answer" in w["error"], "wait_ingest: VM down while waiting is an error")
# ... and that error makes the generation blind on the page and in check
write(grid(lambda t: 50.0))
mem = om.build(NOW, ["t"], RULES, VM.get)
mem["ingest"] = {"error": "telemetryd had not carried the pass", "missing": ["t"]}
out3 = Path(TMP) / "out_ingest"
_g, md = om.publish(mem, out3)
good, why = om.check(out3, NOW + 60)
ok("BLIND: this generation does not hold the pass" in md and not good and "lacks the pass" in why,
   "ingest error: the page says so and check refuses (%s)" % why)

print("selftest_ops_memory: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)

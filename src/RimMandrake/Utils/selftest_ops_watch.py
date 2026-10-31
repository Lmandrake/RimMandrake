#!/usr/bin/env python3
"""selftest for ops_watch.py (V3_ROLES_BUILD_EIGHT_CHAIRS_ONE_TABLE, the Dispatcher's measurement arm for Operations).

Fixtures only: the store, the steward files, the testq done records and the scratch-reap log live under a temp dir;
no real ledger, systemd, filer or meter is touched (collectors that would are replaced). Covers: runway, the four Andon
rules (band, run, silent, target and its marks), the alarm edge (file once, hold while crossed, hold on UNMEASURED,
re-arm and note after it clears, PENDING retried after a failed filing), a collector that raises turning into
UNMEASURED never 0, the Steve collector's unowned-stall and INVALID-streak logic, the testing "caught" rule, the
production de-dup, the digest's deltas, and the CLI's install plan writing nothing.

    python3 src/RimMandrake/Utils/selftest_ops_watch.py
"""
import copy
import json
import os
import re
import subprocess
import types
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_watch_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
os.environ["RM_SCRATCH_REAP_RUNS"] = str(TMP / "reap.jsonl")
os.environ["RM_OPS_DISKS"] = "root=%s" % TMP
import ops_watch as OW  # noqa: E402

for _k in [k for k in os.environ if k.startswith("GIT_")]:      # nor may a collector's git follow a hook's GIT_DIR out of the fixture
    del os.environ[_k]

FAILS = []
H = 3600.0
DAY = 86400.0
NOW = 1793050000.0
RULES = OW.load_rules()


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def wj(p, obj):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj))


def rules(**over):
    r = json.loads(json.dumps(RULES))
    r.update(over)
    return r


# ---------------------------------------------------------------- runway
check("runway: 50% left at 1%/h, 100 h to reset -> 0.5", OW.runway(50, 1.0, 100) == 0.5)
check("runway: no burn -> capped 10", OW.runway(50, 0, 100) == 10.0)
check("runway: no reset time -> None", OW.runway(50, 1.0, None) is None)
check("runway: cap 10", OW.runway(90, 0.01, 10) == 10.0)

# ---------------------------------------------------------------- Andon
M = OW.M
hist = {"x.a": [(NOW - (i + 2) * H, 10.0 + (i % 2)) for i in range(30)]}
fl = OW.andon({"x.a": M(30.0)}, hist, {}, rules(targets=[]), NOW)
check("band: 30 vs a 10-11 baseline flags", any(f["rule"] == "band" and f["key"] == "x.a" for f in fl), fl)
check("band: the flag names its window", any("baseline" in f["window"] for f in fl if f["rule"] == "band"))
fl = OW.andon({"x.a": M(10.5)}, hist, {}, rules(targets=[]), NOW)
check("band: 10.5 inside the band does not flag", not any(f["rule"] == "band" for f in fl), fl)
few = {"x.a": hist["x.a"][:5]}
fl = OW.andon({"x.a": M(99.0)}, few, {}, rules(targets=[]), NOW)
check("band: under min_points no flag", not any(f["rule"] == "band" for f in fl), fl)
flat = {"x.a": [(NOW - (i + 2) * H, 100.0) for i in range(30)]}
fl = OW.andon({"x.a": M(102.0)}, flat, {}, rules(targets=[]), NOW)
check("band: a flat series uses the sigma floor (102 vs 100 does not flag)", not any(f["rule"] == "band" for f in fl), fl)
fl = OW.andon({"x.a": OW.U("blind")}, hist, {}, rules(targets=[]), NOW)
check("band: an UNMEASURED point never flags band", not any(f["rule"] == "band" for f in fl), fl)
skip = {"disk.root_used_gb": [(NOW - (i + 2) * H, 10.0) for i in range(30)]}
fl = OW.andon({"disk.root_used_gb": M(500.0)}, skip, {}, rules(targets=[]), NOW)
check("band: a skipped key (disk.*_used_gb) does not flag", not any(f["rule"] == "band" for f in fl), fl)

rr = rules(targets=[], run={"n": 4, "keys": ["k.*"]})
rise = {"k.r": [(NOW - (10 - i) * H, v) for i, v in enumerate([1, 2, 2, 3, 4])]}
fl = OW.andon({"k.r": M(5.0)}, rise, {}, rr, NOW)
check("run: 1,2,2,3,4,5 is 4 rises in a row (equal neighbours collapse)",
      any(f["rule"] == "run" and "rising 4" in f["detail"] for f in fl), fl)
fl = OW.andon({"k.r": M(3.5)}, rise, {}, rr, NOW)
check("run: a reversal breaks the run", not any(f["rule"] == "run" for f in fl), fl)
fl = OW.andon({"z.r": M(5.0)}, {"z.r": rise["k.r"]}, {}, rr, NOW)
check("run: a key not listed is not run-checked", not any(f["rule"] == "run" for f in fl), fl)

sr = rules(targets=[])
fl = OW.andon({"steve.state": OW.U("steward.json missing")}, {}, {"steve.state": NOW - 3 * H}, sr, NOW)
check("silent: MEASURED 3 h ago, now UNMEASURED, limit 2 h -> flag",
      any(f["rule"] == "silent" and f["key"] == "steve.state" for f in fl), fl)
fl = OW.andon({"steve.state": OW.U("x")}, {}, {"steve.state": NOW - 1 * H}, sr, NOW)
check("silent: within its hours no flag", not any(f["rule"] == "silent" for f in fl), fl)
fl = OW.andon({"tps.ratio_median": OW.U("game off")}, {}, {"tps.ratio_median": NOW - 30 * H}, sr, NOW)
check("silent: tps.* (game off is normal) never flags", not any(f["rule"] == "silent" for f in fl), fl)
fl = OW.andon({"steve.state": OW.U("x")}, {}, {}, sr, NOW)
check("silent: never MEASURED in the baseline -> no flag (nothing went blind)", not fl, fl)

tr = rules(band={**RULES["band"], "keys": []})
fl = OW.andon({"accounts.a.runway": OW.E(0.5, "avg burn")}, {}, {}, tr, NOW)
check("target: an ESTIMATE runway < 1 flags (marks allow ESTIMATE)",
      any(f["rule"] == "target" and f.get("tag") == "RUNWAY_LOW" for f in fl), fl)
fl = OW.andon({"steve.invalid_streak": OW.E(5, "guess")}, {}, {}, tr, NOW)
check("target: an ESTIMATE where only MEASURED counts does not flag", not any(f["rule"] == "target" for f in fl), fl)
fl = OW.andon({"disk.root_free_gb": M(300.0)}, {}, {}, tr, NOW)
tags = sorted(f.get("tag") for f in fl if f["rule"] == "target")
check("target: 300 GB free on / is DISK_TWO_DAYS (flag) but not DISK_LOW", tags == ["DISK_TWO_DAYS"], tags)
fl = OW.andon({"disk.root_free_gb": M(100.0)}, {}, {}, tr, NOW)
tags = sorted(f.get("tag") for f in fl if f["rule"] == "target")
check("target: 100 GB free on / is DISK_LOW and DISK_TWO_DAYS", tags == ["DISK_LOW", "DISK_TWO_DAYS"], tags)

# ---------------------------------------------------------------- alarms (edge-triggered)
calls = []


def filer_ok(todo, conf):
    calls.append([dict(a) for a in todo])
    known.update(a["name"] for a in todo if not a.get("note_only"))  # the real ledger now holds the name
    return {a["name"]: None for a in todo}


def filer_bad(todo, conf):
    calls.append([dict(a) for a in todo])
    return {a["name"]: "push refused" for a in todo}


known = set()
MINTS = []


def fake_mint(tag, known, prefix):
    # unique per mint and never a known name, so a re-mint on retry or a reused name after a clear shows up
    MINTS.append(prefix)
    for i in range(100):
        name = "%s_%s" % (prefix, "AB12" if i == 0 else "C%03d" % (len(MINTS) * 100 + i))
        if name not in known:
            return name
    raise RuntimeError("no name")


def no_mint(tag, known, prefix):
    raise RuntimeError("no mintable alarm name for " + tag)


OW.mint_name = no_mint
pts = {"timers.failed_units": M(2)}
st = OW.run_alarms(pts, RULES, NOW, known, filer_bad)
a = st.get("TIMER_FAILED:timers.failed_units") or {}
check("alarm: an unnameable alarm stays PENDING and said, the pass survives",
      a.get("state") == "PENDING" and "no mintable" in (a.get("error") or "") and a.get("tries") == 1 and not calls, a)
OW.mint_name = fake_mint
st = OW.run_alarms(pts, RULES, NOW, known, filer_bad)
a = st.get("TIMER_FAILED:timers.failed_units") or {}
check("alarm: a NEW crossing tries to file", len(calls) == 1 and calls[0][0]["name"] == "OPS_TIMER_REPAIR_AB12", calls)
check("alarm: a failed filing stays PENDING with the error", a.get("state") == "PENDING" and a.get("error") == "push refused", a)
st = OW.run_alarms(pts, RULES, NOW + 900, known, filer_ok)
a = st.get("TIMER_FAILED:timers.failed_units") or {}
check("alarm: PENDING is retried next pass and opens", len(calls) == 2 and a.get("state") == "OPEN" and a.get("item"), a)
check("alarm: the retry keeps the same name and mints nothing", calls[1][0]["name"] == "OPS_TIMER_REPAIR_AB12"
      and MINTS.count("OPS_TIMER_REPAIR") == 1, (calls[1], MINTS))
st = OW.run_alarms(pts, RULES, NOW + 1800, known, filer_ok)
check("alarm: still crossed and OPEN -> nothing filed again", len(calls) == 2, calls)
st = OW.run_alarms({"timers.failed_units": OW.U("systemctl failed")}, RULES, NOW + 2700, known, filer_ok)
check("alarm: an UNMEASURED reading holds the alarm (no clear, no file)",
      len(calls) == 2 and (st.get("TIMER_FAILED:timers.failed_units") or {}).get("state") == "OPEN", st)
CP = RULES["alarm"]["clear_passes"]
check("alarm: rules hold off a clear for more than one pass", CP > 1, CP)
st = OW.run_alarms({"timers.failed_units": M(0)}, RULES, NOW + 3600, known, filer_ok)
check("alarm: one clear reading does not clear (hysteresis)",
      (st.get("TIMER_FAILED:timers.failed_units") or {}).get("state") == "OPEN" and len(calls) == 2, st)
st = OW.run_alarms(pts, RULES, NOW + 3700, known, filer_ok)
check("alarm: crossing again during hysteresis files nothing and resets the clear count",
      len(calls) == 2 and (st.get("TIMER_FAILED:timers.failed_units") or {}).get("clear_seen") == 0, st)
for i in range(CP):
    st = OW.run_alarms({"timers.failed_units": M(0)}, RULES, NOW + 3800 + i, known, filer_ok)
    if i < CP - 1:
        check("alarm: clear reading %d of %d keeps it OPEN, no note" % (i + 1, CP),
              (st.get("TIMER_FAILED:timers.failed_units") or {}).get("state") == "OPEN" and len(calls) == 2, st)
check("alarm: clear_passes clear readings in a row re-arm the alarm and note the item",
      "TIMER_FAILED:timers.failed_units" not in st and len(calls) == 3 and calls[2][0].get("note_only")
      and calls[2][0]["item"] == "OPS_TIMER_REPAIR_AB12", calls[-1])
st = OW.run_alarms(pts, RULES, NOW + 4500, known, filer_ok)
check("alarm: a second crossing after the clear files a NEW item under a NEW name", len(calls) == 4
      and not calls[3][0].get("note_only") and calls[3][0]["name"] != "OPS_TIMER_REPAIR_AB12", calls)
calls.clear()
st = OW.run_alarms({"disk.root_free_gb": M(50.0)}, RULES, NOW, known, None)
a = st.get("DISK_LOW:disk.root_free_gb") or {}
check("alarm: without --file-alarms the crossing is recorded PENDING and nothing is filed",
      a.get("state") == "PENDING" and "filing off" in (a.get("error") or "") and not calls, a)
check("alarm: DISK_TWO_DAYS (alarm false) never makes an alarm", not any(k.startswith("DISK_TWO_DAYS") for k in st), st)
log = (TMP / "ops" / "alarms_log.jsonl").read_text().splitlines()
ev = [json.loads(x)["event"] for x in log]
check("alarm: the log records crossed / file_failed / filed / cleared", all(e in ev for e in
                                                                             ("crossed", "file_failed", "filed", "cleared")), ev)

# a failed filing keeps retrying while the reading is UNMEASURED (the crossing was real)
calls.clear()
(TMP / "ops" / "alarms.json").unlink()
st = OW.run_alarms({"steve.invalid_streak": M(4)}, RULES, NOW, known, filer_bad)
st = OW.run_alarms({"steve.invalid_streak": OW.U("steward.json missing")}, RULES, NOW + 900, known, filer_ok)
a = st.get("STEVE_INVALID:steve.invalid_streak") or {}
check("alarm: PENDING + UNMEASURED still retries the filing, same name, and opens",
      len(calls) == 2 and calls[1][0]["name"] == calls[0][0]["name"] and a.get("state") == "OPEN", (calls, a))
# a pass that filed and died before saving: the next pass finds the name in the ledger and never files it twice
calls.clear()
(TMP / "ops" / "alarms.json").unlink()


def filer_dies(todo, conf):
    calls.append([dict(x) for x in todo])
    raise SystemExit("killed mid-filing")


died = False
try:
    OW.run_alarms({"disk.d_free_gb": M(10.0)}, RULES, NOW, known, filer_dies)
except SystemExit:
    died = True
check("alarm: (fixture) the first pass died inside the spawn after one call", died and len(calls) == 1, calls)
saved = OW.read_json(TMP / "ops" / "alarms.json") or {}
nm = (saved.get("DISK_LOW:disk.d_free_gb") or {}).get("name")
check("alarm: the minted name is on disk before the spawn", nm == "OPS_DISK_DRAIN_AB12", saved)
st = OW.run_alarms({"disk.d_free_gb": M(10.0)}, RULES, NOW + 900, {nm}, filer_ok)
a = st.get("DISK_LOW:disk.d_free_gb") or {}
check("alarm: a name already in the ledger opens without a second spawn (the retry adds no call)",
      len(calls) == 1 and a.get("state") == "OPEN" and a.get("item") == nm, (calls, a))
# one pass at a time
import fcntl  # noqa: E402
with open(TMP / "ops" / "run.lock", "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    try:
        OW.run(now=NOW, rules=RULES, filer=None, families=["disk"])
        busy = False
    except OW.Busy:
        busy = True
check("run: a second pass while one holds run.lock raises Busy (main exits 0, says skipped)", busy)

# ---------------------------------------------------------------- Steve collector (fixture QHOME)
Q = TMP / "q"
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
wj(Q / "steward_watch.json", {"epoch": NOW - 30, "incident": None})


def job(i, outcome, fin, started=None, fail=0, findings=None, item=None):
    d = {"job": {"id": "j%d" % i, "item": item}, "finished": OW.iso(fin),
         "result": {"outcome": outcome, "counts": {"PASS": 1, "FAIL": fail}, "started": OW.iso(started or fin - 600),
                    "finished": OW.iso(fin)}}
    if findings is not None:
        d["ingested"] = {"groups": {item or "X": {"findings": findings}}}
    p = Q / "done" / ("j%d.json" % i)
    wj(p, d)
    os.utime(p, (fin, fin))


job(1, "DONE", NOW - 5 * H)
job(2, "INVALID", NOW - 4 * H)
job(3, "INVALID", NOW - 3 * H)
job(4, "INVALID", NOW - 2 * H)
ctx = {}
s = OW.c_steve(NOW, RULES, ctx)
check("steve: 3 trailing INVALID -> streak 3 MEASURED", s["steve.invalid_streak"] == {**s["steve.invalid_streak"], "v": 3, "m": "MEASURED"}, s["steve.invalid_streak"])
check("steve: RUNNING with live heartbeats -> unowned stall 0", s["steve.unowned_stall_min"]["v"] == 0.0, s["steve.unowned_stall_min"])
check("steve: jobs_24h counts the fixture", s["steve.jobs_24h"]["v"] == 4, s["steve.jobs_24h"])
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": True, "incident": None,
                        "since": OW.iso(NOW - 45 * 60)})
s = OW.c_steve(NOW, RULES, {})
check("steve: a 45 min fault with no steward incident -> unowned stall 45",
      abs(s["steve.unowned_stall_min"]["v"] - 45) < 0.2, s["steve.unowned_stall_min"])
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": True, "incident": "INC1",
                        "since": OW.iso(NOW - 45 * 60)})
s = OW.c_steve(NOW, RULES, {})
check("steve: the same fault with a steward incident is owned -> 0", s["steve.unowned_stall_min"]["v"] == 0.0,
      s["steve.unowned_stall_min"])
wj(Q / "steward.json", {"epoch": NOW - 50 * 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
wj(Q / "steward_watch.json", {"epoch": NOW - 40 * 60, "incident": None})
s = OW.c_steve(NOW, RULES, {})
check("steve: steward AND watcher both silent > 30 min -> unowned stall = heartbeat age",
      abs(s["steve.unowned_stall_min"]["v"] - 50) < 0.2, s["steve.unowned_stall_min"])
wj(Q / "steward_watch.json", {"epoch": NOW - 40 * 60, "incident": {"item": "STEVE_LANE_UNSTICK_AB12"}})
_ic = OW.incident_item_closed
OW.incident_item_closed = lambda inc: False
s = OW.c_steve(NOW, RULES, {})
check("steve: an open incident is not an unowned stall (its ownership cannot be seen, so unknown)", s["steve.unowned_stall_min"]["v"] is None, s["steve.unowned_stall_min"])
OW.incident_item_closed = lambda inc: True
s = OW.c_steve(NOW, RULES, {})
check("steve: a closed incident owns nothing when steward and watcher are both silent",
      abs(s["steve.unowned_stall_min"]["v"] - 50) < 0.2, s["steve.unowned_stall_min"])
OW.incident_item_closed = _ic
check("steve: an incident with no item is not closed", OW.incident_item_closed({"level": 1}) is False
      and OW.incident_item_closed("text") is False, "")
wj(Q / "steward_watch.json", {"epoch": NOW - 40 * 60, "incident": None})
_it = types.SimpleNamespace(id="STEVE_LANE_UNSTICK_F1", state="proposed", blocked=False, created_at=NOW + 3600)
_wd = types.SimpleNamespace(items={"a": _it})
_md = types.SimpleNamespace(lease_status=lambda i, n: "none", epoch=lambda v: v)
check("steve: a future incident time is UNMEASURED, not 0 min",
      OW.steve_incident_unclaimed(_wd, _md, NOW, RULES)["m"] == "UNMEASURED", "")
(Q / "steward.json").unlink()
s = OW.c_steve(NOW, RULES, {})
check("steve: no steward.json -> state UNMEASURED, not a number", s["steve.state"]["m"] == "UNMEASURED"
      and s["steve.unowned_stall_min"]["v"] is None, s["steve.state"])

# ---------------------------------------------------------------- testing "caught"
d0 = {"job": {"item": "IT_A"}, "finished": OW.iso(NOW), "result": {"counts": {"FAIL": 0}, "finished": OW.iso(NOW)}}
check("caught: no FAIL, no finding, no close -> nothing", not OW.caught(d0, {}, 24))
check("caught: a FAIL row counts", OW.caught({**d0, "result": {"counts": {"FAIL": 1}}}, {}, 24))
check("caught: a close of the run item within 24 h counts", OW.caught(d0, {"IT_A": [NOW + 5 * H]}, 24))
check("caught: a close 30 h later does not", not OW.caught(d0, {"IT_A": [NOW + 30 * H]}, 24))
check("caught: a close BEFORE the run does not", not OW.caught(d0, {"IT_A": [NOW - H]}, 24))
check("caught: an ingested finding counts", OW.caught({**d0, "ingested": {"groups": {"IT_A": {"findings": ["F"]}}}}, {}, 24))
t = OW.c_testing(NOW, RULES, {"steve_jobs": [], "closes": None})
check("testing: an unreadable ledger -> UNMEASURED (never 0)", t["testing.nothing_h_7d"]["m"] == "UNMEASURED", t)

# ---------------------------------------------------------------- disk (fixture mount + reap log)
Path(os.environ["RM_SCRATCH_REAP_RUNS"]).write_text(json.dumps({"ts": OW.iso(NOW - H), "rows": [
    {"verdict": "YOUNG", "bytes": 3e9}, {"verdict": "REFUSE", "bytes": 1e9}, {"verdict": "DELETED", "bytes": 9e9}]}) + "\n")
dk = OW.c_disk(NOW, RULES, {})
check("disk: the fixture mount reads MEASURED", dk["disk.root_free_gb"]["m"] == "MEASURED", dk["disk.root_free_gb"])
check("disk: scratch = YOUNG + REFUSE (DELETED is gone)", dk["disk.scratch_total_gb"]["v"] == 4.0, dk["disk.scratch_total_gb"])
dk = OW.c_disk(NOW + 10 * H, RULES, {})
check("disk: a reap log 11 h old -> scratch UNMEASURED", dk["disk.scratch_total_gb"]["m"] == "UNMEASURED", dk["disk.scratch_total_gb"])
os.environ["RM_OPS_DISKS"] = "root=/no/such/mount_ops_watch"
dk = OW.c_disk(NOW, RULES, {})
check("disk: a missing mount -> UNMEASURED, never 0", dk["disk.root_free_gb"]["m"] == "UNMEASURED"
      and dk["disk.root_free_gb"]["v"] is None, dk["disk.root_free_gb"])
os.environ["RM_OPS_DISKS"] = "root=%s" % TMP

# ---------------------------------------------------------------- run(): a raising collector, de-dup, digest
saved = dict(OW.COLLECTORS)
state = {"n": 0}


def fake_disk(now, rules, ctx):
    state["n"] += 1
    if state["n"] == 2:
        raise OSError("mount gone")
    return {"disk.root_free_gb": M(400.0 - state["n"]), "disk.d_free_gb": M(1000.0)}


def fake_prod(now, rules, ctx):
    ctx["production_src_t"] = 1234.0
    return {"production.P1": M(5)}


for k in list(OW.COLLECTORS):
    OW.COLLECTORS[k] = (lambda now, rules, ctx: {})
OW.COLLECTORS["disk"] = fake_disk
OW.COLLECTORS["production"] = fake_prod
OW.mint_name = lambda tag, known, prefix: prefix + "_CD34"
r0 = OW.run(now=NOW - DAY, rules=RULES, filer=None)
r1 = OW.run(now=NOW - 60, rules=RULES, filer=None)
r2 = OW.run(now=NOW, rules=RULES, filer=None)
k = r1["kpis"]
check("run: a raising collector -> its keys UNMEASURED with the error (never 0)",
      k["disk.root_free_gb"]["m"] == "UNMEASURED" and k["disk.root_free_gb"]["v"] is None
      and "mount gone" in (k["disk._collector"]["why"] or ""), k.get("disk.root_free_gb"))
recs = [json.loads(x) for x in OW.series_path("disk").read_text().splitlines()]
k = r2["kpis"]
check("run: every pass appends one disk record (3)", len(recs) == 3, len(recs))
prod = OW.series_path("production").read_text().splitlines()
check("run: production with an unchanged source record is not re-appended", len(prod) == 1, len(prod))
check("run: status.json carries the points for the allocator",
      json.loads((TMP / "ops" / "status.json").read_text())["points"]["disk.d_free_gb"]["v"] == 1000.0)
check("run: a key's first MEASURED sample counts in the digest's n7 (1, review night r1)",
      r0["kpis"]["production.P1"]["n7"] == 1, r0["kpis"]["production.P1"])
check("run: digest d24 for d_free_gb is 0 (1000 a day ago, 1000 now)", k["disk.d_free_gb"]["d24"] == 0.0, k["disk.d_free_gb"])
check("run: digest d24 is the real change (399 a day ago, 397 now)", k["disk.root_free_gb"]["d24"] == -2.0, k["disk.root_free_gb"])
check("run: the digest.md exists and leads with the headline",
      (TMP / "ops" / "digest.md").read_text().splitlines()[2].startswith("runway"))
def fake_prod_new(now, rules, ctx):
    ctx["production_src_t"] = 1235.0
    return {"production.P1": M(6)}


OW.COLLECTORS["production"] = fake_prod_new
OW.run(now=NOW + 1, rules=RULES, filer=None)
check("run: a changed production source record IS appended", len(OW.series_path("production").read_text().splitlines()) == 2)
OW.COLLECTORS.clear()
OW.COLLECTORS.update(saved)

# ---------------------------------------------------------------- flags keep their first-open time
fl1 = json.loads((TMP / "ops" / "flags.json").read_text())["flags"]
check("flags: flags.json written", isinstance(fl1, list))

# ---------------------------------------------------------------- CLI: install plans only
env = dict(os.environ, HOME=str(TMP / "home"))
r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "install"], capture_output=True, text=True, env=env, timeout=60)
check("cli: install without --apply prints a plan and writes nothing",
      r.returncode == 0 and "plan only" in r.stdout and not (TMP / "home").exists(), r.stdout + r.stderr)

# ---------------------------------------------------------------- GPT review fixes (2026-10-27)
check("runway: an unknown burn rate is None, not 'no burn'", OW.runway(50, None, 100) is None)
check("runway: a spent quota is 0 whatever the rate, even with no rate yet", OW.runway(0, 0, 100) == 0.0
      and OW.runway(-1, 2.0, 50) == 0.0 and OW.runway(0, None, 166) == 0.0)
check("epoch: NaN / bool are not times", OW.epoch(float("nan")) is None and OW.epoch(True) is None)
calls.clear()
(TMP / "ops" / "alarms.json").unlink()


def filer_raises(todo, conf):
    raise OSError("ingest.lock: permission denied")


st = OW.run_alarms({"disk.c_free_gb": M(5.0)}, RULES, NOW, set(), filer_raises)
a = st.get("DISK_LOW:disk.c_free_gb") or {}
check("alarm: a filer that raises leaves the alarm PENDING with the error (the pass goes on)",
      a.get("state") == "PENDING" and "filer raised OSError" in (a.get("error") or ""), a)
sp = OW.series_path("zz")
sp.parent.mkdir(parents=True, exist_ok=True)
sp.write_text('[]\n{"t": "bad"}\n{"t": 5, "points": null}\n{"t": %d, "points": {"zz.a": null, "zz.b": {"v": 1, "m": "MEASURED"}}}\n{"t": 1' % NOW)
recs = OW.read_series("zz", 0)
check("read_series: torn and foreign lines are skipped, not fatal", len(recs) == 1, recs)
check("history: a null point is skipped", OW.history(recs) == {"zz.b": [(NOW, 1.0)]}, OW.history(recs))
fl = OW.andon({}, {}, {"disk.d_free_gb": NOW - 5 * H}, rules(targets=[]), NOW)
check("silent: a key its collector stopped reporting still goes silent",
      any(f["rule"] == "silent" and f["key"] == "disk.d_free_gb" for f in fl), fl)
# a key UNMEASURED longer than series_days keeps its silent flag (last_measured.json outlives the series)
_pts = {"steve.state": {"m": "UNMEASURED", "why": "x"}, "disk.d_free_gb": {"v": 5.0, "m": "MEASURED"}}
_lm, _sv = OW.carry_last_measured({}, {"steve.state": NOW - 40 * 24 * H, "old.key": NOW - 400 * 24 * H}, _pts, NOW)
check("silent outlives series: the saved last MEASURED fills a key the loaded history lost",
      _lm.get("steve.state") == NOW - 40 * 24 * H, _lm)
check("silent outlives series: a measured key is stamped now; a key past the retire horizon is dropped",
      _sv.get("disk.d_free_gb") == NOW and "old.key" not in _sv and "steve.state" in _sv, _sv)
check("silent outlives series: a retired key not reported is not handed to the 'gone' rule",
      "old.key" not in _lm and "gone.key" not in OW.carry_last_measured({}, {"gone.key": NOW - H}, {}, NOW)[0])
fl = OW.andon(_pts, {}, _lm, rules(targets=[]), NOW)
check("silent outlives series: the flag fires for a key blind past the series window",
      any(f["rule"] == "silent" and f["key"] == "steve.state" for f in fl), fl)
os.environ["RM_OPS_DISKS"] = "d=/mnt/zz_ops_watch_not_mounted"
s = OW.c_disk(NOW, RULES, {})
check("disk: a /mnt drive that is not a mount point is UNMEASURED (df would read the parent volume)",
      s["disk.d_free_gb"]["m"] == "UNMEASURED", s["disk.d_free_gb"])
os.environ["RM_OPS_DISKS"] = "root=%s" % TMP
Path(os.environ["RM_SCRATCH_REAP_RUNS"]).write_text(json.dumps({"ts": OW.iso(NOW - H), "rows": []}) + "\n")
s = OW.c_disk(NOW, RULES, {})
check("disk: a reaper run with no rows is UNMEASURED, not 0 GB", s["disk.scratch_total_gb"]["m"] == "UNMEASURED", s)
Path(os.environ["RM_SCRATCH_REAP_RUNS"]).write_text(json.dumps({"ts": OW.iso(NOW - H), "rows": [
    {"verdict": "YOUNG", "bytes": 2e9}, {"verdict": "REFUSE"}]}) + "\n")
s = OW.c_disk(NOW, RULES, {})
check("disk: a row with no byte count makes scratch an ESTIMATE", s["disk.scratch_total_gb"]["m"] == "ESTIMATE"
      and s["disk.scratch_total_gb"]["v"] == 2.0, s["disk.scratch_total_gb"])
Path(os.environ["RM_SCRATCH_REAP_RUNS"]).write_text(json.dumps({"ts": OW.iso(NOW - H), "rows": [
    {"verdict": "YOUNG", "bytes": 2e9}, {"verdict": [], "bytes": 1e9}]}) + "\n")
s = OW.c_disk(NOW, RULES, {})
check("disk: an unhashable verdict costs its row, not the scratch total", s["disk.scratch_total_gb"]["m"] == "ESTIMATE"
      and s["disk.scratch_total_gb"]["v"] == 2.0, s["disk.scratch_total_gb"])
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": True, "incident": None, "since": "garbage"})
s = OW.c_steve(NOW, RULES, {})
check("steve: a fault with no readable since is UNMEASURED duration, not 0 min",
      s["steve.fault_min"]["m"] == "UNMEASURED" and s["steve.unowned_stall_min"]["m"] == "UNMEASURED", s)
wj(Q / "steward.json", {"epoch": NOW - 90 * 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
s = OW.c_steve(NOW, RULES, {})
check("steve: a 90 min old steward state is an ESTIMATE, not MEASURED now", s["steve.state"]["m"] == "ESTIMATE", s["steve.state"])
SD = TMP / "streams2"
SD.mkdir()
(SD / "series.jsonl").write_text(json.dumps({"t": NOW - 60, "measures": {
    "P1": {"m": "ERROR", "v": 0}, "P2": {"m": "ESTIMATE", "v": 3}, "P3": {"m": "MEASURED", "v": 7}}}) + "\n")
old_sd = os.environ.get("RM_STREAMS_DIR")
os.environ["RM_STREAMS_DIR"] = str(SD)
s = OW.c_production(NOW, RULES, {})
check("production: a mark outside the three is UNMEASURED with no value",
      s["production.P1"]["m"] == "UNMEASURED" and s["production.P1"]["v"] is None and s["production.P2"]["m"] == "ESTIMATE"
      and s["production.P3"]["m"] == "MEASURED", s)
if old_sd is None:
    os.environ.pop("RM_STREAMS_DIR")
else:
    os.environ["RM_STREAMS_DIR"] = old_sd

# ---------------------------------------------------------------- testing: provisional "caught nothing" (review round 3)
TD = TMP / "testing_metrics3"
TD.mkdir()
old_td = os.environ.get("RM_TESTING_METRICS_DIR")
os.environ["RM_TESTING_METRICS_DIR"] = str(TD)
young = [(NOW - H, {"result": {"outcome": "DONE", "started": OW.iso(NOW - 3 * H)}, "job": {"item": "IT_Y"}})]
grown = [(NOW - 30 * H, {"result": {"outcome": "DONE", "started": OW.iso(NOW - 32 * H)}, "job": {"item": "IT_G"}})]
mute = [(NOW - 30 * H, {"result": {"started": OW.iso(NOW - 32 * H)}, "job": {"item": "IT_M"}})]
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown + mute, "closes": {}})
check("testing: a done record with no outcome is not counted as caught-nothing (ESTIMATE, 2 h not 4)",
      t["testing.steve_nothing_h_7d"]["m"] == "ESTIMATE" and t["testing.steve_nothing_h_7d"]["v"] == 2.0, t)
t = OW.c_testing(NOW, RULES, {"steve_jobs": young, "closes": {}})
check("testing: a job still inside its close window makes the Steve total an ESTIMATE",
      t["testing.steve_nothing_h_7d"]["m"] == "ESTIMATE" and t["testing.steve_nothing_h_7d"]["x"].get("young") == 1, t)
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown, "closes": {}})
check("testing: a job past its close window counts MEASURED", t["testing.steve_nothing_h_7d"]["m"] == "MEASURED"
      and t["testing.steve_nothing_h_7d"]["v"] == 2.0, t)
U_ = {"m": "UNMEASURED", "v": None}
rows = []
for i in range(7):
    a_ = {"busy_pct": 50, "window_h": 10, "findings": 0, "closed_after_pass": 0, "regressions": 0, "fail_split": {"mod": 0}}
    if i == 3:
        a_.update(closed_after_pass=U_, regressions=U_)        # findings 0 known, the close counter unseen
    rows.append({"day": time.strftime("%Y-%m-%d", time.localtime(NOW - i * DAY)), "machines": {"archmagi": a_}})
(TD / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown, "closes": {}})
check("testing: a caught-nothing day with an unseen counter makes the week an ESTIMATE, not MEASURED",
      t["testing.archmagi_nothing_h_7d"]["m"] == "ESTIMATE" and t["testing.archmagi_nothing_h_7d"]["x"].get("soft_days") == 1, t)
rows[3]["machines"]["archmagi"].update(closed_after_pass=0, regressions=0, busy_pct={"m": "ESTIMATE", "v": 50})
(TD / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown, "closes": {}})
check("testing: an ESTIMATE-marked day value keeps the week an ESTIMATE",
      t["testing.archmagi_nothing_h_7d"]["m"] == "ESTIMATE" and t["testing.nothing_h_7d"]["m"] == "ESTIMATE", t)
rows[3]["machines"]["archmagi"]["busy_pct"] = 50
(TD / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown, "closes": {}})
check("testing: (control) seven fully measured days are MEASURED 35 h", t["testing.archmagi_nothing_h_7d"]["m"] == "MEASURED"
      and t["testing.archmagi_nothing_h_7d"]["v"] == 35.0 and t["testing.nothing_h_7d"]["m"] == "MEASURED", t)
rows[3]["machines"]["archmagi"]["busy_pct"] = float("nan")
(TD / "history.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
t = OW.c_testing(NOW, RULES, {"steve_jobs": grown, "closes": {}})
_v = t["testing.archmagi_nothing_h_7d"].get("v")
check("testing: a NaN busy_pct is one blind day, never a NaN week", _v is None or _v == _v, t)
check("testing: the NaN day is not counted as 35 h of the week", _v != 35.0, t)
rows[3]["machines"]["archmagi"]["busy_pct"] = 50
if old_td is None:
    os.environ.pop("RM_TESTING_METRICS_DIR")
else:
    os.environ["RM_TESTING_METRICS_DIR"] = old_td
sp = OW.soft_point({"m": "ERROR", "v": 0, "why": "x"})
check("backfill/production share one normaliser: ERROR -> UNMEASURED, no value", sp["m"] == "UNMEASURED" and sp["v"] is None, sp)

# ---------------------------------------------------------------- review round 4
wj(Q / "steward.json", {"epoch": NOW - 60 * 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
wj(Q / "steward_watch.json", {"epoch": NOW - 60, "incident": None})
s = OW.c_steve(NOW, RULES, {})
check("steve: a stale steward cannot report MEASURED 0 fault or 0 stall (it would clear a real alarm)",
      s["steve.fault_min"]["m"] == "UNMEASURED" and s["steve.unowned_stall_min"]["m"] == "UNMEASURED", s)
wj(Q / "steward.json", {"epoch": "NaN", "state": "RUNNING", "fault": False})
s = OW.c_steve(NOW, RULES, {})
check("steve: a NaN steward epoch is unreadable -> UNMEASURED", s["steve.state"]["m"] == "UNMEASURED", s["steve.state"])
DD = Q / "done"
DD.mkdir(parents=True, exist_ok=True)
for i in range(3):
    wj(DD / ("inv%d.json" % i), {"finished": OW.iso(NOW - (10 - i) * 60), "job": {"id": "j%d" % i},
                                 "result": {"outcome": "INVALID", "started": OW.iso(NOW - 20 * 60)}})
(DD / "zz_torn.json").write_text('{"finished": "2026-')
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
s = OW.c_steve(NOW, RULES, {})
check("steve: a torn done record makes the INVALID streak an ESTIMATE (no alarm on a readable subset)",
      s["steve.invalid_streak"]["m"] == "ESTIMATE" and s["steve.invalid_streak"]["v"] >= 3, s["steve.invalid_streak"])
check("steve: with a torn done record the last-done age is an ESTIMATE too",
      s["steve.last_done_age_min"]["m"] == "ESTIMATE", s["steve.last_done_age_min"])
for f in DD.iterdir():
    f.unlink()
calls.clear()
(TMP / "ops" / "alarms.json").unlink(missing_ok=True)
OW.mint_name = lambda tag, known, prefix: "OPS_SAME_" + ("AB12" if "OPS_SAME_AB12" not in known else "CD34")
st = OW.run_alarms({"disk.c_free_gb": M(10.0), "disk.d_free_gb": M(10.0)}, RULES, NOW, set(), filer_ok)
nm = sorted(a.get("name") for a in st.values())
check("alarm: two crossings in one pass never get the same name", len(set(nm)) == 2, nm)
n0 = len(calls)
(TMP / "ops" / "alarms.json").write_text('{"DISK_LOW:disk.c_free_gb": {"state": "OP')
st = OW.run_alarms({"disk.c_free_gb": M(10.0), "disk.d_free_gb": M(10.0)}, RULES, NOW + 900, set(), filer_ok)
check("alarm: an unreadable alarms.json holds all filing (no duplicate items) and is left for a human",
      len(calls) == n0 and st.get("_alarm_state", {}).get("state") == "UNREADABLE"
      and (TMP / "ops" / "alarms.json").read_text().endswith('"OP'), st)
(TMP / "ops" / "alarms.json").unlink()
OW.append("disk", {"schema": OW.SCHEMA, "t": NOW + 10, "family": "disk", "points": {"disk.weird": 7}})
saved = dict(OW.COLLECTORS)


def dies(now, rules, ctx):
    raise OSError("gone again")


OW.COLLECTORS["disk"] = dies
try:
    r = OW.run(now=NOW + 20, rules=RULES, filer=None, families=["disk"])
    ok = r["kpis"].get("disk.weird", {}).get("m") == "UNMEASURED"
except Exception as e:  # noqa: BLE001
    ok, r = False, repr(e)
check("run: a non-dict point in the last record does not abort the collector-error fallback", ok, r)
OW.COLLECTORS.clear()
OW.COLLECTORS.update(saved)
SD3 = TMP / "streams3"
SD3.mkdir()
(SD3 / "series.jsonl").write_text(json.dumps({"t": "NaN", "measures": {"P1": {"m": "MEASURED", "v": 1}}}) + "\n")
old_sd = os.environ.get("RM_STREAMS_DIR")
os.environ["RM_STREAMS_DIR"] = str(SD3)
s = OW.c_production(NOW, RULES, {})
check("production: a NaN record time is unreadable -> UNMEASURED, not fresh", list(s) == ["production._collector"], s)
if old_sd is None:
    os.environ.pop("RM_STREAMS_DIR")
else:
    os.environ["RM_STREAMS_DIR"] = old_sd

OW.append("disk", {"schema": OW.SCHEMA, "t": 1e999, "family": "disk", "points": {"disk.inf": M(1.0)}})
check("series: a record with an infinite time is skipped (it would mute the silent flag forever)",
      not any("disk.inf" in r["points"] for r in OW.read_series("disk", 0)))

for f in DD.iterdir():
    f.unlink()
for i, age in enumerate((8 * DAY, 2 * H, H)):
    wj(DD / ("old%d.json" % i), {"finished": OW.iso(NOW - age), "job": {"id": "o%d" % i},
                                 "result": {"outcome": "INVALID", "started": OW.iso(NOW - age - 600)}})
    os.utime(DD / ("old%d.json" % i), (NOW - age, NOW - age))
s = OW.c_steve(NOW, RULES, {})
check("steve: an INVALID run that started before the 7 d window is counted whole (3, not 2)",
      s["steve.invalid_streak"]["v"] == 3 and s["steve.jobs_24h"]["v"] == 2, s["steve.invalid_streak"])
wj(DD / "old0.json", {"finished": OW.iso(NOW - 8 * DAY), "job": {"id": "o0"}, "result": {"started": OW.iso(NOW - 8 * DAY - 600)}})
os.utime(DD / "old0.json", (NOW - 8 * DAY, NOW - 8 * DAY))
s = OW.c_steve(NOW, RULES, {})
check("steve: a streak stopped by a record with no outcome is an ESTIMATE", s["steve.invalid_streak"]["m"] == "ESTIMATE"
      and s["steve.invalid_streak"]["v"] == 2, s["steve.invalid_streak"])
for f in DD.iterdir():
    f.unlink()

# ---------------------------------------------------------------- token-talk drift
TT = TMP / "tt"
os.environ["GIT_CEILING_DIRECTORIES"] = str(TT)     # "notarepo" stays no repo wherever TMPDIR sits
RR = TT / "roles"
GIT = TT / "repo"
GIT.mkdir(parents=True)
os.environ["RM_ROLE_RUNS_DIR"] = str(RR)
old_bench = os.environ.get("RM_STREAMS_BENCH")
os.environ["RM_STREAMS_BENCH"] = str(TT / "notarepo")
(TT / "notarepo").mkdir()


def ev(seat, i, text, kind="note", ago=H):
    return {"seat": seat, "event": kind, "id": i, "text": text, "ts": OW.iso(NOW - ago)}


evs = [ev("BENCH", "X_A", "fixed the thing %d" % n) for n in range(8)] + [ev("BENCH", "X_A", "we are over budget, save tokens")] * 2 \
    + [ev("BENCH", "OPS_X", "the token burn is high")] * 20 + [ev("FOUNDRY", "Y", "plain note %d" % n) for n in range(3)] \
    + [ev("BENCH", "X_A", "old token talk", ago=9 * DAY)] * 50
R = rules()
check("tokentalk: the live rules measure neither seat BENCH nor the conductor role (owner 2026-10-31: the Conductor has no closed sources)",
      "BENCH" not in R["token_talk"]["seats"] and "conductor" not in R["token_talk"]["roles"], R["token_talk"]["seats"])
# the mechanism below is exercised on a fixture word-list config, seats and roles as named here, not the live ones
R = dict(R, token_talk=dict(R["token_talk"], seats=["BENCH", "FOUNDRY"],
                            roles=["conductor", "producer", "arbiter", "auditor", "innovator"]))
rx = OW.tt_regex(R)
check("tokentalk: the word list matches whole words only (a bare cap and 'tokenizer' do not)",
      rx.search("save tokens") and rx.search("Budget!") and not rx.search("the log cap") and not rx.search("tokenizer")
      and rx.search("the daily cap"))
out = OW.c_tokentalk(NOW, R, {"events": evs})
b = out["tokentalk.BENCH.share"]
check("tokentalk: BENCH share counts 2 of 10 reports, Operations' OPS_ items and the 9-day-old ones left out",
      b["m"] == "MEASURED" and b["v"] == 20.0 and b["x"]["reports"] == 10, b)
check("tokentalk: a seat with 3 reports (under min_reports) is UNMEASURED, never 0",
      out["tokentalk.FOUNDRY.share"]["m"] == "UNMEASURED" and out["tokentalk.FOUNDRY.share"]["v"] is None)
check("tokentalk: a repo that cannot be read makes the commit series UNMEASURED, not 0",
      out["tokentalk.commits.BENCH.share"]["m"] == "UNMEASURED" and "git log" in out["tokentalk.commits.BENCH.share"]["why"],
      out["tokentalk.commits.BENCH.share"])
check("tokentalk: no role run folder makes every role series UNMEASURED",
      all(out["tokentalk.role.%s.share" % r]["m"] == "UNMEASURED" for r in ("conductor", "producer", "arbiter", "auditor", "innovator")))
out = OW.c_tokentalk(NOW, R, {"events": []})
check("tokentalk: an empty ledger read is UNMEASURED (an unreadable source), not a clean 0",
      out["tokentalk.BENCH.share"]["m"] == "UNMEASURED" and "ledger" in out["tokentalk.BENCH.share"]["why"])
for n in range(6):
    wj(RR / ("rm-role-conductor-%d.json" % (NOW - n * 100)), {"result": "ok done" if n else "I will trim work to save tokens"})
wj(RR / ("rm-role-operations-%d.json" % (NOW - 5)), {"result": "token burn token burn"})
wj(RR / ("rm-role-producer-%d.json" % (NOW - 5)), {"type": "result"})
out = OW.c_tokentalk(NOW, R, {"events": evs})
c = out["tokentalk.role.conductor.share"]
check("tokentalk: conductor run results are read, 1 of 6 has token talk", c["m"] == "MEASURED" and abs(c["v"] - 16.7) < 0.05, c)
check("tokentalk: a run with no result text is UNMEASURED with its reason, Operations' runs are not a series",
      out["tokentalk.role.producer.share"]["m"] == "UNMEASURED" and "tokentalk.role.operations.share" not in out)
(RR / ("rm-role-auditor-%d.json" % (NOW - 60))).write_text("")                # in flight: skipped, no failure
dead = RR / ("rm-role-arbiter-%d.json" % (NOW - 3 * DAY))
dead.write_text("")                                                              # killed run: only the arbiter is bad
os.utime(dead, (NOW - 3 * DAY, NOW - 3 * DAY))
os.utime(RR / ("rm-role-auditor-%d.json" % (NOW - 60)), (NOW - 60, NOW - 60))
texts, bad = OW.tt_texts(NOW, R, {"events": evs})
check("tokentalk: an empty killed-run file marks only its own role bad, an in-flight one is skipped, the rest stay read",
      list(k for k in bad if k.startswith("role.")) == ["role.arbiter", "role.producer"] and "role._all" not in bad
      and len(texts.get("role.conductor", [])) == 6, (bad, list(texts)))
_GITENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}     # -C does not beat an inherited GIT_DIR
_GITENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")           # nor may a user hooksPath run on these commits
subprocess.run(["git", "-C", str(GIT), "init", "-q"], check=True, env=_GITENV)
for name, msg in (("src/RimMandrake/Mod/a.xml", "tokens spent here"), ("src/RimMandrake/Utils/b.py", "plain"),
                  ("src/RimMandrake/Utils/c.py", "ledger: skip me tokens")):
    f = GIT / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(msg)
    subprocess.run(["git", "-C", str(GIT), "add", "-A"], check=True, env=_GITENV)
    subprocess.run(["git", "-C", str(GIT), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg], env=_GITENV, check=True)
texts, bad = OW.tt_texts(time.time(), R, {"events": evs})
check("tokentalk: commits are split by path owner and ledger: commits skipped (no repo yet -> bad)", "commits.BENCH" in bad)
os.environ["RM_STREAMS_BENCH"] = str(GIT)
texts, bad = OW.tt_texts(time.time(), R, {"events": evs})
check("tokentalk: Utils commit is BENCH's, mod commit FOUNDRY's, 'ledger:' commit left out",
      texts.get("commits.BENCH") == ["plain"] and texts.get("commits.FOUNDRY") == ["tokens spent here"], texts)
if old_bench is None:
    del os.environ["RM_STREAMS_BENCH"]
else:
    os.environ["RM_STREAMS_BENCH"] = old_bench
check("tokentalk: the family is registered and its series is in the run and silent rules",
      "tokentalk" in OW.COLLECTORS and "tokentalk" in OW.ORDER and OW.matches("tokentalk.role.conductor.share", R["run"]["keys"])
      and OW.matches("tokentalk.BENCH.share", list(R["silent"]["per_key"])))

# ---------------------------------------------------------------- digest_blind.md: an ALLOW-LIST (review U N2/F6, V V1)
RX = OW.tt_regex(RULES)
# realistic: every account, codex and tokentalk series the live digest carries, production.B (the week used, phrased
# with no token word: review V's leak), a flag and an alarm on each, plus a brand-new family nobody named
SECRET = {"accounts.lukas.runway": 0.8213, "accounts.lukas.week_left_pct": 41.37, "accounts.lukas.hours_to_reset": 77.71,
          "accounts.system.runway": 0.8117, "accounts.system.week_left_pct": 23.93,
          "accounts.system.hours_to_reset": 51.29, "codex.runway": 0.6431, "codex.week_used_pct": 61.83,
          "codex.hours_to_reset": 33.07, "tokentalk.role.producer.share": 12.77, "tokentalk.BENCH.share": 4.391,
          "production.B": 93.17, "newfam.thing": 5.551}
pts = {k: M(v) for k, v in SECRET.items()}
pts["production.B"] = dict(M(93.17), unit="% of the week used (highest account)")
pts.update({"steve.state": M("ok"), "steve.invalid_streak": M(0), "disk.root_free_gb": M(300.0),
            "disk.c_free_gb": M(120.0), "production.A1": M(14.0), "production.G7": dict(M(9.0), unit="per merged commit"),
            "tps.stalls": M(2.0), "flow.untriaged_findings": OW.U("collector error: the burn table was unreadable")})
fl = [{"rule": "target", "tag": "RUNWAY_LOW", "key": "accounts.lukas.runway", "window": "now", "detail": "0.8213 < 1"},
      {"rule": "z", "tag": "WEEK_HOT", "key": "production.B", "window": "7d", "detail": "93.17 rising"},
      {"rule": "z", "tag": "NEW", "key": "newfam.thing", "window": "now", "detail": "5.551"},
      {"rule": "target", "tag": "DISK_TWO_DAYS", "key": "disk.root_free_gb", "window": "now", "detail": "300 < 420"}]
al = {"RUNWAY_LOW:accounts.lukas.runway": {"state": "OPEN", "since": "x", "for": "Operations", "item": None},
      "RUNWAY_LOW:codex.runway": {"state": "OPEN", "since": "x", "legacy_item": "OPS_RUNWAY_RESCUE_E2BB"},
      "DISK_LOW:disk.root_free_gb": {"state": "OPEN", "since": "x", "item": "OPS_DISK_DRAIN"}}
dg = OW.build_digest(pts, {}, fl, al, NOW, 1.0)
blind = OW.blind_digest_md(dg, RULES)
full = OW.digest_md(dg)
hits = [ln for ln in blind.splitlines() if RX.search(ln)]
check("blind digest: no line holds a token_talk term (ops_watch_rules.json word list)", not hits, hits)
leak = [k for k in SECRET if k in blind or k.split(".", 1)[1] in blind.split()] + \
       [x for v in SECRET.values() for x in {str(v), OW.fmt(v)} if x in blind]
check("blind digest (allow-list): no account, codex, tokentalk, production.B or unnamed key, nor any of their values",
      not leak and "week" not in blind and "OPS_RUNWAY" not in blind and "RUNWAY" not in blind
      and "Operations" not in blind.split("\n", 1)[1], (leak, blind))
check("blind digest: production.B's row is gone, production A1 and G7 stay",
      not any(ln.startswith("B |") for ln in blind.splitlines()) and any(ln.startswith("A1 |") for ln in blind.splitlines())
      and any(ln.startswith("G7 |") for ln in blind.splitlines()), blind)
check("blind digest: the full digest DOES carry them (the instrument can see)",
      all(OW.fmt(v) in full for v in (0.8213, 93.17, 0.6431)) and "% of the week used" in full, full[:300])
check("blind digest: health stays (steve, disk, stalls, disk alarm, disk flag), counts over allowed keys only",
      "steve ok" in blind and "DISK_LOW:disk.root_free_gb" in blind and "DISK_TWO_DAYS" in blind
      and "stalls" in blind and "1 flag(s), 1 alarm(s) open" in blind, blind)
check("blind digest: every allowed key is a real family of ours (no wildcard crept in)",
      all("." in k and "*" not in k and k.split(".")[0] in ("companion", "disk", "flow", "process", "production", "steve",
                                                              "testing", "timers", "tps", "v3") for k in OW.BLIND_KEYS)
      and "production.B" not in OW.BLIND_KEYS and not any(OW.is_token_key(k) for k in OW.BLIND_KEYS))
check("blind digest: run() writes digest_blind.md", (TMP / "ops" / "digest_blind.md").exists())
# ---------------------------------------------------------------- V2: account/runway alarms are Operations', never items
filed = []
def filer_rec(todo, conf):
    filed.extend(todo)
    return {a["name"]: None for a in todo}      # None is what run_alarms reads as filed
ap = OW.ops_dir() / "alarms.json"
ap.unlink(missing_ok=True)
st = OW.run_alarms({"accounts.lukas.runway": M(0.5), "codex.runway": M(0.25), "disk.c_free_gb": M(5.0)},
                   RULES, NOW, set(), filer_rec)
ta = {k: a for k, a in st.items() if k.startswith("RUNWAY")}
check("V2: an account/runway crossing files NO ledger item (the blind roles read `rimflow queue`)",
      set(ta) == {"RUNWAY_LOW:accounts.lukas.runway", "RUNWAY_LOW:codex.runway"}
      and not [t for t in filed if OW.is_token_key(t["aid"].split(":", 1)[1])], filed)
check("V2: it is kept OPEN for Operations with a number-free title naming no account",
      all(a.get("state") == "OPEN" and a.get("for") == "Operations" and not a.get("item")
          and not re.search(r"\d", a.get("title") or "1") and "lukas" not in a["title"] for a in ta.values()), ta)
check("V2: a non-account alarm (disk) still files for BENCH", any(t["aid"].startswith("DISK") for t in filed)
      and any(k.startswith("DISK") and a.get("state") == "OPEN" and a.get("item") for k, a in st.items()), st)
ap.write_text(json.dumps({"RUNWAY_LOW:accounts.system.runway": {
    "state": "OPEN", "since": "x", "item": "OPS_RUNWAY_RESCUE_C01D", "name": "OPS_RUNWAY_RESCUE_C01D",
    "title": "Ops alarm RUNWAY_LOW: accounts.system.runway = 0.81"}}))
filed.clear()
st = OW.run_alarms({"accounts.system.runway": M(0.5)}, RULES, NOW + 900, set(), filer_rec)
mv = st.get("RUNWAY_LOW:accounts.system.runway") or {}
check("V2: an alarm filed as an item before the fix moves to Operations (legacy_item kept, never noted again)",
      mv.get("for") == "Operations" and mv.get("legacy_item") == "OPS_RUNWAY_RESCUE_C01D" and not mv.get("item")
      and "0.81" not in mv.get("title", "") and not filed, (mv, filed))
for _i in range(RULES["alarm"]["clear_passes"]):
    st = OW.run_alarms({"accounts.system.runway": M(5.0)}, RULES, NOW + 1800 + _i, set(), filer_rec)
check("V2: when it clears, no clear note lands on the legacy item",
      not filed and "RUNWAY_LOW:accounts.system.runway" not in st, (filed, st))
ap.unlink(missing_ok=True)
# opt-in: the suite proper is fixtures only, so its assertions do not depend on the live directory
live = Path(os.environ.get("RM_OPS_WATCH_LIVE") or TMP / "no_live") / "digest.json"
if live.exists():
    ld = json.loads(live.read_text())
    lb = OW.blind_digest_md(ld, RULES)
    fams = {k.split(".", 1)[0] for k in OW.BLIND_KEYS}
    bad = sorted({"## " + k.split(".", 1)[0] for k in ld.get("kpis") or {} if k.split(".", 1)[0] not in fams}
                 & set(lb.splitlines()))
    check("blind digest over the live digest.json: no token term, no withheld key, no week reading (%d lines)"
          % len(lb.splitlines()),
          not [ln for ln in lb.splitlines() if RX.search(ln)] and "week" not in lb and not bad
          and not any(ln.startswith("B |") for ln in lb.splitlines()) and len(lb.splitlines()) > 5, lb[:400])

# ---------------------------------------------------------------- OPSWATCH_SILENCE_FRESH_WEEK_RUNWAY
# a week under 6 h old has no slope yet; it used to read UNMEASURED and the live dispatcher alarmed account:unmeasured
# every tick. Its runway is now an ESTIMATE from the week's burn with its age floored at FRESH_WEEK_H.
import types  # noqa: E402
_saved = {m: sys.modules.get(m) for m in ("account_usage", "slot_allocator")}


def _fake_accounts(accts):
    sys.modules["account_usage"] = types.SimpleNamespace(read_now=lambda now: {"accounts": accts})
    sys.modules["slot_allocator"] = types.SimpleNamespace(slope=lambda *a: (None, 0, 0.0))


def _acct(used, h, src="MEASURED"):
    return {"source": src, "stale": False, "week_pct_left": 100.0 - used, "week_pct_used": used,
            "hours_to_week_reset": h, "week_resets_at": "2026-11-04T13:00:00-08:00", "measured_at": "x"}


try:
    _fake_accounts({"fresh": _acct(1.0, 167.0), "zero": _acct(0.0, 167.5), "hot": _acct(30.0, 165.0),
                    "old": _acct(50.0, 68.0), "unk": {"source": "UNMEASURED", "why": "nothing"}})
    out = OW.c_accounts(NOW, RULES, {})
    _ok_slope = sys.modules["slot_allocator"].slope
    sys.modules["slot_allocator"].slope = lambda a, r, n, rules: (rules["fit"]["window_h"], 0, 0.0)  # reads the rule as the real one does
    _nf = OW.c_accounts(NOW, {k: v for k, v in RULES.items() if k != "accounts_fit"}, {})
    sys.modules["slot_allocator"].slope = _ok_slope
    check("accounts: no accounts_fit costs the slope, said aloud; readings and runway stay",
          _nf["accounts.old.week_left_pct"]["m"] == "MEASURED" and _nf["accounts.old.runway"]["v"] is not None
          and "accounts_fit" in _nf.get("accounts._collector", {}).get("why", ""), _nf.get("accounts._collector"))
    fr = out["accounts.fresh.runway"]
    check("fresh week: runway is an ESTIMATE, not UNMEASURED", fr["m"] == "ESTIMATE" and fr["v"] is not None, fr)
    check("fresh week: 1%% used in its first hour reads ample (>= 1), so no alarm", (fr["v"] or 0) >= 1.0, fr)
    check("fresh week: the why says the week is fresh", "fresh" in fr.get("why", ""), fr)
    check("fresh week: nothing used reads the cap (not being spent)", out["accounts.zero.runway"]["v"] == 10.0,
          out["accounts.zero.runway"])
    hot = out["accounts.hot.runway"]
    check("fresh week: a heavy burn (30%% in 3 h) still reads under 1 (it still flags)",
          hot["m"] == "ESTIMATE" and hot["v"] is not None and hot["v"] < 1.0, hot)
    old = out["accounts.old.runway"]
    check("older week: the plain week average is unchanged (50%% over 100 h, 68 h left -> 1.47)",
          old["m"] == "ESTIMATE" and old["v"] == 1.47 and "fresh" not in old.get("why", ""), old)
    check("an UNMEASURED reading still reads UNMEASURED", out["accounts.unk.runway"]["m"] == "UNMEASURED")
    r, how = OW.week_avg_rate(3.0, 167.0)
    check("week_avg_rate: under the floor the age counts as FRESH_WEEK_H", r == 3.0 / OW.FRESH_WEEK_H and "fresh" in how,
          (r, how))
    check("week_avg_rate: no figure -> None", OW.week_avg_rate(None, 100.0) == (None, None))
finally:
    for m, v in _saved.items():
        if v is None:
            sys.modules.pop(m, None)
        else:
            sys.modules[m] = v

# ---------------------------------------------------------------- unclaimed steward incident (owner 2026-10-28)
import types as _ty
_M = _ty.SimpleNamespace(epoch=lambda ts: ts, lease_status=lambda it, now: it.lease)
def _it(iid, state, age_min, lease=None, blocked=False):
    return _ty.SimpleNamespace(id=iid, state=state, open=state != "done", blocked=blocked, lease=lease,
                               created_at=NOW - age_min * 60)
def _w(*its):
    return _ty.SimpleNamespace(items={i.id: i for i in its})
_P = "STEVE_LANE_UNSTICK_"
r = OW.steve_incident_unclaimed(_w(_it(_P + "PAUSED_UNOWNED_C45B", "proposed", 21)), _M, NOW, RULES)
check("incident: today's 21 min unclaimed case -> 21 MEASURED", r["m"] == "MEASURED" and abs(r["v"] - 21) < 0.1, r)
_tg = [t for t in RULES["targets"] if t["key"] == "steve.incident_unclaimed_min"][0]
check("incident: 21 min is over the alarm line and the line is 10", _tg["alarm"] and _tg["value"] == 10 and r["v"] > _tg["value"], _tg)
r = OW.steve_incident_unclaimed(_w(_it(_P + "A", "doing", 40)), _M, NOW, RULES)
check("incident: a claimed (doing) incident -> 0", r["v"] == 0.0, r)
r = OW.steve_incident_unclaimed(_w(_it(_P + "A", "ready", 40, lease="live")), _M, NOW, RULES)
check("incident: a live lease -> 0", r["v"] == 0.0, r)
r = OW.steve_incident_unclaimed(_w(_it(_P + "A", "ready", 40, lease="lapsed")), _M, NOW, RULES)
check("incident: a lapsed lease is unclaimed again", abs(r["v"] - 40) < 0.1, r)
r = OW.steve_incident_unclaimed(_w(_it("OTHER_ITEM", "proposed", 90), _it(_P + "B", "done", 90), _it(_P + "C", "built", 90)), _M, NOW, RULES)
check("incident: other items and closed incidents do not count", r["v"] == 0.0, r)
r = OW.steve_incident_unclaimed(_w(_it(_P + "A", "proposed", 5), _it(_P + "B", "proposed", 30)), _M, NOW, RULES)
check("incident: the oldest of several counts", abs(r["v"] - 30) < 0.1, r)

# ---------------------------------------------------------------- arena alarm reader (ARENA_SWITCH_BUILD_ONE_ARM_LIVE_ONLY)
# The pre-push hook appends PUSH_REFUSED / PUSH_HOOK_CRASH lines to <arena>/alarms/arena.jsonl; ARENA_PUSH_REFUSED is
# their reader. arena.ops_two_live is stubbed: no systemctl of any kind runs here.
sys.path.insert(0, str(HERE / "arena"))
import arena as _AR  # noqa: E402
_ad = TMP / "arena_ow"; _ad.mkdir()
_env0 = {k: os.environ.get(k) for k in ("ARENA_ROOT", "ARENA_ARM_TOML", "ARENA_ALARM_FILE")}
_two0 = _AR.ops_two_live
os.environ.update(ARENA_ROOT=str(_ad), ARENA_ARM_TOML=str(_ad / "arm.toml"), ARENA_ALARM_FILE=str(_ad / "alarms" / "arena.jsonl"))
_AR.ops_two_live = lambda *a, **k: {"value": 0, "why": "stub", "mode": "ralph_a"}
try:
    _tg = [t for t in RULES["targets"] if t["key"] == "arena.push_refused_24h"]
    check("arena: ARENA_PUSH_REFUSED rule exists, alarms on > 0, MEASURED only",
          len(_tg) == 1 and _tg[0]["tag"] == "ARENA_PUSH_REFUSED" and _tg[0]["alarm"] and _tg[0]["op"] == ">"
          and _tg[0]["value"] == 0 and _tg[0]["marks"] == ["MEASURED"], _tg)
    _p = OW.c_arena(NOW, RULES, {})
    check("arena: no arm.toml -> push_refused UNMEASURED, rule holds", _p["arena.push_refused_24h"]["m"] == "UNMEASURED"
          and OW.target_state(_p, RULES).get("ARENA_PUSH_REFUSED:arena.push_refused_24h") is None, _p)
    (_ad / "arm.toml").write_text('mode = "ralph_a"\n')
    _p = OW.c_arena(NOW, RULES, {})
    check("arena: arm.toml but no alarm file -> MEASURED 0, not crossed", _p["arena.push_refused_24h"]["m"] == "MEASURED"
          and _p["arena.push_refused_24h"]["v"] == 0
          and OW.target_state(_p, RULES).get("ARENA_PUSH_REFUSED:arena.push_refused_24h") is False, _p)
    _af = _ad / "alarms" / "arena.jsonl"; _af.parent.mkdir()
    _iso = lambda e: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(e))
    _af.write_text(json.dumps({"ts": _iso(NOW - 3 * DAY), "kind": "PUSH_REFUSED"}) + "\n")
    _p = OW.c_arena(NOW, RULES, {})
    check("arena: a 3-day-old refusal is outside the 24 h window -> 0", _p["arena.push_refused_24h"]["v"] == 0, _p)
    with open(_af, "a") as _fh:
        _fh.write(json.dumps({"ts": _iso(NOW - 60), "kind": "PUSH_REFUSED", "arm": "ralph_c"}) + "\n")
    _p = OW.c_arena(NOW, RULES, {})
    check("FORCED arena: a refusal a minute ago -> 1 and ARENA_PUSH_REFUSED crosses", _p["arena.push_refused_24h"]["v"] == 1
          and OW.target_state(_p, RULES).get("ARENA_PUSH_REFUSED:arena.push_refused_24h") is True, _p)
    with open(_af, "a") as _fh:
        _fh.write("not json at all\n")
    check("FORCED arena: an unreadable alarm line counts (someone wrote it)", OW.c_arena(NOW, RULES, {})["arena.push_refused_24h"]["v"] == 2)
finally:
    _AR.ops_two_live = _two0
    for _k, _v in _env0.items():
        if _v is None:
            os.environ.pop(_k, None)
        else:
            os.environ[_k] = _v

import pulse_core as _pc  # noqa: E402
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ops_watch_rules.json"), encoding="utf-8") as _f:
    _real = json.load(_f)
_bad = [t["name"] for t in _real["targets"] if t.get("name") and _pc._model().mint_problems(t["name"] + "_A1B2", set())]
check("every shipped rule's name mints: a refused prefix kills the whole pass", not _bad, _bad)
# ---- one bad rule, row, entry or write costs only itself and is said aloud (Codex review 2026-10-31)
_bad_rules = dict(RULES)
_bad_rules["targets"] = [{"key": "x.*", "op": "~", "value": 1, "tag": "BADOP", "alarm": True},
                         {"key": "x.*", "op": ">", "value": 1, "tag": "A:B", "alarm": True}, "junk",
                         {"key": "x.k", "op": ">", "value": 1, "tag": "GOOD", "alarm": True, "name": "OPS_DISK_FULL_DIAGNOSE"}]
_pts = {"x.k": OW.M(5.0, "n")}
_fl = OW.andon(_pts, {}, {}, _bad_rules, NOW)
check("rules: three bad targets each raise a bad_target flag", sum(f["rule"] == "bad_target" for f in _fl) == 3, _fl)
check("rules: the good target still fires beside the bad ones", any(f.get("tag") == "GOOD" for f in _fl), _fl)
check("rules: only the good target reaches the alarm state", OW.target_state(_pts, _bad_rules) == {"GOOD:x.k": True},
      OW.target_state(_pts, _bad_rules))
_ap = OW.ops_dir() / "alarms.json"
_ap.write_text(json.dumps({"GOOD:x.k": "junk", "OLD:y.z": 5}), encoding="utf-8")
_filed = []
_st = OW.run_alarms(_pts, _bad_rules, NOW, set(), lambda todo, conf: _filed.extend(todo) or {a["name"]: None for a in todo})
check("alarms: a non-object state entry holds that alarm and files nothing",
      _st["GOOD:x.k"]["state"] == "UNREADABLE" and _st["OLD:y.z"]["state"] == "UNREADABLE" and not _filed, (_st, _filed))
_ap.write_text(json.dumps({"GOOD:x.k": {"state": "OPEN"}, "OTHER:y.z": {"state": "OPEN", "item": "X_Y_Z"}}), encoding="utf-8")
_tk = OW.is_token_key
OW.is_token_key = lambda k: 1 / 0 if k == "x.k" else False
try:
    _r2 = copy.deepcopy(_bad_rules)
    _r2["targets"].append(dict([t for t in _r2["targets"] if isinstance(t, dict) and t.get("tag") == "GOOD"][0], key="y.z", tag="OTHER"))
    _st = OW.run_alarms({"x.k": OW.M(0.0, "n"), "y.z": OW.M(0.0, "n")}, _r2, NOW, set(), None)
finally:
    OW.is_token_key = _tk
check("alarms: a step that raises costs its alarm only and records why", "alarm step raised" in str(_st["GOOD:x.k"].get("error"))
      and _st["OTHER:y.z"].get("clear_seen") == 1, _st)
_ap.unlink()

import account_usage as _AU
_rn = _AU.read_now
_AU.read_now = lambda now: {"accounts": {"nullrow": None}}
try:
    _a = OW.c_accounts(NOW, RULES, {})
finally:
    _AU.read_now = _rn
check("accounts: a malformed account is UNMEASURED, not a lost family", _a["accounts.nullrow.runway"]["m"] == "UNMEASURED", _a)

_ss = OW.streams_series
_sf = TMP / "streams_null.jsonl"
_sf.write_text(json.dumps({"t": NOW - 60, "measures": {"nullm": None}}) + "\n", encoding="utf-8")
OW.streams_series = lambda: _sf
try:
    _p = OW.c_production(NOW, RULES, {})
finally:
    OW.streams_series = _ss
check("production: a null measure says so instead of vanishing", _p["production.nullm"]["m"] == "UNMEASURED", _p)

_qh = OW.qhome
_q2 = TMP / "q_streak"
(_q2 / "done").mkdir(parents=True)
OW.qhome = lambda: _q2
try:
    for i in range(3):
        wj(_q2 / "done" / ("inv%d.json" % i), {"finished": OW.iso(NOW - (10 - i) * 60), "job": {"id": "j%d" % i},
                                               "result": {"outcome": "INVALID", "started": OW.iso(NOW - 20 * 60)}})
    wj(_q2 / "done" / "pass.json", {"finished": OW.iso(NOW - 3600), "job": {"id": "p"}, "result": {"outcome": "DONE"}})
    wj(_q2 / "done" / "noout.json", {"finished": OW.iso(NOW - 2 * 3600), "job": {"id": "n"}, "result": {}})
    (_q2 / "done" / "old_torn.json").write_text('{"finished": "2026-')
    os.utime(_q2 / "done" / "old_torn.json", (NOW - 3 * 3600, NOW - 3 * 3600))
    wj(_q2 / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": False, "incident": None, "since": None})
    _s = OW.c_steve(NOW, RULES, {})
    check("steve: bad records older than the run leave the streak MEASURED, so its alarm can fire",
          _s["steve.invalid_streak"]["m"] == "MEASURED" and _s["steve.invalid_streak"]["v"] == 3, _s["steve.invalid_streak"])
    check("steve: those bad records still mark the window counts", _s["steve.jobs_24h"]["m"] == "ESTIMATE", _s["steve.jobs_24h"])
    os.utime(_q2 / "done" / "old_torn.json", (NOW, NOW))
    _s = OW.c_steve(NOW, RULES, {})
    check("steve: a torn record inside the run keeps the streak an ESTIMATE", _s["steve.invalid_streak"]["m"] == "ESTIMATE",
          _s["steve.invalid_streak"])
finally:
    OW.qhome = _qh

_ap2 = OW.append
def _no_room(*a):
    raise OSError("no space left")
OW.append = _no_room
(OW.ops_dir() / "flags.json").write_text("[1]", encoding="utf-8")
(OW.ops_dir() / "last_measured.json").write_text("[2]", encoding="utf-8")
_ap.write_text("[3]", encoding="utf-8")
try:
    _r = OW.run(now=NOW + 7, rules=_bad_rules, families={"v3"})
finally:
    OW.append = _ap2
    _ap.unlink()
_fl = json.loads((OW.ops_dir() / "flags.json").read_text(encoding="utf-8"))["flags"]
check("run: an unwritable series is a flag and the pass finishes", any(f["rule"] == "series_write" for f in _fl), _fl)
check("run: an unreadable alarms.json is a flag, not a quiet zero", any(f["rule"] == "alarm_state" for f in _fl), _fl)
check("run: wrong-shaped flags.json and last_measured.json are survived", any(f["rule"] == "bad_target" for f in _fl), _fl)
_r2 = OW.run(now=NOW + 20, rules=_bad_rules, families={"v3"})
_fl2 = json.loads((OW.ops_dir() / "flags.json").read_text(encoding="utf-8"))["flags"]
_old = [f for f in _fl2 if f["rule"] == "bad_target"]
check("flags: a flag keeps its first-open time across passes", _old and all(f["since"] == OW.iso(NOW + 7) for f in _old), _fl2)
_rr = copy.deepcopy(RULES)
_rr["run"]["n"] = 0
_rr["run"]["keys"] = ["x.*"]
_fl = OW.andon({"x.k": OW.M(5.0, "n")}, {"x.k": [(NOW - 60, 4.0), (NOW - 30, 3.0)]}, {}, _rr, NOW)
check("rules: a run rule of n=0 is a flag, not a dead pass", any(f["rule"] == "bad_rule" for f in _fl), _fl)
_rm = copy.deepcopy(_bad_rules)
_rm["targets"] = [{"key": "x.k", "op": ">", "value": 1, "tag": "M", "marks": ["MESURED"], "alarm": True},
                  {"key": "x.k", "op": ">", "value": 1, "tag": "DUP", "alarm": True},
                  {"key": "x.k", "op": ">", "value": 9, "tag": "DUP", "alarm": True}]
_fl = OW.andon({"x.k": OW.M(5.0, "n")}, {}, {}, _rm, NOW)
check("rules: a misspelled mark is a bad target", any(f["rule"] == "bad_target" for f in _fl), _fl)
check("rules: a later row on the same alarm id cannot hide a crossing",
      OW.target_state({"x.k": OW.M(5.0, "n")}, _rm) == {"DUP:x.k": True}, OW.target_state({"x.k": OW.M(5.0, "n")}, _rm))
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN"}}), encoding="utf-8")
_filed.clear()
_ok = lambda todo, conf: _filed.extend(todo) or {a["name"]: None for a in todo}
_st = OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rm, NOW, set(), _ok)
check("alarms: OPEN with no item told nobody, so it is filed", len(_filed) == 1 and _st["DUP:x.k"].get("item"), (_filed, _st))
check("alarms: the title quotes the row that crossed", "line > 1" in _filed[0]["title"], _filed)
_ap.write_text(json.dumps({"DUP:x.k": {"state": "PENDING", "name": "OPS_DISK_FULL_DIAGNOSE_AB12", "title": "t", "tries": "bad"}}), encoding="utf-8")
_st = OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rm, NOW, set(), _ok)
check("alarms: a corrupt retry counter does not stop the pass, and a good filing opens",
      json.loads(_ap.read_text(encoding="utf-8"))["DUP:x.k"]["state"] == "OPEN", _ap.read_text(encoding="utf-8")[:300])
_ap.unlink()
_AU.read_now = lambda now: {"accounts": {"zgood": {"source": "ESTIMATE", "week_pct_left": 50.0, "hours_to_week_reset": 10.0,
                                                   "week_pct_used": 50.0}, "strpct": {"source": "ESTIMATE", "week_pct_left": "bad"}}}
try:
    _a = OW.c_accounts(NOW, RULES, {})
finally:
    _AU.read_now = _rn
check("accounts: a row that raises costs itself, the next account still reads",
      _a["accounts.strpct.runway"]["m"] == "UNMEASURED" and _a["accounts.zgood.week_left_pct"]["m"] == "ESTIMATE", _a)
_rt = copy.deepcopy(_bad_rules)
_rt["token_talk"]["terms"] = list(_rt["token_talk"]["terms"]) + ["("]
OW.run(now=NOW + 30, rules=_rt, families={"v3"})
check("digest: a bad token_talk term fails the blind digest closed and aloud",
      "unavailable" in (OW.ops_dir() / "digest_blind.md").read_text(encoding="utf-8"))
check("rules: an enormous integer value is a bad target, not a dead pass", OW.target_problem(
    {"key": "x", "op": ">", "value": 10 ** 400, "tag": "T"}) is not None)
check("accounts: NaN is no reading of runway", OW.runway(50.0, float("nan"), 10.0) is None)
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN", "for": "Operations"}}), encoding="utf-8")
_filed.clear()
OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rm, NOW, set(), _ok)
check("alarms: a non-token alarm marked for Operations with no item is filed", len(_filed) == 1, _filed)
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN", "item": 123}}), encoding="utf-8")
OW.qhome = lambda: _q2
(_q2 / "done" / "old_torn.json").unlink()
wj(_q2 / "done" / "listresult.json", {"finished": OW.iso(NOW - 5 * 60), "job": {"id": "l"}, "result": [1]})
os.utime(_q2 / "done" / "listresult.json", (NOW, NOW))
wj(_q2 / "steward.json", {"epoch": NOW - 60})
try:
    _s = OW.c_steve(NOW, RULES, {})
    check("steve: a done record with a list result is one bad record, not a lost family",
          _s["steve.invalid_streak"]["m"] == "ESTIMATE", _s["steve.invalid_streak"])
    check("steve: a steward record with no state or fault is unknown, not healthy",
          _s["steve.unowned_stall_min"]["m"] == "UNMEASURED", _s["steve.unowned_stall_min"])
finally:
    OW.qhome = _qh
OW.run(now=NOW + 40, rules=_rm, families={"v3"})
check("digest: a non-string item is repaired to pending, and the digest still names the alarm",
      "PENDING DUP:x.k" in (OW.ops_dir() / "digest.md").read_text(encoding="utf-8"), (OW.ops_dir() / "digest.md").read_text(encoding="utf-8")[:400])
_ap.unlink()
_rb = copy.deepcopy(_rr)
_rb["band"]["min_points"] = "20"
_rb["band"]["keys"] = ["x.*"]
_rb["band"]["skip"] = []
_rb["run"]["n"] = 2
_fl = OW.andon({"x.k": OW.M(5.0, "n")}, {"x.k": [(NOW - 90, 1.0), (NOW - 60, 2.0), (NOW - 30, 3.0)]}, {}, _rb, NOW)
check("rules: a bad band rule leaves the run rule working", any(f["rule"] == "run" for f in _fl)
      and any(f["rule"] == "bad_rule" and f["tag"] == "band" for f in _fl), _fl)
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN", "item": ["bad"], "name": ["bad"]}}), encoding="utf-8")
_filed.clear()
_rc = copy.deepcopy(_rm)
_rc["alarm"]["clear_passes"] = "four"
OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rc, NOW, set(), _ok)
check("alarms: a bad clear_passes, and an item or name of the wrong type, still file", len(_filed) == 1, _filed)
_ap.unlink()
_sj = OW.systemctl_json
OW.systemctl_json = lambda *a: [{"unit": "x.service"}] if a[0] == "list-units" else [{"unit": "t", "next": "unknown"}]
try:
    _t = OW.c_timers(NOW, RULES, {})
finally:
    OW.systemctl_json = _sj
check("timers: a bad timer row keeps the failed-unit count MEASURED", _t["timers.failed_units"]["v"] == 1
      and _t["timers.overdue_timers"]["m"] == "ESTIMATE", _t)
check("testing: a job with list counts is not a caught job, and does not raise",
      OW.caught({"result": {"counts": ["bad"]}, "job": {"item": ["x"]}, "ingested": 5}, {}, 1) is False)
_lm, _keep = OW.carry_last_measured({}, {"x.k": 1e20}, {"x.k": OW.U("gone")}, NOW)
check("silence: a future saved time is dropped, not a muted key", "x.k" not in _lm and "x.k" not in _keep, (_lm, _keep))
OW.qhome = lambda: _q2
wj(_q2 / "steward.json", {"epoch": NOW + 3600, "state": "RUNNING", "fault": False})
try:
    _s = OW.c_steve(NOW, RULES, {})
finally:
    OW.qhome = _qh
check("steve: a steward record from the future is unknown, not a fresh heartbeat", _s["steve.state"]["m"] == "UNMEASURED", _s["steve.state"])
_dm = OW.digest_md
_digest_before = None
OW.digest_md = lambda dg: (globals().__setitem__("_digest_before", dg.get("headline")), len(5))[1]
try:
    OW.run(now=NOW + 50, rules=_rm, families={"v3"})
finally:
    OW.digest_md = _dm
_dtxt = (OW.ops_dir() / "digest.md").read_text(encoding="utf-8")
check("digest: a render failure writes the failure and the headline", "failed to render" in _dtxt and _digest_before and _digest_before in _dtxt, _dtxt[:300])
_ap.write_text(json.dumps({"DUP:x.k": {"state": "PENDING", "name": "OPS_DISK_FULL_DIAGNOSE_AB12", "title": "t", "tries": "bad"}}), encoding="utf-8")
_filed.clear()
OW.run_alarms({"x.k": OW.U("off")}, _rm, NOW, set(), _ok)
_st = json.loads(_ap.read_text(encoding="utf-8"))
_n1 = len(_filed)
OW.run_alarms({"x.k": OW.U("off")}, _rm, NOW + 60, set(), _ok)
check("alarms: a corrupt retry count still opens on a good filing, and is never filed twice",
      _n1 == 1 and _st["DUP:x.k"]["state"] == "OPEN" and len(_filed) == 1, (_filed, _st))
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN", "item": "NO_SUCH_ITEM", "name": "NO_SUCH_ITEM"}}), encoding="utf-8")
_filed.clear()
OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rm, NOW, {"OTHER_ITEM"}, _ok)
check("alarms: OPEN on an item the ledger never held is filed", len(_filed) == 1, _filed)
_ap.write_text(json.dumps({"DUP:x.k": {"state": "OPEN", "item": "NO_SUCH_ITEM", "name": "NO_SUCH_ITEM"}}), encoding="utf-8")
_filed.clear()
OW.run_alarms({"x.k": OW.M(5.0, "n")}, _rm, NOW, set(), _ok)
check("alarms: control: an unread ledger judges no OPEN item", not _filed, _filed)
_ap.unlink()
check("numbers: a 401-digit integer is no number and no time, not a crash",
      OW.num({"v": 10 ** 400}) is None and OW.epoch(10 ** 400) is None and OW.finite(1.0) and not OW.finite(10 ** 400))
_lm, _keep = OW.carry_last_measured({}, {"x.k": 10 ** 400}, {"x.k": OW.U("gone")}, NOW)
check("silence: an overflowing saved time is dropped", "x.k" not in _keep, _keep)
OW.qhome = lambda: _q2
wj(_q2 / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": True, "since": OW.iso(NOW + 86400)})
for _i in range(3):
    wj(_q2 / "done" / ("inv%d.json" % _i), {"finished": OW.iso(NOW - 600 + _i), "job": {"id": "i%d" % _i}, "result": {"verdict": "INVALID"}})
_bad = []
wj(_q2 / "done" / "tomorrow.json", {"finished": OW.iso(NOW + 86400), "job": {"id": "t"}, "result": {"verdict": "PASS"}})
_j = OW.done_jobs(NOW - 3600, _bad, NOW)
check("steve: a done record from the future is unreadable, not the newest result",
      "tomorrow.json" in _bad and not [1 for _f, _d in _j if _d["job"]["id"] == "t"]
      and [1 for _f, _d in OW.done_jobs(NOW - 3600, None) if _d["job"]["id"] == "t"], _bad)
try:
    _s = OW.c_steve(NOW, RULES, {})
finally:
    OW.qhome = _qh
check("steve: a fault that starts in the future has an unknown duration, not a healthy 0",
      _s["steve.fault_min"]["m"] == "UNMEASURED" and _s["steve.unowned_stall_min"]["m"] != "MEASURED", _s["steve.fault_min"])
_cxm, _dirs = sys.modules.get("csuite_codex_limits"), OW.codex_dirs
_cxs = types.SimpleNamespace()
sys.modules["csuite_codex_limits"] = _cxs
_rs = OW.iso(NOW + 3 * 86400)
OW.codex_dirs = lambda: [str(TMP)]
_cxs.readings = lambda *a, **k: ([(OW.iso(NOW - 3600), 90.0, 10080, _rs, None, None, None, "x"),
                                   (OW.iso(NOW - 60), "broken", 10080, _rs, None, None, None, "x")], 1)
_c1 = OW.c_codex(NOW, RULES, {})
_cxs.readings = lambda *a, **k: ([(OW.iso(NOW - 3600), 90.0, 10080, _rs, None, None, None, "x"),
                                   (OW.iso(NOW + 86400), 0.0, 10080, OW.iso(NOW + 8 * 86400), None, None, None, "x")], 1)
_c2 = OW.c_codex(NOW, RULES, {})
OW.codex_dirs = _dirs
if _cxm is not None:
    sys.modules["csuite_codex_limits"] = _cxm
else:
    del sys.modules["csuite_codex_limits"]
check("codex: a newer broken record leaves the older reading an ESTIMATE, said aloud",
      _c1["codex.week_used_pct"]["v"] == 90.0 and _c1["codex.week_used_pct"]["m"] == "ESTIMATE", _c1["codex.week_used_pct"])
check("codex: a record from tomorrow is not the reading", _c2["codex.week_used_pct"]["v"] == 90.0
      and _c2["codex.week_used_pct"]["m"] == "ESTIMATE", _c2["codex.week_used_pct"])
_sj = OW.systemctl_json
def _nofail(*a):
    if a[0] == "list-units":
        raise RuntimeError("down")
    return [{"unit": "t", "next": 1}]
OW.systemctl_json = _nofail
try:
    _t = OW.c_timers(NOW, RULES, {})
finally:
    OW.systemctl_json = _sj
check("timers: list-units failing still reads the timers", _t["timers.failed_units"]["m"] == "UNMEASURED"
      and _t["timers.overdue_timers"]["v"] == 1, _t)
_rx = copy.deepcopy(RULES)
del _rx["run"]
_fl = OW.andon({"disk.root_free_gb": OW.M(5.0, "GB")}, {}, {}, _rx, NOW)
check("andon: a missing rule section is one flag, and the other rules still run",
      len([f for f in _fl if f["rule"] == "bad_rule"]) == 1 and [f for f in _fl if f["rule"] == "bad_rule"][0]["key"] == "rules.run"
      and any(f["key"] == "disk.root_free_gb" and f["rule"] != "bad_rule" for f in _fl), _fl[:3])
_rx = copy.deepcopy(RULES)
del _rx["alarm"]
OW.run(now=NOW + 60, rules=_rx, families={"v3"})
_dg = (OW.ops_dir() / "digest.md").read_text(encoding="utf-8")
check("run: a missing alarm section is said aloud, and the digest goes out", "NO ALARM CAN BE FILED" in _dg, _dg[:300])
_aj = OW.atomic_json
def _full(path, obj):
    if str(path).endswith("last_measured.json"):
        raise OSError(28, "No space left on device")
    return _aj(path, obj)
OW.atomic_json = _full
_ra = OW.run_alarms
_ran = []
OW.run_alarms = lambda *a, **k: (_ran.append(1), _ra(*a, **k))[1]
try:
    OW.run(now=NOW + 70, rules=RULES, families={"v3"})
finally:
    OW.atomic_json, OW.run_alarms = _aj, _ra
check("run: a full disk at last_measured.json still runs the alarms", _ran == [1], _ran)
_rp = TMP / "rules_torn.json"
_rp.write_text(json.dumps({"series_days": 8}), encoding="utf-8")
OW.load_rules(_rp)
_rp.write_text('{"series_days": 8, ', encoding="utf-8")
_lr = OW.load_rules(_rp)
check("rules: a torn file falls back to the last good copy, said aloud", _lr.get("series_days") == 8 and _lr.get("_load_error"), _lr)
_rp.write_text("[1]", encoding="utf-8")
check("rules: a list root is torn too", OW.load_rules(_rp).get("_load_error"))
_dj = {"result": {"outcome": {"status": "INVALID"}}, "job": {}}
check("steve: an outcome that is no string is no outcome", OW.outcome_of(_dj) is None and OW.outcome_of({"result": {"outcome": "DONE"}}) == "DONE")
OW.qhome = lambda: _q2
wj(_q2 / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": False, "reason": 42})
try:
    _s = OW.c_steve(NOW, RULES, {})
finally:
    OW.qhome = _qh
check("steve: a numeric reason costs nothing", _s["steve.state"]["m"] == "MEASURED", _s["steve.state"])
import pulse_core as _pc  # noqa: E402
_rl, _si = _pc.read_ledger, OW.steve_incident_unclaimed
def _boom(*a):
    raise TypeError("bad steve_incident")
_pc.read_ledger, OW.steve_incident_unclaimed = (lambda *a, **k: []), _boom
try:
    _f = OW.c_flow(NOW, RULES, {})
finally:
    _pc.read_ledger, OW.steve_incident_unclaimed = _rl, _si
check("flow: a bad steve_incident rule costs its own reading, the family's others survive",
      _f["steve.incident_unclaimed_min"]["m"] == "UNMEASURED" and any(k.startswith("flow.") and p["m"] == "MEASURED" for k, p in _f.items()), _f)
_rx = copy.deepcopy(RULES)
_rx["targets"] = [{"key": "disk.root_free_bg", "op": "<", "value": 210, "alarm": False, "tag": "T_X", "title_field": None, "marks": ["MEASURED"]}]
_cs = dict(OW.COLLECTORS)
OW.COLLECTORS.clear()
OW.COLLECTORS["disk"] = lambda now, rules, ctx: {"disk.root_free_gb": OW.M(500.0, "GB")}
OW.ORDER, _od = ("disk",), OW.ORDER
try:
    _dg = OW.run(now=NOW + 80, rules=_rx, filer=None)
    _txt = (OW.ops_dir() / "flags.json").read_text(encoding="utf-8")
finally:
    OW.ORDER = _od
    OW.COLLECTORS.clear()
    OW.COLLECTORS.update(_cs)
check("run: a target key matching no reading is said aloud", "matches no reading" in _txt, _txt[:300])
_sp = OW.series_path("steve")
_sp.parent.mkdir(parents=True, exist_ok=True)
_T0 = NOW + 7200
OW.COLLECTORS["steve"] = lambda now, rules, ctx: {"steve.state": OW.M("RUNNING", "steward state")}
_rq = copy.deepcopy(RULES)
_rq["targets"] = []
_rq["silent"] = {"keys": ["steve.state"], "skip": [], "per_key": {}, "default_h": 1}
OW.run(now=_T0, rules=_rq, families={"steve"})
OW.COLLECTORS["steve"] = lambda now, rules, ctx: {"steve.state": OW.U("gone")}
OW.run(now=_T0 + 3 * 3600, rules=_rq, families={"steve"})
OW.COLLECTORS.update(_cs)
_txt = (OW.ops_dir() / "flags.json").read_text(encoding="utf-8")
check("silent: a state string that went unmeasured raises the flag, through run", '"silent"' in _txt and "steve.state" in _txt, _txt[:300])
_fp = OW.series_path("steve")
with open(_fp, "a", encoding="utf-8") as _fh:
    _fh.write(json.dumps({"t": _T0 + 400 * 86400, "ts": "x", "points": {"steve.state": OW.M("RUNNING", "s")}}) + "\n")
OW.COLLECTORS["steve"] = lambda now, rules, ctx: {"steve.state": OW.U("gone")}
OW.run(now=_T0 + 4 * 3600, rules=_rq, families={"steve"})
OW.COLLECTORS.update(_cs)
_txt = (OW.ops_dir() / "flags.json").read_text(encoding="utf-8")
check("silent: a series row from the future does not read as just measured", '"silent"' in _txt, _txt[:300])
_rp.write_text(json.dumps({"series_days": 8}), encoding="utf-8")
OW.load_rules(_rp)
_rp.write_text(json.dumps({"series_days": "8"}), encoding="utf-8")
_lr = OW.load_rules(_rp)
check("rules: a string series_days is torn, and never becomes the last good copy",
      _lr.get("series_days") == 8 and _lr.get("_load_error") and OW.read_json(OW.ops_dir() / "rules_last_good.json")["series_days"] == 8, _lr)
OW.qhome = lambda: _q2
wj(_q2 / "steward.json", {"epoch": NOW - 60, "state": "FAULT", "fault": None, "since": OW.iso(NOW - 3600), "reason": "x"})
try:
    _s = OW.c_steve(NOW, RULES, {})
finally:
    OW.qhome = _qh
check("steve: a null fault is unknown, never a healthy 0", _s["steve.fault_min"]["m"] == "UNMEASURED", _s["steve.fault_min"])
_ap2 = OW.ops_dir() / "alarms.json"
_ap2.write_text(json.dumps({"DISK_LOW:disk.root_free_gb": {"state": "OPEN", "item": "X_Y_Z", "clear_seen": "3", "since": OW.iso(NOW)}}), encoding="utf-8")
_st = OW.run_alarms({"disk.root_free_gb": OW.M(500.0, "GB")}, RULES, NOW, set(), None)
check("alarm: a string clear_seen restarts the count instead of crashing", _st.get("DISK_LOW:disk.root_free_gb", {}).get("clear_seen") == 1, _st)
check("testing: a string FAIL count is unreadable, not a catch", OW.fail_count_unreadable({"result": {"counts": {"FAIL": "0"}}})
      and not OW.fail_count_unreadable({"result": {"counts": {"FAIL": 0}}}) and not OW.caught({"result": {"counts": {"FAIL": "0"}}, "job": {}}, {}, 24), "")
_rc = copy.deepcopy(RULES)
_rc.setdefault("alarm", {})["clear_passes"] = float("inf")
_ap2.write_text(json.dumps({"DISK_LOW:disk.root_free_gb": {"state": "OPEN", "item": "X_Y_Z", "since": OW.iso(NOW)}}), encoding="utf-8")
_st = OW.run_alarms({"disk.root_free_gb": OW.M(500.0, "GB")}, _rc, NOW, set(), None)
check("alarm: an infinite clear_passes falls back to 4, the alarm neither crashes nor clears at once",
      _st.get("DISK_LOW:disk.root_free_gb", {}).get("clear_seen") == 1, _st)
for _i in (2, 3):
    _st = OW.run_alarms({"disk.root_free_gb": OW.M(500.0, "GB")}, _rc, NOW + _i, set(), lambda t, c: {})
check("alarm: the fallback holds the alarm through three clear readings",
      _st.get("DISK_LOW:disk.root_free_gb", {}).get("clear_seen") == 3, _st)
_st = OW.run_alarms({"disk.root_free_gb": OW.M(500.0, "GB")}, _rc, NOW + 4, set(), lambda t, c: {})
check("alarm: the fallback clears on the fourth", "DISK_LOW:disk.root_free_gb" not in _st, _st)
os.environ["RM_OPS_DISKS"] = "root=%s,d,=x,e=" % TMP
_d = OW.c_disk(NOW, RULES, {})
check("disk: a bad entry is its own UNMEASURED disk, the good one still reads",
      _d["disk.root_free_gb"].get("m") == "MEASURED" and _d["disk.d_free_gb"].get("m") == "UNMEASURED"
      and _d["disk.bad2_free_gb"].get("m") == "UNMEASURED" and _d["disk.e_used_gb"].get("m") == "UNMEASURED", _d)
os.environ["RM_OPS_DISKS"] = "root=%s" % TMP
_saved = {k: os.environ.pop(k, None) for k in ("RM_OPS_ALARM_CLONE", "RM_OPS_ALARM_PARENT")}
for _rc in ({k: v for k, v in RULES.items() if k != "alarm"},
            dict(RULES, alarm={k: v for k, v in RULES["alarm"].items() if k not in ("clone", "parent")})):
    _ap2.write_text("{}", encoding="utf-8")
    _st = OW.run_alarms({"disk.root_free_gb": OW.M(0.0, "GB")}, _rc, NOW, set(), OW.real_filer)
    _e = _st.get("DISK_LOW:disk.root_free_gb", {})
    check("alarm: no filing settings cost filing only: PENDING with the error on it",
          _e.get("state") == "PENDING" and "filer raised" in str(_e.get("error")), _st)
for _k, _v in _saved.items():
    if _v is not None:
        os.environ[_k] = _v
_rd = copy.deepcopy(RULES)
_sv = OW.COLLECTORS["disk"]
def _dead(*a):
    raise RuntimeError("source gone")
OW.COLLECTORS["disk"] = _dead
OW.series_path("disk").unlink(missing_ok=True)
OW.run(now=NOW + 90, rules=_rd, families={"disk"})
OW.COLLECTORS["disk"] = _sv
_fl = json.loads((OW.ops_dir() / "flags.json").read_text(encoding="utf-8"))["flags"]
check("run: a collector with no history left is still flagged by name",
      [f for f in _fl if f["rule"] == "collector" and f["key"] == "disk._collector" and "source gone" in f["detail"]], _fl[:3])
_run = OW.subprocess.run
def _tps(ratio, stalls, smax):
    OW.subprocess.run = lambda *a, **k: types.SimpleNamespace(returncode=0, stdout=json.dumps({"summary": {
        "coverage": "FRESH", "ratioMedian": ratio, "stalls": stalls, "stallMaxS": smax}}), stderr="")
    try:
        return OW.c_tps(NOW, RULES, {})
    finally:
        OW.subprocess.run = _run
_t = _tps("fast", "2", "x")
check("tps: text from the recorder is UNMEASURED in all three readings",
      all(_t[k].get("m") == "UNMEASURED" for k in ("tps.ratio_median", "tps.stalls", "tps.stall_max_s")), _t)
_t = _tps(0.9, 2, 1.5)
check("tps: numbers still read MEASURED",
      all(_t[k].get("m") == "MEASURED" for k in ("tps.ratio_median", "tps.stalls", "tps.stall_max_s")), _t)
sys.path.insert(0, str(Path(OW.__file__).parent / "testq"))
import schema as _schema  # noqa: E402
check("steve: the outcome words are the schema's", tuple(OW.OUTCOMES) == tuple(_schema.OUTCOMES), _schema.OUTCOMES)
check("steve: a misspelt outcome is no outcome", OW.outcome_of({"result": {"outcome": "INVALD"}}) is None)
OW.qhome = lambda: _q2
wj(_q2 / "steward.json", {"epoch": NOW - 50 * 60, "state": "RUNNING", "fault": False, "since": None})
wj(_q2 / "steward_watch.json", {"epoch": NOW + 86400})
try:
    _s = OW.c_steve(NOW, RULES, {})
finally:
    OW.qhome = _qh
check("steve: a watcher from the future does not hide the stall", _s["steve.unowned_stall_min"]["m"] == "MEASURED" and _s["steve.unowned_stall_min"]["v"] > 0, _s["steve.unowned_stall_min"])
check("patterns: a bare string is one key, not its characters", OW.matches("a.b", "a.*") and not OW.matches("a", "a.*"))
check("v3: a reason that is no string still renders", isinstance(OW.c_v3(NOW, {"v3_owed": {"k": {"reason": "x"}}}, {})["v3.k"]["why"], str))
print("GREEN" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)

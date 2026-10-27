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
import json
import os
import subprocess
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


OW.mint_name = fake_mint
pts = {"timers.failed_units": M(2)}
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
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "RUNNING", "fault": None, "incident": None, "since": None})
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
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": "ssh", "incident": None,
                        "since": OW.iso(NOW - 45 * 60)})
s = OW.c_steve(NOW, RULES, {})
check("steve: a 45 min fault with no steward incident -> unowned stall 45",
      abs(s["steve.unowned_stall_min"]["v"] - 45) < 0.2, s["steve.unowned_stall_min"])
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": "ssh", "incident": "INC1",
                        "since": OW.iso(NOW - 45 * 60)})
s = OW.c_steve(NOW, RULES, {})
check("steve: the same fault with a steward incident is owned -> 0", s["steve.unowned_stall_min"]["v"] == 0.0,
      s["steve.unowned_stall_min"])
wj(Q / "steward.json", {"epoch": NOW - 50 * 60, "state": "RUNNING", "fault": None, "incident": None, "since": None})
wj(Q / "steward_watch.json", {"epoch": NOW - 40 * 60, "incident": None})
s = OW.c_steve(NOW, RULES, {})
check("steve: steward AND watcher both silent > 30 min -> unowned stall = heartbeat age",
      abs(s["steve.unowned_stall_min"]["v"] - 50) < 0.2, s["steve.unowned_stall_min"])
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
check("run: digest d24 for d_free_gb is 0 (1000 a day ago, 1000 now)", k["disk.d_free_gb"]["d24"] == 0.0, k["disk.d_free_gb"])
check("run: the digest.md exists and leads with the headline",
      (TMP / "ops" / "digest.md").read_text().splitlines()[2].startswith("runway"))
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
check("runway: a spent quota is 0 whatever the rate", OW.runway(0, 0, 100) == 0.0 and OW.runway(-1, 2.0, 50) == 0.0)
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
wj(Q / "steward.json", {"epoch": NOW - 60, "state": "UNREACHABLE", "fault": "ssh", "incident": None, "since": "garbage"})
s = OW.c_steve(NOW, RULES, {})
check("steve: a fault with no readable since is UNMEASURED duration, not 0 min",
      s["steve.fault_min"]["m"] == "UNMEASURED" and s["steve.unowned_stall_min"]["m"] == "UNMEASURED", s)
wj(Q / "steward.json", {"epoch": NOW - 90 * 60, "state": "RUNNING", "fault": None, "incident": None, "since": None})
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

print("GREEN" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)

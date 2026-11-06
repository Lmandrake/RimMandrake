#!/usr/bin/env python3
"""selftest_ops_watch_root_grower.py -- disk.root_fall_gb (GROWER_ALARM_WIRE_NOBODY_READS_IT), by planted faults.

Each case plants growth.jsonl and growth_capture.json where disk_grower writes them (the folder RM_SCRATCH_REAP_RUNS
names) and runs the real `ops_watch.py run` CLI on the disk family into a temp dir, then reads what the pass wrote.
Nothing is filed: alarms.json holds the crossing as PENDING. One case makes the planted files with disk_grower.tick
itself, over a fake /proc, so the two halves agree on the shape. The line comes from the shipped rules and is held to
disk_grower's own capture line."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import disk_grower as DG  # noqa: E402
import ops_watch as OW  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_root_grower_"))
FAILS = []
KEY, HOT, BLIND = "disk.root_fall_gb", "disk.root_fall_distressed", "disk.root_fall_blind"
NAME, BLIND_NAME = "OPS_ROOT_GROWER_MEASURE_CAUGHT_WRITING", "OPS_ROOT_GROWTH_RESTORE_GONE_QUIET"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
RANGE = RULES["ranges"][KEY]
MAX_MIN = RANGE["max_age_min"]
ENV = {"RM_POOL_ROOT": str(TMP / "pool"), "RM_SCRATCH_ROOT": str(TMP / "scratch"), "RM_OBJSTORE_STATE": str(TMP / "objstore"),
       "RM_SESSION_GLOB": str(TMP / "none/*"), "RM_OPS_DISKS": "root=/"}
(TMP / "pool").mkdir()
(TMP / "scratch").mkdir()
WRITER = {"pid": 4242, "unit": "rm-hog.service", "cwd": "/home/mandrake/rm/hog", "cmd": "python3 fill_the_disk.py --forever",
          "gb": 33.1, "gb_per_min": 3.31}


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def row(fall, age_min=2.0, free=140.0):
    t = time.time() - age_min * 60
    return {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)), "t": t, "free_gb": free, "fall_gb": fall,
            "window_min": 30.0, "readable": 90, "blind": 70, "top_writer_gb": 33.1, "captured": fall >= DG.FALL_GB}


def capture(r, writers=(WRITER,), open_big=()):
    return {"ts": r["ts"], "why": ["root fell %s GB within 30 min" % r["fall_gb"]], "free_gb": r["free_gb"],
            "fall_gb": r["fall_gb"], "since_last_sample_s": 600, "writers": list(writers), "open_big": list(open_big),
            "open_scan_finished": True, "readable": 90, "blind": 70}


def plant(name, growth, cap=None):
    """growth: a list of rows (or raw text, or None for no file)."""
    d = TMP / name
    d.mkdir()
    (d / "runs.jsonl").write_text("")
    if growth is not None:
        (d / "growth.jsonl").write_text(growth if isinstance(growth, str) else "".join(json.dumps(x) + "\n" for x in growth))
    if cap is not None:
        (d / "growth_capture.json").write_text(json.dumps(cap))
    return d


def cli_pass(d):
    ops = d / "ops"
    env = {**os.environ, **ENV, "RM_SCRATCH_REAP_RUNS": str(d / "runs.jsonl"), "RM_OPS_WATCH_DIR": str(ops)}
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "run", "--family", "disk"], env=env, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-600:]
    dg = json.loads((ops / "digest.json").read_text())
    return dg["kpis"], json.loads((ops / "alarms.json").read_text())


def alarm(alarms, key):
    return [a for k, a in alarms.items() if key in k and isinstance(a, dict)]


# Sanity probe: a quiet root reads its small fall, sane, so a distressed reading below is the fault, not a blind instrument.
q = row(9.3, free=558.6)
k, al = cli_pass(plant("quiet", [row(0.0, age_min=12), q]))
check("a quiet root reads its fall of 9.3 GB, sane", k[KEY]["m"] == "MEASURED" and k[KEY]["v"] == 9.3 and k[KEY]["class"] == "sane", k[KEY])
check("a quiet root alarms nothing", k[HOT]["v"] == 0 and k[BLIND]["v"] == 0 and not alarm(al, HOT) and not alarm(al, BLIND), al)
check("the reading names its owner and age", k[KEY]["owner"] == "Operations" and k[KEY]["max_age_min"] == MAX_MIN, k[KEY])

# The fault of the item: the 2026-11-04 fall, ~33 GB a tick, with the writer caught in the capture.
f = row(66.2)
gone = {"path": "/home/mandrake/rm/hog/big.bin", "deleted": True, "alloc_gb": 40.0, "pids": [4242]}
k, al = cli_pass(plant("fast_fall", [row(30.0, age_min=12), f], capture(f, open_big=[gone])))
a = alarm(al, HOT)
txt = json.dumps(a)
check("a fast fall reads distressed", k[KEY]["v"] == 66.2 and k[KEY]["class"] == "distressed" and k[HOT]["v"] == 1, k[KEY])
check("its alarm is raised on this pass, under its fixed item", a and NAME in txt, al)
check("the alarm names the writer: pid, unit, cwd, command", all(s in txt for s in ("4242", "rm-hog.service", "/home/mandrake/rm/hog",
                                                                                    "fill_the_disk.py")), txt[:600])
# The title is cut at 160 characters, so the full cause and the writers are read off the point itself.
pt = OW.root_growth(TMP / "fast_fall", time.time(), RULES)[HOT]["x"]
check("the full cause names the open deleted file", "big.bin" in pt["cause"], pt["cause"])
check("the writers ride on the reading", pt["writers"][0]["pid"] == 4242, pt)

# A fast fall whose capture is from another tick (or absent) still alarms, and says the writer is unnamed.
old = row(40.0, age_min=40)
k, al = cli_pass(plant("stale_capture", [f], capture(old)))
check("a capture from another tick: still distressed, writer unnamed", k[HOT]["v"] == 1 and "writer unnamed" in json.dumps(alarm(al, HOT)), al)
k, al = cli_pass(plant("no_capture", [f]))
check("no capture at all: still distressed, writer unnamed", k[HOT]["v"] == 1 and "writer unnamed" in json.dumps(alarm(al, HOT)), al)
k, al = cli_pass(plant("no_writers", [f], capture(f, writers=())))
check("a capture with no readable writer says so", k[HOT]["v"] == 1 and "no readable writer" in json.dumps(alarm(al, HOT)), al)

# Under the line only (free low, no fall) is disk.root_free_gb's business, not this alarm.
k, al = cli_pass(plant("low_not_falling", [row(0.0, free=100.0)]))
check("low but not falling is not a grower", k[HOT]["v"] == 0 and not alarm(al, HOT), k[KEY])

# Line edges, held to disk_grower's capture line.
line = RANGE["classes"]["distressed"]["at_least"]
check("the distressed line is disk_grower.FALL_GB", line == DG.FALL_GB, (line, DG.FALL_GB))
check("sane under the line, distressed on it", OW.base_class(RANGE, line - 0.1) == "sane" and OW.base_class(RANGE, line) == "distressed")

# Every way of not seeing: UNMEASURED and alarmed, never sane. A stale fast fall must not read as sane either.
for name, body, says in (("missing", None, "No such file"), ("empty", "", "no row"), ("torn", '{"ts": "2026', "growth record"),
                         ("not_object", "[1]\n", "no row"), ("stale_quiet", [row(0.0, age_min=MAX_MIN + 5)], "frozen"),
                         ("stale_fall", [row(66.0, age_min=MAX_MIN + 5)], "frozen"), ("future", [row(0.0, age_min=-30)], "ahead"),
                         ("no_stamp", [{"fall_gb": 0.0}], "no stamp"), ("no_fall", [{k2: v for k2, v in row(0).items() if k2 != "fall_gb"}], "no fall_gb"),
                         ("neg_fall", [row(-1.0)], "no fall_gb"), ("bool_fall", [row(0) | {"fall_gb": True}], "no fall_gb")):
    k, al = cli_pass(plant("blind_" + name, body))
    check("%s: reads UNMEASURED, not sane" % name, k[KEY]["m"] == "UNMEASURED" and k[KEY].get("class") is None
          and says in (k[KEY].get("why") or ""), k[KEY])
    check("%s: the blind alarm stands under its own item" % name, k[BLIND]["v"] == 1 and k[BLIND]["class"] == "distressed"
          and BLIND_NAME in json.dumps(alarm(al, BLIND)), al)
    check("%s: no false grower alarm" % name, not alarm(al, HOT), al)

# A range taken out of the rules: a limit that is missing reads blind.
cut = json.loads(json.dumps(RULES))
del cut["ranges"][KEY]
p = OW.root_growth(plant("no_range", [f], capture(f)), time.time(), cut)
check("no range reads blind, never sane", p[KEY]["m"] == "UNMEASURED" and p[BLIND]["v"] == 1, p)

# The two halves agree: disk_grower.tick over a fake /proc writes what ops_watch reads.
proc = TMP / "proc"
pid = proc / "4242"
pid.mkdir(parents=True)
(pid / "stat").write_text("4242 (python3) S " + " ".join(["0"] * 18) + " 777 0 0\n")
(pid / "cgroup").write_text("0::/user.slice/user@1000.service/app.slice/rm-hog.service\n")
(pid / "cmdline").write_text("python3\0fill_the_disk.py\0")
sd = TMP / "real_tick"
sd.mkdir()
(sd / "runs.jsonl").write_text("")
os.environ["DISK_GROWER_PROC"] = str(proc)
now = time.time()
(pid / "io").write_text("write_bytes: 1000\n")
DG.tick(sd, 500.0, 210.0, now=now - 600)
(pid / "io").write_text("write_bytes: %d\n" % (1000 + 50 * 10 ** 9))
g = DG.tick(sd, 450.0, 210.0, now=now)
k, al = cli_pass(sd)
check("a real tick's capture reaches the alarm: distressed and naming pid 4242", g["captured"] and k[HOT]["v"] == 1
      and "4242" in json.dumps(alarm(al, HOT)) and "rm-hog.service" in json.dumps(alarm(al, HOT)), (g, alarm(al, HOT)))

if not FAILS:
    shutil.rmtree(TMP, ignore_errors=True)
print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)

#!/usr/bin/env python3
"""selftest_ops_watch_partial_pass.py -- a --family pass without --compose is a sample, never the live reading.

STATUS_FIX_HALF_PASS_ATE_THE_SLOT: a lone `run --family disk` pass replaced the live status.json with only its own
families (role_launch then refused a scheduled Operations slot), appended a fixture row to the live disk series, and
filed two false scratch alarms. Expect: on a store marked live (RM_OPS_WATCH_LIVE_DIR = RM_OPS_WATCH_DIR) such a pass
exits 2 and leaves status.json, the series and alarms.json byte-identical; `--family --file-alarms` without --compose
exits 2 anywhere and writes nothing; run() with the real filer on a partial pass raises before any filing; a partial
pass into a scratch dir still writes its sample; the metronome's --compose pass on the live store is not refused; and
with no env at all the default store counts as live."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_partial_"))
FAILS = []
(TMP / "pool").mkdir()
(TMP / "scratch").mkdir()
(TMP / "reap").mkdir()
(TMP / "reap" / "runs.jsonl").write_text("")
ENV = {"RM_POOL_ROOT": str(TMP / "pool"), "RM_SCRATCH_ROOT": str(TMP / "scratch"), "RM_OBJSTORE_STATE": str(TMP / "objstore"),
       "RM_SESSION_GLOB": str(TMP / "none/*"), "RM_OPS_DISKS": "root=/", "RM_SCRATCH_REAP_RUNS": str(TMP / "reap" / "runs.jsonl"),
       "TESTQ_QUEUE": str(TMP / "q"), "METRONOME_DIR": str(TMP / "metronome")}


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def plant_live(d):
    """A live store as the 15-minute pass leaves it: status.json, a disk series row, an alarms.json."""
    (d / "series").mkdir(parents=True)
    files = {d / "status.json": json.dumps({"at": "2026-11-01T15:08:00Z", "t": 1.0, "points": {"accounts.x": {"v": 1}}}),
             d / "series" / "disk.jsonl": json.dumps({"t": 1.0, "family": "disk", "points": {}}) + "\n",
             d / "alarms.json": json.dumps({"A:b": {"state": "OPEN", "item": "OPS_X"}})}
    for p, body in files.items():
        p.write_text(body)
    return {p: p.read_bytes() for p in files}


def cli(ops, live, *args):
    env = {**os.environ, **ENV, "RM_OPS_WATCH_DIR": str(ops), "RM_OPS_WATCH_LIVE_DIR": str(live)}
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "run"] + list(args), env=env, capture_output=True,
                       text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


# 1. the incident: a lone --family disk pass on the live store
live = TMP / "live"
before = plant_live(live)
rc, out = cli(live, live, "--family", "disk")
check("live store: a --family pass without --compose exits 2 and says REFUSED", rc == 2 and "REFUSED" in out, (rc, out))
check("live store: status.json, the disk series and alarms.json are byte-identical",
      all(p.read_bytes() == b for p, b in before.items()), [str(p) for p, b in before.items() if p.read_bytes() != b])
check("live store: no other family's series was started", sorted(x.name for x in (live / "series").iterdir()) == ["disk.jsonl"],
      list((live / "series").iterdir()))
check("live store: no flags.json, digest or last_measured written",
      not any((live / n).exists() for n in ("flags.json", "digest.json", "digest.md", "last_measured.json")),
      sorted(x.name for x in live.iterdir()))

# 2. --family --file-alarms without --compose: refused anywhere, before anything is written
side = TMP / "side"
rc, out = cli(side, live, "--family", "disk", "--file-alarms")
check("anywhere: --family --file-alarms without --compose exits 2", rc == 2 and "REFUSED" in out, (rc, out))
check("anywhere: that refusal wrote no status.json", not (side / "status.json").exists(), "")

# 3. in process: the real filer on a partial pass raises before any filing
os.environ.update(ENV, RM_OPS_WATCH_DIR=str(TMP / "inproc"), RM_OPS_WATCH_LIVE_DIR=str(live))
calls = []
_rf = OW.real_filer
OW.real_filer = lambda todo, conf: calls.append(todo) or {}
try:
    try:
        OW.run(filer=OW.real_filer, families=["disk"])
        raised = False
    except OW.PartialPass:
        raised = True
finally:
    OW.real_filer = _rf
check("run(): the real filer on a --family pass raises PartialPass", raised, "")
check("run(): and files nothing", calls == [], calls)
check("run(): and writes no status.json", not (TMP / "inproc" / "status.json").exists(), "")

# 4. a sample into a scratch dir still works
scratch = TMP / "sample"
rc, out = cli(scratch, live, "--family", "disk")
st = json.loads((scratch / "status.json").read_text()) if (scratch / "status.json").exists() else {}
check("scratch dir: a --family pass runs and writes its sample", rc == 0 and any(k.startswith("disk.") for k in st.get("points", {})),
      (rc, out[-300:]))

# 5. the metronome's compose pass on the live store is not refused (in process, no filer)
os.environ.update(RM_OPS_WATCH_DIR=str(live), RM_OPS_WATCH_LIVE_DIR=str(live))
try:
    OW.run(filer=None, families=["disk"], compose=True)
    ok, why = True, ""
except OW.PartialPass as e:
    ok, why = False, str(e)
st = json.loads((live / "status.json").read_text())
check("compose: a --compose pass on the live store runs and replaces status.json", ok and any(k.startswith("disk.") for k in st.get("points", {})), (why, sorted(st.get("points", {}))[:5]))
check("compose: its status is whole (the carried families are named)", "accounts._collector" in st.get("points", {})
      and st.get("measured") == ["disk"], (st.get("measured"), sorted(st.get("points", {}))[:8]))

# 6. with no env at all the default store is the live one
for k in ("RM_OPS_WATCH_DIR", "RM_OPS_WATCH_LIVE_DIR"):
    os.environ.pop(k, None)
check("default: no RM_OPS_WATCH_DIR means the live store", OW.live_store() and str(OW.ops_dir()) == OW.LIVE_OPS_DIR, OW.ops_dir())
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "elsewhere")
check("default: a scratch RM_OPS_WATCH_DIR is not live", not OW.live_store(), OW.ops_dir())

print("FAIL: %d" % len(FAILS) if FAILS else "ALL PASS")
sys.exit(1 if FAILS else 0)

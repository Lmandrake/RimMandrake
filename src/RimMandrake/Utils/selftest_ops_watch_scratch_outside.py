#!/usr/bin/env python3
"""selftest_ops_watch_scratch_outside.py -- disk.scratch_outside_cap, proved by planted faults on the real path.

Each case plants a sanity record where the reaper writes it (RM_SCRATCH_REAP_RUNS names the folder) and runs the real
`ops_watch.py run` CLI on the disk family into a temp dir, then reads what the pass wrote. Nothing is filed: alarms.json
holds the crossing as PENDING. One case runs in-process to take the collector away. The limits come from the shipped
rules, and the distressed line is held to scratch_reap's own start line."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ops_watch as OW  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_scratch_outside_"))
FAILS = []
KEY, HOT, BLIND = "disk.scratch_outside_cap", "disk.scratch_outside_distressed", "disk.scratch_outside_blind"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
RANGE = RULES["ranges"][KEY]
MAX_MIN = RANGE["max_age_min"]
ENV = {"RM_POOL_ROOT": str(TMP / "pool"), "RM_SCRATCH_ROOT": str(TMP / "scratch"), "RM_OBJSTORE_STATE": str(TMP / "objstore"),
       "RM_SESSION_GLOB": str(TMP / "none/*"), "RM_OPS_DISKS": "root=/"}
(TMP / "pool").mkdir()
(TMP / "scratch").mkdir()


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  %s" % str(detail)[:400]))
    if not cond:
        FAILS.append(name)


def rec(clones=3, age_min=5.0, phase="end", problems=()):
    """The shape scratch_reap.sanity_write leaves; the other phase is older, as in a finished run."""
    t = time.time() - age_min * 60
    body = {} if clones is None else {"rm_scratch_clones": clones, "pool_clones": 4, "pool_clones_cap": 10}
    other = "start" if phase == "end" else "end"
    return {other: {"at": t - 300, "measures": {"rm_scratch_clones": 1}, "problems": []},
            phase: {"at": t, "measures": body, "problems": list(problems)}}


def plant(name, content):
    d = TMP / name
    d.mkdir()
    (d / "runs.jsonl").write_text("")
    if content is not None:
        (d / "sanity.json").write_text(content if isinstance(content, str) else json.dumps(content))
    return d


def cli_pass(name, content):
    """One real pass. -> the digest.json points, alarms.json, digest.md and digest_blind.md."""
    d = plant(name, content)
    ops = d / "ops"
    env = {**os.environ, **ENV, "RM_SCRATCH_REAP_RUNS": str(d / "runs.jsonl"), "RM_OPS_WATCH_DIR": str(ops)}
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "run", "--family", "disk"], env=env, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-600:]
    dg = json.loads((ops / "digest.json").read_text())
    return dg["kpis"], json.loads((ops / "alarms.json").read_text()), (ops / "digest.md").read_text(), (ops / "digest_blind.md").read_text()


def alarm(alarms, key):
    return [a for k, a in alarms.items() if key in k and isinstance(a, dict)]


# The sanity probe: a sane record reads sane, so a distressed reading below means the fault, not a blind instrument.
k, al, _, _ = cli_pass("sane", rec(3))
check("a sane record reads 3 clones, sane", k[KEY]["v"] == 3 and k[KEY]["class"] == "sane" and k[KEY]["m"] == "MEASURED", k[KEY])
check("a sane record alarms nothing", k[HOT]["v"] == 0 and k[BLIND]["v"] == 0 and not alarm(al, HOT) and not alarm(al, BLIND), al)
check("the reading names its owner and age", k[KEY]["owner"] == "Operations" and k[KEY]["max_age_min"] == MAX_MIN, k[KEY])

# The planted fault of the item: 279 outside the cap.
k, al, md, blind = cli_pass("fault_279", rec(279))
check("279 outside the cap reads distressed on this pass", k[KEY]["v"] == 279 and k[KEY]["class"] == "distressed", k[KEY])
check("its alarm is raised on this pass", k[HOT]["v"] == 1 and alarm(al, HOT), al)
check("the cause names the count", "279" in json.dumps(alarm(al, HOT)) or "279" in md, alarm(al, HOT))
row = [ln for ln in md.splitlines() if ln.startswith("scratch_outside_cap |")]
check("digest.md carries it with its class", row and "279" in row[0] and "distressed" in row[0], row)
check("digest_blind.md carries it", "disk.scratch_outside_cap" in blind or "scratch_outside_cap" in blind, blind[:300])

# The newest phase decides: a new start drops the last run's end, and a run in progress has only its start.
k, _, _, _ = cli_pass("mid_run", rec(279, phase="start"))
check("the newest phase is the reading, here the start", k[KEY]["v"] == 279 and k[KEY]["class"] == "distressed", k[KEY])
only = rec(279, phase="start")
del only["end"]
k, _, _, _ = cli_pass("start_only", only)
check("a run in progress reads from its start", k[KEY]["v"] == 279, k[KEY])

# Line edges, from the shipped limit.
line = RANGE["classes"]["distressed"]["at_least"]
check("sane under the line, distressed on it", OW.base_class(RANGE, line - 1) == "sane" and OW.base_class(RANGE, line) == "distressed")
start_line = json.loads((HERE / "scratch_reap_sanity.json").read_text())["start"]["rm_scratch_clones"]
check("the distressed line stays one past the cleaner's start line", line == start_line + 1, (line, start_line))

# Every way of not seeing: UNMEASURED and alarmed, never sane. A stale record at a SANE value is the case that matters.
for name, body, says in (("stale_sane", rec(3, age_min=MAX_MIN + 5), "frozen"), ("stale_fault", rec(279, age_min=MAX_MIN + 5), "frozen"),
                         ("missing", None, "missing or torn"), ("torn", '{"start": {"at"', "missing or torn"),
                         ("empty", {}, "missing or torn"), ("not_object", [1], "missing or torn"),
                         ("future", rec(3, age_min=-30), "ahead of the clock"),
                         ("blind_run", rec(None, problems=["sanity end blind: OSError: x"]), "no rm_scratch_clones"),
                         ("null_count", rec(3) | {"end": {"at": time.time(), "measures": {"rm_scratch_clones": None}}}, "no rm_scratch_clones"),
                         ("bool_count", rec(3) | {"end": {"at": time.time(), "measures": {"rm_scratch_clones": True}}}, "no rm_scratch_clones"),
                         ("neg_count", rec(-1), "no rm_scratch_clones"), ("list_measures", rec(3) | {"end": {"at": time.time(), "measures": [3]}}, "no rm_scratch_clones")):
    k, al, md, _ = cli_pass(name, body)
    check("%s: reads UNMEASURED, not sane" % name, k[KEY]["m"] == "UNMEASURED" and k[KEY].get("class") is None
          and says in (k[KEY].get("why") or ""), k[KEY])
    check("%s: the blind alarm stands" % name, k[BLIND]["v"] == 1 and k[BLIND]["class"] == "distressed" and alarm(al, BLIND), al)
    check("%s: no false count alarm" % name, not alarm(al, HOT), al)

# Age inside the limit is not stale: one missed hourly run stays quiet.
k, _, _, _ = cli_pass("one_miss", rec(3, age_min=MAX_MIN - 25))
check("one missed reaper hour is not an alarm", k[KEY]["class"] == "sane" and k[BLIND]["v"] == 0, k[KEY])

# A range taken out of the rules: a limit that is missing reads blind.
cut = json.loads(json.dumps(RULES))
del cut["ranges"][KEY]
p = OW.scratch_outside(plant("no_range", rec(279)) / "sanity.json", time.time(), cut)
check("no range reads blind, never sane", p[KEY]["m"] == "UNMEASURED" and p[BLIND]["v"] == 1, p)

# The collector taken out of the pass: the keys go UNMEASURED and the blind alarm is written by run() itself.
d = plant("suppressed", rec(3))
os.environ.update(ENV, RM_SCRATCH_REAP_RUNS=str(d / "runs.jsonl"), RM_OPS_WATCH_DIR=str(d / "ops"))
OW.run(filer=None, families=["disk"])
real, OW.COLLECTORS["disk"] = OW.COLLECTORS["disk"], lambda now, rules, ctx: 1 / 0
try:
    dg = OW.run(filer=None, families=["disk"])
finally:
    OW.COLLECTORS["disk"] = real
k = dg["kpis"]
check("a raising collector: the blind reading alarms, no reading is sane", k[BLIND]["v"] == 1 and k[BLIND]["class"] == "distressed"
      and k[KEY]["m"] == "UNMEASURED", (k.get(BLIND), k.get(KEY)))
check("a raising collector: the alarm stands on that pass", alarm(dg["alarms"], BLIND), dg["alarms"])

print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)

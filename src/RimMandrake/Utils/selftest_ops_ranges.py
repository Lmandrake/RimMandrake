#!/usr/bin/env python3
"""selftest_ops_ranges: ALARM_RANGES_BUILD_CLASSES_AS_DATA (OP1, the ranges block of ops_watch_rules.json).

Everything runs on the real path under the shipped rules file: `ops_watch.py lint` as a process, load_rules on a file,
and ops_watch.run over store files laid down as the Dispatcher leaves them (the relentless metrics, its first example, went
with c_relentless on 2026-11-18). The fixture values come
from the shipped block, so every class it fills is exercised, including one added later.
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_ops_ranges_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
import ops_watch as OW  # noqa: E402

RULES_FILE = HERE / "ops_watch_rules.json"
RULES = json.loads(RULES_FILE.read_text(encoding="utf-8"))
for tg in RULES["targets"]:     # never the real Conductor log
    if tg.get("conductor_log"):
        tg["conductor_log"] = str(TMP / "conductor.md")
for k in OW.ORDER:              # the family the block judges here, and the real pass around it
    if k != "seats":
        OW.COLLECTORS[k] = lambda now, rules, ctx: {}
DISP = TMP / "disp"
T0 = 1793500000.0
FAILS = []
RAN = 0


def check(name, ok, detail=None):
    global RAN
    RAN += 1
    print("%s %s" % ("ok  " if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)
        print("     ", str(detail)[:600])


def lint(rules_obj):
    p = TMP / "lint_rules.json"
    p.write_text(json.dumps(rules_obj), encoding="utf-8")
    r = subprocess.run([sys.executable, str(HERE / "ops_watch.py"), "lint", "--rules", str(p)], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def world(idle=0, paused=False, drop=(), tick=0.0):
    """Lay down the Dispatcher's store for one instant, T0: `idle` is the minutes the seat sat idle with work, `tick` how
    long ago the last good tick was; files named in `drop` are left missing."""
    shutil.rmtree(DISP, ignore_errors=True)
    DISP.mkdir(parents=True)
    ring = {"at": OW.iso(T0 - 60), "do": "ring", "seat": "FOUNDRY", "ring_id": "R", "idle_since": T0 - idle * 60}
    skip = {"at": OW.iso(T0 - 30), "do": "skip", "why": "PAUSE file present"}
    (DISP / "journal.jsonl").write_text(json.dumps(ring) + "\n" + (json.dumps(skip) + "\n" if paused else ""), encoding="utf-8")
    seat = {"ring": {"ring_id": "R"}, "idle_since": T0 - idle * 60} if idle else {}
    if "state.json" not in drop:
        (DISP / "state.json").write_text(json.dumps({"last_ok_tick": OW.iso(T0 - tick), "seats": {"FOUNDRY": seat}}), encoding="utf-8")


def passed(rules=None, **kw):
    world(**kw)
    return OW.run(now=T0, rules=rules or RULES, filer=lambda todo, conf: None)


# ---------------------------------------------------------------- lint
rc, out = lint(RULES)
check("the shipped block is clean, and it has metrics (the instrument can see)", rc == 0 and len(OW.ranges_of(RULES)) >= 12, out)
for key in sorted(OW.ranges_of(RULES)):
    bad = copy.deepcopy(RULES)
    del bad["ranges"][key]["owner"]
    rc, out = lint(bad)
    check("lint refuses %s with no owner" % key, rc == 1 and "%s has no owner" % key in out, (rc, out))
for name, edit, says in (
        ("a blank owner", lambda m: m.update(owner="  "), "has no owner"),
        ("no why", lambda m: m.pop("why"), "names no why"),
        ("no max_age_min", lambda m: m.pop("max_age_min"), "has no max_age_min"),
        ("no ack_within_min on a metric that can distress", lambda m: m.pop("ack_within_min"), "no ack_within_min"),
        ("an unknown class", lambda m: m["classes"].update(broken={"at_least": 9}), "unknown classes"),
        ("no class", lambda m: m.update(classes={}), "fills no class"),
        ("a lowest class above 0", lambda m: m["classes"].pop("sane"), "not 0"),
        ("two classes on one bound", lambda m: m["classes"]["emergency"].update(at_least=30), "differ")):
    bad = copy.deepcopy(RULES)
    edit(bad["ranges"]["seats.idle_with_work_min"])
    rc, out = lint(bad)
    check("lint refuses " + name, rc == 1 and says in out, (rc, out))
bad = copy.deepcopy(RULES)
bad["ranges"]["seats.idle_with_work_min"]["idle_if"] = ["seats.no_such"]
check("lint refuses an idle_if naming nothing", lint(bad)[0] == 1)
bad = copy.deepcopy(RULES)
del bad["ranges"]
check("lint refuses a file with no ranges block", lint(bad)[0] == 1)

# the planted fault on the real load path: the timer reads the file, refuses it, keeps the last good, and says so
os.environ["RM_OPS_WATCH_RULES"] = str(TMP / "planted.json")
planted = json.loads(RULES_FILE.read_text(encoding="utf-8"))
Path(os.environ["RM_OPS_WATCH_RULES"]).write_text(json.dumps(planted), encoding="utf-8")
good = OW.load_rules()
check("load_rules takes the shipped file", "_load_error" not in good and "ranges" in good)
del planted["ranges"]["seats.idle_with_work_min"]["owner"]
Path(os.environ["RM_OPS_WATCH_RULES"]).write_text(json.dumps(planted), encoding="utf-8")
loaded = OW.load_rules()
check("load_rules refuses the file with an unowned metric, last good in use", "seats.idle_with_work_min has no owner" in
      str(loaded.get("_load_error")) and loaded["ranges"]["seats.idle_with_work_min"].get("owner") == "Operations", loaded.get("_load_error"))
dg = passed(rules={**RULES, "_load_error": loaded["_load_error"]})
check("the pass says so aloud", any(f["rule"] == "bad_rule" and f["key"] == "rules.file" for f in dg["flags"]), dg["flags"])
del os.environ["RM_OPS_WATCH_RULES"]

# ---------------------------------------------------------------- a fixture value in each filled class
FIELD = {"seats.idle_with_work_min": "idle"}
filled = 0
for key, field in sorted(FIELD.items()):
    for cls, spec in RULES["ranges"][key]["classes"].items():
        at = spec["at_least"]
        dg = passed(**{field: at})
        got = dg["kpis"][key]
        check("%s at %g reports %s" % (key, at, cls), got.get("class") == cls and got["v"] == at, got)
        fam = key.split(".")[0]
        check("  and %s.distressed agrees" % fam, dg["kpis"][fam + ".distressed"]["v"] == int(cls in OW.ALARMED), dg["kpis"][fam + ".distressed"])
        check("  owner and clocks travel with it", got.get("owner") == "Operations" and got.get("max_age_min") == RULES["ranges"][key]["max_age_min"]
              and got.get("ack_within_min") == RULES["ranges"][key].get("ack_within_min"), got)
        filled += 1
        if at:      # just under this class's line is the class below it
            below = max((s["at_least"], c) for c, s in RULES["ranges"][key]["classes"].items() if s["at_least"] < at)
            got = passed(**{field: at - 1})["kpis"][key]
            check("%s at %g reports %s" % (key, at - 1, below[1]), got.get("class") == below[1], got)
check("seats.tick_age_s reports sane", passed()["kpis"]["seats.tick_age_s"].get("class") == "sane")
check("seats.paused 0 reports sane", passed()["kpis"]["seats.paused"].get("class") == "sane")
check("seats.paused 1 reports idle", passed(paused=True)["kpis"]["seats.paused"].get("class") == "idle")
filled += 3
for fam, drop in (("seats", "state.json"),):
    check("%s.blind 0 reports sane" % fam, passed()["kpis"][fam + ".blind"].get("class") == "sane")
    got = passed(drop=(drop,))["kpis"][fam + ".blind"]
    check("%s.blind 1 reports distressed" % fam, got["v"] == 1 and got.get("class") == "distressed", got)
    limit = RULES["ranges"][fam + ".blind"]["classes"]["distressed"]["at_least"]
    tg = [t for t in RULES["targets"] if t["key"] == fam + ".blind"][0]
    check("%s.blind's distressed line is its target's" % fam, tg["op"] == ">" and tg["value"] + 1 == limit, tg)
    filled += 2
# plan.* takes its fixtures from src/RimMandrake/rimflow/selftest_priority_list.py, on a data clone this rig has not got;
# roles.* from selftest_role_use.py, on a fixture ledger; queues.* from selftest_ops_watch_queues.py; disk.scratch_outside_* from selftest_ops_watch_scratch_outside.py;
# disk.root_fall_* from selftest_ops_watch_root_grower.py (planted disk_grower captures this rig does not stage)
every = sum(len(m["classes"]) for k, m in OW.ranges_of(RULES).items() if not k.startswith(("plan.", "roles.", "queues.", "disk.scratch_outside", "disk.root_fall")))
check("every filled class of every metric had its fixture", filled == every, (filled, every))

# idle_if: the class a stop gives, on the metrics that name it
dg = passed(idle=500, paused=True)
check("a PAUSE file reads idle however long the seat sat", dg["kpis"]["seats.idle_with_work_min"].get("class") == "idle"
      and dg["kpis"]["seats.distressed"]["v"] == 0, dg["kpis"]["seats.idle_with_work_min"])

# unseen is never sane: no class on an UNMEASURED reading, and its gate unseen leaves it unjudged
dg = passed(drop=("state.json",))
check("an UNMEASURED reading has no class", dg["kpis"]["seats.idle_with_work_min"]["m"] == "UNMEASURED"
      and dg["kpis"]["seats.idle_with_work_min"].get("class") is None and dg["kpis"]["seats.blind"]["v"] >= 1, dg["kpis"]["seats.idle_with_work_min"])
ms = OW.ranges_of(RULES)
check("a gate unseen leaves the metric unjudged", OW.read_class(ms, "seats.idle_with_work_min", {
    "seats.idle_with_work_min": OW.M(5), "seats.paused": OW.U("gone")}) is None)

# ---------------------------------------------------------------- the block is the only source
r = copy.deepcopy(RULES)
r["ranges"]["seats.idle_with_work_min"]["classes"]["distressed"]["at_least"] = 20
check("the shipped line leaves a seat 25 min idle sane", passed(idle=25)["kpis"]["seats.distressed"]["v"] == 0)
check("moving the line in the block alone moves the seat's verdict", passed(rules=r, idle=25)["kpis"]["seats.distressed"]["v"] == 1)
r = copy.deepcopy(RULES)
r["ranges"]["seats.tick_age_s"]["max_age_min"] = 0.5
world(tick=60)
pts = OW.c_seats(T0, r, {})
check("max_age_min in the block alone freezes a source", pts["seats.blind"]["v"] >= 1, pts["seats.blind"])
pts = OW.c_seats(T0, RULES, {})
check("  and the shipped age does not", pts["seats.blind"]["v"] == 0, pts["seats.blind"])
check("no limit is left in the old block", not {"max_age_min", "distressed_min"} & set(RULES["seats"]))
for fam, fn in (("seats", OW.c_seats),):
    world(idle=500)
    for k in list(OW.ranges_of(RULES)):
        if k.startswith(fam + "."):
            r = copy.deepcopy(RULES)
            del r["ranges"][k]
            pts = fn(T0, r, {})
            check("%s out of the block: blind, never sane" % k, pts[fam + ".blind"]["v"] == 1 and pts[fam + ".distressed"]["m"] == "UNMEASURED", pts[fam + ".blind"])
r = copy.deepcopy(RULES)
del r["ranges"]
world()
check("no ranges block at all: blind", OW.c_seats(T0, r, {})["seats.blind"]["v"] == 1)

# a reading the block did not foresee is flagged; a range matching no reading too; the digests show the class
r = copy.deepcopy(RULES)
r["ranges"]["seats.paused"]["classes"] = {"sane": {"at_least": 0}}
world()
pts = {"seats.paused": OW.M(-1)}
check("a value outside every class is named", OW.stamp_ranges(pts, r) == ["seats.paused"] and pts["seats.paused"]["class"] is None)
r = copy.deepcopy(RULES)
r["ranges"]["seats.nothing"] = copy.deepcopy(r["ranges"]["seats.blind"])
check("a range no collector reports is flagged", any(f["key"] == "rules.range.seats.nothing" for f in passed(rules=r)["flags"]))
passed(idle=RULES["ranges"]["seats.idle_with_work_min"]["classes"]["emergency"]["at_least"])
full = (TMP / "ops" / "digest.md").read_text(encoding="utf-8")
blind = (TMP / "ops" / "digest_blind.md").read_text(encoding="utf-8")
check("the digest shows the class", any(ln.startswith("idle_with_work_min |") and "| emergency |" in ln for ln in full.splitlines()), full[:400])
check("the blind digest shows it", any(ln.startswith("idle_with_work_min |") and "| emergency |" in ln for ln in blind.splitlines()), blind[:400])
series = [json.loads(ln) for ln in (TMP / "ops" / "series" / "seats.jsonl").read_text(encoding="utf-8").splitlines()]
check("the series keeps the class", series[-1]["points"]["seats.idle_with_work_min"].get("class") == "emergency")

shutil.rmtree(TMP, ignore_errors=True)
print("selftest_ops_ranges: %d checks, %d failed" % (RAN, len(FAILS)))
sys.exit(1 if FAILS else 0)

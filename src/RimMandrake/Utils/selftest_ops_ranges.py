#!/usr/bin/env python3
"""selftest_ops_ranges: ALARM_RANGES_BUILD_CLASSES_AS_DATA (OP1, the ranges block of ops_watch_rules.json).

Everything runs on the real path under the shipped rules file: `ops_watch.py lint` as a process, load_rules on a file,
and ops_watch.run over store files laid down as relentless.tick and the Dispatcher leave them. The fixture values come
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
os.environ["RELENTLESS_ROOT"] = str(TMP / "belt")
import ops_watch as OW  # noqa: E402

RULES_FILE = HERE / "ops_watch_rules.json"
RULES = json.loads(RULES_FILE.read_text(encoding="utf-8"))
for tg in RULES["targets"]:     # never the real Conductor log
    if tg.get("conductor_log"):
        tg["conductor_log"] = str(TMP / "conductor.md")
for k in OW.ORDER:              # the two families the block judges, and the real pass around them
    if k not in ("relentless", "seats"):
        OW.COLLECTORS[k] = lambda now, rules, ctx: {}
STORE = TMP / "belt" / "store"
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


def world(under=0, ready=3, why="filling", breaker=0, nolive=0, progress=0.0, idle=0, paused=False, drop=()):
    """Lay down the two stores for one instant, T0: `under`, `breaker`, `nolive`, `progress`, `idle` are the minutes
    each reading should come to; files named in `drop` are left missing."""
    for d in (STORE, DISP):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    run = max(breaker, nolive, 1)
    rows = []
    for m in range(int(run * 60), -1, -60):        # a staffing row a minute, up to T0
        t = T0 - m
        rows.append({"t": t, "at": OW.iso(t), "running": 0 if nolive and m / 60.0 <= nolive else 2, "target": 4,
                     "places": 2, "ready": ready, "under": bool(under), "minutes_under": under,
                     "live": 0 if nolive and m / 60.0 <= nolive else 2,
                     "why": "breaker open until x" if breaker and m / 60.0 <= breaker else why, "checks": {"waiting": 0}})
    if len(rows) == 1 or nolive == 0:
        rows[-1]["live"] = 2
    files = {"staffing.json": json.dumps(rows[-1]), "staffing.jsonl": "".join(json.dumps(r) + "\n" for r in rows),
             "reading.json": json.dumps({"at": OW.iso(T0)}),
             "breaker.json": json.dumps({"until": T0 + 600, "fails": 3, "why": "planted"} if breaker else {}),
             "journal.jsonl": json.dumps({"at": OW.iso(T0 - progress * 60), "do": "done"}) + "\n"}
    for name, text in files.items():
        if name not in drop:
            (STORE / name).write_text(text, encoding="utf-8")
    ring = {"at": OW.iso(T0 - 60), "do": "ring", "seat": "FOUNDRY", "ring_id": "R", "idle_since": T0 - idle * 60}
    skip = {"at": OW.iso(T0 - 30), "do": "skip", "why": "PAUSE file present"}
    (DISP / "journal.jsonl").write_text(json.dumps(ring) + "\n" + (json.dumps(skip) + "\n" if paused else ""), encoding="utf-8")
    seat = {"ring": {"ring_id": "R"}, "idle_since": T0 - idle * 60} if idle else {}
    if "state.json" not in drop:
        (DISP / "state.json").write_text(json.dumps({"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": seat}}), encoding="utf-8")


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
    edit(bad["ranges"]["relentless.under_min"])
    rc, out = lint(bad)
    check("lint refuses " + name, rc == 1 and says in out, (rc, out))
bad = copy.deepcopy(RULES)
bad["ranges"]["relentless.under_min"]["idle_if"] = ["relentless.no_such"]
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
FIELD = {"relentless.under_min": "under", "relentless.breaker_open_min": "breaker", "relentless.no_live_min": "nolive",
         "relentless.progress_age_min": "progress", "seats.idle_with_work_min": "idle"}
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
for w in RULES["ranges"]["relentless.why"]["classes"]["idle"]["in"]:
    check("relentless.why %r reports idle" % w, passed(why=w)["kpis"]["relentless.why"].get("class") == "idle")
    filled += 1
check("relentless.why filling reports sane", passed()["kpis"]["relentless.why"].get("class") == "sane")
check("relentless.ready 0 reports idle", passed(ready=0)["kpis"]["relentless.ready"].get("class") == "idle")
check("relentless.ready 3 reports sane", passed()["kpis"]["relentless.ready"].get("class") == "sane")
check("relentless.tick_age_s reports sane", passed()["kpis"]["relentless.tick_age_s"].get("class") == "sane")
check("seats.tick_age_s reports sane", passed()["kpis"]["seats.tick_age_s"].get("class") == "sane")
check("seats.paused 0 reports sane", passed()["kpis"]["seats.paused"].get("class") == "sane")
check("seats.paused 1 reports idle", passed(paused=True)["kpis"]["seats.paused"].get("class") == "idle")
filled += 7
for fam, drop in (("relentless", "staffing.jsonl"), ("seats", "state.json")):
    check("%s.blind 0 reports sane" % fam, passed()["kpis"][fam + ".blind"].get("class") == "sane")
    got = passed(drop=(drop,))["kpis"][fam + ".blind"]
    check("%s.blind 1 reports distressed" % fam, got["v"] == 1 and got.get("class") == "distressed", got)
    limit = RULES["ranges"][fam + ".blind"]["classes"]["distressed"]["at_least"]
    tg = [t for t in RULES["targets"] if t["key"] == fam + ".blind"][0]
    check("%s.blind's distressed line is its target's" % fam, tg["op"] == ">" and tg["value"] + 1 == limit, tg)
    filled += 2
# plan.* takes its fixtures from src/RimMandrake/rimflow/selftest_priority_list.py, on a data clone this rig has not got
every = sum(len(m["classes"]) for k, m in OW.ranges_of(RULES).items() if not k.startswith("plan.")) + len(RULES["ranges"]["relentless.why"]["classes"]["idle"]["in"]) - 1
check("every filled class of every metric had its fixture", filled == every, (filled, every))

# idle_if: the class a stop gives, on the metrics that name it
dg = passed(under=500, why="paused")
check("a chosen stop reads idle on the metrics that name it, whatever their minutes",
      dg["kpis"]["relentless.under_min"].get("class") == "idle" and dg["kpis"]["relentless.distressed"]["v"] == 0, dg["kpis"]["relentless.under_min"])
dg = passed(progress=500, nolive=100, ready=0)
check("nothing ready: a silent belt is idle, not late", dg["kpis"]["relentless.progress_age_min"].get("class") == "idle"
      and dg["kpis"]["relentless.no_live_min"].get("class") == "idle" and dg["kpis"]["relentless.distressed"]["v"] == 0)
dg = passed(idle=500, paused=True)
check("a PAUSE file reads idle however long the seat sat", dg["kpis"]["seats.idle_with_work_min"].get("class") == "idle"
      and dg["kpis"]["seats.distressed"]["v"] == 0, dg["kpis"]["seats.idle_with_work_min"])

# emergency outranks whichever metric comes first; the cause names the worst
dg = passed(under=30, breaker=121)
st = OW.read_json(TMP / "ops" / "status.json")["points"]["relentless.distressed"]["x"]
check("the worst class names the cause", st["state"] == "emergency" and st["cause"].startswith("breaker open"), st)

# unseen is never sane: no class on an UNMEASURED reading, and its gate unseen leaves it unjudged
dg = passed(drop=("staffing.json",))
check("an UNMEASURED reading has no class", dg["kpis"]["relentless.under_min"]["m"] == "UNMEASURED" and dg["kpis"]["relentless.under_min"].get("class") is None
      and dg["kpis"]["relentless.blind"]["v"] >= 1, dg["kpis"]["relentless.under_min"])
ms = OW.ranges_of(RULES)
check("a gate unseen leaves the metric unjudged", OW.read_class(ms, "relentless.under_min", {
    "relentless.under_min": OW.M(5), "relentless.why": OW.U("gone")}) is None)

# ---------------------------------------------------------------- the block is the only source
r = copy.deepcopy(RULES)
r["ranges"]["relentless.under_min"]["classes"]["distressed"]["at_least"] = 20
check("the shipped line leaves 25 min under sane", passed(under=25)["kpis"]["relentless.distressed"]["v"] == 0)
check("moving the line in the block alone moves the belt's verdict", passed(rules=r, under=25)["kpis"]["relentless.distressed"]["v"] == 1)
r = copy.deepcopy(RULES)
r["ranges"]["seats.idle_with_work_min"]["classes"]["distressed"]["at_least"] = 20
check("the shipped line leaves a seat 25 min idle sane", passed(idle=25)["kpis"]["seats.distressed"]["v"] == 0)
check("moving the line in the block alone moves the seat's verdict", passed(rules=r, idle=25)["kpis"]["seats.distressed"]["v"] == 1)
r = copy.deepcopy(RULES)
r["ranges"]["relentless.why"]["classes"]["idle"]["in"].append("filling")
check("a stop named in the block alone reads idle", passed(rules=r, under=500)["kpis"]["relentless.distressed"]["v"] == 0)
r = copy.deepcopy(RULES)
r["ranges"]["relentless.tick_age_s"]["max_age_min"] = 0.5
world()
(STORE / "staffing.json").write_text(json.dumps({**json.loads((STORE / "staffing.json").read_text()), "t": T0 - 60}), encoding="utf-8")
pts = OW.c_relentless(T0, r, {})
check("max_age_min in the block alone freezes a source", pts["relentless.blind"]["v"] >= 1 and pts["relentless.under_min"]["m"] == "UNMEASURED", pts["relentless.blind"])
pts = OW.c_relentless(T0, RULES, {})
check("  and the shipped age does not", pts["relentless.under_min"]["m"] == "MEASURED", pts["relentless.under_min"])
check("no limit is left in the old blocks", not {"max_age_min", "under_min", "breaker_open_min", "no_live_min", "progress_min", "idle_why"} & set(RULES["relentless"])
      and not {"max_age_min", "distressed_min"} & set(RULES["seats"]))
for fam, fn in (("relentless", OW.c_relentless), ("seats", OW.c_seats)):
    world(under=500, idle=500)
    for k in list(OW.ranges_of(RULES)):
        if k.startswith(fam + "."):
            r = copy.deepcopy(RULES)
            del r["ranges"][k]
            pts = fn(T0, r, {})
            check("%s out of the block: blind, never sane" % k, pts[fam + ".blind"]["v"] == 1 and pts[fam + ".distressed"]["m"] == "UNMEASURED", pts[fam + ".blind"])
r = copy.deepcopy(RULES)
del r["ranges"]
world()
check("no ranges block at all: blind", OW.c_relentless(T0, r, {})["relentless.blind"]["v"] == 1 and OW.c_seats(T0, r, {})["seats.blind"]["v"] == 1)

# a reading the block did not foresee is flagged; a range matching no reading too; the digests show the class
r = copy.deepcopy(RULES)
r["ranges"]["relentless.ready"]["classes"] = {"sane": {"at_least": 0}}
world()
pts = {"relentless.ready": OW.M(-1)}
check("a value outside every class is named", OW.stamp_ranges(pts, r) == ["relentless.ready"] and pts["relentless.ready"]["class"] is None)
r = copy.deepcopy(RULES)
r["ranges"]["relentless.nothing"] = copy.deepcopy(r["ranges"]["relentless.blind"])
check("a range no collector reports is flagged", any(f["key"] == "rules.range.relentless.nothing" for f in passed(rules=r)["flags"]))
passed(under=RULES["ranges"]["relentless.under_min"]["classes"]["emergency"]["at_least"])
full = (TMP / "ops" / "digest.md").read_text(encoding="utf-8")
blind = (TMP / "ops" / "digest_blind.md").read_text(encoding="utf-8")
check("the digest shows the class", any(ln.startswith("under_min |") and "| emergency |" in ln for ln in full.splitlines()), full[:400])
check("the blind digest shows it", any(ln.startswith("under_min |") and "| emergency |" in ln for ln in blind.splitlines()), blind[:400])
series = [json.loads(ln) for ln in (TMP / "ops" / "series" / "relentless.jsonl").read_text(encoding="utf-8").splitlines()]
check("the series keeps the class", series[-1]["points"]["relentless.under_min"].get("class") == "emergency")

shutil.rmtree(TMP, ignore_errors=True)
print("selftest_ops_ranges: %d checks, %d failed" % (RAN, len(FAILS)))
sys.exit(1 if FAILS else 0)

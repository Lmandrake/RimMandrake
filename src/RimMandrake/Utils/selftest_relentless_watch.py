#!/usr/bin/env python3
"""selftest_relentless_watch: JAM_WATCH_BUILD_RELENTLESS_IN_OPS_DIGEST (OP2, DI2).

Everything runs on the real path: rows are written as the real files of a throwaway relentless store, and read by
ops_watch.c_relentless and ops_watch.run under the shipped ops_watch_rules.json. testdata/relentless_jam_2026-11-01.jsonl
is the real record, cut from the store's staffing.jsonl and journal.jsonl (03:30 to 13:20Z).
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_relentless_watch_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RELENTLESS_ROOT"] = str(TMP / "belt")
import ops_watch as OW  # noqa: E402

FAILS = []
STORE = TMP / "belt" / "store"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
for tg in RULES["targets"]:     # never the real Conductor log
    if tg.get("conductor_log"):
        tg["conductor_log"] = str(TMP / "conductor.md")
RECORD = [json.loads(ln) for ln in (HERE / "testdata/relentless_jam_2026-11-01.jsonl").read_text(encoding="utf-8").splitlines()]
for k in OW.ORDER:              # one family's collector and the real pass around it
    if k != "relentless":
        OW.COLLECTORS[k] = lambda now, rules, ctx: {}
FILED = []


def filer(todo, conf):
    FILED.extend(todo)
    return {a["name"]: None for a in todo}


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def fresh():
    """An empty belt and an empty ops_watch directory."""
    shutil.rmtree(TMP / "belt", ignore_errors=True)
    shutil.rmtree(TMP / "ops", ignore_errors=True)
    STORE.mkdir(parents=True)
    (STORE / "journal.jsonl").write_text("")
    (STORE / "staffing.jsonl").write_text("")
    FILED.clear()


def put(name, obj):
    (STORE / name).write_text(json.dumps(obj))


def add(name, obj):
    with open(STORE / name, "a") as f:
        f.write(json.dumps(obj) + "\n")


def tick(row):
    """What relentless.tick leaves on disk for one staffing row. The record's `why` holds the breaker's until."""
    put("staffing.json", row)
    add("staffing.jsonl", row)
    put("reading.json", {"at": row["at"]})
    why = str(row.get("why") or "")
    put("breaker.json", breaker_of(why))


def breaker_of(why):
    if not why.startswith("breaker open until "):
        return {}
    return {"until": OW.epoch(why[len("breaker open until "):].split(": ")[0]), "fails": 3, "why": "POOL REFUSED: pool full"}


def replay():
    """Yield (row, points) at every tick of the record, journal lines laid down in order."""
    for r in RECORD:
        if r["kind"] == "journal":
            add("journal.jsonl", {"at": r["at"], "do": r["do"]})
            continue
        row = {k: v for k, v in r.items() if k != "kind"}
        tick(row)
        yield row, OW.c_relentless(row["t"], RULES, {})


def sane_row(t):
    return {"at": OW.iso(t), "t": t, "live": 3, "running": 3, "places": 3, "target": 3, "ready": 400, "minutes_under": 0,
            "under": False, "why": None, "checks": {"waiting": 0, "running": 1, "oldest_wait_s": 0}}


# ------------------------------------------------------------------------- the 2026-11-01 04:00-13:00Z staffing record
fresh()
seen = [(row, pts) for row, pts in replay()]
win = [(row, pts) for row, pts in seen if "2026-11-01T04:00" <= row["at"] < "2026-11-01T13:00"]
check("the fixture holds the record, not a sample", len(win) > 150 and win[0][0]["at"] < "2026-11-01T04:03", len(win))
record_minute = next(row["at"] for row, _ in win if row["alarmed"])
first = next((row["at"], pts) for row, pts in win if pts["relentless.distressed"]["v"] == 1)
check("the record's own alarm minute is 06:59Z", record_minute.startswith("2026-11-01T06:59"), record_minute)
check("distressed at the minute the record says", first[0] == record_minute, first[0])
check("it names the cause: the breaker", "breaker open until 2026-11-01T07:16:10Z" in first[1]["relentless.cause"]["v"]
      and "383 ready" in first[1]["relentless.cause"]["v"], first[1]["relentless.cause"])
check("sane before it, through both short fills (05:33, 06:16)", all(
    pts["relentless.distressed"]["v"] == 0 for row, pts in win if row["at"] < record_minute))
check("distressed unbroken from there to 13:00", all(
    pts["relentless.distressed"]["v"] == 1 for row, pts in win if row["at"] >= record_minute))
end = win[-1][1]
check("the jam's breaker reads hours open", end["relentless.breaker_open_min"]["v"] > 360, end["relentless.breaker_open_min"])
check("each reading is measured from the record", (end["relentless.live"]["v"], end["relentless.ready"]["v"],
      end["relentless.checks_wait"]["v"]) == (win[-1][0]["live"], win[-1][0]["ready"], win[-1][0]["checks"]["waiting"]), end)
back = next(pts for row, pts in seen if row["at"] >= "2026-11-01T13:16")
check("recovered once the record does", back["relentless.distressed"]["v"] == 0, back["relentless.cause"])
check("blind never rose on a whole record", all(pts["relentless.blind"]["v"] == 0 for _, pts in seen),
      next((pts["relentless.blind"] for _, pts in seen if pts["relentless.blind"]["v"]), None))
limits = json.loads((HERE.parent / "rimflow/relentless_rules.json").read_text(encoding="utf-8"))
check("the line is relentless's own alarm line", RULES["relentless"]["under_min"] == limits["staffing"]["alarm_after_min"])

# the same record through full passes at the timer's 15 min: the alarm, its item, the digests
fresh()
passes = []
nxt = None
for row, pts in replay():
    if nxt is None or row["t"] >= nxt:
        nxt = row["t"] + 900
        passes.append((row["at"], OW.run(now=row["t"], rules=RULES, filer=filer)))
    if row["at"] >= "2026-11-01T13:00":
        break
jam = [a for a in FILED if a["aid"] == "RELENTLESS_DISTRESS:relentless.distressed"]
check("one outage, one filing", len(jam) == 1, FILED)
check("the filing names the cause", jam and "breaker open until" in jam[0]["title"], jam)
check("the filing reaches the Conductor's log", (TMP / "conductor.md").exists() and "breaker open" in (TMP / "conductor.md").read_text())
at = next((a for a, dg in passes if "RELENTLESS_DISTRESS:relentless.distressed" in dg["alarms"]), None)
check("filed on the first pass after 06:59", at and "2026-11-01T06:59" <= at < "2026-11-01T07:15", at)
md, blind = (OW.ops_dir() / "digest.md").read_text(), (OW.ops_dir() / "digest_blind.md").read_text()
for name, text in (("digest", md), ("blind digest", blind)):
    check(name + " carries the family and the cause", "## relentless" in text and "breaker open" in text
          and all(k in text for k in ("live", "under_min", "breaker_open_min", "checks_wait", "ready", "tick_age_s")))
check("the headline says it", "relentless 0 live, 383 ready" in md.splitlines()[2], md.splitlines()[2])

# ---------------------------------------------------------------------------------------- a missing source
T0 = 1793600000.0
for gone in ("staffing.json", "reading.json", "breaker.json", "staffing.jsonl", "journal.jsonl"):
    fresh()
    add("journal.jsonl", {"at": OW.iso(T0 - 60), "do": "lease"})
    tick(sane_row(T0))
    check("sane with every source there (%s run)" % gone, OW.c_relentless(T0, RULES, {})["relentless.blind"]["v"] == 0)
    (STORE / gone).unlink()
    dg = OW.run(now=T0 + 60, rules=RULES, filer=filer)
    pts = OW.read_json(OW.ops_dir() / "status.json")["points"]
    check("missing %s alarms" % gone, "RELENTLESS_BLIND:relentless.blind" in dg["alarms"] and gone in FILED[-1]["title"],
          dg["alarms"])
    check("missing %s never reads sane" % gone, pts["relentless.distressed"]["v"] != 0 or gone != "staffing.json")
    if gone == "staffing.json":
        check("every staffing reading UNMEASURED", all(pts[k]["m"] == "UNMEASURED" for k in (
            OW.RL_STAFFING + ("relentless.tick_age_s", "relentless.distressed", "relentless.cause"))), pts)
    if gone == "breaker.json":
        check("the breaker reading UNMEASURED", pts["relentless.breaker_open_min"]["m"] == "UNMEASURED")
fresh()
(STORE / "staffing.json").write_text('{"t": 1793')
check("a torn staffing.json is blind", OW.c_relentless(T0, RULES, {})["relentless.blind"]["v"] >= 1)
put("staffing.json", {**sane_row(T0), "live": None})
pts = OW.c_relentless(T0, RULES, {})
check("a reading absent from a fresh file is not 0", pts["relentless.live"]["m"] == "UNMEASURED" and pts["relentless.blind"]["v"] >= 1, pts)
put("staffing.json", sane_row(T0 + 3600))
check("a stamp from the future is blind", OW.c_relentless(T0, RULES, {})["relentless.blind"]["v"] >= 1)
r = dict(RULES)
r.pop("relentless")
check("no rules block is blind", OW.c_relentless(T0, r, {})["relentless.blind"]["v"] == 1)


# ---------------------------------------------------------------------- frozen sane, timers firing: within two passes
def frozen(offset):
    """staffing.json stops `offset` s before the first pass at a sane value; the tick still writes reading.json."""
    fresh()
    add("journal.jsonl", {"at": OW.iso(T0 - 60), "do": "lease"})
    tick(sane_row(T0))
    out = []
    for i in range(2):
        now = T0 + offset + i * 900
        put("reading.json", {"at": OW.iso(now)})
        os.utime(STORE / "staffing.json", (now, now))       # a touched file is not a fresh reading
        dg = OW.run(now=now, rules=RULES, filer=filer)
        out.append("RELENTLESS_BLIND:relentless.blind" in dg["alarms"])
    return out


for off in (60, 300, 590):
    got = frozen(off)
    check("frozen %d s before the first pass alarms within two passes" % off, got[1], got)
    check("and says which source", any("staffing.json frozen" in a["title"] for a in FILED), FILED)

# the stamp moves, the belt does not: the progress reading
fresh()
add("journal.jsonl", {"at": OW.iso(T0), "do": "done"})
got = []
for i in range(5):
    now = T0 + (i + 1) * 900
    tick(sane_row(now))
    got.append(OW.run(now=now, rules=RULES, filer=filer)["kpis"]["relentless.distressed"]["v"])
check("a stamp moving on a belt that does not alarms", got[0] == 0 and got[-1] == 1, got)
check("named as no progress", any("no progress" in a["title"] for a in FILED), FILED)
fresh()
add("journal.jsonl", {"at": OW.iso(T0), "do": "done"})
(STORE / "items" / "A").mkdir(parents=True)
put("items/A/state.json", {"status": "running", "last_beat": T0 + 3500})
tick(sane_row(T0 + 3600))
check("a beating worker is progress", OW.c_relentless(T0 + 3600, RULES, {})["relentless.distressed"]["v"] == 0)

# a stop somebody chose is idle, and all of it is not a jam
fresh()
add("journal.jsonl", {"at": OW.iso(T0), "do": "done"})
for w in RULES["relentless"]["idle_why"]:
    tick({**sane_row(T0 + 7200), "live": 0, "under": True, "minutes_under": 90, "why": w})
    pts = OW.c_relentless(T0 + 7200, RULES, {})
    check("%s reads idle" % w, pts["relentless.distressed"]["v"] == 0 and pts["relentless.distressed"]["x"]["state"] == "idle", pts)

# nothing live with places all held: `under` false, as the record's 13:13 row, and still a jam after no_live_min
fresh()
add("journal.jsonl", {"at": OW.iso(T0), "do": "done"})
for i in range(3):
    tick({**sane_row(T0 + i * 120), "live": 0, "running": 0})
pts = OW.c_relentless(T0 + 240, RULES, {})
check("under 5 min of nothing live is not yet a jam", pts["relentless.distressed"]["v"] == 0, pts)
tick({**sane_row(T0 + 360), "live": 0, "running": 0})
pts = OW.c_relentless(T0 + 360, RULES, {})
check("over it is, though `under` is false", pts["relentless.distressed"]["v"] == 1 and "nothing live" in pts["relentless.cause"]["v"], pts)


# ------------------------------------------------------------------------- collection suppressed, the timers still firing
def boom(now, rules, ctx):
    raise RuntimeError("collection suppressed")


real = OW.COLLECTORS["relentless"]
fresh()
add("journal.jsonl", {"at": OW.iso(T0 - 60), "do": "lease"})
tick(sane_row(T0))
OW.run(now=T0, rules=RULES, filer=filer)
check("a healthy pass files nothing", not FILED, FILED)
OW.COLLECTORS["relentless"] = boom
dg = OW.run(now=T0 + 900, rules=RULES, filer=filer)
check("a collector that raises alarms on that pass", "RELENTLESS_BLIND:relentless.blind" in dg["alarms"], dg["alarms"])
check("and says why", "collection suppressed" in FILED[-1]["title"], FILED)
OW.COLLECTORS["relentless"] = real
fresh()
tick(sane_row(T0))
OW.run(now=T0, rules=RULES, filer=filer)
order, OW.ORDER = OW.ORDER, tuple(k for k in OW.ORDER if k != "relentless")
dg = OW.run(now=T0 + 900, rules=RULES, filer=filer)
OW.ORDER = order
check("a collector dropped from the pass alarms too", "RELENTLESS_BLIND:relentless.blind" in dg["alarms"], dg["alarms"])

shutil.rmtree(TMP, ignore_errors=True)
print("selftest_relentless_watch: %s" % ("FAIL " + ", ".join(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)

#!/usr/bin/env python3
"""selftest_seats_watch: IDLE_WATCH_BUILD_SEAT_MINUTES_IN_DIGEST (OP2, seats.idle_with_work_min).

Everything runs on the real path. testdata/seats_idle_2026-10-31.jsonl is the real record, FOUNDRY's rows cut from the
Dispatcher's journal.jsonl (05:30 to 21:30Z), replayed through ops_watch.c_seats and ops_watch.run under the shipped
ops_watch_rules.json. The planted fault is the real dispatcher.tick against a window that ignores its rings: the
journal and state.json the watcher reads are the ones that program wrote, so a renamed field fails here.
"""
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
TMP = Path(tempfile.mkdtemp(prefix="selftest_seats_watch_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
import ops_watch as OW  # noqa: E402
import dispatcher as D  # noqa: E402

FAILS = []
ROOT = TMP / "disp"
RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
for tg in RULES["targets"]:     # never the real Conductor log
    if tg.get("conductor_log"):
        tg["conductor_log"] = str(TMP / "conductor.md")
RECORD = [json.loads(ln) for ln in (HERE / "testdata/seats_idle_2026-10-31.jsonl").read_text(encoding="utf-8").splitlines()]
for k in OW.ORDER:              # one family's collector and the real pass around it
    if k != "seats":
        OW.COLLECTORS[k] = lambda now, rules, ctx: {k2: OW.M(0) for k2 in ("relentless.blind", "plan.blind", "disk.scratch_outside_blind")}
FILED = []
ALARM = "SEAT_IDLE_WITH_WORK:seats.distressed"
BLIND = "SEATS_BLIND:seats.blind"


def filer(todo, conf):
    FILED.extend(todo)
    return {a["name"]: None for a in todo}


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  %s" % (detail,)))
    if not cond:
        FAILS.append(name)


def fresh():
    shutil.rmtree(ROOT, ignore_errors=True)
    shutil.rmtree(TMP / "ops", ignore_errors=True)
    ROOT.mkdir(parents=True)
    (ROOT / "journal.jsonl").write_text("")
    FILED.clear()


def put_state(st):
    (ROOT / "state.json").write_text(json.dumps(st))


def t_of(s):
    return OW.epoch(s)


def state_at(now, busy):
    """state.json as the Dispatcher held it at `now`, from the record: the fields one_seat keeps for a seat. `busy`: the
    seat was at work at `now`, which drops idle_since and keeps nh_streak; last_ok_tick is the last 2-min tick."""
    ss, streak = {}, 0
    for r in RECORD:
        if t_of(r["at"]) > now:
            break
        if r["do"] == "ring":
            ss = {"ring": {"ring_id": r["ring_id"]}, "idle_since": t_of(r["at"])}
        elif r["do"] == "woke_no_handoff":
            streak += 1
            ss = {"nh_streak": streak, "idle_since": ss.get("idle_since")}
        elif r["do"] == "verified":
            streak, ss = 0, {}
    if busy:
        ss.pop("idle_since", None)
    return {"last_ok_tick": OW.iso(now - 60), "seats": {"FOUNDRY": ss, "BENCH": {}}}


def replay_to(now, busy=False):
    fresh()
    (ROOT / "journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in RECORD if t_of(r["at"]) <= now))
    put_state(state_at(now, busy))
    return OW.c_seats(now, RULES, {})


# ------------------------------------------------------------------------- the real record, 2026-10-31
ALARM_AT = t_of("2026-10-31T14:55:49Z")
IDLE_FROM = next(r for r in RECORD if r["at"] == "2026-10-31T14:18:21Z")["idle_since"]
check("the record is the real one: the idle_full_queue row is in it",
      any(r["do"] == "alarm" and r["kind"] == "idle_full_queue:FOUNDRY" and r["at"] == "2026-10-31T14:55:49Z" for r in RECORD))
pts = replay_to(ALARM_AT)
check("at the 14:55Z idle_full_queue record the seat reads distressed", pts["seats.distressed"]["v"] == 1, pts)
check("and reads its minutes since the idle began at 14:14:17Z, not the 05:43 ring a busy spell cut off",
      abs(pts["seats.idle_with_work_min"]["v"] - 41.5) < 0.1, pts)
check("it names the seat", "FOUNDRY" in pts["seats.cause"]["v"], pts)
pts = replay_to(IDLE_FROM + 29.9 * 60)
check("at 29.9 min it is not yet distressed", pts["seats.distressed"]["v"] == 0 and pts["seats.idle_with_work_min"]["v"] == 29.9, pts)
pts = replay_to(IDLE_FROM + 30 * 60)
check("at 30 min it reads distressed", pts["seats.distressed"]["v"] == 1 and pts["seats.idle_with_work_min"]["v"] == 30.0, pts)
pts = replay_to(t_of("2026-10-31T10:00:00Z"), busy=True)
check("between the spells the seat was busy: nh_streak alone reads sane", pts["seats.idle_with_work_min"]["v"] == 0, pts)
pts = replay_to(t_of("2026-10-31T21:12:00Z"))
check("a verified hand-off ends it", pts["seats.distressed"]["v"] == 0 and pts["seats.idle_with_work_min"]["v"] == 0, pts)
dg = OW.run(now=t_of("2026-10-31T21:12:00Z"), rules=RULES, filer=filer)
check("a sane pass files nothing", not FILED and not dg["alarms"], (FILED, dg["alarms"]))
replay_to(ALARM_AT)
dg = OW.run(now=ALARM_AT, rules=RULES, filer=filer)
check("the real pass raises the alarm", ALARM in dg["alarms"], dg["alarms"])
check("filed once, its title naming seat and minutes", len(FILED) == 1 and "FOUNDRY idle 42 min" in FILED[0]["title"], FILED)
md = (TMP / "ops" / "digest.md").read_text()
blind = (TMP / "ops" / "digest_blind.md").read_text()
check("in the digest headline", "seats idle with work 41.5 min" in md and "FOUNDRY idle 42 min" in md, md[:900])
check("in the digest's KPI list", "seats.idle_with_work_min" in dg["kpis"], sorted(dg["kpis"]))
check("in the token-blind digest", "seats idle with work 41.5 min" in blind, blind[:900])


# ------------------------------------------------------------------------- the planted fault: the real dispatcher
def sched():
    p = TMP / "sched.json"
    p.write_text(json.dumps({"seats": {"FOUNDRY": {"enabled": True, "wake": True, "session_name": "AGENT FOUNDRY",
                                                   "clone": str(TMP), "model": "sonnet"}},
                             "roles": [], "alarm_item": "X_Y", "stall_after_s": 60, "handoff_s": 600, "ledger_notes": False, "publish": False,
                             "no_handoff": {"conductor_log": str(TMP / "conductor.md")}}))
    return D.load_schedule(str(p))


def window(status="idle", events=()):
    return {"paused": None, "agents": {"state": "MEASURED", "sessions": [
                {"name": "AGENT FOUNDRY", "status": status, "sessionId": "s1", "kind": "interactive", "pid": 1}]},
            "peek": lambda seat: {"id": "SOME_ITEM_DO_IT", "needs": "offline"},
            "events": lambda seat, since: [e for e in events if e.get("ts", "") >= since],
            "consumed": lambda seat, rid: {"consumed_at": 1.0},
            "armed": lambda seat: {"pid": 1}, "alive": lambda pid: True}


FX = {"note": lambda item, text: (True, "ok"), "publish": lambda n: "published", "conductor_log": lambda *a, **k: "logged"}
T0 = t_of("2026-11-01T00:00:00Z")
TICK = 120
fresh()
sch = sched()
crossed = None
now = T0
while now < T0 + 3000:
    D.tick(sch, True, obs=window(), now=now, fx=FX)
    pts = OW.c_seats(now, RULES, {})
    if crossed is None and pts["seats.distressed"].get("v") == 1:
        crossed = now
    now += TICK
rows = [json.loads(x) for x in (ROOT / "journal.jsonl").read_text().splitlines()]
check("planted: the real dispatcher rang a window that ignored it", sum(r["do"] == "woke_no_handoff" for r in rows) >= 2, [r["do"] for r in rows])
check("planted: the reading crosses at 30 min of real ticks, not before", crossed and 1800 <= crossed - T0 <= 1800 + 2 * TICK,
      crossed and crossed - T0)
dg = OW.run(now=now, rules=RULES, filer=filer)
check("planted: the real pass alarms", ALARM in dg["alarms"], dg["alarms"])

fresh()
sch = sched()
got = []
for i in range(30):                 # a live seat at work: rung, takes the item in a tick, works, rung again
    now = T0 + i * TICK
    ev = [{"event": "lease", "action": "take", "id": "SOME_ITEM_DO_IT", "ts": OW.iso(now)}]
    D.tick(sch, True, obs=window("idle" if i % 4 < 2 else "busy", ev), now=now, fx=FX)
    got.append(OW.c_seats(now, RULES, {}))
check("a live seat at work reads sane on every tick", all(p["seats.distressed"]["v"] == 0 and p["seats.blind"]["v"] == 0 for p in got), got[-1])
dos = [json.loads(x)["do"] for x in (ROOT / "journal.jsonl").read_text().splitlines()]
check("and its rings were real", "verified" in dos, dos)
dg = OW.run(now=now, rules=RULES, filer=filer)
check("a live seat at work alarms nothing", not dg["alarms"], dg["alarms"])

fresh()
sch = sched()
now = T0
while now < T0 + 1200:              # ignored its ring, then went to work with no lease
    D.tick(sch, True, obs=window(), now=now, fx=FX)
    now += TICK
while now < T0 + 4000:
    D.tick(sch, True, obs=window("busy"), now=now, fx=FX)
    now += TICK
pts = OW.c_seats(now, RULES, {})
check("a seat that went to work after an unanswered ring reads sane", pts["seats.idle_with_work_min"]["v"] == 0, pts)


fresh()
(ROOT / "journal.jsonl").write_text("".join(json.dumps(r) + "\n" for r in (
    {"at": OW.iso(T0 - 7200), "do": "ring", "seat": "FOUNDRY", "ring_id": "A", "idle_since": T0 - 7300},
    {"at": OW.iso(T0 - 3600), "do": "ring", "seat": "FOUNDRY", "ring_id": "B", "idle_since": T0 - 7200},
    {"at": OW.iso(T0 - 3500), "do": "verified", "seat": "FOUNDRY", "ring_id": "B"},
    {"at": OW.iso(T0 - 600), "do": "ring", "seat": "FOUNDRY", "ring_id": "C", "idle_since": T0 - 3600})))
put_state({"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"ring": {"ring_id": "C"}, "idle_since": T0 - 600}}})
pts = OW.c_seats(T0, RULES, {})
check("a hand-off cuts the run however the rings chain", pts["seats.idle_with_work_min"]["v"] == 60.0, pts)


# ------------------------------------------------------------------------- frozen, missing, torn: never sane
def sane_state(t):
    return {"last_ok_tick": OW.iso(t), "seats": {"FOUNDRY": {}}}


def frozen(offset):
    """state.json stops `offset` s before the first pass at a sane value, its file touched as if written."""
    fresh()
    put_state(sane_state(T0))
    out = []
    for i in range(2):
        t = T0 + offset + i * 900
        os.utime(ROOT / "state.json", (t, t))
        out.append(BLIND in OW.run(now=t, rules=RULES, filer=filer)["alarms"])
    return out


for off in (60, 300, 590):
    got = frozen(off)
    check("frozen %d s before the first pass alarms within two passes" % off, got[1], got)
    check("and says so", any("state.json frozen" in a["title"] for a in FILED), FILED)
fresh()
put_state(sane_state(T0))
pts = OW.c_seats(T0 + 3600, RULES, {})
check("a frozen sane reading is not a sane reading", pts["seats.idle_with_work_min"]["m"] == "UNMEASURED" and pts["seats.distressed"]["m"] == "UNMEASURED", pts)


def blind_when(name, plant):
    fresh()
    put_state(sane_state(T0))
    plant()
    pts = OW.c_seats(T0, RULES, {})
    check("%s: UNMEASURED and blind, never sane" % name,
          pts["seats.idle_with_work_min"]["m"] == "UNMEASURED" and pts["seats.blind"]["v"] == 1, pts)
    dg = OW.run(now=T0, rules=RULES, filer=filer)
    check("%s: alarms" % name, BLIND in dg["alarms"], dg["alarms"])


blind_when("state.json missing", lambda: (ROOT / "state.json").unlink())
blind_when("state.json torn", lambda: (ROOT / "state.json").write_text("{torn"))
blind_when("state.json dated ahead", lambda: put_state(sane_state(T0 + 3600)))
blind_when("state.json with no good tick yet", lambda: put_state({"last_ok_tick": None, "seats": {}}))
blind_when("journal.jsonl missing", lambda: (ROOT / "journal.jsonl").unlink())
blind_when("the journal frozen behind state.json", lambda: put_state(
    {"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-1-1"}, "idle_since": T0}}}))
blind_when("a streak with no ring in the journal", lambda: put_state(
    {"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"nh_streak": 2, "idle_since": T0 - 60}}}))

blind_when("the open ring is not the journal's last", lambda: (
    put_state({"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-9-1"}, "idle_since": T0}}}),
    (ROOT / "journal.jsonl").write_text(json.dumps({"at": OW.iso(T0 - 600), "do": "ring", "seat": "FOUNDRY", "ring_id": "FOUNDRY-8-1"}) + "\n")))

blind_when("a ring out 10 min with no journal row", lambda: put_state(
    {"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-7-1", "rung_at": T0 - 600}, "idle_since": T0 - 600}}}))
fresh()
put_state({"last_ok_tick": OW.iso(T0), "seats": {"FOUNDRY": {"ring": {"ring_id": "FOUNDRY-7-1", "rung_at": T0 - 30}, "idle_since": T0 - 30}}})
pts = OW.c_seats(T0, RULES, {})
check("a ring 30 s old, journalled when its tick ends, is not blind", pts["seats.blind"]["v"] == 0, pts)

no_block = {k: v for k, v in RULES.items() if k != "seats"}
fresh()
put_state(sane_state(T0))
pts = OW.c_seats(T0, no_block, {})
check("no seats block: UNMEASURED and blind", pts["seats.idle_with_work_min"]["m"] == "UNMEASURED" and pts["seats.blind"]["v"] == 1, pts)
pts = OW.c_seats(T0, {**RULES, "seats": {**RULES["seats"], "schedule": str(TMP / "none.json")}}, {})
check("schedule unreadable: UNMEASURED and blind", pts["seats.distressed"]["m"] == "UNMEASURED" and pts["seats.blind"]["v"] == 1, pts)


def boom(now, rules, ctx):
    raise RuntimeError("collection suppressed")


real = OW.COLLECTORS["seats"]
fresh()
put_state(sane_state(T0))
OW.run(now=T0, rules=RULES, filer=filer)
check("a healthy pass files nothing", not FILED, FILED)
OW.COLLECTORS["seats"] = boom
dg = OW.run(now=T0 + 900, rules=RULES, filer=filer)
check("a collector that raises alarms on that pass", BLIND in dg["alarms"], dg["alarms"])
check("and says why", "collection suppressed" in FILED[-1]["title"], FILED)
OW.COLLECTORS["seats"] = real
fresh()
put_state(sane_state(T0))
OW.run(now=T0, rules=RULES, filer=filer)
order, OW.ORDER = OW.ORDER, tuple(k for k in OW.ORDER if k != "seats")
dg = OW.run(now=T0 + 900, rules=RULES, filer=filer)
OW.ORDER = order
check("a collector dropped from the pass alarms too", BLIND in dg["alarms"], dg["alarms"])

# ------------------------------------------------------------------------- a stop somebody chose
fresh()
sch = sched()
now = T0
while now < T0 + 2400:
    D.tick(sch, True, obs=window(), now=now, fx=FX)
    now += TICK
for i in range(3):
    D.tick(sch, True, obs={**window(), "paused": "owner said stop"}, now=now, fx=FX)
    now += TICK
pts = OW.c_seats(now, RULES, {})
check("under a PAUSE file it reads idle, not distressed", pts["seats.distressed"]["v"] == 0 and pts["seats.distressed"]["x"]["state"] == "idle", pts)
fresh()
(ROOT / "journal.jsonl").write_text(json.dumps({"at": OW.iso(T0 - 60), "do": "ring", "seat": "BENCH", "ring_id": "B-1", "idle_since": T0 - 3000}) + "\n")
put_state({"last_ok_tick": OW.iso(T0), "seats": {"BENCH": {"ring": {"ring_id": "B-1"}}}})
pts = OW.c_seats(T0, RULES, {})
check("a seat the schedule does not wake is not counted", pts["seats.idle_with_work_min"]["v"] == 0, pts)

shutil.rmtree(TMP, ignore_errors=True)
print("selftest_seats_watch: %s" % ("FAIL " + ", ".join(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)

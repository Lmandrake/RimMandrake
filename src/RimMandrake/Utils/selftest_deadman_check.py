#!/usr/bin/env python3
"""selftest for deadman_check.py (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT, LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING). Fixtures only; no ledger/systemd touched.

    python3 src/RimMandrake/Utils/selftest_deadman_check.py
"""
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_deadman_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["RM_DISPATCHER_STATE"] = str(TMP / "disp")
os.environ["TESTQ_QUEUE"] = str(TMP / "q")
import deadman_check as DM  # noqa: E402
import ops_watch as OW  # noqa: E402

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


NOW = 1_800_000_000.0


def write_stamps(ops_t, disp_t, dry=False):
    (TMP / "ops").mkdir(parents=True, exist_ok=True)
    if ops_t is not None:
        (TMP / "ops/status.json").write_text(json.dumps({"t": ops_t}))
    d = TMP / "disp" / ("dry" if dry else "")
    d.mkdir(parents=True, exist_ok=True)
    if disp_t is not None:
        (d / "state.json").write_text(json.dumps({"last_tick": OW.iso(disp_t)}))


class It:
    def __init__(self, state="done", live=None, live_broken=None, live_repeats=0):
        self.state, self.live, self.live_broken, self.live_repeats = state, live, live_broken, live_repeats


GOOD = "unit=rm-good.timer max_age=1h"
DEAD = "unit=rm-dead.timer max_age=1h"


def sweeps():
    calls = []

    def filer(todo, conf):
        calls.append(todo)
        return {t["item"]: None for t in todo}

    chk = lambda line: "it died" if "dead" in line else None
    # the promise the ledger holds: reopen the SAME item
    items = {"A_FIX_1": It(live=DEAD), "B_FIX_1": It(live=GOOD)}
    r = DM.sweep(NOW, filer, items, [], {}, chk)
    check(len(calls) == 1 and calls[0] == [{"item": "A_FIX_1", "result": "broken", "detail": "it died"}],
          "a dead promise reopens its own item and files nothing new")
    check(r["line"] == "2 promises, 1 kept, 1 broken", "the one report line: " + r["line"])
    check(json.loads((TMP / "ops/live_sweep.json").read_text())["line"] == r["line"], "the line reaches live_sweep.json")
    # already reopened: nothing to say, the ledger is the state
    calls.clear()
    items["A_FIX_1"] = It(state="ready", live=DEAD, live_broken="it died", live_repeats=1)
    DM.sweep(NOW, filer, items, [], {}, chk)
    check(not calls, "still dead: no second event")
    # recovery puts it back
    items["A_FIX_1"].live = GOOD
    DM.sweep(NOW, filer, items, [], {}, chk)
    check(calls and calls[0][0]["item"] == "A_FIX_1" and calls[0][0]["result"] == "kept", "recovery closes the item itself")
    # a promise with no item: fixed id, spawned once
    calls.clear()
    DM.sweep(NOW, filer, {}, [DEAD], {}, chk)
    check(calls[0][0]["item"] == "LIVE_RESTORE_RM_DEAD" and calls[0][0].get("spawn"), "a baseline promise files its fixed id")
    calls.clear()
    DM.sweep(NOW, filer, {"LIVE_RESTORE_RM_DEAD": It(state="done", live_repeats=1)}, [DEAD], {}, chk)
    check(calls[0][0]["item"] == "LIVE_RESTORE_RM_DEAD" and not calls[0][0].get("spawn"), "a returning outage reuses the id")
    # the second outage asks for a fold
    r = DM.sweep(NOW, filer, {"LIVE_RESTORE_RM_DEAD": It(state="done", live_repeats=1)}, [DEAD], {}, chk)
    check(r["fold"] == ["LIVE_RESTORE_RM_DEAD"] and "1 need a fold" in r["line"], "repeat 2 reads needs-fold")
    # arms take the same road
    calls.clear()
    r = DM.sweep(NOW, filer, {}, [], {"dispatcher": "too old", "ops_watch": None}, chk)
    check([t["item"] for t in calls[0]] == ["LIVE_RESTORE_DISPATCHER"], "a dead arm has a fixed id too")
    # once, retired and worked items are not swept; one pass never floods
    p = DM.promises({"O": It(live="once: repair"), "D": It(state="dropped", live=DEAD), "W": It(state="doing", live=DEAD)}, [])
    check(p == [], "once, dropped and an item in work are not swept")
    check(DM.promises({"LIVE_RESTORE_RM_DEAD": It(state="superseded")}, [DEAD]) == [], "a retired fixed id is not swept")
    calls.clear()
    many = ["unit=rm-dead%d.timer max_age=1h" % i for i in range(14)]
    kinds = lambda line: "fault kind %s" % "abcdefghijklmn"[int(re.search(r"dead(\d+)", line).group(1))]
    r = DM.sweep(NOW, filer, {}, many, {}, kinds)
    check(len(calls[0]) == DM.MAX_PER_PASS and r["held"] == 4 and len(r["broken"]) == 14, "a mass outage is capped and counted")
    calls.clear()
    r = DM.sweep(NOW, filer, {}, many, {}, chk)
    check(len(calls[0]) == 1 and calls[0][0]["item"].startswith("LIVE_RESTORE_CAUSE_") and len(r["broken"]) == 14,
          "14 promises broken for one reason are one ticket, and the report still counts 14")
    # one shared timer down under two fixes is ONE outage: only the host is filed (RIMMANDRAKE_CHARGE_SHARED_OUTAGE_
    # ONCE_FORTY_FIVE_DEATHS, then RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET: the fixes are not reopened)
    calls.clear()
    r = DM.sweep(NOW, filer, {"A_FIX_1": It(live=DEAD), "C_FIX_1": It(live=DEAD)}, [], {}, chk)
    got = [(t["item"], bool(t.get("spawn"))) for t in calls[0]]
    check(got == [("LIVE_RESTORE_RM_DEAD", True)], "a shared outage files its host alone: %s" % got)
    check(r["line"] == "2 promises, 0 kept, 2 broken", "the host filed for a shared outage is not a promise: " + r["line"])
    calls.clear()
    DM.sweep(NOW, filer, {"A_FIX_1": It(live=DEAD), "C_FIX_1": It(live=DEAD),
                          "LIVE_RESTORE_RM_DEAD": It(state="ready", live_broken=DM.SHARED_MARK + "it died",
                                                     live_repeats=1)}, [], {}, chk)
    check(not calls, "a host already broken is not filed again, and its sharers file nothing: %s" % calls)
    calls.clear()
    DM.sweep(NOW, filer, {"A_FIX_1": It(live=DEAD)}, [], {}, chk)
    check(calls[0] == [{"item": "A_FIX_1", "result": "broken", "detail": "it died"}], "one fix alone shares nothing")
    # blind: nothing moves
    calls.clear()
    r = DM.sweep(NOW, filer, {"A": It(live=DEAD)}, [], {}, chk, sees=False)
    check(not calls and r.get("blind") and "unread" in r["line"], "a blind pass reopens nothing and says so")
    # a failed filing is reported, and repeats next pass because the ledger did not move
    def boom(todo, conf):
        raise RuntimeError("no")
    r = DM.sweep(NOW, boom, {"A": It(live=DEAD)}, [], {}, chk)
    check(r["errors"].get("A"), "a filer that raises is reported")
    # a reading that could not be pushed is retried by the next pass, with nothing new to file
    seen = []
    def stuck(todo, conf):
        seen.append(todo)
        return {"_publish": "pushed" if len(seen) > 1 else "publish stopped: no"}
    ok_chk = lambda line: None
    r = DM.sweep(NOW, stuck, {"A": It(live=DEAD)}, [], {}, chk)
    check(r["unpublished"] == "publish stopped: no", "a failed publish is on the report")
    r = DM.sweep(NOW, stuck, {"A": It(state="ready", live=DEAD, live_broken="x")}, [], {}, chk)
    check(seen[1] == [] and r["unpublished"] is None, "the next pass pushes it, and the flag clears")
    check(DM.unpushed({"_publish": "nothing to publish"}, {"unpublished": "no"}) == "no", "nothing tried settles nothing")
    (TMP / "ops/live_sweep.json").write_text(json.dumps({"unpublished": "no"}))
    r = DM.sweep(NOW, stuck, {}, [], {}, chk, sees=False)
    check(r["unpublished"] == "no", "a blind pass keeps the debt")
    (TMP / "ops/live_sweep.json").write_text("{}")
    # paused: not broken, and not recovered either
    calls.clear()
    r = DM.sweep(NOW, filer, {"A": It(state="ready", live=DEAD, live_broken="x")}, [], {}, lambda l: DM.EXCUSED)
    check(not calls and "1 paused" in r["line"] and not r["broken"], "a paused promise neither reopens nor ends an outage")
    # a fixed id answers for its baseline line whatever it closed with
    p = DM.promises({"LIVE_RESTORE_RM_DEAD": It(live=GOOD)}, [DEAD])
    check(p == [{"item": "LIVE_RESTORE_RM_DEAD", "line": DEAD}], "a ledger line cannot hide a baseline line")
    DM.MOVED_READINGS["/d/OLD_PAGE.md"] = "/d/NEW_PAGE.md"
    OLD = "unit=rm-x.timer reading=/d/OLD_PAGE.md max_age=5m"
    p = DM.promises({"I": It(live=OLD)}, [])
    DM.MOVED_READINGS.clear()
    check(p == [{"item": "I", "line": OLD.replace("OLD_PAGE", "NEW_PAGE")}], "a moved reading= path is swept at its new home")
    # an old pause record excuses nothing; a pending restart does
    (TMP / "ops/timers_pauses.json").write_text(json.dumps({"timer-resume-1.timer": ["rm-dead.timer"]}))
    import subprocess as SP
    # the promised timer itself is stopped; `state` is what its armed restart reads
    run = lambda state: (lambda argv, **kw: SP.CompletedProcess(argv, 0, "inactive" if argv[-1] == "rm-dead.timer" else state, ""))
    check(not DM.excused(DEAD, run("inactive")), "a pause whose restart is gone excuses nothing")
    check(DM.excused(DEAD, run("active")), "a pause with its restart armed is excused")
    check(DM.duration_s("{ OnBootUSec=3min ; x }\n{ OnUnitInactiveUSec=1h 30min ; next }") == 5400, "timer period parsed")
    check(DM.duration_s("{ OnBootUSec=3min ; x }") is None, "no period is unknown")
    base = DM.load_baseline()
    names = [DM.item_id(x) for x in base]
    check(len(base) > 30 and len(set(names)) == len(names), "baseline: %d lines, one id each" % len(base))
    bad = TMP / "bad.txt"
    bad.write_text("unit=rm-x.timer\n")
    try:
        DM.load_baseline(bad)
        check(False, "a bad baseline line must raise")
    except ValueError:
        check(True, "a bad baseline line raises")


# ---- one fault files one ticket (RIMMANDRAKE_KEY_AUTO_FILERS_ONE_FAULT_ONE_TICKET), one test per promise on
# design/specs/2026-11-19-one-fault-one-ticket/boundary.md

HOOKS = ["hook=a_one.py", "hook=b_two.py", "hook=c_three.py"]


def unwired(line):
    """The 2026-11-08 flood's reason: every hook reads unwired because the settings path moved."""
    return "hook %s is not wired in /x/.claude/settings.json" % line.split("=", 1)[1]


def filed(baseline, items=None, chk=unwired):
    calls = []
    DM.sweep(NOW, lambda todo, conf: calls.append(todo) or {t["item"]: None for t in todo},
             items or {}, baseline, {}, chk)
    return calls[0] if calls else []


def t_one_cause_files_one_ticket():
    todo = filed(HOOKS)
    ids = [t["item"] for t in todo]
    check(len(todo) == 1 and ids[0].startswith("LIVE_RESTORE_CAUSE_") and todo[0].get("spawn"),
          "three hooks unwired for one reason file one cause ticket: %s" % ids)
    check(todo and all(DM.item_id(h) in todo[0]["detail"] for h in HOOKS),
          "the cause ticket names every promise it holds: %s" % (todo[0]["detail"] if todo else None))


def t_a_repeat_reopens_the_same_ticket():
    first = filed(HOOKS)
    cid = first[0]["item"] if first else None
    again = filed(list(reversed(HOOKS)), {cid: It(state="done", live_repeats=1)} if cid else {})
    check(cid is not None and [t["item"] for t in again] == [cid] and not again[0].get("spawn"),
          "the same fault fed again reopens the same ticket, whatever the order: %s" % again)
    held = filed(HOOKS, {cid: It(state="ready", live_broken=DM.SHARED_MARK + "x", live_repeats=1)} if cid else {})
    check(held == [], "a fault still open files nothing more: %s" % held)


def t_two_causes_stay_two_tickets():
    why = lambda line: unwired(line) if line in HOOKS[:2] else "hook %s file is missing" % line.split("=", 1)[1]
    todo = filed(HOOKS + ["hook=d_four.py"], chk=why)
    ids = sorted(t["item"] for t in todo)
    check(len(ids) == 2 and all(i.startswith("LIVE_RESTORE_CAUSE_") for i in ids) and ids[0] != ids[1],
          "two reasons, two pairs: two cause tickets: %s" % ids)
    todo = filed([HOOKS[0], DEAD], chk=lambda line: "it died")
    check(sorted(t["item"] for t in todo) == ["LIVE_RESTORE_A_ONE", "LIVE_RESTORE_RM_DEAD"],
          "a hook and a timer with the same words are two kinds, two tickets: %s" % [t["item"] for t in todo])


def t_a_lone_fault_keeps_its_own_ticket():
    why = lambda line: unwired(line) if line == HOOKS[0] else ("hook b_two.py is wired in /x but /y is absent"
                                                              if line == HOOKS[1] else None)
    todo = filed(HOOKS, chk=why)
    check(sorted(t["item"] for t in todo) == ["LIVE_RESTORE_A_ONE", "LIVE_RESTORE_B_TWO"],
          "two promises broken for two reasons stay two tickets, each its own id: %s" % [t["item"] for t in todo])


def t_members_file_no_ticket_of_their_own():
    todo = filed([], {"A_FIX_1": It(live=DEAD), "C_FIX_1": It(live=DEAD)}, chk=lambda line: "it died")
    got = [(t["item"], bool(t.get("spawn"))) for t in todo]
    check(got == [("LIVE_RESTORE_RM_DEAD", True)], "one shared timer under two fixes files its host only: %s" % got)
    todo = filed(HOOKS, {"LIVE_RESTORE_A_ONE": It(state="done", live_repeats=1)})
    check(len(todo) == 1 and todo[0]["item"].startswith("LIVE_RESTORE_CAUSE_"),
          "a member that has its own item is not reopened: %s" % [t["item"] for t in todo])


def t_the_cause_ticket_is_put_back_when_the_cause_clears():
    cid = filed(HOOKS)[0]["item"]
    todo = filed(HOOKS, {cid: It(state="ready", live_broken=DM.SHARED_MARK + "x", live_repeats=1)}, chk=lambda l: None)
    check([(t["item"], t["result"]) for t in todo] == [(cid, "kept")], "the cause clears, its ticket is kept: %s" % todo)
    why = lambda line: unwired(line) if line == HOOKS[0] else None
    todo = filed(HOOKS, {cid: It(state="ready", live_broken=DM.SHARED_MARK + "x", live_repeats=1)}, chk=why)
    got = sorted((t["item"], t["result"]) for t in todo)
    check(got == sorted([(cid, "kept"), ("LIVE_RESTORE_A_ONE", "broken")]),
          "one member left: the cause ticket is kept and the member files its own: %s" % got)


def t_a_retired_cause_ticket_gets_a_successor():
    cid = filed(HOOKS)[0]["item"]
    todo = filed(HOOKS, {cid: It(state="dropped")})
    nid = todo[0]["item"] if todo else None
    check(nid and nid != cid and nid.startswith("LIVE_RESTORE_CAUSE_") and todo[0].get("spawn"),
          "a dropped cause ticket is not reopened; the cause files its successor: %s" % nid)
    again = filed(HOOKS, {cid: It(state="dropped"), nid: It(state="done", live_repeats=1)} if nid else {})
    check([t["item"] for t in again] == [nid], "the successor is the cause's ticket from then on: %s" % again)


def t_cause_ids_are_item_names():
    import importlib
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    model = importlib.import_module("model")
    cid = filed(HOOKS)[0]["item"]
    check(not model.mint_problems(cid, set()), "%s parses as an item name: %s" % (cid, model.mint_problems(cid, set())))


def no_todoist():
    """Owner, 2026-11-19: Todoist is retired as an alert route. With RM_TODOIST_ALARM_POSTS unset the real pusher's
    sweep attempts no HTTP call to Todoist, the sweep still reports, and the report says the phone route is off."""
    import types
    import urllib.request
    sys.path.insert(0, str(HERE / "ops_core"))
    import phone_push as pp
    keep_t, keep_ul = pp.todoist_transport, urllib.request.urlopen
    keep_mod = sys.modules.get("todoist_api")
    import importlib
    importlib.reload(pp)
    pp.STATE = TMP / "phone_push_off.json"
    os.environ.pop("RM_TODOIST_ALARM_POSTS", None)
    calls = []

    def boom(*a, **k):
        calls.append(a)
        raise AssertionError("HTTP to Todoist attempted")
    sys.modules["todoist_api"] = types.SimpleNamespace(Todoist=boom)
    urllib.request.urlopen = boom
    try:
        pusher = DM.real_pusher()
        chk = lambda line: "rm-dead.timer is inactive" if "dead" in line else None
        refused = lambda todo, conf: {t["item"]: "ledger write refused" for t in todo}
        arms = {"dispatcher": None, "ops_watch": "ops_watch last ran 61 min ago (limit 50 min)"}
        r = DM.sweep(NOW, refused, {}, [DEAD], arms, chk, pusher=pusher)
        check(not calls, "deadman with Todoist retired attempts no HTTP call: %r" % calls)
        check(r["phone"] and all(x.startswith("phone off") for x in r["phone"]),
              "the report says the phone route is off, never 'pushed': %r" % r.get("phone"))
        check(r["line"], "the sweep still reports with the phone off")
    finally:
        urllib.request.urlopen = keep_ul
        if keep_mod is None:
            sys.modules.pop("todoist_api", None)
        else:
            sys.modules["todoist_api"] = keep_mod
        pp.todoist_transport = keep_t


def phones():
    """DEADMAN_WIRE_PHONE_WITHOUT_AI: a dead arm or a broken timer rings the phone through the real phone_push (its
    transport faked, its state in TMP), once per outage, whatever the filer did; recovery closes the key."""
    sys.path.insert(0, str(HERE / "ops_core"))
    import phone_push as pp
    pp.STATE = TMP / "phone_push.json"
    sent = []
    pp.todoist_transport = lambda title, body: sent.append((title, body))
    os.environ["RM_TODOIST_ALARM_POSTS"] = "1"  # the routing is tested with the retired Todoist route switched back on
    chk = lambda line: "rm-dead.timer is inactive" if "dead" in line else None
    refused = lambda todo, conf: {t["item"]: "ledger write refused" for t in todo}
    arms = {"dispatcher": None, "ops_watch": "ops_watch last ran 61 min ago (limit 50 min)"}
    r = DM.sweep(NOW, refused, {"B_FIX_1": It(live=GOOD)}, [DEAD], arms, chk, pusher=pp)
    titles = sorted(t for t, _ in sent)
    check(titles == ["RimMandrake: dead-man LIVE_RESTORE_OPS_WATCH is red", "RimMandrake: dead-man LIVE_RESTORE_RM_DEAD is red"],
          "a dead ops_watch and a broken timer each ring the phone, though the ledger write was refused: %s" % titles)
    body = dict((t, b) for t, b in sent)["RimMandrake: dead-man LIVE_RESTORE_OPS_WATCH is red"]
    check(body == "deadman_check (no AI): ops_watch last ran 61 min ago (limit 50 min). The ledger holds "
                  "LIVE_RESTORE_OPS_WATCH; restore it, then the sweep puts it back.", "the fixed phone line: " + body)
    check(sorted(r["phone"]) == ["pushed deadman:LIVE_RESTORE_OPS_WATCH", "pushed deadman:LIVE_RESTORE_RM_DEAD"],
          "the report says what was pushed: %s" % r["phone"])
    DM.sweep(NOW, refused, {}, [DEAD], arms, chk, pusher=pp)
    check(len(sent) == 2, "still dead: no second ring")
    DM.sweep(NOW, refused, {}, [DEAD], {"dispatcher": "dispatcher last ran 20 min ago (limit 15 min)",
                                        "ops_watch": None}, chk, pusher=pp)
    check(len(sent) == 3 and "LIVE_RESTORE_DISPATCHER" in sent[-1][0], "a dead Dispatcher rings too")
    DM.sweep(NOW, refused, {}, [DEAD], arms, chk, pusher=pp)
    check(len(sent) == 4 and "OPS_WATCH" in sent[-1][0], "ops_watch recovered then died again: a new ring")
    sent.clear()
    DM.sweep(NOW, refused, {"X": It(live="hook=block_x.py")}, [], {}, lambda l: "hook missing", pusher=pp)
    check(not sent, "a broken non-timer promise goes to the ledger only")

    class Boom:
        def send(self, row):
            raise OSError("no network")

        def close(self, key):
            pass
    r = DM.sweep(NOW, refused, {}, [], arms, chk, pusher=Boom())
    check(r["phone"] and r["phone"][0].startswith("push failed LIVE_RESTORE_OPS_WATCH: OSError")
          and json.loads((TMP / "ops/live_sweep.json").read_text()).get("phone") == r["phone"],
          "a failing phone is reported and the sweep still writes its line: %s" % r["phone"])
    r = DM.sweep(NOW, refused, {}, [], arms, chk)
    check("phone" not in r, "no pusher (run without --file-alarms): no phone")


def receivers():
    """T2 (ALARMS_REWIRE_OFF_RETIRED_BENCH): the real live_filer against a stub ingest in a stub clone."""
    stub = TMP / "stubclone/src/RimMandrake/Utils/testq"
    stub.mkdir(parents=True, exist_ok=True)
    (TMP / "q").mkdir(exist_ok=True)
    log = TMP / "stub.log"
    os.environ["STUB_LOG"] = str(log)
    (stub / "ingest.py").write_text("import json, os\ndef rimflow(*a):\n    open(os.environ['STUB_LOG'], 'a').write("
                                    "json.dumps(a) + '\\n')\n    return 0, ''\ndef publish(n, message=''):\n    return 'ok'\n")
    conf = {"clone": str(TMP / "stubclone"), "parent": "P", "for": "BENCH", "needs": "offline", "lock_wait_s": 1}
    todo = [{"item": "LIVE_RESTORE_X", "spawn": True, "title": "t", "result": "broken", "detail": "d"},
            {"item": "LIVE_RESTORE_Y", "result": "kept", "detail": "back"}]
    # nothing drains BENCH offline in the real table now (RIMMANDRAKE_FIX_ALARM_RECEIVER_TRUSTS_RETIRED_RELENTLESS_POOL):
    # the filing path runs against a fixture table with a drainer row
    routes = json.loads((HERE.parent / "rimflow" / "alarm_routes.json").read_text(encoding="utf-8"))
    routes["drainers"] = [{"by": "fixture", "seat": "BENCH", "needs": ["offline"]}]
    (TMP / "routes.json").write_text(json.dumps(routes), encoding="utf-8")
    rt = os.environ.get("RIMFLOW_ROUTES")
    os.environ["RIMFLOW_ROUTES"] = str(TMP / "routes.json")
    res = DM.live_filer(todo, conf)
    seen = [json.loads(x) for x in log.read_text().splitlines()]
    check(res.get("LIVE_RESTORE_X") is None and [s[:2] for s in seen] == [["spawn", "--from"], ["live", "LIVE_RESTORE_X"],
          ["raise", "LIVE_RESTORE_X"], ["live", "LIVE_RESTORE_Y"]] and seen[0][seen[0].index("--for") + 1] == "BENCH",
          "a broken promise is spawned for a drainer, recorded, then raised; a kept one is not raised: %s" % seen)
    log.write_text("")
    res = DM.live_filer(todo, dict(conf, needs="live"))
    seen = [json.loads(x) for x in log.read_text().splitlines()]
    check("no receiver" in str(res.get("LIVE_RESTORE_X")) and [s[:2] for s in seen] == [["live", "LIVE_RESTORE_Y"]],
          "a new item nobody would pick up is not spawned; a reading on a filed item still goes: %s %s" % (res, seen))
    if rt is None:
        os.environ.pop("RIMFLOW_ROUTES", None)
    else:
        os.environ["RIMFLOW_ROUTES"] = rt
    # RIMMANDRAKE_NAME_RECEIVER_FOR_SEAT_ALARMS_PENDING_WITH_NONE: the Conductor seat receives BENCH offline alarms, so the
    # dead-man's new items are filed on the real table (797a08f5e7 had left them unfiled with "no receiver")
    nobody = OW.alarm_receiver_problem(dict(OW.alarm_conf(OW.load_rules()), clone=str(TMP)))
    check(nobody is None, "the real alarm conf (ops_watch_rules.json) files for a receiver, the Conductor seat: %s" % nobody)


def main():
    j = DM.judge({"ops_watch": NOW - 600, "dispatcher": NOW - 60}, NOW)
    check(j == {"ops_watch": None, "dispatcher": None}, "fresh stamps: both alive")
    j = DM.judge({"ops_watch": NOW - 3600, "dispatcher": None}, NOW)
    check("60 min ago" in j["ops_watch"] and "no readable" in j["dispatcher"], "stale and missing stamps are faults")
    check(DM.judge({"ops_watch": NOW + 3600, "dispatcher": NOW}, NOW)["ops_watch"], "future stamp is a fault")

    # OPS_DEADMAN_REVIVE_17EC: this pass restarts beside the arm after a mass stop, 3 s before its first tick
    began = lambda t: (lambda argv, **kw: __import__("subprocess").CompletedProcess(argv, 0, "@%d\n" % t, ""))
    st = {"ops_watch": NOW - 600, "dispatcher": NOW - 21 * 60}
    check(DM.arm_faults(st, NOW, began(NOW - 3))["dispatcher"] is None, "arm: a timer started 3 s ago is not dead")
    check("21 min" in DM.arm_faults(st, NOW, began(NOW - 86400))["dispatcher"], "arm: stale stamp + old timer still alarms")
    check("16 min" in DM.arm_faults({"ops_watch": NOW, "dispatcher": NOW - 40 * 60}, NOW, began(NOW - 16 * 60))["dispatcher"],
          "arm: a restart buys one limit, not silence")
    check("no readable" in DM.arm_faults({"ops_watch": NOW, "dispatcher": None}, NOW, began(NOW - 3))["dispatcher"],
          "arm: a missing stamp stays a fault beside a fresh timer")
    check("21 min" in DM.judge(DM.arm_clocks(st, NOW, began(NOW + 9999)), NOW)["dispatcher"], "arm: a future start buys nothing")
    orig_excused, DM.excused = DM.excused, lambda line, runner=None: DM.ARM_UNITS["dispatcher"] in line
    check("dispatcher" not in DM.arm_faults(st, NOW, began(NOW - 86400)), "arm: paused with its restart armed is excused")
    DM.excused = orig_excused

    write_stamps(NOW - 60, NOW - 60, dry=True)
    s = DM.stamps(mode="dry")
    check(abs(s["dispatcher"] - (NOW - 60)) < 1 and abs(s["ops_watch"] - (NOW - 60)) < 1, "stamps read (dry dispatcher counts)")
    # review Q 12: the timer's mode is monitored, a fresh dry stamp never masks a dead live one
    write_stamps(NOW - 60, NOW - 3600, dry=False)
    s = DM.stamps(mode="live")
    check(abs(s["dispatcher"] - (NOW - 3600)) < 1, "live mode: the live stamp, not the fresher dry one")
    check(DM.judge(s, NOW)["dispatcher"], "live mode: a stale live Dispatcher is a fault despite fresh dry ticks")
    import subprocess as SP
    fake = lambda out, rc=0: (lambda argv, **kw: SP.CompletedProcess(argv, rc, out, ""))
    os.environ.pop("RM_DISPATCHER_MODE", None)
    ex = "{ path=/usr/bin/python3 ; argv[]=/usr/bin/python3 /x/dispatcher.py tick%s ; ignore_errors=no }"
    tbl = lambda name, phases: (TMP / name).write_text(json.dumps({"phases": phases})) and (TMP / name)
    unowned = tbl("t_unowned.json", {"dispatch": {"argv": ["x", "tick", "--json"]}})
    owned = lambda apply: tbl("t_owned.json", {"dispatch": {"owns": ["rm-dispatcher.timer"],
                                                             "argv": ["x", "tick"] + (["--apply"] if apply else [])}})
    check(DM.dispatcher_mode(fake(ex % ""), owned(True)) == "live", "mode: an owning phase with --apply -> live, ExecStart ignored")
    check(DM.dispatcher_mode(fake(ex % " --apply"), owned(False)) == "dry", "mode: an owning phase without --apply -> dry")
    check(DM.dispatcher_mode(fake("", 1)) == "live", "mode: the shipped table's dispatch phase ticks --apply -> live")
    check(DM.dispatcher_mode(fake(ex % " --apply"), unowned) == "live", "mode: --apply in ExecStart -> live")
    check(DM.dispatcher_mode(fake(ex % ""), unowned) == "dry", "mode: no --apply -> dry")
    check(DM.dispatcher_mode(fake("", 1), unowned) is None, "mode: systemctl failure -> unknown, not dry")
    # review Q 11: last_ok_tick wins; last_tick only for a state with no last_ok_tick key
    check(DM.dispatcher_stamp({"last_tick": OW.iso(NOW), "last_ok_tick": None}) is None,
          "last_ok_tick null (every tick raised): no stamp, last_tick does not count")
    check(abs(DM.dispatcher_stamp({"last_tick": OW.iso(NOW), "last_ok_tick": OW.iso(NOW - 999)}) - (NOW - 999)) < 1,
          "last_ok_tick is the stamp, not last_tick")
    check(abs(DM.dispatcher_stamp({"last_tick": OW.iso(NOW)}) - NOW) < 1, "pre-Q state (no last_ok_tick key): last_tick")
    # review Q 10: non-finite stamps are no stamps
    for bad in (float("nan"), float("inf"), True):
        check(DM.judge({"ops_watch": bad, "dispatcher": NOW}, NOW)["ops_watch"], "stamp %r is a fault" % (bad,))
    (TMP / "ops/status.json").write_text('{"t": NaN}')
    check(DM.stamps(mode="dry")["ops_watch"] is None, "status.json t NaN -> None, not alive")
    (TMP / "ops/status.json").write_text("{torn")
    check(DM.stamps(mode="dry")["ops_watch"] is None, "torn status.json -> None, not fresh")

    sweeps()
    for t in (t_one_cause_files_one_ticket, t_a_repeat_reopens_the_same_ticket, t_two_causes_stay_two_tickets,
              t_a_lone_fault_keeps_its_own_ticket, t_members_file_no_ticket_of_their_own,
              t_the_cause_ticket_is_put_back_when_the_cause_clears, t_a_retired_cause_ticket_gets_a_successor,
              t_cause_ids_are_item_names):
        try:
            t()
        except Exception as e:  # noqa: BLE001  a test that raises on the base code is a red, not a crash of the rest
            check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    phones()
    no_todoist()
    receivers()
    # the pass reads the shard it files into, from a clone no other reader lists
    import ops_ledger as pc
    seen, keep_rl, keep_cl, keep_here = [], pc.read_ledger, pc.CLONES, DM.HERE
    pc.read_ledger = lambda clones: seen.extend(clones) or []
    pc.CLONES, DM.HERE = [Path("/a")], Path("/d/src/RimMandrake/Utils")
    DM.read_items()
    pc.read_ledger, pc.CLONES, DM.HERE = keep_rl, keep_cl, keep_here
    check(seen == [Path("/a"), Path("/d")], "a sweep reads its own clone's shards as well: %r" % seen)
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

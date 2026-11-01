#!/usr/bin/env python3
"""selftest for deadman_check.py (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT, LIVE_PROOF_ENFORCE_DONE_MEANS_RUNNING). Fixtures only; no ledger/systemd touched.

    python3 src/RimMandrake/Utils/selftest_deadman_check.py
"""
import json
import os
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
    r = DM.sweep(NOW, filer, {}, many, {}, chk)
    check(len(calls[0]) == DM.MAX_PER_PASS and r["held"] == 4 and len(r["broken"]) == 14, "a mass outage is capped and counted")
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
    # an old pause record excuses nothing; a pending restart does
    (TMP / "ops/timers_pauses.json").write_text(json.dumps({"timer-resume-1.timer": ["rm-dead.timer"]}))
    import subprocess as SP
    run = lambda state: (lambda argv, **kw: SP.CompletedProcess(argv, 0, state, ""))
    check(not DM.excused(DEAD, run("inactive")), "a pause whose restart is gone excuses nothing")
    check(DM.excused(DEAD, run("active")), "a pause with its restart armed is excused")
    check(DM.duration_s("{ OnBootUSec=3min ; x }\n{ OnUnitInactiveUSec=1h 30min ; next }") == 5400, "timer period parsed")
    check(DM.duration_s("{ OnBootUSec=3min ; x }") is None, "no period is unknown")
    base = DM.load_baseline()
    names = [DM.item_id(x) for x in base]
    check(len(base) > 40 and len(set(names)) == len(names), "baseline: %d lines, one id each" % len(base))
    bad = TMP / "bad.txt"
    bad.write_text("unit=rm-x.timer\n")
    try:
        DM.load_baseline(bad)
        check(False, "a bad baseline line must raise")
    except ValueError:
        check(True, "a bad baseline line raises")


def phones():
    """DEADMAN_WIRE_PHONE_WITHOUT_AI: a dead arm or a broken timer rings the phone through the real phone_push (its
    transport faked, its state in TMP), once per outage, whatever the filer did; recovery closes the key."""
    sys.path.insert(0, str(HERE / "pulse"))
    import phone_push as pp
    pp.STATE = TMP / "phone_push.json"
    sent = []
    pp.todoist_transport = lambda title, body: sent.append((title, body))
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
    orig_excused, DM.excused = DM.excused, lambda line, runner=None: "rm-dispatcher.timer" in line
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
    check(DM.dispatcher_mode(fake(ex % " --apply")) == "live", "mode: --apply in ExecStart -> live")
    check(DM.dispatcher_mode(fake(ex % "")) == "dry", "mode: no --apply -> dry")
    check(DM.dispatcher_mode(fake("", 1)) is None, "mode: systemctl failure -> unknown, not dry")
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
    phones()
    # the pass reads the shard it files into, from a clone no other reader lists
    import pulse_core as pc
    seen, keep_rl, keep_cl, keep_here = [], pc.read_ledger, pc.CLONES, DM.HERE
    pc.read_ledger = lambda clones: seen.extend(clones) or []
    pc.CLONES, DM.HERE = [Path("/a")], Path("/d/src/RimMandrake/Utils")
    DM.read_items()
    pc.read_ledger, pc.CLONES, DM.HERE = keep_rl, keep_cl, keep_here
    check(seen == [Path("/a"), Path("/d")], "a sweep reads its own clone's shards as well: %r" % seen)
    # install plan writes nothing
    home = TMP / "home"
    os.environ["HOME"] = str(home)
    DM.install(False, "/x")
    check(not home.exists(), "install plan writes nothing")
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

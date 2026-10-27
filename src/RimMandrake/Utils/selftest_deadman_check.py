#!/usr/bin/env python3
"""selftest for deadman_check.py (DISPATCHER_BUILD_OUTSIDE_DEADMAN_HEARTBEAT). Fixtures only; no ledger/systemd touched.

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


def main():
    j = DM.judge({"ops_watch": NOW - 600, "dispatcher": NOW - 60}, NOW)
    check(j == {"ops_watch": None, "dispatcher": None}, "fresh stamps: both alive")
    j = DM.judge({"ops_watch": NOW - 3600, "dispatcher": None}, NOW)
    check("60 min ago" in j["ops_watch"] and "no readable" in j["dispatcher"], "stale and missing stamps are faults")
    check(DM.judge({"ops_watch": NOW + 3600, "dispatcher": NOW}, NOW)["ops_watch"], "future stamp is a fault")

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

    filed = []

    def filer(todo, conf):
        filed.append([dict(a) for a in todo])
        return {a["name"]: None for a in todo}

    ids = set()
    # dead dispatcher: one filing
    st = DM.check(NOW, filer, ids, {"ops_watch": NOW - 60, "dispatcher": NOW - 7200})
    check(len(filed) == 1 and st["dispatcher"]["state"] == "OPEN" and st["dispatcher"]["name"].startswith("OPS_DEADMAN_REVIVE"),
          "dead dispatcher files one item")
    check("ops_watch" not in st, "live ops_watch not filed")
    DM.check(NOW + 600, filer, ids, {"ops_watch": NOW, "dispatcher": NOW - 7200})
    check(len(filed) == 1, "still dead: no second filing")
    # recovers: note, state cleared
    DM.check(NOW + 1200, filer, ids, {"ops_watch": NOW + 1000, "dispatcher": NOW + 1100})
    check(len(filed) == 2 and filed[1][0].get("note_only") and "dispatcher" not in json.loads((TMP / "ops/deadman.json").read_text()),
          "recovery notes the item and re-arms")
    # failed filing stays PENDING and retries under the same name
    bad = []
    def failer(todo, conf):
        bad.append(todo[0]["name"])
        return {todo[0]["name"]: "boom"}
    DM.check(NOW + 2000, failer, ids, {"ops_watch": 0.0, "dispatcher": NOW + 1900})
    st = DM.check(NOW + 2100, failer, ids, {"ops_watch": 0.0, "dispatcher": NOW + 2000})
    check(st["ops_watch"]["state"] == "PENDING" and len(bad) == 2 and bad[0] == bad[1], "failed filing retried under one name")
    # no filer: nothing written to a ledger
    (TMP / "ops/deadman.json").unlink()
    st = DM.check(NOW, None, ids, {"ops_watch": NOW, "dispatcher": 0.0})
    check(st["dispatcher"]["state"] == "PENDING", "run without --file-alarms stays PENDING")
    # unreadable dedup state holds filing
    (TMP / "ops/deadman.json").write_text("[1]")
    check("_state" in DM.check(NOW, filer, ids, {"ops_watch": 0.0, "dispatcher": 0.0}), "unreadable state holds filing")
    # install plan writes nothing
    home = TMP / "home"
    os.environ["HOME"] = str(home)
    DM.install(False, "/x")
    check(not home.exists(), "install plan writes nothing")
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

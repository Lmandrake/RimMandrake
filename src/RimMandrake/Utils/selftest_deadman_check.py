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
    s = DM.stamps()
    check(abs(s["dispatcher"] - (NOW - 60)) < 1 and abs(s["ops_watch"] - (NOW - 60)) < 1, "stamps read (dry dispatcher counts)")
    (TMP / "ops/status.json").write_text("{torn")
    check(DM.stamps()["ops_watch"] is None, "torn status.json -> None, not fresh")

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

#!/usr/bin/env python3
"""Selftest: launch_unit's hooks never write into the unit's result file (item
RIMMANDRAKE_MOVE_END_RECEIPT_OFF_RESULT_FILE_ROLES_FAILED). systemd reopens StandardOutput=file: at offset 0 for every
Exec* step, so a hook that prints (ExecCondition's START, ExecStopPost's ENDED) overwrote the head of a role's result
JSON, read_result got a ValueError, and a run that succeeded was recorded failed (2026-11-18 from 12:54 PM PST).
Real transient `systemd-run --user` units against a temp control store; never the live store.

  intact     a unit launched through launch_unit with StandardOutput=file: and StandardError=file: whose main process
             writes a JSON result: after its ExecStopPost the result file is byte-identical and read_result returns it;
             the stderr file is empty (the hooks wrote nothing there either)
  receipt    the end is still recorded: the control store reads ended with the systemd result, and the journal holds
             the ENDED receipt
  empty      a unit whose main process wrote nothing leaves an empty result file and reads as no result (None)
  garbled    a truncated result still reads as unreadable (None, its stderr kept as err_tail): read_result does not tell
             no result from unreadable, so both are None and both are a failed run, never an answer
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []
UNRUN = []
TMP = tempfile.mkdtemp(prefix="selftest-end-receipt-")
DB = os.path.join(TMP, "c.db")
os.environ["RM_CONTROL_DB"] = DB
os.environ["RM_CONTROL_MODS"] = "Graffiti"
os.environ["RM_CONTROL_TICK_UNIT"] = ""
os.environ["RM_MATURATION_DISPATCH_DIR"] = os.path.join(TMP, "md")
os.environ["RM_CONTROL_CONCEPTS"] = os.path.join(TMP, "concepts")
os.makedirs(os.environ["RM_MATURATION_DISPATCH_DIR"])
os.makedirs(os.environ["RM_CONTROL_CONCEPTS"])
import control as C  # noqa: E402
from role_launch import read_result  # noqa: E402

RESULT = {"type": "result", "subtype": "success", "is_error": False, "result": "x" * 40, "session_id": "s-1"}


def check(ok, msg, got=None):
    print("%s %s%s" % ("ok  " if ok else "FAIL", msg, "" if ok or got is None else "  (got %r)" % (got,)))
    if not ok:
        FAILS.append(msg)


def systemd_ok():
    try:
        r = subprocess.run(["systemctl", "--user", "is-system-running"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() in ("running", "degraded")
    except (OSError, subprocess.SubprocessError):
        return False


def wait_for(pred, secs):
    t = time.monotonic() + secs
    while time.monotonic() < t:
        if pred():
            return True
        time.sleep(0.1)
    return pred()


def launch(name, payload):
    """One role-shaped unit: stdout and stderr to files, as role_launch does. -> (run record, rid, unit)."""
    unit = "rm-probe-receipt-%s-%d" % (name, os.getpid())
    out, err = os.path.join(TMP, name + ".out"), os.path.join(TMP, name + ".err")
    res = C.launch_unit(["systemd-run", "--user", "--quiet", "--collect", "--unit", unit,
                         "-p", "StandardOutput=file:" + out, "-p", "StandardError=file:" + err,
                         "/bin/sh", "-c", payload], {"family": "probe", "unit": unit},
                        capture_output=True, text=True, timeout=30)
    check(res.returncode == 0 and not res.refused, "%s: the unit launches" % name, (res.returncode, res.stderr))
    ended = wait_for(lambda: (C.run_state(res.run) or {}).get("state") == "ended", 15)
    check(ended, "%s: its ExecStopPost ran (the store reads ended)" % name, C.run_state(res.run))
    wait_for(lambda: subprocess.run(["systemctl", "--user", "is-active", "--quiet", unit]).returncode != 0, 5)
    return {"out": out, "err": err}, res.run, unit


def raw(path):
    with open(path, "rb") as f:
        return f.read()


def t_intact():
    body = json.dumps(RESULT)
    src = os.path.join(TMP, "result.json")
    with open(src, "w") as f:
        f.write(body)
    run, rid, unit = launch("intact", "cat " + src)
    check(raw(run["out"]) == body.encode(), "intact: the result file is byte-identical to what the process wrote",
          raw(run["out"])[:80])
    check(read_result(run) == RESULT, "intact: read_result returns the result")
    check(raw(run["err"]) == b"", "intact: the stderr file is empty (no hook wrote there)", raw(run["err"])[:80])
    return rid, unit


def t_receipt(rid, unit):
    st = C.run_state(rid)
    check(st["state"] == "ended" and (st["result"] or "").startswith("success/exited/0"),
          "receipt: the control store records the end with its systemd result", dict(st))
    try:
        j = subprocess.run(["journalctl", "--user", "-t", C.RECEIPT_TAG, "--since", "-10min", "-o", "cat",
                            "--no-pager"], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError, AttributeError) as e:
        check(False, "receipt: the journal could be read", e)
        return
    want = "ENDED %s" % rid
    seen = wait_for(lambda: want in subprocess.run(
        ["journalctl", "--user", "-t", C.RECEIPT_TAG, "--since", "-10min", "-o", "cat", "--no-pager"],
        capture_output=True, text=True, timeout=10).stdout, 5) or want in j.stdout
    check(seen, "receipt: the journal holds the ENDED receipt (tag %s)" % C.RECEIPT_TAG, j.stdout[-200:])


def t_empty():
    run, _, _ = launch("empty", "true")
    check(raw(run["out"]) == b"", "empty: a process that wrote nothing leaves an empty result file", raw(run["out"]))
    check(read_result(run) is None, "empty: it reads as no result")


def t_garbled():
    run, _, _ = launch("garbled", "printf '%s'; echo boom >&2" % '{"type": "result", "subtype": "succ')
    check(raw(run["out"]) == b'{"type": "result", "subtype": "succ', "garbled: the truncated bytes are left as written",
          raw(run["out"]))
    check(read_result(run) is None and run.get("err_tail") == "boom\n",
          "garbled: it reads as unreadable (None), its stderr kept and free of receipts", run.get("err_tail"))


def main():
    if not systemd_ok():
        UNRUN.append("no user systemd here: the receipt can only be proved through a real unit")
    else:
        C.init(DB)
        for t in (t_intact, t_empty, t_garbled):
            print("== %s" % t.__name__)
            try:
                got = t()
                if t is t_intact:
                    print("== t_receipt")
                    t_receipt(*got)
            except Exception as e:      # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (t.__name__, type(e).__name__, e))
    for u in UNRUN:
        print("UNRUN %s" % u)
    shutil.rmtree(TMP, ignore_errors=True)
    if FAILS:
        print("FAILED %d: %s" % (len(FAILS), "; ".join(FAILS[:8])))
        return 1
    if UNRUN:
        print("FAILED: %d part(s) UNRUN (a test that could not look is not a pass)" % len(UNRUN))
        return 1
    print("PASS selftest_end_receipt_off_result")
    return 0


if __name__ == "__main__":
    sys.exit(main())

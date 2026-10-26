"""selftest_bridge_evidence.py - every rimbridge_client call leaves evidence, and a lost mutating reply blocks the
next mutation until reconciled (BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN). Written failing-first. No socket:
RimBridge._request is replaced per case.
"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_bridge_evidence_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import json
import os
import sys
import tempfile

d = tempfile.mkdtemp()
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(d, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402

LOG = os.environ["RIMBRIDGE_EVIDENCE_LOG"]


def rows():
    with open(LOG) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail))
    return bool(cond)


def bridge(reply):
    b = C.RimBridge(token="t")

    def req(method, params=None):
        if isinstance(reply, Exception):
            raise reply
        return reply
    b._request = req
    return b


def main():
    good = []
    b = bridge({"success": True, "n": 3})
    b.call("rimworld/get_game_info", check=False)
    r = rows()
    good.append(case("a read call writes start+end with tool, args hash, identity",
                     [x["ev"] for x in r] == ["start", "end"] and r[0]["tool"] == "rimworld/get_game_info" and
                     r[0].get("args_sha256") and r[0].get("pid") and r[1]["status"] == "ok", r))
    good.append(case("an ok end row carries outcome/transport/timeout (folded from obs_events)",
                     r[1].get("outcome") == "ok" and r[1].get("transport") == "ok" and r[1].get("timeout") is False,
                     r[1]))

    b = bridge(C.RimBridgeError("timed out after 30s waiting for the bridge"))
    try:
        b.call("rimworld/get_game_info", check=False)
    except C.RimBridgeError:
        pass
    good.append(case("a lost READ reply is recorded but blocks nothing", rows()[-1]["status"] == "lost" and
                     not C.outstanding_indeterminate(), rows()[-1]))
    good.append(case("a timed-out end row reads outcome=timeout, timeout=True",
                     rows()[-1].get("outcome") == "timeout" and rows()[-1].get("timeout") is True and
                     rows()[-1].get("transport") == "timeout", rows()[-1]))

    b = bridge(C.RimBridgeError("timed out after 30s waiting for the bridge"))
    try:
        b.call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
    except C.RimBridgeError:
        pass
    good.append(case("a lost MUTATING reply is INDETERMINATE", rows()[-1]["status"] == "INDETERMINATE" and
                     len(C.outstanding_indeterminate()) == 1, rows()[-1]))

    b = bridge({"success": True})
    try:
        b.call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
        refused = False
    except C.IndeterminateError as e:
        refused = "reconcile" in str(e)
    good.append(case("the retry (a dependent mutation) is refused until reconciled", refused))
    b.call("rimworld/get_game_info", check=False)
    good.append(case("read-only calls still run while a mutation is indeterminate", rows()[-1]["status"] == "ok"))

    cid = C.outstanding_indeterminate()[0]["cid"]
    C.reconcile_resolve(cid, "applied", "get_game_info shows the muffalo")
    good.append(case("reconcile clears it and records the verdict", not C.outstanding_indeterminate() and
                     rows()[-1]["ev"] == "reconciled" and rows()[-1]["as"] == "applied", rows()[-1]))
    b.call("jawa/spawn_pawn", {"kind": "Muffalo"}, check=False)
    good.append(case("mutations run again after reconcile", rows()[-1]["status"] == "ok"))

    # a process that dies mid-mutation leaves an in-flight marker -> indeterminate for the next process
    C._inflight_write({"cid": "dead1", "tool": "jawa/destroy_batch", "pid": 999999, "t": "x"})
    good.append(case("an orphaned in-flight mutation (dead process) counts as INDETERMINATE",
                     any(x["cid"] == "dead1" for x in C.outstanding_indeterminate())))
    C.reconcile_resolve("dead1", "not-applied", "selftest")

    # MODCHECK_DRIVERS_HARDEN_OWN_TIMEOUT_MIDCALL: a process under a hard kill deadline (a modcheck driver) must not
    # START a mutating call that could still be in flight at the kill: that strands an UNKNOWN-outcome marker.
    import time as _t
    n0 = len(rows())
    os.environ["RIMBRIDGE_CALL_DEADLINE"] = "%.3f" % (_t.time() + 20)     # 20 s left < the 30 s call timeout
    try:
        bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
        refused = False
    except C.DeadlineError as e:
        refused = "RIMBRIDGE_CALL_DEADLINE" in str(e)
    except Exception:   # noqa: BLE001 - an old client has no DeadlineError: the mutation ran
        refused = False
    good.append(case("a mutation that could outlive the kill deadline is refused before it starts", refused))
    good.append(case("the refused mutation leaves no marker and no start row",
                     not C.outstanding_indeterminate() and len(rows()) == n0, rows()[n0:]))
    good.append(case("a DeadlineError is a RimBridgeError (drivers' broad handlers still catch it)",
                     issubclass(getattr(C, "DeadlineError", Exception), C.RimBridgeError)))
    bridge({"success": True}).call("rimworld/get_game_info", check=False)
    good.append(case("a read still runs inside the deadline window", rows()[-1]["status"] == "ok"))
    os.environ["RIMBRIDGE_CALL_DEADLINE"] = "%.3f" % (_t.time() + 600)
    bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
    good.append(case("a mutation with time to finish before the deadline runs", rows()[-1]["status"] == "ok"))
    os.environ["RIMBRIDGE_CALL_DEADLINE"] = "not-a-number"
    bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
    good.append(case("an unparseable deadline is ignored", rows()[-1]["status"] == "ok"))
    del os.environ["RIMBRIDGE_CALL_DEADLINE"]

    # bounded: rotation
    C.EVIDENCE_MAX_BYTES = 2000
    for _ in range(30):
        b.call("rimworld/get_game_info", check=False)
    good.append(case("the evidence log is bounded (rotated)", os.path.getsize(LOG) <= 4000 and
                     os.path.exists(LOG + ".1"), os.path.getsize(LOG)))

    # an evidence write that fails refuses a MUTATING call (intent must be durable), not a read
    os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(d, "no_such_dir", "x", "calls.jsonl")
    C.EVIDENCE_LOG = os.environ["RIMBRIDGE_EVIDENCE_LOG"]
    open(os.path.join(d, "no_such_dir"), "w").close()      # a FILE where the dir should be: makedirs fails
    try:
        bridge({"success": True}).call("jawa/spawn_pawn", {"kind": "Hare"}, check=False)
        refused = False
    except C.RimBridgeError as e:
        refused = "evidence" in str(e)
    good.append(case("unrecordable intent refuses a mutation", refused))
    try:
        bridge({"success": True}).call("rimworld/get_game_info", check=False)
        ran = True
    except C.RimBridgeError:
        ran = False
    good.append(case("unrecordable evidence does not block a read", ran))

    print("%d/%d" % (sum(good), len(good)))
    return 0 if all(good) else 1


if __name__ == "__main__":
    sys.exit(main())

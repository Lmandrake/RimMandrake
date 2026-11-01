"""selftest_bridge_lock_crossing.py - a mutating bridge call refuses while another live process holds the driver lock
(BRIDGE_LOCK_PROBE_PROOF_CROSSED_HOLDER: a Scald proof connected directly and made a map under a held lock). No game,
no socket: RimBridge._request is replaced, the lock is a temp file, the holder a real sleeping child process.
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile

d = tempfile.mkdtemp(prefix="st_bridge_lock_crossing_")
atexit.register(shutil.rmtree, d, True)
LOCK = os.path.join(d, "DRIVER_LOCK.json")
os.environ["TMPDIR"] = d
os.environ["RIMFLOW_DRIVER_LOCK"] = LOCK
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(d, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
for k in ("RM_HOST_GUARD_GEN", "RM_BRIDGE_CROSS_WHY", "RM_DRIVER_PID"):
    os.environ.pop(k, None)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "rimflow")]
import driver_lock  # noqa: E402
import rimbridge_client as C  # noqa: E402

GOOD = []


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, detail if not cond else ""))
    GOOD.append(bool(cond))


def attempt(tool="jawa/spawn_pawn", host=C.DEFAULT_HOST):
    """-> 'sent' when the call reached the wire, else the DriverHeldError text."""
    b = C.RimBridge(host=host, token="t")
    sent = []
    b._request = lambda method, params=None: sent.append(method) or {"success": True}
    try:
        b.call(tool, {"kind": "Hare"}, check=False)
    except C.DriverHeldError as ex:
        return str(ex)
    return "sent" if sent else "not sent"


def hold(identity, generation=7):
    with open(LOCK, "w", encoding="utf-8") as fh:
        json.dump({"seat": "BENCH", "purpose": "a read-only sitting", "generation": generation,
                   "identity": identity}, fh)


child = subprocess.Popen(["sleep", "60"])
atexit.register(child.kill)
live = dict(driver_lock.my_identity(), pid=child.pid, start=driver_lock._proc_start(child.pid))

case("a free lock lets a mutation through", attempt() == "sent")
hold(live)
r = attempt()
case("a live other holder refuses the mutation", "held by BENCH" in r and "read-only sitting" in r, r)
case("the refusal names the way through", "RM_BRIDGE_CROSS_WHY" in r, r)
case("a read still passes under a holder", attempt("rimworld/get_game_info") == "sent")
case("another machine's game is not judged by this lock", attempt(host="192.0.2.7") == "sent")
os.environ["RM_HOST_GUARD_GEN"] = "7"
case("a child of the holder inherits the take", attempt() == "sent")
os.environ["RM_HOST_GUARD_GEN"] = "6"
case("a stale generation does not", attempt() != "sent")
del os.environ["RM_HOST_GUARD_GEN"]
hold(dict(driver_lock.my_identity()))
case("the holder's own window passes", attempt() == "sent")
hold(live)
os.environ["RM_BRIDGE_CROSS_WHY"] = "owner asked"
case("a deliberate crossing passes", attempt() == "sent")
with open(os.environ["RIMBRIDGE_EVIDENCE_LOG"]) as fh:
    rows = [json.loads(line) for line in fh if line.strip()]
case("and is recorded on the evidence row", "owner asked: " in str(rows[-2:]), rows[-2:])
del os.environ["RM_BRIDGE_CROSS_WHY"]
child.kill()
child.wait()
case("a dead holder does not refuse", attempt() == "sent")
sys.exit(0 if all(GOOD) else 1)

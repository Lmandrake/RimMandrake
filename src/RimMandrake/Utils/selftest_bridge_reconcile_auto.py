"""selftest_bridge_reconcile_auto.py - BRIDGE_PENDINGCALL_RECONCILE_INDETERMINATE. No game, no socket.

A lost-reply mutation left marker b7164851922b4797 (jawa/safe_advance, prove_sandswim.py, dead writer) and every later
live proof died on IndeterminateError (PIT_LIP_OCCLUDER_FIX_GHOSTED_HALVES A1-A3) because nothing ran the reconcile.
rimbridge_client.reconcile_auto() now settles, as "moot", exactly the markers whose outcome cannot matter, and call()
runs it before refusing. Each case below holds one side of that line.
"""
import atexit
import json
import os
import shutil
import sys
import tempfile
import time

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_bridge_reconcile_auto_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
D = tempfile.mkdtemp()
os.environ["RIMBRIDGE_EVIDENCE_LOG"] = os.path.join(D, "bridge_calls.jsonl")
os.environ["RIMBRIDGE_SESSION_LOG"] = ""
os.environ["RIMBRIDGE_ALIVE_PROBE"] = "off"
os.environ["RIMFLOW_DRIVER_LOCK"] = os.path.join(D, "no_driver_lock.json")
for _k in ("GABP_TOKEN", "GABP_SERVER_PORT", "RIMBRIDGE_HOST", "RIMBRIDGE_DEADLINE"):
    os.environ.pop(_k, None)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rimbridge_client as C  # noqa: E402

DEAD_PID = 2 ** 22 + 12345          # above Linux pid_max default: no process holds it
T_CALL = "2026-11-04T02:14:39Z"
T_EPOCH = C._iso_epoch(T_CALL)
SAME_GAME = [T_EPOCH - 3600.0]       # the game that was running when the call went out
NEW_GAME = [T_EPOCH + 3000.0]        # a game started after the call
GOOD = []


def case(name, cond, detail=""):
    print("%-4s %s %s" % ("ok" if cond else "FAIL", name, "" if cond else detail))
    GOOD.append(bool(cond))


def rows():
    with open(os.environ["RIMBRIDGE_EVIDENCE_LOG"], encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def clear():
    for x in C.outstanding_indeterminate():
        C.reconcile_resolve(x["cid"], "not-applied", "selftest cleanup")
    C._UNRESOLVED.clear()


def marker(cid, tool, pid=DEAD_PID, status="INDETERMINATE", **kw):
    rec = dict({"ev": "start", "cid": cid, "t": T_CALL, "tool": tool, "mutating": True, "pid": pid, "os": os.name,
                "pid_start": None, "script": "prove_sandswim.py", "status": status}, **kw)
    C._inflight_write(rec)
    return rec


def bridge():
    b = C.RimBridge(token="t")
    b._request = lambda method, params=None: {"success": True}
    return b


def left_cids(starts):
    return sorted(r["cid"] for r in C.reconcile_auto(starts=starts)[1])


def try_call(tool, starts):
    real = C.game_starts
    C.game_starts = lambda: starts
    try:
        bridge().call(tool, {"pause": True} if tool == "rimworld/pause_game" else {}, check=False)
        return None
    except C.IndeterminateError as e:
        return str(e)
    finally:
        C.game_starts = real


# 1 the PIT_LIP replay: same game, dead writer, repeat-safe safe_advance -> the next proof's pause_game runs
clear()
marker("b7164851922b4797", "jawa/safe_advance")
err = try_call("rimworld/pause_game", SAME_GAME)
last = [r for r in rows() if r.get("ev") == "reconciled"][-1]
case("PIT_LIP replay: a dead writer's safe_advance no longer refuses the next proof's pause_game", err is None, err)
case("... it is recorded as reconciled 'moot' with the reason, and the marker is gone",
     last.get("cid") == "b7164851922b4797" and last.get("as") == "moot" and "repeat-safe" in last.get("note", "")
     and not C.outstanding_indeterminate(), last)
case("... the mutation itself then ran and answered", rows()[-1].get("status") == "ok", rows()[-1])

# 2 same game, dead writer, NOT repeat-safe -> still refused, still listed
clear()
marker("d1", "jawa/destroy_batch")
err = try_call("rimworld/pause_game", SAME_GAME)
case("same game, a dead writer's destroy_batch still refuses (its effect may be half on the map)",
     err is not None and "d1 jawa/destroy_batch" in err, err)
case("... and stays outstanding for a human verdict", [r["cid"] for r in C.outstanding_indeterminate()] == ["d1"])

# 3 the game process it went to is gone -> anything is moot
case("a game started after the call makes even destroy_batch moot", left_cids(NEW_GAME) == [])
marker("d2", "jawa/spawn_pawn")
case("no game running makes it moot", left_cids([]) == [])
case("... its note names the gone game", "game process it went to is gone" in rows()[-1].get("note", ""), rows()[-1])

# 4 fail closed when the instrument cannot see
marker("d3", "jawa/spawn_pawn")
case("game starts unknown (None, e.g. WSL) settles nothing that is not repeat-safe", left_cids(None) == ["d3"])
case("two games, one older than the call: not 'gone'", left_cids([SAME_GAME[0], NEW_GAME[0]]) == ["d3"])
case("a game started inside the slack of the call's whole-second stamp is not 'after'",
     left_cids([T_EPOCH + 1.0]) == ["d3"])
case("game_starts() off Windows is None, never [] (which would read as 'gone')",
     os.name == "nt" or C.game_starts() is None)
clear()

# 5 a live writer keeps its own unknown, even for a repeat-safe tool in the same game
marker("live1", "jawa/safe_advance", pid=os.getpid(), pid_start=C._proc_start(os.getpid()))
case("a LIVE writer's repeat-safe marker is not settled for it", left_cids(SAME_GAME) == ["live1"])
clear()

# 6 an unreadable marker and an in-process unwritten marker are never settled
os.makedirs(C._inflight_dir(), exist_ok=True)
with open(os.path.join(C._inflight_dir(), "junk1.json"), "w") as fh:
    fh.write("{not json")
case("an unreadable marker is never settled, even with the game gone", left_cids([]) == ["junk1"])
os.remove(os.path.join(C._inflight_dir(), "junk1.json"))
C._UNRESOLVED["u1"] = {"cid": "u1", "tool": "jawa/safe_advance", "t": T_CALL, "status": "INDETERMINATE",
                       "pid": DEAD_PID}
case("a marker this process failed to write is never settled", left_cids([]) == ["u1"])
clear()

# 7 an unparseable timestamp cannot prove the game is newer
marker("badt", "jawa/spawn_pawn", t="x")
case("an unparseable marker time settles nothing by the game-gone rule", left_cids([]) == ["badt"])
clear()

# 8 the CLI: --reconcile --auto settles and exits 0; bare --reconcile only lists
marker("cli1", "jawa/safe_advance")
real = C.game_starts
C.game_starts = lambda: SAME_GAME
try:
    rc_list = C._main(["--reconcile"])
    still = [r["cid"] for r in C.outstanding_indeterminate()]
    rc_auto = C._main(["--reconcile", "--auto"])
finally:
    C.game_starts = real
case("CLI: bare --reconcile lists without settling (exit 1)", rc_list == 1 and still == ["cli1"], (rc_list, still))
case("CLI: --reconcile --auto settles it (exit 0)", rc_auto == 0 and not C.outstanding_indeterminate(), rc_auto)
rc = C._main(["--reconcile", "--resolve", "x9", "--as", "moot", "--note", "read: no map"])
case("CLI: --as moot is an accepted verdict", rc == 0 and rows()[-1].get("as") == "moot", rc)

# 9 the repeat-safe list is the reviewed four, each with its reason
case("REPEAT_SAFE_TOOLS is exactly the reviewed set, each with a reason",
     sorted(C.REPEAT_SAFE_TOOLS) == ["jawa/safe_advance", "jawa/weather_set", "rimworld/pause_game",
                                     "rimworld/set_time_speed"] and all(C.REPEAT_SAFE_TOOLS.values()))

ok = all(GOOD)
print("%s: %d/%d" % ("PASS" if ok else "FAIL", sum(GOOD), len(GOOD)))
sys.exit(0 if ok else 1)

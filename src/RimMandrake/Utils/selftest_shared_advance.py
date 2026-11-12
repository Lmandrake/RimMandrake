"""speed_20261112 step 1d/2c: the ONE shared clock advance (tickburst_step.advance) and the client's reroute of long
rimworld/step_game_ticks calls onto it, with its single fallback switch (RM_STEP_PATH=slow), plus the exit report's
call-count and long-step warnings (rimbridge_client.split_report).

Offline: a RimBridge built without a socket, its `_call_one` replaced by a recorder that plays a companion with (or
without) jawa/safe_advance. SELFTEST_SHARED_ADVANCE_UTILS points the imports at another Utils copy (the fail-before run)."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UT = os.environ.get("SELFTEST_SHARED_ADVANCE_UTILS") or HERE
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, UT)
sys.path.insert(1, os.path.join(UT, "modcheck"))
os.environ["RM_BRIDGE_SPLIT"] = "0"
import rimbridge_client as RB  # noqa: E402
import tickburst_step as TS  # noqa: E402

fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


class Recorder(object):
    """Plays the companion: safe_advance status/start, step_game_ticks; records every tool reaching the socket."""

    def __init__(self, has_safe=True):
        self.sent, self.has_safe, self.tick = [], has_safe, 1000

    def __call__(self, tool, params=None, check=True):
        p = dict(params or {})
        self.sent.append((tool, p))
        if tool == "jawa/safe_advance":
            if not self.has_safe:
                return {"success": False, "error": "unknown tool"}
            if p.get("action") == "status":
                return {"success": True, "state": "idle", "ticksGame": self.tick}
            self.tick += int(p["ticks"])
            return {"success": True, "state": "done", "executed": int(p["ticks"])}
        if tool == "rimworld/step_game_ticks":
            self.tick += int(p.get("ticks") or 1)
            return {"success": True, "status": "completed"}
        return {"success": True}


def bridge(has_safe=True):
    b = RB.RimBridge.__new__(RB.RimBridge)
    rec = Recorder(has_safe)
    b._call_one = rec
    return b, rec


def tools(rec):
    return [t for t, _ in rec.sent]


def case(name, fn):
    try:
        fn()
    except Exception as ex:  # noqa: BLE001 - a crash is a failed row, named
        check(False, name, "raised %s: %s" % (type(ex).__name__, str(ex)[:160]))


def long_step_goes_fast():
    b, rec = bridge()
    r = b.call("rimworld/step_game_ticks", {"ticks": 2500, "pauseFirst": True, "timeoutMs": 240000}, check=False)
    starts = [p for t, p in rec.sent if t == "jawa/safe_advance" and p.get("action") != "status"]
    check("rimworld/step_game_ticks" not in tools(rec) and len(starts) == 1 and starts[0].get("ticks") == 2500
          and starts[0].get("stopOn") == "cancel", "long_step_sent_through_safe_advance_no_latch", str(tools(rec)))
    check(r.get("success") is True and r.get("completedTicks") == 2500 and r.get("path") == "jawa/safe_advance",
          "long_step_reply_shaped_like_step_game_ticks", str(r))
    b.call("rimworld/step_game_ticks", {"ticks": 5000}, check=False)
    st = [t for t, p in rec.sent if t == "jawa/safe_advance" and p.get("action") == "status"]
    big = [p.get("ticks") for t, p in rec.sent if t == "jawa/safe_advance" and p.get("action") != "status"][1:]
    check(big == [2500, 2500] and len(st) == 1, "5000_ticks_two_chunks_one_status_per_bridge", "%s status=%d" % (big, len(st)))


def slow_switch():
    os.environ["RM_STEP_PATH"] = "slow"
    try:
        b, rec = bridge()
        b.call("rimworld/step_game_ticks", {"ticks": 2500, "pauseFirst": True}, check=False)
        check(tools(rec) == ["rimworld/step_game_ticks"], "RM_STEP_PATH_slow_is_one_tick_per_frame", str(tools(rec)))
        r = TS.advance(lambda t, **kw: rec(t, kw), 300, force_fast=True)
        check(tools(rec)[-1] == "rimworld/step_game_ticks" and r.get("success"), "switch_beats_force_fast", str(tools(rec)))
    finally:
        os.environ.pop("RM_STEP_PATH", None)


def literal_cases():
    b, rec = bridge()
    b.call("rimworld/step_game_ticks", {"ticks": 25, "pauseFirst": True}, check=False)
    check(tools(rec) == ["rimworld/step_game_ticks"], "short_step_left_alone", str(tools(rec)))
    b, rec = bridge()
    with TS.one_tick_per_frame():
        b.call("rimworld/step_game_ticks", {"ticks": 180, "pauseFirst": True}, check=False)
    check(tools(rec) == ["rimworld/step_game_ticks"], "one_tick_per_frame_block_reaches_the_tool", str(tools(rec)))
    b, rec = bridge()
    b.call("rimworld/step_game_ticks", {"ticks": 600, "pauseFirst": False}, check=False)
    check(tools(rec) == ["rimworld/step_game_ticks"], "unpaused_step_left_alone", str(tools(rec)))


def no_safe_advance_falls_back():
    b, rec = bridge(has_safe=False)
    r = b.call("rimworld/step_game_ticks", {"ticks": 2500, "pauseFirst": True}, check=False)
    st = [p for t, p in rec.sent if t == "rimworld/step_game_ticks"]
    check(len(st) == 1 and st[0].get("ticks") == 2500 and r.get("path") == "rimworld/step_game_ticks",
          "old_companion_falls_back_once_no_recursion", str(tools(rec)))


def force_fast_short():
    rec = Recorder()
    r = TS.advance(lambda t, **kw: rec(t, kw), 25, force_fast=True)
    check("rimworld/step_game_ticks" not in tools(rec) and r.get("completedTicks") == 25, "force_fast_short_step", str(tools(rec)))


def split_warnings():
    RB._TOOL_STATS.clear()
    del RB._LONG_STEPS[:]
    for _ in range(51):
        RB._note_call("jawa/mod_settings_field", {"action": "get"}, 66, True)
    RB._note_call("rimworld/step_game_ticks", {"ticks": 2500}, 41670, False)
    RB._note_call("rimworld/step_game_ticks", {"ticks": 60}, 1000, False)
    out = "\n".join(RB.split_report())
    check("WARN 51 calls of jawa/mod_settings_field" in out, "warns_over_50_calls_of_one_tool", out[:200])
    check("WARN 1 rimworld/step_game_ticks call(s) over 60 ticks" in out, "warns_long_step_reaching_game", out[:300])
    check(re.search(r"ticks 42\.7 / reads 3\.4", out) is not None, "time_split_load_ticks_reads", out.splitlines()[0])
    RB._TOOL_STATS.clear()
    del RB._LONG_STEPS[:]


def callers():
    ek = open(os.path.join(REPO, "src/RimMandrake/ExplosiveKnockback/proof/storeroom_pit_proof.py"), encoding="utf-8").read()
    check("ticks=25," not in ek, "knockback_no_25_tick_loop")
    v2 = open(os.path.join(REPO, "src/RimMandrake/FlowWorks/northstar/validation_v2.py"), encoding="utf-8").read()
    i = v2.find("ticks=FLYER_LAND_TICKS")
    check(i > 0 and "TS.one_tick_per_frame()" in v2[i - 260:i], "flyer_landing_stays_one_tick_per_frame")


for n, f in (("long_step_goes_fast", long_step_goes_fast), ("slow_switch", slow_switch), ("literal_cases", literal_cases),
             ("no_safe_advance_falls_back", no_safe_advance_falls_back), ("force_fast_short", force_fast_short),
             ("split_warnings", split_warnings), ("callers", callers)):
    case(n, f)
print("%d FAIL" % len(fails) if fails else "ALL OK")
sys.exit(1 if fails else 0)

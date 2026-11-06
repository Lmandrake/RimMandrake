#!/usr/bin/env python3
"""selftest_shotsettle.py - the paused tween barrier for screenshots (SHOTSETTLE_BUILD_PAUSED_BARRIER).

Offline, no game:
1. HELPER (rimbench/shotsettle.py) against a fake bridge:
   - order is pause -> ticksGame -> clear_ui -> settle_tweens -> take_screenshot -> ticksGame;
   - a capture during which ticksGame moves is REFUSED, as is a settle that saw other ticks,
     a refused settle, and a ticksGame read that is not an integer (UNMEASURED, never 0);
   - rimbench Session.look(settle=True) goes through the barrier; settle=False does not.
2. COMPANION SOURCE (JawaBenchShotSettleTools.cs):
   - registers jawa/settle_tweens, resets each spawned pawn's tweener (ResetTweenedPosToRoot),
     refuses an unpaused game unless pauseFirst, reports ticksBefore/ticksAfter;
   - calls nothing that advances ticks (DoSingleTick, step, a non-Paused TimeSpeed).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "Utils"))
sys.path.insert(0, UTILS)
from rimbench.shotsettle import settled_shot, ShotSettleError  # noqa: E402

CS = os.path.join(HERE, "JawaBench.BridgeTools", "JawaBenchShotSettleTools.cs")
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


class Fake:
    def __init__(self, tick=1000, drift=0, settle=None, ticks_value=None):
        self.tick, self.drift, self.settle, self.ticks_value = tick, drift, settle, ticks_value
        self.log = []

    def __call__(self, tool, **p):
        self.log.append(tool)
        if tool == "rimworld/pause_game":
            return {"success": True}
        if tool == "rimworld/get_game_info":
            return {"success": True, "ticksGame": self.tick if self.ticks_value is None else self.ticks_value}
        if tool == "jawa/clear_ui":
            return {"success": True}
        if tool == "jawa/settle_tweens":
            return self.settle or {"success": True, "ticksBefore": self.tick, "ticksAfter": self.tick,
                                   "settled": 3, "maxShiftCells": 4.5}
        if tool == "rimworld/take_screenshot":
            self.tick += self.drift
            return {"success": True, "path": "C:/shots/%s.png" % p.get("fileName")}
        return {"success": False, "message": "no tool " + tool}


def raises(fn):
    try:
        fn()
    except ShotSettleError as e:
        return str(e)
    return None


# ---- 1. helper -----------------------------------------------------------------
f = Fake()
r = settled_shot(f, "a")
check("order pause, ticks, clear_ui, settle, shot, ticks",
      f.log == ["rimworld/pause_game", "rimworld/get_game_info", "jawa/clear_ui", "jawa/settle_tweens",
                "rimworld/take_screenshot", "rimworld/get_game_info"], f.log)
check("tick-free shot returns equal ticks and the settle counts",
      r["ticksBefore"] == r["ticksAfter"] == 1000 and r["settled"] == 3 and r["path"].endswith("a.png"), r)
check("a shot that advanced ticks is refused", raises(lambda: settled_shot(Fake(drift=2), "b")) is not None)
check("a settle that saw other ticks is refused",
      raises(lambda: settled_shot(Fake(settle={"success": True, "ticksBefore": 1000, "ticksAfter": 1001}), "c"))
      is not None)
check("a refused settle is refused",
      raises(lambda: settled_shot(Fake(settle={"success": False, "message": "not paused"}), "d")) is not None)
msg = raises(lambda: settled_shot(Fake(ticks_value="x"), "e"))
check("a non-integer ticksGame is UNMEASURED, not a pass", msg is not None and "UNMEASURED" in msg, msg)
check("a missing ticksGame is UNMEASURED",
      (raises(lambda: settled_shot(lambda t, **p: {"success": True}, "g")) or "").startswith("UNMEASURED"))

# Session.look wiring, without a live bridge: bind the methods onto a stand-in.
from rimbench import core  # noqa: E402


class Stand:
    _shots = 0
    _shot_name = core.Session._shot_name
    _shoot = core.Session._shoot
    look = core.Session.look
    frame = core.Session.frame

    def __init__(self):
        self.fake = Fake()

    def call(self, tool, **p):
        return self.fake(tool, **p)


s = Stand()
s.look(5, 5, settle=True)
check("look(settle=True) runs the barrier", "jawa/settle_tweens" in s.fake.log
      and s.fake.log[-1] == "rimworld/get_game_info", s.fake.log)
s2 = Stand()
s2.look(5, 5)
check("look() default is unchanged (no settle)", "jawa/settle_tweens" not in s2.fake.log, s2.fake.log)

s3 = Stand()
s3.frame(1, 1, 4, 4, settle=True)
check("frame(settle=True) runs the barrier", "jawa/settle_tweens" in s3.fake.log, s3.fake.log)


class PauseFails(Fake):
    def __call__(self, tool, **p):
        if tool == "rimworld/pause_game":
            return {"success": False, "message": "no game"}
        return Fake.__call__(self, tool, **p)


class UiFails(Fake):
    def __call__(self, tool, **p):
        if tool == "jawa/clear_ui":
            return {"success": False, "message": "log open"}
        return Fake.__call__(self, tool, **p)


check("a failed pause is refused", raises(lambda: settled_shot(PauseFails(), "h")) is not None)
check("a failed clear_ui is refused", raises(lambda: settled_shot(UiFails(), "i")) is not None)

# ---- 2. companion source -------------------------------------------------------
src = open(CS, encoding="utf-8").read()
code = "\n".join(l for l in src.splitlines() if not l.strip().startswith("//"))
check("tool jawa/settle_tweens registered", '"jawa/settle_tweens"' in code)
check("resets each spawned pawn's tweener",
      "AllPawnsSpawned" in code and "tweener" in code and ".ResetTweenedPosToRoot()" in code)
check("refuses an unpaused game unless pauseFirst",
      re.search(r"if \(!tm\.Paused\)\s*\{\s*if \(!pauseFirst\)\s*return Fail", code) is not None)
check("reports ticksBefore and ticksAfter", "ticksBefore = before" in code and "ticksAfter = after" in code)
bad = [w for w in ("DoSingleTick", "step_game_ticks", "safe_advance", "TimeSpeed.Normal",
                   "TimeSpeed.Fast", "TimeSpeed.Superfast", "TimeSpeed.Ultrafast", "TickManagerUpdate")
       if w in code]
check("calls nothing that advances ticks", not bad, bad)
check("the only speed it sets is Paused",
      re.findall(r"CurTimeSpeed\s*=\s*([\w.]+)", code) == ["TimeSpeed.Paused"])

print("%d FAIL" % len(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)

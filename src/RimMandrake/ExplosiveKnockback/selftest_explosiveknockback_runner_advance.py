#!/usr/bin/env python3
"""RIMMANDRAKE_ADVANCE_PIT_FETCH_PAST_ONE_TICK_A_FRAME: knockback_runner.advance_scene moves a long --ticks through
jawa/safe_advance (tickburst_step.advance, <=2500-tick chunks, stopOn=cancel), loops past its halts to the target
tick, and reports a short advance instead of reading the scene's verdict as if it had run its full time.

Offline: a fake bridge plays the companion (safe_advance status/start, halts on a schedule, a stuck refusal).
SELFTEST_EK_RUNNER points at another knockback_runner.py (the fail-before run)."""
import ast
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RUNNER = os.environ.get("SELFTEST_EK_RUNNER") or os.path.join(HERE, "knockback_runner.py")
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
os.environ.pop("RM_STEP_PATH", None)
fails = []


def check(ok, name, why=""):
    print("%s %s %s" % ("ok  " if ok else "FAIL", name, why))
    if not ok:
        fails.append(name)


class FakeBridge(object):
    """`halts`: game ticks at which safe_advance stops (a mental break, a social fight); `stuck`: every start executes
    nothing (a refusal)."""

    def __init__(self, halts=(), stuck=False, tick=5000):
        self.tick, self.halts, self.stuck, self.sent = tick, sorted(halts), stuck, []

    def call(self, tool, params=None, check=True):
        p = dict(params or {})
        self.sent.append((tool, p))
        if tool == "rimworld/step_game_ticks":
            self.tick += int(p.get("ticks") or 1)
            return {"success": True, "status": "completed"}
        if tool != "jawa/safe_advance":
            return {"success": True}
        if p.get("action") == "status":
            return {"success": True, "state": "idle", "ticksGame": self.tick}
        if p.get("action") == "cancel":
            return {"success": True}
        if self.stuck:
            return {"success": True, "state": "refused", "executed": 0, "error": "populated map refusal"}
        n = int(p["ticks"])
        nxt = [h for h in self.halts if self.tick < h <= self.tick + n]
        if nxt:
            ex = nxt[0] - self.tick
            self.tick = nxt[0]
            self.halts.remove(nxt[0])
            return {"success": True, "state": "stopped", "executed": ex, "ticksGame": self.tick,
                    "stopBy": {"detail": "mental state SocialFighting"}}
        self.tick += n
        return {"success": True, "state": "done", "executed": n, "ticksGame": self.tick}


def starts(fb):
    return [p for t, p in fb.sent if t == "jawa/safe_advance" and p.get("action") not in ("status", "cancel")]


def load():
    spec = importlib.util.spec_from_file_location("knockback_runner_under_test", RUNNER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def case(name, fn, *a):
    try:
        fn(*a)
    except Exception as ex:  # noqa: BLE001 - a crash is a failed row, named
        check(False, name, "raised %s: %s" % (type(ex).__name__, str(ex)[:200]))


def long_fetch(m):
    fb = FakeBridge()
    r = m.advance_scene(fb, 60000)
    st = starts(fb)
    check(not [t for t, _ in fb.sent if t == "rimworld/step_game_ticks"] and st and max(p["ticks"] for p in st) <= 2500
          and all(p.get("stopOn") == "cancel" for p in st), "60000_ticks_through_safe_advance_chunks",
          "%d starts, tools %s" % (len(st), sorted(set(t for t, _ in fb.sent))))
    check(r.get("reached") is True and fb.tick == 65000 and r.get("ticksGame") == 65000,
          "60000_ticks_reach_the_target_tick", str({k: r.get(k) for k in ("reached", "target", "ticksGame")}))


def loops_past_halts(m):
    fb = FakeBridge(halts=(5700, 19000, 19001, 41234, 64999))
    r = m.advance_scene(fb, 60000)
    check(r.get("reached") is True and fb.tick == 65000, "loops_past_mental_break_halts_to_target",
          "tick %d %s" % (fb.tick, r))
    check(len(r.get("halts") or []) >= 1, "halts_are_reported_not_swallowed", str(r.get("halts")))


def stuck_reports_short(m):
    fb = FakeBridge(stuck=True)
    r = m.advance_scene(fb, 60000)
    check(r.get("reached") is False and len(starts(fb)) <= 3, "a_refusal_ends_short_without_spinning",
          "%d starts %s" % (len(starts(fb)), r))


def short_ticks(m):
    fb = FakeBridge()
    r = m.advance_scene(fb, 300)
    check(r.get("reached") is True and fb.tick == 5300, "default_300_ticks_still_reach_target", str(r))


def main_wired():
    src = open(RUNNER, encoding="utf-8").read()
    tree = ast.parse(src)
    direct = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and n.args
              and isinstance(n.args[0], ast.Constant) and n.args[0].value == "rimworld/step_game_ticks"]
    mains = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main"]
    uses = bool(mains) and any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "advance_scene"
                               for n in ast.walk(mains[0]))
    check(not direct and uses, "main_advances_through_advance_scene_not_step_game_ticks",
          "direct step_game_ticks calls at %s, advance_scene in main: %s" % (direct, uses))


try:
    M = load()
except Exception as ex:  # noqa: BLE001
    M = None
    check(False, "runner_imports", "%s: %s" % (type(ex).__name__, ex))
if M is not None and not hasattr(M, "advance_scene"):
    check(False, "advance_scene_exists", "knockback_runner.py has no advance_scene")
elif M is not None:
    for nm, fn in (("long_fetch", long_fetch), ("loops_past_halts", loops_past_halts),
                   ("stuck_reports_short", stuck_reports_short), ("short_ticks", short_ticks)):
        case(nm, fn, M)
case("main_wired", main_wired)
print("%s runner advance: %d failed" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)

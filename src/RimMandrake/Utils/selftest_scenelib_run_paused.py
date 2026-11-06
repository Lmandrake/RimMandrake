"""Offline selftest: scenes/scenelib.run advances paused through validation_core._BridgeBase.ticks
(SCENERUN_MIGRATE_OFF_UNPAUSED_PLAY, tickburst final.md L-f).

Proves, against a fake bridge: run(n) moves ticksGame by exactly n through jawa/safe_advance with the scene's narrow
stopOn, never calls rimworld/play_for or jawa/set_game_speed, chunks long runs, raises on a short delta or a latch stop
(never heals), falls back to step_game_ticks without safe_advance, and leaves every other _BridgeBase caller's
advance_chunk call shape unchanged."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modcheck"))
os.environ["RIMBRIDGE_GOVERNOR_LOG"] = ""   # the fake latch stop below must not write a real governor_stops.jsonl

from scenes import scenelib as S  # noqa: E402
import validation_core as V  # noqa: E402
import clockgate as cg  # noqa: E402

FAILS = []


def ok(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


class FakeGame(object):
    """Answers the calls run() makes. `short` ticks are silently lost per safe_advance; `stop` answers state=stopped."""

    def __init__(self, safe=True, short=0, stop=None):
        self.t, self.safe, self.short, self.stop, self.log = 1000, safe, short, stop, []

    def call(self, tool, params, check=False):
        self.log.append((tool, dict(params)))
        if tool == "jawa/time_clock":
            return {"success": True, "ticksGame": self.t, "paused": True}
        if tool == "jawa/safe_advance":
            if not self.safe:
                return {"success": False, "error": "unknown tool"}
            if params.get("action") == "status":
                return {"success": True, "ticksGame": self.t, "advance": None}
            n = int(params["ticks"])
            if self.stop:
                self.t += 5
                return {"success": True, "state": "stopped", "requested": n, "executed": 5,
                        "stopBy": {"kind": self.stop, "severity": "critical", "detail": "fake " + self.stop}}
            self.t += n - self.short
            return {"success": True, "state": "done", "requested": n, "executed": n, "tickFrom": self.t - n,
                    "tickTo": self.t}
        if tool == "rimworld/step_game_ticks":
            self.t += int(params["ticks"])
            return {"success": True}
        return {"success": True}

    def tools(self):
        return [c[0] for c in self.log]


def fresh(game):
    S._c, S._B = game, None
    return game


def main():
    # 1. exact, paused, one safe_advance, the scene's stopOn
    g = fresh(FakeGame())
    d = S.run(600)
    adv = [p for t, p in g.log if t == "jawa/safe_advance" and p.get("action") != "status"]
    ok(d == 600 and g.t == 1600, "run(600) moves ticksGame by exactly 600 (got %s)" % d)
    ok(len(adv) == 1 and adv[0]["ticks"] == 600, "one safe_advance call of 600 ticks (%s)" % adv)
    ok(adv and adv[0].get("stopOn") == S.SCENE_STOP_ON, "safe_advance carries the scene stopOn (%s)" % (adv[0].get("stopOn") if adv else None))
    ok("rimworld/play_for" not in g.tools() and "jawa/set_game_speed" not in g.tools(),
       "no play_for and no set_game_speed: the game is never unpaused")
    for k in ("death", "downed", "hurt", "starving", "mental"):
        ok(k not in S.SCENE_STOP_ON.split(","), "scene stopOn leaves out %s (scenes do it on purpose)" % k)

    # 2. a long run is chunked at SAFE_CHUNK_MAX and still exact
    g = fresh(FakeGame())
    d = S.run(6000)
    adv = [p["ticks"] for t, p in g.log if t == "jawa/safe_advance" and p.get("action") != "status"]
    ok(d == 6000 and sum(adv) == 6000 and max(adv) <= cg.SAFE_CHUNK_MAX, "run(6000) chunked %s, exact" % adv)

    # 3. a delta that is not n raises instead of returning a wrong count
    fresh(FakeGame(short=3))
    try:
        S.run(600)
        ok(False, "a short ticksGame delta raises")
    except RuntimeError as e:
        ok("not 600" in str(e), "a short ticksGame delta raises: %s" % e)

    # 4. a latch stop in the scene list raises, and nothing heals or removes anything
    g = fresh(FakeGame(stop="modal_stuck"))
    try:
        S.run(600)
        ok(False, "a modal_stuck stop raises")
    except cg.GovernorStop:
        ok(True, "a modal_stuck stop raises GovernorStop (loud, where play_for used to hang)")
    ok(not any(t not in ("jawa/time_clock", "jawa/safe_advance") for t in g.tools()),
       "the stop sent no recovery call (%s)" % sorted(set(g.tools())))

    # 5. no safe_advance: legacy step_game_ticks, still exact, still no play_for
    g = fresh(FakeGame(safe=False))
    d = S.run(300)
    ok(d == 300 and "rimworld/step_game_ticks" in g.tools() and "rimworld/play_for" not in g.tools(),
       "without safe_advance run(300) steps 300 through step_game_ticks")

    # 6. run(0) and the ignored speed argument
    g = fresh(FakeGame())
    ok(S.run(0) == 0 and not g.log, "run(0) makes no call")
    ok(S.run(60, speed=4) == 60 and "jawa/set_game_speed" not in g.tools(), "speed= is accepted and ignored")
    ok(S.step is S.run, "step is still run")

    # 7. every other _BridgeBase keeps the two-argument advance_chunk call (monkeypatches with that shape still work)
    seen = []
    keep = cg.advance_chunk
    cg.advance_chunk = lambda session, n: seen.append(n) or n
    try:
        class B(V._BridgeBase):
            def _raw(self, tool, kw):
                return {"success": True}
        r = B().ticks(100)
    finally:
        cg.advance_chunk = keep
    ok(seen == [100] and r.get("advanced") == 100 and V._BridgeBase.stop_on == "default",
       "a default _BridgeBase calls advance_chunk(self, n) unchanged")

    S._c, S._B = None, None
    print("selftest_scenelib_run_paused: %s" % ("FAIL %d" % len(FAILS) if FAILS else "OK"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

"""Offline tests of stage_review.py: one function per promise in design/specs/2026-11-23-stage-review-midday/boundary.md.
A fake bridge that holds a clock, a weather and a few things; no game. Exit 0 all hold, 1 a promise is broken."""
import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stage_review as S  # noqa: E402

FAILS = []


def check(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


class FakeRB:
    def __init__(self, hour=12.0, weather="Rain", things=(), hour_fault=None, clock_stuck=False, weather_stuck=False,
                 step_dead=False):
        self.t = int(round(hour * 2500)) + 600000
        self.weather, self.age, self.things = weather, 99999, list(things)
        self.hour_fault, self.clock_stuck = hour_fault, clock_stuck
        self.weather_stuck, self.step_dead = weather_stuck, step_dead
        self.shots, self.calls = [], []

    def call(self, tool, p=None):
        p = p or {}
        self.calls.append((tool, p))
        if tool == "jawa/glow_at":
            if self.hour_fault:
                return dict(self.hour_fault)
            return {"success": True, "hour": (self.t / 2500.0) % 24, "ticksGame": self.t}
        if tool == "jawa/time_set_ticks":
            if not p.get("timeException"):
                return {"success": False, "message": "REFUSED: populated map"}
            if not self.clock_stuck:
                self.t = p["ticks"]
            return {"success": True}
        if tool == "rimworld/step_game_ticks":
            if self.step_dead:
                raise RuntimeError("timed out")
            self.t += p["ticks"]
            self.age += p["ticks"]
            return {"success": True}
        if tool == "rimworld/get_game_info":
            return {"ticksGame": self.t}
        if tool == "jawa/weather_set":
            if not self.weather_stuck and p["weather"] != self.weather:
                self.weather, self.age = p["weather"], 0
            return {"success": True, "after": self.weather}
        if tool == "rimworld/take_screenshot":
            self.shots.append((p["fileName"], (self.t / 2500.0) % 24, self.weather, self.age))
            return {"path": p["fileName"] + ".png"}
        if tool == "jawa/list_things":
            rows = [t for t in self.things if p["group"] == "HaulableEver" or t["id"].startswith("Chunk")]
            return {"success": True, "things": rows, "countMatched": len(rows), "isCompleteList": True}
        if tool == "jawa/destroy_batch":
            if p.get("categories") != "Item":
                return {"success": True, "destroyed": 0}
            cells = {tuple(int(v) for v in c.split(",")) for c in p["rects"].split(";") if c.count(",") == 1}
            rects = [tuple(int(v) for v in c.split(",")) for c in p["rects"].split(";") if c.count(",") == 3]

            def hit(t):
                return (t["x"], t["z"]) in cells or any(x <= t["x"] < x + w and z <= t["z"] < z + h for x, z, w, h in rects)
            n = len(self.things)
            self.things = [t for t in self.things if not hit(t)]
            return {"success": True, "destroyed": n - len(self.things)}
        return {"success": True}


def quiet(fn, *a):
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        return fn(*a)


def refuses(fn, *a):
    try:
        quiet(fn, *a)
    except RuntimeError:
        return True
    return False


def run_main(rb, *argv):
    keep = S.connect, S.pause, S.time.sleep, S.wrapup_debt.owe, S.wrapup_debt.paid, sys.argv
    S.connect, S.pause, S.time.sleep = (lambda: rb), (lambda r: True), (lambda s: None)
    S.wrapup_debt.owe, S.wrapup_debt.paid = (lambda *a, **k: "t"), (lambda t: None)
    sys.argv = ["stage_review.py"] + list(argv)
    try:
        return quiet(S.main)
    finally:
        S.connect, S.pause, S.time.sleep, S.wrapup_debt.owe, S.wrapup_debt.paid, sys.argv = keep


def t_daylight_ends_between_10_and_14():
    """daylight-ends-between-10-and-14"""
    name = "daylight-ends-between-10-and-14"
    bad, back, moved = [], [], []
    for i in range(96):
        rb = FakeRB(hour=i / 4.0)
        t0, h0 = rb.t, i / 4.0
        quiet(S.daylight, rb)
        h = (rb.t / 2500.0) % 24
        if not 10 <= h <= 14:
            bad.append((h0, h))
        if not 0 <= rb.t - t0 < 60000:
            back.append(h0)
        if 10 <= h0 <= 14 and rb.t != t0:
            moved.append(h0)
    check(not bad, "%s: every start hour ends in the window %r" % (name, bad[:3]))
    check(not back, "%s: the clock goes forward, under a day %r" % (name, back[:3]))
    check(not moved, "%s: an hour already in the window is left alone %r" % (name, moved[:3]))
    rb = FakeRB(hour=18)
    rc = run_main(rb, "--weather", "Fog", "--settle", "4000", "--daylight", "--frame", "1,1,9,9", "--shot", "s")
    check(rc == 0 and len(rb.shots) == 1 and 10 <= rb.shots[0][1] <= 14,
          "%s: --daylight --weather --settle 4000 still shoots in the window %r" % (name, rb.shots))


def t_unread_hour_is_not_midday():
    """unread-hour-is-not-midday"""
    name = "unread-hour-is-not-midday"
    check(refuses(S.daylight, FakeRB(hour_fault={"success": False, "message": "No current map."})), name + ": a failed read raises")
    check(refuses(S.daylight, FakeRB(hour_fault={"success": True, "ticksGame": 5})), name + ": a reply with no hour raises")
    check(refuses(S.daylight, FakeRB(hour=18, clock_stuck=True)), name + ": a jump that reports success and moves nothing raises")


def t_clear_chunks_takes_chunks_only():
    """clear-chunks-takes-chunks-only"""
    name = "clear-chunks-takes-chunks-only"

    def th(i, x):
        return {"id": i, "x": x, "z": 5}
    rb = FakeRB(things=[th("ChunkGranite1", 1), th("ChunkSlagSteel2", 2), th("Steel3", 3), th("ChunkGranite4", 4), th("Gold5", 4)])
    out = quiet(S.clear, rb, ["chunks"], "0,0,50,50")
    left = sorted(t["id"] for t in rb.things)
    check(left == ["ChunkGranite4", "Gold5", "Steel3"], "%s: only lone chunks go %r" % (name, left))
    check(out == {"chunks": {"destroyed": 2, "left_beside_items": 1}}, "%s: the report counts both %r" % (name, out))
    rb = FakeRB(things=[th("Steel3", 3)])
    quiet(S.clear, rb, ["chunks"], "0,0,50,50")
    check([t["id"] for t in rb.things] == ["Steel3"], name + ": no chunk on the map, nothing destroyed")
    rb = FakeRB(things=[th("Steel3", 3), th("ChunkGranite1", 1)])
    quiet(S.clear, rb, ["items"], "0,0,50,50")
    check(rb.things == [], name + ": control, `items` still takes every loose item")


def t_two_pass_shoots_clear_first():
    """two-pass-shoots-clear-first"""
    name = "two-pass-shoots-clear-first"
    for h in (0, 9, 12, 13, 18):
        rb = FakeRB(hour=h, weather="RainyThunderstorm")
        run_main(rb, "--frame", "1,1,9,9", "--shot", "s", "--two-pass", "RM_FE_Weather_AshFall")
        ok = [s[0] for s in rb.shots] == ["s_clear", "s_ashfall"] and rb.shots[0][2] == "Clear" and rb.shots[0][3] >= 4000
        check(ok and rb.shots[1][2] == "RM_FE_Weather_AshFall", "%s: from %s h in rain %r" % (name, h, rb.shots))
        check(ok and all(10 <= s[1] <= 14 for s in rb.shots), "%s: both shots fall in 10-14 h from %s h" % (name, h))
    rb = FakeRB(weather_stuck=True)
    check(refuses(run_main, rb, "--shot", "s", "--two-pass", "Fog") and not rb.shots, name + ": a weather that does not take stops the run with no shot")
    rb = FakeRB(step_dead=True)
    check(refuses(run_main, rb, "--shot", "s", "--two-pass", "Fog") and not rb.shots, name + ": a settle whose ticks did not run stops the run with no shot")


def main():
    t_daylight_ends_between_10_and_14()
    t_unread_hour_is_not_midday()
    t_clear_chunks_takes_chunks_only()
    t_two_pass_shoots_clear_first()
    print("FAILED %d" % len(FAILS) if FAILS else "ALL OK")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

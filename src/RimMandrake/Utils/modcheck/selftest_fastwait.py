#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1: offline proof of helpers.fast_advance and of its seven callers.

  1. a moving clock reaches start+n-margin through rimworld/play_for, never overshooting by a whole window;
  2. a play_for refusal, a raised call and a clock that stops each end the fast run with a reason, never a hang;
  3. an unreadable clock is reported before anything runs;
  4. every exit leaves the game paused (jawa/set_game_speed Paused is the last call);
  5. none of the seven validation _wait helpers still calls rimworld/set_time_speed (it left the live game PAUSED:
     no Ultrafast wait in 47 modcheck results moved the clock) and each one calls helpers.fast_advance;
  6. the wait is ULTRAFAST: the fake clock runs at the speed play_for asks for (Normal 60/s, Fast 180/s, Superfast 360/s,
     Ultrafast `rate`), every play_for carries speed=4, fast_advance defaults to speed 4, no caller passes another
     speed, and the simulated play time for 30000 ticks stays inside the Ultrafast budget;
  7. the live A1 probe's judge() fails a run at Normal speed, at a slow rate or with a non-4 play_for speed.
Exit 0 all hold, 1 any fails.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import helpers as H  # noqa: E402

SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
CALLERS = ("LeaningScrub", "Contagion", "Cauldron", "ExplosiveGrowth", "Greentide", "BlueDesert", "Pyrelands")


SPEED_RATE = {1: 60.0, 2: 180.0, 3: 360.0}    # ticks per real second at Normal/Fast/Superfast; 4 (Ultrafast) = rate


class Fake(object):
    """A clock that runs `rate` ticks per real second of play_for at speed 4 (SPEED_RATE at slower speeds, 0 for any
    other speed); `stop_at` freezes it there; `refuse` fails play_for."""

    def __init__(self, rate=400.0, stop_at=None, refuse=None, unreadable=False, raise_on_play=False):
        self.ticks, self.rate, self.stop_at = 1000, rate, stop_at
        self.refuse, self.unreadable, self.raise_on_play = refuse, unreadable, raise_on_play
        self.calls = []

    def call(self, tool, **p):
        self.calls.append((tool, p))
        if tool == "rimworld/get_game_info":
            return {} if self.unreadable else {"ticksGame": self.ticks}
        if tool == "rimworld/play_for":
            if self.raise_on_play:
                raise RuntimeError("socket died")
            if self.refuse:
                return {"success": False, "error": self.refuse}
            r = self.rate if p.get("speed") == 4 else SPEED_RATE.get(p.get("speed"), 0.0)
            t = self.ticks + int(p["durationMs"] * r / 1000.0)
            self.ticks = min(t, self.stop_at) if self.stop_at is not None else t
            return {"success": True}
        if tool == "jawa/set_game_speed":
            return {"success": True, "speedAfter": p.get("speed")}
        raise AssertionError("unexpected tool %s" % tool)


def check(name, ok, detail=""):
    print("%s  %s %s" % ("PASS" if ok else "FAIL", name, detail))
    return ok


def paused_last(f):
    return f.calls and f.calls[-1] == ("jawa/set_game_speed", {"speed": "Paused"})


def main():
    ok = True
    for rate in (50.0, 400.0, 2500.0):     # slower and faster than the 400/s window estimate
        f = Fake(rate=rate)
        start, now, why = H.fast_advance(f, 30000)
        plays = [c for c in f.calls if c[0] == "rimworld/play_for"]
        ok &= check("reaches at %d/s" % rate, why is None and start == 1000 and now >= 1000 + 30000 - 400,
                    "now=%s why=%s windows=%d" % (now, why, len(plays)))
        # A steady clock overshoots the target by at most one minimum (200 ms) window once its rate is seen.
        ok &= check("overshoot bounded at %d/s" % rate, now - 31000 <= rate * 0.2, "overshoot=%d" % (now - 31000))
        ok &= check("windows bounded at %d/s" % rate, all(200 <= c[1]["durationMs"] <= 8000 for c in plays))
        ok &= check("paused after reach at %d/s" % rate, paused_last(f))
        ok &= check("set_time_speed never called at %d/s" % rate,
                    not any(c[0] == "rimworld/set_time_speed" for c in f.calls))
        ok &= check("every play_for at speed 4 (Ultrafast) at %d/s" % rate,
                    plays and all(c[1].get("speed") == 4 for c in plays),
                    "speeds=%s" % sorted(set(str(c[1].get("speed")) for c in plays)))
        # Played wall time: 30000-400 ticks at `rate`, plus at most the first 200-8000 ms window's mis-estimate.
        played = sum(c[1]["durationMs"] for c in plays) / 1000.0
        budget = (30000 - 400) / rate * 1.25 + 8.0
        ok &= check("play time inside the Ultrafast budget at %d/s" % rate, played <= budget,
                    "played=%.1fs budget=%.1fs" % (played, budget))

    # A Normal-speed clock is 400/60 slower: 30000 ticks must cost far more play time than at Ultrafast, so the budget
    # check above can see a speed change (sanity probe of the instrument, not of the code).
    f = Fake(rate=60.0)
    H.fast_advance(f, 30000)
    slow = sum(c[1]["durationMs"] for c in f.calls if c[0] == "rimworld/play_for") / 1000.0
    ok &= check("budget instrument sees a Normal-rate clock", slow > (30000 - 400) / 400.0 * 1.25 + 8.0, "%.1fs" % slow)

    import inspect
    dflt = inspect.signature(H.fast_advance).parameters["speed"].default
    ok &= check("fast_advance defaults to speed 4 (Ultrafast)", dflt == 4, "default=%r" % (dflt,))

    f = Fake(refuse="window forces pause")
    _, now, why = H.fast_advance(f, 9000)
    ok &= check("refusal ends the run", why is not None and why.startswith("play_for refused") and now == 1000, why)
    ok &= check("paused after refusal", paused_last(f))

    f = Fake(raise_on_play=True)
    _, _, why = H.fast_advance(f, 9000)
    ok &= check("raised call ends the run", why is not None and "RuntimeError" in why, why)
    ok &= check("paused after raise", paused_last(f))

    f = Fake(stop_at=3000)
    _, now, why = H.fast_advance(f, 9000)
    nplay = len([c for c in f.calls if c[0] == "rimworld/play_for"])
    ok &= check("stall ends the run", why == "stalled at 3000" and now == 3000 and nplay <= 4, "%s windows=%d" % (why, nplay))
    ok &= check("paused after stall", paused_last(f))

    f = Fake(unreadable=True)
    start, now, why = H.fast_advance(f, 9000)
    ok &= check("unreadable clock reported first", start is None and why == "clock unreadable"
                and not any(c[0] == "rimworld/play_for" for c in f.calls))

    for m in CALLERS:
        p = os.path.join(SRC, m, "validation.py")
        s = open(p).read()
        bodies = [b for _, b in re.findall(r"\n( *)def _wait(?:_raw)?\(t, n[^)]*\):\n(.*?)(?=\n\1def |\Z)", s, re.S)]
        ok &= check("%s _wait uses fast_advance" % m, any("H.fast_advance(" in b for b in bodies), "%d bodies" % len(bodies))
        ok &= check("%s no set_time_speed call in _wait" % m,
                    bodies and not any('"rimworld/set_time_speed"' in b for b in bodies))
        # Any speed a caller hands fast_advance must be 4; the args are read up to the call's closing paren.
        args = re.findall(r"H\.fast_advance\(([^)]*)\)", s)
        other = [a for a in args if re.search(r"\bspeed\s*=", a) and not re.search(r"\bspeed\s*=\s*4\b", a)]
        positional = [a for a in args if len([x for x in a.split(",") if x.strip()]) >= 7]
        ok &= check("%s fast_advance called at Ultrafast" % m, args and not other and not positional,
                    "calls=%d other=%s" % (len(args), other))

    # 7. The live A1 probe's verdict, offline.
    import ultrafast_clock_probe as P
    good = dict(start=1000, now=7000, why=None, wall=16.0, paused=True, speeds=[4, 4, 4], ticks=6000, wall_max=60.0,
                min_rate=150.0)
    ok &= check("A1 judge accepts an Ultrafast run", P.judge(**good)[0] is True, str(P.judge(**good)[1]))
    breaks = {"Normal-speed run (6000 ticks in 100 s)": dict(wall=100.0),
              "slow rate under the wall limit": dict(wall=50.0),
              "a play_for at speed 1": dict(speeds=[4, 1, 4]),
              "every play_for at speed 1": dict(speeds=[1, 1]),
              "no play_for at all": dict(speeds=[]),
              "gave up": dict(why="stalled at 3000"),
              "moved too little": dict(now=3000),
              "left running": dict(paused=False),
              "paused unread": dict(paused=None)}
    for name, change in breaks.items():
        r = dict(good)
        r.update(change)
        ok &= check("A1 judge rejects: %s" % name, P.judge(**r)[0] is False, str(P.judge(**r)[1]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

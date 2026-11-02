#!/usr/bin/env python3
"""MODCHECK_ULTRAFAST_CLOCK_STALL_1: offline proof of helpers.fast_advance and of its seven callers.

  1. a moving clock reaches start+n-margin through rimworld/play_for, never overshooting by a whole window;
  2. a play_for refusal, a raised call and a clock that stops each end the fast run with a reason, never a hang;
  3. an unreadable clock is reported before anything runs;
  4. every exit leaves the game paused (jawa/set_game_speed Paused is the last call);
  5. none of the seven validation _wait helpers still calls rimworld/set_time_speed (it left the live game PAUSED:
     no Ultrafast wait in 47 modcheck results moved the clock) and each one calls helpers.fast_advance.
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


class Fake(object):
    """A clock that runs `rate` ticks per real second of play_for; `stop_at` freezes it there; `refuse` fails play_for."""

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
            t = self.ticks + int(p["durationMs"] * self.rate / 1000.0)
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
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

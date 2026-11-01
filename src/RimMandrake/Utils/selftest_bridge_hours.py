#!/usr/bin/env python3
"""selftest_bridge_hours: the bridge occupancy reading, on hand-made ledgers."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bridge_hours as BH

NOW = dt.datetime(2026, 11, 1, 12, tzinfo=dt.timezone.utc).timestamp()
FAILS = []


def ev(hours_ago, state, event="bridge"):
    t = dt.datetime.fromtimestamp(NOW - hours_ago * 3600, dt.timezone.utc)
    return {"event": event, "state": state, "ts": t.strftime("%Y-%m-%dT%H:%M:%SZ")}


def check(name, got, want):
    if got != want:
        FAILS.append("%s: got %r, want %r" % (name, got, want))


DAY = 86400
check("empty", BH.held_hours([], NOW, DAY), 0.0)
check("one hold", BH.held_hours([ev(5, "taken"), ev(3, "released")], NOW, DAY), 2.0)
check("order in the file means nothing", BH.held_hours([ev(3, "released"), ev(5, "taken")], NOW, DAY), 2.0)
check("open hold runs to now", BH.held_hours([ev(2, "taken")], NOW, DAY), 2.0)
check("a hold is capped", BH.held_hours([ev(20, "taken"), ev(1, "released")], NOW, DAY), 6.0)
check("an open hold is capped", BH.held_hours([ev(20, "taken")], NOW, DAY), 6.0)
check("clipped at the window start", BH.held_hours([ev(25, "taken"), ev(23, "released")], NOW, DAY), 1.0)
check("wholly before the window", BH.held_hours([ev(30, "taken"), ev(28, "released")], NOW, DAY), 0.0)
check("take during a hold ends it", BH.held_hours([ev(5, "taken"), ev(4, "taken"), ev(3, "released")], NOW, DAY), 2.0)
check("stray release", BH.held_hours([ev(5, "released")], NOW, DAY), 0.0)
check("other events ignored", BH.held_hours([ev(5, "taken", "game"), ev(3, "released", "game")], NOW, DAY), 0.0)
check("future events ignored", BH.held_hours([ev(2, "taken"), ev(-1, "released")], NOW, DAY), 2.0)

check("same second, take then release", BH.held_hours([ev(1, "taken"), ev(1, "released")], NOW, DAY), 0.0)
check("same second, release then take", BH.held_hours([ev(1, "released"), ev(1, "taken")], NOW, DAY), 1.0)
bad = [{"event": "bridge", "state": "taken", "ts": "bad"}, {"event": "bridge", "state": "taken", "ts": 123},
       {"event": "bridge", "state": "taken"}]
check("a bad timestamp costs only its line", BH.held_hours(bad + [ev(2, "taken")], NOW, DAY), 2.0)

print("selftest_bridge_hours: %s" % ("FAIL " + "; ".join(FAILS) if FAILS else "OK"))
sys.exit(1 if FAILS else 0)

"""selftest_probe.py — the correction rule, which is the whole ruling in one function.

`contradicts()` is four lines and decides whether a seat may rewrite the one recorded
game-state variable. That is worth more tests than it has lines.

    python3 src/RimMandrake/rimflow/selftest_probe.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rimflow import probe                                          # noqa: E402

FAILED = []


def ok(name, got, want):
    if got == want:
        print("ok    %s" % name)
    else:
        FAILED.append(name)
        print("FAIL  %s\n      got  %r\n      want %r" % (name, got, want))


def reading(running, bridge=None):
    if running is None:
        return {"running": None, "bridge": None, "implies": None,
                "evidence": "could not look"}
    if not running:
        return {"running": False, "bridge": None, "implies": "DOWN",
                "evidence": "no process"}
    return {"running": True, "bridge": bridge,
            "implies": "UP" if bridge else "LOADING", "evidence": "process alive"}


# --- the two real contradictions -------------------------------------------
ok("recorded UP but nothing running -> DOWN",
   probe.contradicts("UP", reading(False)), "DOWN")
ok("recorded LOADING but nothing running -> DOWN",
   probe.contradicts("LOADING", reading(False)), "DOWN")
ok("recorded GOING_DOWN but nothing running -> DOWN",
   probe.contradicts("GOING_DOWN", reading(False)), "DOWN")
ok("recorded DOWN but process running and bridge answers -> UP",
   probe.contradicts("DOWN", reading(True, True)), "UP")
ok("recorded DOWN but process running and bridge silent -> LOADING",
   probe.contradicts("DOWN", reading(True, False)), "LOADING")
ok("recorded DEPLOYING but process running -> UP",
   probe.contradicts("DEPLOYING", reading(True, True)), "UP")

# --- the states the machine CANNOT see, which must be left alone -----------
# DEPLOYING and DOWN are both "no process". GOING_DOWN and UP are both "process alive".
# Correcting either way would destroy something only the owner knows.
ok("DEPLOYING with nothing running is NOT a contradiction",
   probe.contradicts("DEPLOYING", reading(False)), None)
ok("DOWN with nothing running is NOT a contradiction",
   probe.contradicts("DOWN", reading(False)), None)
ok("GOING_DOWN with the process alive is NOT a contradiction",
   probe.contradicts("GOING_DOWN", reading(True, True)), None)
ok("UP with the process alive is NOT a contradiction",
   probe.contradicts("UP", reading(True, True)), None)
ok("LOADING with the process alive is NOT a contradiction",
   probe.contradicts("LOADING", reading(True, False)), None)

# --- ignorance is not evidence ---------------------------------------------
# 🔴 The one that would do real damage: a host with no tasklist.exe answering "nothing
# is running" and silently rewriting a correct UP to DOWN. None must never correct.
ok("could-not-look never corrects UP",
   probe.contradicts("UP", reading(None)), None)
ok("could-not-look never corrects DOWN",
   probe.contradicts("DOWN", reading(None)), None)
ok("could-not-look never corrects LOADING",
   probe.contradicts("LOADING", reading(None)), None)

print()
if FAILED:
    print("%d FAILED: %s" % (len(FAILED), ", ".join(FAILED)))
    sys.exit(1)
print("14/14 passed")

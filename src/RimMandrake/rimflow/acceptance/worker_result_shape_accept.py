#!/usr/bin/env python3
"""Acceptance test for RIMMANDRAKE_READ_ODD_RESULT_SHAPE_AS_BLIND_NOT_CRASH.

infrastructure/stevedesktop/worker.py Attempt.kept_game_unmappable (ab3cb4372d) reads the newest published result.json
with read_json, which returns any JSON value. A record that parses but is not a dict ([], 0) or carries a non-string
note ({"note": 17}) RAISES there (AttributeError / TypeError) instead of reading as a record it cannot use. Measured
2026-11-18 on c32e228e91: all three raise. "Could not look" is the gate's fourth answer: such a record must keep the
game and log the blindness by name, exactly like an unreadable one.

    python3 src/RimMandrake/rimflow/acceptance/worker_result_shape_accept.py     exit 0 = pass, 1 = fail

Expected on a correct result: `PASS 3 of 3 odd result shapes keep the game and say why`. Offline: no game, no host.
The builder does not edit this file.
"""
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
T = tempfile.mkdtemp(prefix="accept_worker_shape_")
os.environ.update(TESTQ_HOME=T, RM_GAME_LOGDIR=T, TESTQ_WORKER_HOST="stevedesktop")
sys.path.insert(0, os.path.join(ROOT, "infrastructure", "stevedesktop"))
import worker as W  # noqa: E402

with open(os.path.join(T, "Player.log"), "w") as f:
    f.write("a healthy load, no wound\n")
bad = []
for shape in ([], 0, {"note": 17}):
    said = []
    a = object.__new__(W.Attempt)
    a.d, a.say = os.path.join(T, "attempts", "mine"), said.append
    a.prior_result = lambda s=shape: (s, os.path.join(T, "attempts", "old", "result.json"))
    try:
        got = a.kept_game_unmappable(None)
    except Exception as e:  # noqa: BLE001
        got = "RAISED %s: %s" % (type(e).__name__, e)
    ok = got is None and any("could not read" in m for m in said)
    print("%s %-14r -> %r; said %r" % ("PASS" if ok else "FAIL", shape, got, said))
    if not ok:
        bad.append(repr(shape))
print(("PASS 3 of 3 odd result shapes keep the game and say why") if not bad else
      ("FAIL an odd result shape is not read as blindness: %s" % ", ".join(bad)))
sys.exit(1 if bad else 0)

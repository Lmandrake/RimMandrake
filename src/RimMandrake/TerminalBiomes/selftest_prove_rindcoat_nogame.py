#!/usr/bin/env python3
"""selftest_prove_rindcoat_nogame.py - prove_rindcoat_scald_live.py against a fake bridge with no game loaded
(GAMEENV_FIX_PROOFSITE_528224CB_ITEMS_WAIT): the main menu's get_game_info carries no ticksGame, and the proof must say
UNMEASURED: no game loaded and exit 2 without staging anything, never a bare KeyError; and RINDCOAT's live_proofs file
names the `live_site.py --game` site step that stages one. No game, no bridge."""
import contextlib
import io
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FAILS = []


def check(label, ok):
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        FAILS.append(label)


def fake_ps(reply, calls):
    ps = types.ModuleType("proof_scald_steam")
    ps.STATE = os.path.join(HERE, "__no_such_state__.json")
    ps.bridge = lambda: object()

    def call(c, tool, **kw):
        calls.append(tool)
        return reply
    ps.call = call
    ps.setup = lambda: calls.append("setup")
    ps.run = lambda *a, **k: calls.append("run")
    ps.read = lambda *a: None
    return ps


import prove_rindcoat_scald_live as P  # noqa: E402

check("game_tick: an int tick", P.game_tick({"ticksGame": 1234}) == 1234)
check("game_tick: the menu reply (no key) is None", P.game_tick({"status": "no_game", "success": True}) is None)
check("game_tick: a non-dict reply is None", P.game_tick(None) is None and P.game_tick("x") is None)
check("game_tick: a bool is not a tick", P.game_tick({"ticksGame": True}) is None)

for reply in ({"success": True, "status": "no_game"}, {"success": False}, None):
    calls = []
    sys.modules["proof_scald_steam"] = fake_ps(reply, calls)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = P.main(["--max-seconds", "600"])
    text = out.getvalue()
    check("no game (%r) -> exit 2, 'UNMEASURED: no game loaded', nothing staged" % (reply,),
          rc == 2 and "UNMEASURED: no game loaded" in text and "setup" not in calls and "run" not in calls
          and "KeyError" not in text and "bridge: 'ticksGame'" not in text)

# the lane stages the game the proof needs: RINDCOAT's live_proofs file carries the --game site line, accepted by the lane
LP = os.path.join(HERE, "..", "..", "..", "infrastructure", "state", "live_proofs", "RINDCOAT_TUNE_NEAR_IMMUNE_AFTER_ALL.txt")
SITE = "live-site A1: python.exe src/RimMandrake/Utils/live_site.py --game"
lines = [ln.strip() for ln in open(LP, encoding="utf-8")] if os.path.exists(LP) else []
check("RINDCOAT live_proofs holds %r" % SITE, SITE in lines)
sys.path.insert(0, os.path.join(HERE, "..", "rimflow"))
import relentless_live  # noqa: E402
check("the lane accepts that site command", relentless_live.refused_site(SITE.split(": ", 1)[1]) is None)

print("SELFTEST " + ("FAIL: %s" % FAILS if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)

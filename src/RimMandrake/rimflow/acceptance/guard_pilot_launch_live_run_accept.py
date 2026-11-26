#!/usr/bin/env python3
"""Acceptance: `maturation_dispatch.py pilot-launch` never starts a second blind judge (or live driver) on a mod a run is
already live on (RIMMANDRAKE_GUARD_PILOT_LAUNCH_TWO_JUDGES_ONE_CYCLE).

Measured 2026-11-16: the Dispatch tick launched judge-1794822790 on GimmeSomeSlack cycle 6 at 01:54:31 PST; a hand
pilot-launch 34 s later started judge-1794822890 on the same cycle, because pilot_launch read only "owed: cycle" (no
cycle_6 folder yet) and never the live runs the tick's decide_blind checks. Two judges then wrote one cycle_6 folder.

    python3 src/RimMandrake/rimflow/acceptance/guard_pilot_launch_live_run_accept.py      (exit 0 = PASS)
Offline, on a temp root; no claude, unit or landing is started."""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
os.environ["RM_MATURATION_DISPATCH_DIR"] = tempfile.mkdtemp(prefix="pl_live_sd_")
os.environ["RM_STAGE_LAND"] = "0"
import maturation as M              # noqa: E402
import maturation_dispatch as D     # noqa: E402
import modledger as L               # noqa: E402

res = []


def check(name, ok, detail=""):
    res.append(bool(ok))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)[:300]))


root = tempfile.mkdtemp(prefix="pl_live_root_")
PILOT = (L.config().get("pilot_mods") or ["ExplosiveKnockback"])[0]
started = []
D.launch_stage = lambda root, cfg, st, mod, cap, item, now=None, fx=None, launch=None, **kw: started.append(
    (mod, item)) or (0, "DETACHED u-new", "u-new")
ready = {"ready": lambda r, m: (True, "PASS 7/7"), "land_ledger": lambda paths: "landed", "open_items": lambda ids: [],
         # a stand-in game reading: the real one reads the live driver lock, so a helper holding a game turned this
         # offline test red (RIMMANDRAKE_SEAL_PILOT_GUARD_TEST_FROM_THE_LIVE_GAME)
         "bridge": lambda p, game="a": (True, "free (test stand-in)")}
# the per-game hold too: pick_game's default reads the live control store, so `./pipe off game:ArchBig` for his walk
# turned this offline test red on 2026-11-22 (RIMMANDRAKE_SEAL_PILOT_GUARD_TEST_FROM_THE_LIVE_GAME, reopened).
# RM_ACCEPT_PLANT_HOLD plants a held game, to show the stand-in is what the in_game launch reads.
D.game_hold = lambda g: (os.environ.get("RM_ACCEPT_PLANT_HOLD") or None)

for stage, owed in (("blind_challenge", "cycle"), ("in_game", "run")):
    M.brief_text = lambda r, m, cap, _s=stage, _o=owed, **k: ("", {"stage": _s, "owed": _o})
    started.clear()
    rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, PILOT, "t", item="RIMMANDRAKE_X_Y_Z_Q",
                              fx=dict(ready, live_units=lambda r, m: ["rm-detached-judge-1"]))
    check("%s: a run live on the mod refuses a second launch" % stage, rc == 2 and "live" in text and not started,
          (rc, text, started))
    started.clear()
    rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, PILOT, "t", item="RIMMANDRAKE_X_Y_Z_Q",
                              fx=dict(ready, live_units=lambda r, m: "UNMEASURED"))
    check("%s: unreadable run records refuse (never launch blind)" % stage, rc == 2 and not started, (rc, text, started))
    started.clear()
    rc, text = D.pilot_launch(root, {"cap_tokens": 3_750_000}, PILOT, "t", item="RIMMANDRAKE_X_Y_Z_Q",
                              fx=dict(ready, live_units=lambda r, m: []))
    check("%s: nothing live still launches" % stage, rc == 0 and started == [(PILOT, "RIMMANDRAKE_X_Y_Z_Q")],
          (rc, text, started))

check("the default live reader exists and reads maturation_now's runs", callable(getattr(D, "live_units_on", None)))
print("PASS %d/%d" % (sum(res), len(res)) if all(res) else "FAIL %d of %d" % (res.count(False), len(res)))
sys.exit(0 if all(res) else 1)

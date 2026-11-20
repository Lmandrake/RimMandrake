#!/usr/bin/env python3
"""Offline test: the bed-less prison scene is in concept_scenes.py's STAGE3_SCENES table, so the certificate's
asks_on_empty_game clause examines it (RIMMANDRAKE_CLEAR_FLOWWORKS_PAPERWORK_TO_GAME_ONLY_ROAD). Before, the certificate
read "asks_on_empty_game did not run on 1 in-game scene(s) scene_hole_prison: not in ... STAGE3_SCENES".
No bridge, no game: the raw scene is replaced by stubs to prove the adapter's two outcomes."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
UTILS = os.path.join(os.path.dirname(MOD), "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import concept_scenes as C  # noqa: E402
import scene_empty_game as SE  # noqa: E402

fails = []


def check(ok, why):
    print("%s %s" % ("ok  " if ok else "FAIL", why))
    if not ok:
        fails.append(why)


entry = C.STAGE3_SCENES.get("scene_hole_prison")
check(entry is not None, "scene_hole_prison is in STAGE3_SCENES")
if entry is not None:
    # on an empty game (every call a bare success) no row of the prison scene reads PASS
    rows = SE.rows_on_empty(entry)
    check(rows and not any(r.get("status") == "PASS" for r in rows),
          "on an empty game the prison scene passes no row (%s)" % [(r.get("id"), r.get("status")) for r in rows])
    check(("scene_hole_prison", None) not in [(s, None) for s, _ in SE.vacuous({"scene_hole_prison": entry})],
          "the empty-game check finds no vacuous prison row")
    raw = C.scene_hole_prison
    seen = {}
    try:
        def ok_scene(B, snapshot, reload_snapshot, receipt, **kw):
            seen.update(kw)
        C.scene_hole_prison = ok_scene
        mid_save, mid_load = object(), object()
        out = entry(None, None, None, {}, save_mid=mid_save, load_mid=mid_load)
        check(out.get("status") == "PASS" and [r["status"] for r in out["rows"]] == ["PASS"],
              "a scene that ends without an assertion is one PASS row (%s)" % out)
        check(seen.get("save_occupied") is mid_save and seen.get("load_occupied") is mid_load,
              "save_mid/load_mid reach the scene as save_occupied/load_occupied (%s)" % sorted(seen))

        def bad_scene(B, snapshot, reload_snapshot, receipt, **kw):
            raise AssertionError("prisoner flag never set")
        C.scene_hole_prison = bad_scene
        out = entry(None, None, None, {})
        check(out.get("status") != "PASS" and out["rows"] and out["rows"][0]["status"] == "UNMEASURED"
              and "prisoner flag never set" in out["rows"][0]["detail"],
              "an assertion is an UNMEASURED staging row naming its cause, never a pass (%s)" % out)
    finally:
        C.scene_hole_prison = raw

print("%s: %d failure(s)" % ("FAIL" if fails else "PASS", len(fails)))
sys.exit(1 if fails else 0)

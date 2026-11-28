#!/usr/bin/env python3
"""Live scene (kind A): a wild animal wholly under tar sends a sign up through the surface.

RIMMANDRAKE_SIGN_WILD_ANIMAL_UNDER_TAR_HAS_NO_LABEL_TO_SHOW (the rule: no animal or pawn ever vanishes without a sign that the
player can read). A colonist under tar keeps her name label and alert; a wild hare under 0.5 m of tar showed nothing at all.
The fix: RM_SubmergeDraw.TickHiddenSigns sends a ring of froth and two bubbles over every living pawn that nothing of shows,
every RM_PawnCutMath.SignIntervalTicks. Offline: SelfTest/PawnCutChecks.cs "PawnCut_hidden_living_pawn_sends_a_sign".

Contract.
- claim: a wild hare in a 2 m pit under 0.5 m of tar is owed the sign and the map sends it; a hare in a dry pit beside it,
  and a hare in 0.15 m of tar (her back above it), are not owed it.
- entry point: the mod's own tick (RM_MapComponent_Excavation -> RM_SubmergeDraw.TickHiddenSigns); the scene only steps
  ticks. RM_SubmergeDraw.ProofHiddenSigns reads the count and the pawns owed now.
- valid opportunity: three hares spawned, the tar hare reads mode=Hidden from ProofPawnCutId (the instrument sees her
  hidden), and the dry hare reads dry.
- success: after STEP ticks the tar hare is owed, the dry and shallow hares are not, and sent rose by at least 2.
- forbidden effects: an exception from the proof surface; a sign owed by the dry hare.
- end: rows and two captures (close, default zoom) written beside the out file; the plots reset in finally.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_hidden_pawn_sign.py <out.json> [--fresh-map] [--origin X,Z]
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (could not look; the reason is in the row).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

SUB = "RimMandrake.FlowWorks.RM_SubmergeDraw"
TAR = "RM_Fluid_Tar"
INTERVAL = 90      # RM_PawnCutMath.SignIntervalTicks
STEP = 4 * INTERVAL


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="110,110")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402  (bridge-side import on a live run only)
    B = PH.PB()
    rows = []
    res = {"script": "live_hidden_pawn_sign.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}
    outdir = os.path.dirname(os.path.abspath(a.out))

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-34s %-10s %s" % (rid, st, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def call(tool, **kw):
        try:
            return B.call(tool, **kw) or {}
        except Exception as ex:  # noqa: BLE001 - a refused call is a row's evidence, not a crash
            return {"success": False, "error": str(ex)}

    def static(method, arg):
        r = call("jawa/static_call", type=SUB, method=method, args=arg)
        return str(r.get("result") or r.get("error") or r)

    def spawned_id(r):
        for v in r.values() if isinstance(r, dict) else []:
            if isinstance(v, list):
                for it in v:
                    if isinstance(it, dict) and it.get("id"):
                        return it["id"]
        return None

    def shot(name, cx, cz, root):
        call("jawa/clear_ui", all=True)
        call("rimworld/jump_camera_to_cell", x=int(cx), z=int(cz))
        call("rimworld/set_camera_zoom", rootSize=root)
        time.sleep(1.2)
        r = call("jawa/take_screenshot", fileName="sign_%s_%d" % (name, int(time.time())))
        src = r.get("filePath")
        for _ in range(12):
            if src and os.path.exists(src):
                break
            time.sleep(0.5)
        if not src or not os.path.exists(src):
            return None
        dst = os.path.join(outdir, "sign_%s.png" % name)
        shutil.copyfile(src, dst)
        return dst

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("HS_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    ox, oz = (int(v) for v in a.origin.split(","))
    plots = {"tar": (ox, oz, 0.5), "dry": (ox + 8, oz, 0.0), "shallow": (ox + 16, oz, 0.15)}
    hares = {}
    try:
        for x0, z0, _m in plots.values():
            call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                 args="%d;%d;%d;%d" % (x0 - 2, z0 - 2, 9, 9))
        # an open sky and noon light, or the captures are unreadable (ArchSmall's quicktest map put 110,110 under a dark
        # roofed patch, 2026-11-28); the rows do not need the light, the art judge does
        sky = V.open_sky_site(B, (ox - 3, oz - 3, 28, 10))
        res["open_sky"] = {k: sky.get(k) for k in ("ok", "roofCells", "rockCells", "why", "cleared")}
        # plants off the site (a fungal quicktest map hid the pits under giant mushrooms, 2026-11-28); destroy_batch never
        # destroys pawns, and the hares are spawned after it
        call("jawa/destroy_batch", rects="%d,%d,28,10" % (ox - 3, oz - 3), categories="All")
        call("jawa/set_terrain_batch", ops="Soil:%d,%d,28,10" % (ox - 3, oz - 3))
        call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % (ox - 3, oz - 3, 28, 10))
        call("jawa/weather_set", weather="Clear", lockWeather=True)
        clock = call("jawa/time_clock")
        ta, tg = clock.get("ticksAbs"), clock.get("ticksGame")
        if isinstance(ta, int) and isinstance(tg, int) and not 10 <= (ta % 60000) / 2500.0 <= 14:
            call("jawa/time_set_ticks", ticks=int(tg + (12 * 2500 - ta % 60000) % 60000), timeException=True,
                 why="live_hidden_pawn_sign: noon light for the captures")
        call("rimworld/pause_game")
        for k, (x0, z0, m) in plots.items():
            for i in range(5):
                for j in range(5):
                    call("jawa/flowworks_excavation_drive", x=x0 + i, z=z0 + j, deepenLevels=4, setBodyWaterM=-1, fillInLevels=0)
            if m > 0:
                res.setdefault("fills", {})[k] = static("ProofFillRect", "%d,%d,5,5,%g,%s" % (x0, z0, m, TAR))
            r = call("jawa/spawn_pawn", kindDef="Hare", x=x0 + 2, z=z0 + 2, faction="none", count=1)
            hares[k] = spawned_id(r)
        if not all(hares.values()):
            row("HS_site", "UNMEASURED", {"why": "a hare did not spawn", "hares": hares})
            return 2
        cut = {k: static("ProofPawnCutId", pid) for k, pid in hares.items()}
        if "mode=Hidden" not in cut["tar"] or "dry" not in cut["dry"]:
            row("HS_site", "UNMEASURED", {"why": "the tar hare does not read Hidden, or the dry hare is wet: no valid opportunity",
                                          "cut": cut, "fills": res.get("fills")})
            return 2
        row("HS_site", "PASS", {"cut": cut, "hares": hares})
        before = static("ProofHiddenSigns", "reset")
        call("rimworld/step_game_ticks", ticks=STEP, pauseFirst=True, timeoutMs=180000)
        after = static("ProofHiddenSigns", "read")
        tar_alive = "mode=Hidden" in static("ProofPawnCutId", hares["tar"])
        if not (before.startswith("SIGNS") and after.startswith("SIGNS")):
            # a build with no sign (main before the fix) or a stale DLL: nothing to read; the captures still show the look
            row("HS_sign_sent_over_tar_hare", "UNMEASURED", {"why": "no ProofHiddenSigns surface on this build",
                                                           "got": after, "tarStillHidden": tar_alive})
            sent, owed = None, []
        else:
            sent = int(after.split("sent=")[1].split()[0])
            owed = after.split("owed=")[1].split(",") if after.split("owed=")[1] else []
        if sent is not None:
            row("HS_dry_hare_owes_no_sign", "FAIL" if hares["dry"] in owed else "PASS", {"owed": owed, "dry": hares["dry"]})
            row("HS_shallow_hare_owes_no_sign", "FAIL" if hares["shallow"] in owed else "PASS",
                {"owed": owed, "shallow": hares["shallow"], "cut": static("ProofPawnCutId", hares["shallow"])})
            ok = hares["tar"] in owed and sent >= 2
            row("HS_sign_sent_over_tar_hare", "PASS" if ok else ("FAIL" if tar_alive else "UNMEASURED"),
                {"sent": sent, "owed": owed, "tar": hares["tar"], "after": after,
                 "why": "the tar hare is owed the sign and the map sent it" if ok else
                 ("she is still hidden and no sign was sent" if tar_alive else "she is no longer hidden (moved or died)")})
        # the look, for the art judge: stop a few ticks after a sign so its froth and bubbles stand on the frame
        t = call("jawa/time_clock").get("ticksGame")
        if isinstance(t, int):
            call("rimworld/step_game_ticks", ticks=(INTERVAL - t % INTERVAL) % INTERVAL + 8, pauseFirst=True, timeoutMs=60000)
        x0, z0, _m = plots["tar"]
        res["shots"] = {"close": shot("close", x0 + 2, z0 + 2, 8.0), "default": shot("default", ox + 10, oz + 2, 24.0)}
        save()
        return 1 if any(r["status"] == "FAIL" for r in rows) else (2 if any(r["status"] == "UNMEASURED" for r in rows) else 0)
    finally:
        for pid in hares.values():
            if pid:
                call("jawa/pawn_force_incapacitate", pawn=str(pid), action="vanish")
        for x0, z0, _m in plots.values():
            call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect",
                 args="%d;%d;%d;%d" % (x0 - 2, z0 - 2, 9, 9))
        save()


if __name__ == "__main__":
    sys.exit(main())

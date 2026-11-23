"""RIMMANDRAKE_REDRAW_STEPPED_PIT_INNER_CLIFF_STOPS_SHORT_OF_THE_RIM, step 3 live: the stepped pits under the game's own sun, moon and
lamps. Run on the map stepped_pit_stage.py left (save RM_STEPPED_PIT_12_CASES, loaded from the main menu): sets the clock to each
light case, waits for the pit relief to re-bake (RM_PitSunDraw reads vanilla's _CastVect every 20 frames), captures the top row
of cases (his L, the 2 m / 6 m step both ways, the west/east step) beside three vanilla walls whose own shadows show the game's
sun, and reads the sky and lamp glow on the pit floors. A person or a judge LOOKS; this script decides no bar.

--compare first captures noon with the relief switch off (the look before this item) and on, with a colonist for scale.
Cases: noon, morning (08 h), evening (17 h), dusk (19 h), night (23 h, the moon), night with a torch on the 6 m floor of the
step and a torch at the south-east rim of the west/east step. Saves the night-with-lamps map as --save.

    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python.exe src/RimMandrake/FlowWorks/northstar/stepped_pit_light_stage.py <out_dir> [--origin 40,40] [--save NAME]

LIES: a refused call is HARNESS. Exit 0 when every case captured and the save landed, 2 otherwise (never PASS/FAIL).
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
for p in (HERE, os.path.abspath(os.path.join(HERE, "..", "..", "Utils"))):
    if p not in sys.path:
        sys.path.insert(0, p)

from stepped_pit_stage import SLOT, wait_file  # noqa: E402

LIGHTS = [("noon", 12.0, False), ("morning_08h", 8.0, False), ("evening_17h", 17.0, False), ("dusk_19h", 19.0, False),
          ("night_23h", 23.0, False), ("night_23h_lamps", 23.0, True)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out_dir")
    ap.add_argument("--origin", default="40,40")
    ap.add_argument("--save", default="RM_STEPPED_PIT_LIGHT_NIGHT_LAMPS")
    ap.add_argument("--root-size", type=float, default=11.0)
    ap.add_argument("--compare", action="store_true", help="first: noon with the relief switch off, then on, and a colonist")
    a = ap.parse_args(argv)
    ox, oz = (int(v) for v in a.origin.split(","))
    os.makedirs(a.out_dir, exist_ok=True)
    import validation_core as V      # noqa: E402
    import proof_hose as PH          # noqa: E402
    B = V.guard(PH.PB())
    top = oz + 2 * SLOT                       # the grid's north row of slots (cases 1-4)
    row = (ox, top, 4 * SLOT, SLOT)
    deep_floor = (ox + SLOT + 3, top + SLOT - 5)     # case 2's 6 m floor (rows 2-3 of its grid)
    rim_se = (ox + 3 * SLOT + 5, top + SLOT - 7)     # south-east of case 4's rim, on the ground
    probe = [deep_floor, (ox + 2, top + 2), (ox + 3 * SLOT + 3, top + 3)]
    res = {"script": "stepped_pit_light_stage.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "lights": []}
    out_json = os.path.join(a.out_dir, "light_stage.json")

    def save():
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    # three vanilla walls in case 1's slot, east of the pit: their shadows are the game's sun, drawn by vanilla
    B.call("jawa/spawn_batch", ops="Wall:%d,%d;Wall:%d,%d;Wall:%d,%d" % (ox + 6, top + 4, ox + 6, top + 5, ox + 6, top + 6))
    g = B.call("jawa/glow_at", cells="%d,%d" % probe[0]) or {}
    hour0, tick0 = float(g.get("hour") or 0.0), int(g.get("ticksGame") or 0)
    bad = 0

    def shoot(name, rect, root):
        r = B.call("rimworld/screenshot_cell_rect", x=rect[0], z=rect[1], width=rect[2], height=rect[3], paddingCells=0,
                   fileName="stpl_%s_%s" % (time.strftime("%H%M%S"), name), rootSize=root) or {}
        src = r.get("path")
        if not (src and wait_file(src)):
            return None
        dst = os.path.join(a.out_dir, "light_%s.png" % name)
        from game_paths import win_to_wsl
        shutil.copyfile(src if os.name == "nt" else win_to_wsl(src), dst)
        return dst

    if a.compare:
        # before / after at noon, one map: the relief switch off (the look before this item) and on; a colonist for true scale
        res["colonist"] = str(B.call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 5, z=top + 2, faction="player") or {})[:160]
        B.call("jawa/time_set_ticks", ticks=tick0 + int(round(((12.0 - hour0) % 24.0) * 2500)), timeException=True,
               why="stepped pit before/after: noon")
        close = (ox, top, 2 * SLOT, SLOT)
        for state in ("off", "on"):
            ok = B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofPitRelief", args=state,
                        _answer=True) or {}
            res["relief_" + state] = str(ok.get("result") or ok)[:120]
            time.sleep(1.5)
            B.call("jawa/clear_ui", all=True)
            res["compare_" + state] = shoot("compare_%s_close" % state, close, 6.0)
            if not res["compare_" + state]:
                bad += 1
        save()
    for name, hour, lamps in LIGHTS:
        rec = {"name": name, "hour_wanted": hour}
        if lamps:
            rec["torches"] = str(B.call("jawa/spawn_batch", ops="TorchLamp:%d,%d;TorchLamp:%d,%d" % (deep_floor + rim_se)) or {})[:160]
        want = tick0 + int(round(((hour - hour0) % 24.0) * 2500))
        B.call("jawa/time_set_ticks", ticks=want, timeException=True, why="stepped pit light stage: the sun's position, nothing time-dated")
        time.sleep(1.5)                           # frames: vanilla sets _CastVect, RM_PitSunDraw re-bakes (every 20 frames)
        B.call("jawa/clear_ui", all=True)
        g = B.call("jawa/glow_at", cells=";".join("%d,%d" % c for c in probe)) or {}
        rec["hour"], rec["skyGlow"] = g.get("hour"), g.get("skyGlow")
        rec["glow"] = [[c.get("x"), c.get("z"), c.get("groundGlow"), c.get("roofed")] for c in g.get("cells") or []]
        shot = "stpl_%s_%s" % (time.strftime("%H%M%S"), name)
        r = B.call("rimworld/screenshot_cell_rect", x=row[0], z=row[1], width=row[2], height=row[3], paddingCells=0, fileName=shot,
                   rootSize=a.root_size) or {}
        src = r.get("path")
        if src and wait_file(src):
            dst = os.path.join(a.out_dir, "light_%s.png" % name)
            try:
                from game_paths import win_to_wsl
                shutil.copyfile(src if os.name == "nt" else win_to_wsl(src), dst)
                rec["capture"] = dst
            except OSError as e:
                rec["capture_error"] = str(e)
        # close: his L and the 2 m / 6 m step (cases 1-2), for the owner's image
        r = B.call("rimworld/screenshot_cell_rect", x=row[0], z=row[1], width=2 * SLOT, height=SLOT, paddingCells=0,
                   fileName=shot + "_close", rootSize=6.0) or {}
        src = r.get("path")
        if src and wait_file(src):
            dst = os.path.join(a.out_dir, "light_%s_close.png" % name)
            try:
                from game_paths import win_to_wsl
                shutil.copyfile(src if os.name == "nt" else win_to_wsl(src), dst)
                rec["capture_close"] = dst
            except OSError as e:
                rec["capture_error"] = str(e)
        if "capture" not in rec:
            bad += 1
        res["lights"].append(rec)
        save()
    sv = B.call("rimworld/save_game", saveName=a.save) or {}
    res["save"] = {"name": a.save, "ok": sv.get("success")}
    save()
    print("%s; save %s; %s" % ("CAPTURED" if bad == 0 else "HARNESS: %d capture(s) missing" % bad, a.save, out_json))
    return 0 if bad == 0 and sv.get("success") else 2


if __name__ == "__main__":
    sys.exit(main())

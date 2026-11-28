#!/usr/bin/env python3
"""Live scene of RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE: the owner's experiment with a DRAWN crown
shadow on one large tree type (card 2026-10-19 Q3 option 3, "to see how painful it is for a single large tree type").
The greatbole's crown shadow is drawn as a soft dark disc on the ground, where the shade grid casts it
(RM_ShadeOverlay.cs, RM_SunHeatMath.CrownShadowQuad); every other tree keeps the flat ground tint.

Kind A (deterministic): the scene plants its own forest on a map with a sun vector, so one valid run decides.
  claim         on a map with a sun vector, every planted grown greatbole gets one drawn shadow (the drawer's count
                equals the grid's list, at least the planted count), the cell at each sampled predicted disc centre
                reads crown shade, the drawer costs a measured CPU time per frame, and switching the setting off
                draws none.
  entry point   the current map of a game with Creature Behaviors of this build (jawa/static_call
                RimMandrake.CreatureBehaviors.RM_ShadeOverlay.CrownShadowReport answers; "Type not found" or a
                missing method = COULD NOT LOOK, an old DLL), jawa/shadegrid_read, jawa/set_plants,
                jawa/mod_settings_field, rimworld/save_game.
  opportunity   the grid reads isDirectional true with E > 0 (a fixed-sun world or a pinned sun). With
                --pin-biome <BiomeDef> the script first regenerates the current map as that biome (a biome that carries
                RM_PinnedSunExtension, e.g. RM_LongShade) when the map has no sun vector.
  success       drawn >= planted, every sampled disc centre reads canopy >= 0.99, drawn 0 with the setting off and
                drawn again with it back on.
  forbidden     a red error in the log naming RM_ShadeOverlay, RM_CrownShadow or the shade grid.
  end           the setting is left on (its default); the forest stays, saved as the review save.

What it writes: the reading src/RimMandrake/CreatureBehaviors/crown_shadow_experiment_reading.json (the item's outcome
check reads shadows_drawn, save, frame_ms_off, frame_ms_on, effort, broke), screenshots named in it, and the save.
The frame time is the mean of Time.unscaledDeltaTime over the sample, read by the drawer itself; the game is not in
focus, so its frame rate may be throttled: compare off with on, never with a number from elsewhere.

Run on the machine that hosts the game, with that game's environment:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env ArchSmall)"
    python3 src/RimMandrake/CreatureBehaviors/live_crown_shadow_experiment.py [--pin-biome RM_LongShade]
        [--side 120] [--spacing 9] [--sample-s 8] [--save CROWN_SHADOW_GREATBOLE_REVIEW]
        [--effort "<text>"] [--broke "<one observation>" ...]
    python3 src/RimMandrake/CreatureBehaviors/live_crown_shadow_experiment.py --annotate --effort "..." --broke "..."
        (no game: the effort and what broke, written after a look at the reading's screenshots)
Exit 0 PASS, 1 FAIL (MOD FAILURE), 2 COULD NOT LOOK (the cause named).
"""
import argparse
import datetime
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils")]

READING = os.path.join(HERE, "crown_shadow_experiment_reading.json")
SETTINGS_TYPE = "RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings"
OVERLAY_TYPE = "RimMandrake.CreatureBehaviors.RM_ShadeOverlay"
TREE = "RM_Greatbole"
RF, HF = 0.97, 0.79          # the greatbole's crown factors, Patches/RM_TreeCrowns_Giants.xml
RECOMPUTE_WAIT = 2001        # planting asks for no recompute; the grid rebuilds every 2000 ticks
FORBIDDEN = re.compile(r"RM_ShadeOverlay|RM_CrownShadow|RM_MapComponent_ShadeGrid|CrownShadow", re.I)


class CouldNotLook(Exception):
    pass


def parse_report(text):
    out = {}
    for tok in (text or "").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            try:
                out[k] = float(v) if re.match(r"^-?[0-9.]+$", v) else v
            except ValueError:
                out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pin-biome", default="", help="regenerate the current map as this biome (with --hilliness) first, "
                    "e.g. RM_LongShade, whose pinned sun gives a sun vector")
    ap.add_argument("--hilliness", default="Flat", help="the regenerated tile's hilliness (a mountainous tile is rock "
                    "and mountain roof: no tree takes, every cell reads indoors)")
    ap.add_argument("--side", type=int, default=120, help="the forest square's side in cells")
    ap.add_argument("--spacing", type=int, default=9, help="cells between greatbole roots")
    ap.add_argument("--sample-s", type=float, default=8.0, help="seconds of frames per off/on sample")
    ap.add_argument("--save", default="CROWN_SHADOW_GREATBOLE_REVIEW")
    ap.add_argument("--effort", default="", help="the effort, in words, for the reading")
    ap.add_argument("--broke", action="append", default=[], help="one observation of what broke (repeatable)")
    ap.add_argument("--previous-as", default="", help="keep the reading already on disk inside the new one under this key "
                    "(e.g. dense_forest: a spacing-9 cost run, then a sparse review run that the owner looks at)")
    ap.add_argument("--frame", type=int, default=70, help="the screenshot frame's width in cells (height 0.55 of it)")
    ap.add_argument("--annotate", action="store_true", help="no game: write --effort and --broke into the reading "
                    "after a look at its screenshots (the --broke lines replace the reading's)")
    a = ap.parse_args()
    if a.annotate:
        with open(READING, encoding="utf-8") as f:
            reading = json.load(f)
        if a.effort:
            reading["effort"] = a.effort
        if a.broke:
            reading["broke"] = a.broke
        with open(READING, "w", encoding="utf-8") as f:
            json.dump(reading, f, indent=1)
            f.write("\n")
        print("annotated %s" % READING)
        return 0
    from northstar_driver.session import FastSession
    with FastSession(strict=False, focus=False) as s:

        def static(method, args=""):
            r = s.call("jawa/static_call", type=OVERLAY_TYPE, method=method, args=args) or {}
            if not r.get("success"):
                raise CouldNotLook("static_call %s.%s: %s" % (OVERLAY_TYPE, method, r.get("message") or r))
            return str(r.get("result"))

        def setting(value):
            r = s.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="set",
                       field="renderedCrownShadows", value=value) or {}
            if not r.get("success"):
                raise CouldNotLook("set renderedCrownShadows=%s: %s" % (value, r.get("message") or r))

        def sample(label):
            static("CrownShadowReport", "current")       # resets the drawer's frame sample
            time.sleep(a.sample_s)
            rep = parse_report(static("CrownShadowReport", "current"))
            print("  %s: %s" % (label, rep), flush=True)
            return rep

        def sun():
            g = s.call("jawa/shadegrid_read") or {}
            return g, g.get("shadeGrid") or {}

        g, sg = sun()
        if not g.get("present"):
            raise CouldNotLook("no shade grid on the current map: %s" % json.dumps(g)[:300])
        if a.pin_biome:
            mi0 = s.call("jawa/map_info") or {}
            w = s.call("jawa/world_tile_set", tiles=str(mi0.get("tile")), biome=a.pin_biome, hilliness=a.hilliness) or {}
            s.call("jawa/world_commit")
            r = s.call("rimworld/execute_debug_action", path=r"Actions\Regenerate Current Map") or {}
            print("regenerate as %s: tile_set %s, regen %s" % (a.pin_biome, w.get("success"), r.get("success")), flush=True)
            for _ in range(60):
                time.sleep(3)
                mi = s.call("jawa/map_info") or {}
                if mi.get("mapId") is not None and mi.get("mapId") != mi0.get("mapId"):
                    break
            # The regenerated map has no colonists (live_site.py's recipe): a colony with none reads as lost, stops
            # every advance on colony_loss and leaves a review save nobody can walk.
            mi1 = s.call("jawa/map_info") or {}
            s.call("jawa/spawn_pawn", kindDef="Colonist", x=int(mi1.get("sizeX") or 250) // 2, z=20, faction="player", count=3)
            s.call("rimworld/execute_debug_action", path="Actions\\Destroy hostile pawns")
            s.call("jawa/safe_advance", action="start", ticks=300)
            g, sg = sun()
        e = sg.get("sunElevationDegrees")
        if not sg.get("isDirectional") or not e:
            raise CouldNotLook("the map has no sun vector (isDirectional %s, E %s); pass --pin-biome RM_LongShade or "
                               "load a fixed-sun world" % (sg.get("isDirectional"), e))
        rep0 = parse_report(static("CrownShadowReport", "current"))
        if "enabled" not in rep0 and rep0.get("drawers") != "none":
            raise CouldNotLook("CrownShadowReport answered %r (an old DLL?)" % rep0)
        mi = s.call("jawa/map_info") or {}
        W, H = int(mi.get("sizeX") or 0), int(mi.get("sizeZ") or 0)
        biome = mi.get("mapBiome")
        side = min(a.side, W - 20, H - 20)
        x0, z0 = (W - side) // 2, (H - side) // 2
        print("map %s %dx%d biome %s, E %.2f, shadow dir (%.2f,%.2f); forest %d cells at %d,%d" % (
            mi.get("mapId"), W, H, biome, e, sg.get("shadowDirX"), sg.get("shadowDirZ"), side, x0, z0), flush=True)
        rect = "%d,%d,%d,%d" % (x0, z0, side, side)
        s.call("jawa/set_fog", action="unfog", rect=rect)
        cl = s.call("jawa/set_plants", ops="CLEAR:" + rect) or {}
        print("clear:", json.dumps(cl)[:200], flush=True)
        # Open sky and soil the greatbole takes (fertilityMin 0.7): a forest floor, so the scene tests the shadow,
        # not the terrain. Rock Things are left: a root on one is rejected and simply not planted.
        rf = s.call("jawa/set_roof_batch", ops="None:" + rect) or {}
        tf = s.call("jawa/set_terrain_batch", ops="Soil:" + rect) or {}
        print("roof off: %s; soil: %s" % (rf.get("cellsChanged"), tf.get("cellsChanged") or json.dumps(tf)[:160]), flush=True)
        roots = [(x, z) for x in range(x0 + 4, x0 + side - 4, a.spacing) for z in range(z0 + 4, z0 + side - 4, a.spacing)]
        # Jitter the rows a little so the forest does not read as an orchard.
        roots = [(x + (z * 7 % 3) - 1, z + (x * 5 % 3) - 1) for x, z in roots]
        # One root per call, so the planted list is exact (a batch's rejectedCells names only its first 12).
        planted, reasons = [], {}
        for x, z in roots:
            r = s.call("jawa/set_plants", ops="%s:%d,%d,1,1" % (TREE, x, z), growth=1.0) or {}
            if int(r.get("planted") or 0) == 1:
                planted.append((x, z))
            else:
                why = ((r.get("rejectedCells") or [{}])[0] or {}).get("reason") or r.get("message")
                reasons[why] = reasons.get(why, 0) + 1
        if reasons:
            print("  rejected roots: %s" % reasons, flush=True)
        print("planted %d greatboles of %d roots" % (len(planted), len(roots)), flush=True)
        if not planted:
            raise CouldNotLook("no greatbole took (terrain): %s" % json.dumps(r)[:300])
        adv = s.call("jawa/safe_advance", action="start", ticks=RECOMPUTE_WAIT) or {}
        print("advance:", json.dumps(adv)[:160], flush=True)
        g, sg = sun()
        e = sg.get("sunElevationDegrees") or e
        fails = []
        # The scene switches renderedCrownShadows; every exit path puts back the value it found.
        prior = str((s.call("jawa/mod_settings_field", typeName=SETTINGS_TYPE, action="get",
                            field="renderedCrownShadows") or {}).get("value", "true")).lower()
        try:
            setting("true")
            on1 = sample("on")
            # The predicted disc centres of a few planted roots read crown shade (the drawn shadow sits on the grid's disc).
            import math
            cot = 1.0 / math.tan(math.radians(max(0.5, min(90.0, e))))
            drawn_size = None
            probe = []
            for x, z in planted[:: max(1, len(planted) // 12)][:12]:
                # The greatbole's drawn size is 12..16 at growth 1; the offset uses its crown height, capped at 16.
                off = min(16.0, HF * 14.0 * cot)
                probe.append((int(round(x + sg["shadowDirX"] * off)), int(round(z + sg["shadowDirZ"] * off))))
            rd = s.call("jawa/shadegrid_read", cells=";".join("%d,%d" % c for c in probe)) or {}
            cells = {(c["x"], c["z"]): c for c in rd.get("cells") or []}
            shaded = [c for c in probe if (cells.get(c) or {}).get("canopy", 0) >= 0.99]
            print("disc centres shaded: %d of %d (%s)" % (len(shaded), len(probe),
                  [(c, (cells.get(c) or {}).get("canopy"), (cells.get(c) or {}).get("cause")) for c in probe[:4]]), flush=True)
            if len(shaded) < len(probe):
                fails.append("disc centres shaded %d of %d" % (len(shaded), len(probe)))
            if int(on1.get("drawn") or 0) < len(planted):
                fails.append("drawn %s < planted %d" % (on1.get("drawn"), len(planted)))
            shots = {}

            def shot(name):
                cx, cz = planted[len(planted) // 2]
                s.call("jawa/clear_ui")
                s.call("rimworld/jump_camera_to_cell", x=cx, z=cz)
                fw, fh = a.frame, int(a.frame * 0.55)
                s.call("rimworld/frame_cell_rect", x=cx - fw // 2, z=cz - fh // 2, width=fw, height=fh, paddingCells=0)
                time.sleep(1.5)
                name = "%s_s%d" % (name, a.spacing)
                r = s.call("rimworld/take_screenshot", fileName=name, suppressMessage=True) or {}
                shots[name] = r.get("path")
                print("  shot %s: %s" % (name, r.get("path")), flush=True)

            shot("crown_shadow_on")
            setting("false")
            off = sample("off")
            if int(off.get("drawn") or 0) != 0:
                fails.append("setting off still draws %s" % off.get("drawn"))
            shot("crown_shadow_off")
            setting("true")
            on2 = sample("on again")
            if int(on2.get("drawn") or 0) < len(planted):
                fails.append("on again draws %s" % on2.get("drawn"))
            logs = s.call("rimbridge/list_logs", minimumLevel="error", limit=200) or {}
            bad = [str(m.get("message") or m)[:200] for m in (logs.get("entries") or logs.get("logs") or [])
                   if FORBIDDEN.search(json.dumps(m))]
            if bad:
                fails.append("forbidden log errors: %s" % bad[:3])
            sv = s.call("rimworld/save_game", saveName=a.save) or {}
            time.sleep(3)
            saves = os.path.join(os.environ.get("RM_GAME_USERDATA") or "", "Saves")
            spath = os.path.join(saves, a.save + ".rws")
            ok = os.path.isfile(spath) and os.path.getsize(spath) > 1000
            print("save: reported %s, on disk %s (%s bytes)" % (sv.get("path"), spath, os.path.getsize(spath) if ok else 0), flush=True)
            if not ok:
                raise CouldNotLook("the save %s did not land in %s" % (a.save, saves))
        finally:
            setting(prior)
        frame_on = (on1.get("frameMsMean", 0) + on2.get("frameMsMean", 0)) / 2.0
        reading = {
            "item": "RIMMANDRAKE_TRY_RENDERED_CROWN_SHADOW_ON_ONE_GIANT_TREE",
            "measured": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
            "game": os.environ.get("RM_GAME_INSTANCE") and {"a": "ArchBig", "b": "ArchSmall"}.get(os.environ["RM_GAME_INSTANCE"]),
            "map": {"biome": biome, "size": [W, H], "sun_elevation_deg": e,
                    "shadow_dir": [sg.get("shadowDirX"), sg.get("shadowDirZ")]},
            "tree": TREE, "planted": len(planted), "forest": [x0, z0, side, side],
            "shadows_drawn": int(on1.get("drawn") or 0),
            "meshes": int(on1.get("meshes") or 0),
            "rebuild_ms": on1.get("rebuildMs"),
            "draw_us_per_frame_on": (on1.get("drawUsMean", 0) + on2.get("drawUsMean", 0)) / 2.0,
            "frame_ms_on": round(frame_on, 3), "frame_ms_off": round(float(off.get("frameMsMean") or 0), 3),
            "frames_sampled": [on1.get("frames"), off.get("frames"), on2.get("frames")],
            "disc_centres_shaded": [len(shaded), len(probe)],
            "save": spath, "screenshots": shots,
            "effort": a.effort, "broke": a.broke, "fails": fails,
            "verdict": "PASS" if not fails else "FAIL",
        }
        if a.previous_as and os.path.isfile(READING):
            with open(READING, encoding="utf-8") as f:
                prev = json.load(f)
            prev.pop(a.previous_as, None)
            reading[a.previous_as] = prev
        with open(READING, "w", encoding="utf-8") as f:
            json.dump(reading, f, indent=1)
            f.write("\n")
        print("wrote %s" % READING)
        for x in fails:
            print("FAIL " + x)
        print("PASS live crown shadow experiment" if not fails else "FAIL live crown shadow experiment (%d)" % len(fails))
        return 0 if not fails else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CouldNotLook as ex:
        print("COULD NOT LOOK: %s" % ex)
        sys.exit(2)

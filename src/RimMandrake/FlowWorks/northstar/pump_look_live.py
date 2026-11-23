"""LIQUID_PUMP_REDRAW_PLAN_VIEW_HUB: stage the four pump looks, each with a pipe on every side and with none, beside its tank,
and photograph each one (kind A; run it when the game is ours).

  python.exe src/RimMandrake/FlowWorks/northstar/pump_look_live.py --out-dir DIR [--origin X,Z] [--fresh-map] [--save NAME]

Claim: a pipe on a pump's south covers the drawn cap and leaves the bolted rim visible; with no pipe the cap shows.
Entry point: build_batch, then the engine's own section meshes. Success: the captures, read by eye and by a judge; this script
only proves that the scene is what it says (defs, styles, drawn textures, sockets printed). Forbidden: any other thing on the
plots. End: captures written, save made.
Exit 0 = staged and captured as stated; 1 = a FAIL; 2 = not measured.
"""
import argparse
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")
W, H, PUMP = 10, 8, (3, 4)
PIPES = [(3, 5), (3, 6), (3, 3), (3, 2), (3, 1), (2, 4), (1, 4), (4, 4), (5, 4)]
TANK = (6, 4)


def local(p):
    p = str(p or "")
    return "/mnt/%s/%s" % (p[0].lower(), p[3:].replace("\\", "/")) if os.name != "nt" and p[1:2] == ":" else p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", default="100,110")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--save")
    ap.add_argument("--close-root-size", type=float, default=1.6)
    a = ap.parse_args()
    import proof_hose as PH
    B, V = PH.PB(), PH.V
    os.makedirs(a.out_dir, exist_ok=True)
    res = {"rows": []}
    bad = []

    def say(ok, text):
        print(("ok   " if ok else "FAIL ") + text, flush=True)
        res["rows"].append([bool(ok), text])
        if not ok:
            bad.append(text)

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        print("UNMEASURED no game in Playing")
        return 2
    ox, oz = (int(v) for v in a.origin.split(","))
    rect = (ox - 1, oz - 1, 4 * W + 2, 2 * H + 2)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site = []
    V.prepare_site(B, rect, site, "pump_look_site")
    say(not [r for r in site if r.get("status") not in (None, "PASS")], "site prepared %s" % str(site[:1])[:150])
    B.call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % rect)
    B.call("jawa/weather_set", weather="Clear", lockWeather=True)
    gl = B.call("jawa/glow_at", cells="%d,%d" % (ox, oz)) or {}
    hour = gl.get("hour")
    res["hour"] = hour
    if hour is not None and not 10 <= float(hour) <= 14:
        info = B.call("rimworld/get_game_info") or {}
        now = info.get("ticksGame") or (info.get("game") or {}).get("ticksGame")
        res["clock"] = B.call("jawa/time_set_ticks", ticks=int(now) + int(((12 - float(hour)) % 24) * 2500), timeException=True, why="noon light") if now else "no ticksGame: %s" % str(info)[:300]
    places = []
    for k, look in enumerate(LOOKS):
        for j, piped in enumerate((True, False)):
            px, pz = ox + k * W, oz + (0 if piped else H)
            ops = ["RM_LiquidPump:%d,%d" % (px + PUMP[0], pz + PUMP[1]), "RM_LiquidTank:%d,%d" % (px + TANK[0], pz + TANK[1])]
            if piped:
                ops += ["RM_UniversalPipe:%d,%d" % (px + x, pz + z) for x, z in PIPES]
            B.call("jawa/build_batch", ops=";".join(ops), faction="player", wipeExisting=False, readBack=0)
            places.append((look, piped, px, pz, len(ops)))
    B.call("rimworld/step_game_ticks", ticks=2, pauseFirst=True, timeoutMs=60000)
    for look, piped, px, pz, want in places:
        r = B.call("jawa/thing_graphic", rect="%d,%d,%d,%d" % (px, pz, W, H), defs="RM_LiquidPump,RM_LiquidTank,RM_UniversalPipe", limit=100) or {}
        things = r.get("things") or []
        say(len(things) == want, "%s %s: %d of %d things" % (look, "piped" if piped else "alone", len(things), want))
        done = 0
        for g in things:
            s = B.call("jawa/set_thing_props", thing=g.get("id"), style="%s_%s" % (g.get("defName"), look)) or {}
            done += s.get("styleDefAfter") == "%s_%s" % (g.get("defName"), look)
        say(done == want, "%s: %d styled" % (look, done))
    B.call("rimworld/step_game_ticks", ticks=30, pauseFirst=True, timeoutMs=60000)
    g = B.call("jawa/thing_graphic", rect="%d,%d,%d,%d" % rect, defs="RM_LiquidPump", limit=20) or {}
    res["pumps"] = [t.get("variantPath") or t.get("resolvedPath") or t.get("graphicPath") for t in g.get("things") or []]

    def power():
        """No 'needs power' icon over the art: the game stays paused, so the forced state holds."""
        n = 0
        for t in (B.call("jawa/thing_graphic", rect="%d,%d,%d,%d" % rect, defs="RM_LiquidPump", limit=20) or {}).get("things") or []:
            n += (B.call("jawa/power_net", thing=t.get("id"), forcePowerOn=True) or {}).get("success") is True
        return n

    say(power() == len(places), "pumps shown powered")
    shot_dir = None
    for look, piped, px, pz, _ in places:
        B.call("jawa/clear_ui", all=True)
        fn = "pump_%s_%s_block" % (look, "piped" if piped else "alone")
        B.call("rimworld/set_camera_zoom", rootSize=8)
        B.call("rimworld/jump_camera_to_cell", x=px + W // 2, z=pz + H // 2)
        time.sleep(0.7)     # the camera eases to its place over real frames
        s = B.call("rimworld/screenshot_cell_rect", x=px, z=pz, width=W, height=H, paddingCells=0, fileName=fn, suppressMessage=True) or {}
        src = local(s.get("path"))
        if src and os.path.isfile(src):
            shutil.copyfile(src, os.path.join(a.out_dir, fn + ".png"))
            shot_dir = local(s.get("screenshotFolder"))
        say(bool(src) and os.path.isfile(src), "capture %s" % fn)
    if a.save:
        sv = B.call("rimworld/save_game", saveName=a.save) or {}
        path = local(sv.get("path"))
        say(sv.get("success") is True and os.path.isfile(path), "save %s" % a.save)
        # close-ups: the bridge clamps the zoom at 8; a save opens at the camera it remembers
        import re
        with open(path, encoding="utf-8-sig", newline="") as f:
            txt = f.read()
        txt, n = re.subn(r"(<rememberedCameraPos>\s*<rootPos>[^<]*</rootPos>\s*<rootSize>)[^<]*", r"\g<1>%g" % a.close_root_size, txt)
        say(n == 1, "camera in the save set to %g" % a.close_root_size)
        close = os.path.join(os.path.dirname(path), a.save + "_CLOSE.rws")
        with open(close, "w", encoding="utf-8-sig", newline="") as f:
            f.write(txt)
        B.call("rimworld/load_game_ready", saveName=a.save + "_CLOSE", readiness="mapData", pauseIfNeeded=True, timeoutMs=200000)
        ok, _ = V._wait_playing(B, leave_s=0)
        res["close_power"] = power()
        res["close_camera"] = B.call("rimworld/get_camera_state")
        for look, piped, px, pz, _ in places:
            B.call("jawa/clear_ui", all=True)
            B.call("rimworld/jump_camera_to_cell", x=px + PUMP[0], z=pz + PUMP[1])
            time.sleep(1.2)
            fn = "pump_%s_%s_close" % (look, "piped" if piped else "alone")
            s = B.call("rimworld/take_screenshot", fileName=fn, suppressMessage=True) or {}
            src = local(s.get("path"))
            time.sleep(0.5)
            if src and os.path.isfile(src):
                shutil.copyfile(src, os.path.join(a.out_dir, fn + ".png"))
            say(bool(src) and os.path.isfile(src), "capture %s" % fn)
        res["close_camera_end"] = B.call("rimworld/get_camera_state")
    with open(os.path.join(a.out_dir, "pump_look_result_%s.json" % time.strftime("%Y%m%dT%H%M%S")), "w") as f:
        json.dump(res, f, indent=1, default=str)
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001  a transport fault is not measured, never a mod failure
        print("UNMEASURED HARNESS %s: %s" % (type(e).__name__, e), flush=True)
        sys.exit(2)

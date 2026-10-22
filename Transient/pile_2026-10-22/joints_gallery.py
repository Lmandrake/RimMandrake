"""joints_gallery.py -- FlowWorks pipe/hose JOINTS gallery for the 2026-10-22 night joints study (BENCH live helper).

    python.exe Transient/pile_2026-10-22/joints_gallery.py build [--ox 70 --oz 196]
    python.exe Transient/pile_2026-10-22/joints_gallery.py shoot <name> x z [rootSize]   # frame + screenshot
    python.exe Transient/pile_2026-10-22/joints_gallery.py things x z w h                 # list things in a rect

One row per look (Scrapper, Industrial, Modern, Futuristic), 12 cells apart, every join the owner asked about:
pipe straight H/V, bend, T, cross, end cap, pipe->tank (W and N), pipe->tall tank, pipe->pump (3 sides),
pipe->sprinklers (on the pipe), pipe->taps (beside + at the end), pole span over a ditch, pipe under a wall,
hose reel->tank, ->pump, ->pipe end, plump (flow on) vs flat, wound (reeled in), free end; a vanilla PowerConduit
run and a colonist in every row for girth.
"""
import json, os, sys, time
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint

LOOKS = ["Scrapper", "Industrial", "Modern", "Futuristic"]
HP = "RimMandrake.FlowWorks.Hose.HoseProbe"
LPROOF = "RimMandrake.FlowWorks.Machinery.RM_LineProofs"
notes = []


def main():
    a = sys.argv[1:]
    h, p, t = resolve_endpoint()
    with RimBridge(h, p, t) as B:
        def call(n, **kw):
            try:
                return B.call(n, kw) or {}
            except Exception as e:  # noqa
                return {"success": False, "error": str(e)[:300]}

        def hose(cmd, wait=20.0):
            before = call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value")
            call("jawa/mod_settings_field", typeName=HP, action="set", field="request", value=cmd)
            t0 = time.time()
            while time.time() - t0 < wait:
                if call("jawa/mod_settings_field", typeName=HP, action="get", field="serial").get("value") != before:
                    r = str(call("jawa/mod_settings_field", typeName=HP, action="get", field="result").get("value"))
                    if '"success":false' in r.replace(" ", ""):
                        notes.append("hose %s: %s" % (cmd, r[:200]))
                    return r
                time.sleep(0.25)
            notes.append("hose %s: timeout" % cmd)
            return ""

        if a[0] == "things":
            x, z, w, hh = (int(v) for v in a[1:5])
            r = call("jawa/list_things", rect="%d,%d,%d,%d" % (x, z, w, hh), limit=500)
            for th in r.get("things") or []:
                print(th.get("defName"), th.get("x"), th.get("z"), th.get("rotation") or th.get("rot"), th.get("style") or "")
            return
        if a[0] == "shoot":
            name, x, z = a[1], int(a[2]), int(a[3])
            rs = float(a[4]) if len(a) > 4 else 11
            call("rimworld/jump_camera_to_cell", x=x, z=z)
            call("rimworld/set_camera_zoom", rootSize=rs)
            call("jawa/clear_ui")
            for _ in range(10):
                ws = call("jawa/window_list_close").get("windows") or []
                hit = [w for w in ws if w.get("forcePause")]
                if not hit:
                    break
                call("jawa/window_list_close", action="close", typeName=hit[0]["type"])
            time.sleep(3.0)
            cam = call("rimworld/get_camera_state")
            s = call("jawa/take_screenshot", fileName=name)
            fp = s.get("filePath") or ""
            for _ in range(40):
                if fp and os.path.exists(fp) and os.path.getsize(fp) > 0:
                    break
                time.sleep(0.25)
            print(json.dumps({"shot": s.get("filePath") or s, "cam": {k: cam.get(k) for k in
                  ("position", "zoom", "rootSize", "viewRect", "mapId", "sizeRange")}}, default=str))
            return
        if a[0] == "cam":
            print(json.dumps(call("rimworld/get_camera_state"), default=str)[:1500])
            return
        if a[0] == "flow":
            for c in a[1:]:
                print(c, hose("flow:%s=on" % c)[:200])
            call("rimworld/step_game_ticks", ticks=200)
            return
        if a[0] == "hose":
            for c in a[1:]:
                print(c, hose(c)[:300])
            call("rimworld/step_game_ticks", ticks=2)
            return
        if a[0] == "facings":
            # reels in all 4 rotations laying east to a tank; tanks fed from N/S/E/W; Scrapper (z 196-222) and Modern (z 224-248)
            for L, zb in (("Scrapper", 196), ("Modern", 224)):
                rr = "%d,%d,%d,%d" % (220, zb - 1, 29, 27)
                call("jawa/destroy_batch", rects=rr, categories="All")
                call("jawa/set_terrain_batch", ops="Soil:" + rr)
                call("jawa/set_fog", action="unfog", rect=rr)
                for k, rot in enumerate((0, 1, 2, 3)):
                    z = zb + 1 + 5 * k
                    call("jawa/build_batch", ops="RM_HoseReel:%d,%d,%d" % (222, z, rot), faction="player", wipeExisting=False)
                    call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % (236, z), faction="player", wipeExisting=False)
                    for d, x in (("RM_HoseReel", 222), ("RM_LiquidTank", 236)):
                        th = call("jawa/list_things", defName=d, rect="%d,%d,1,1" % (x, z), limit=3).get("things") or []
                        if th:
                            call("jawa/set_thing_props", thing=str(th[0].get("id")), style="%s_%s" % (d, L))
                call("rimworld/step_game_ticks", ticks=1)
                for k in range(4):
                    z = zb + 1 + 5 * k
                    print(L, k, hose("lay:%d,%d,%d,%d" % (222, z, 235, z))[:160])
                # tank fed on 4 sides
                tz = zb + 20
                call("jawa/build_batch", ops="RM_LiquidTank:%d,%d" % (242, tz), faction="player", wipeExisting=False)
                th = call("jawa/list_things", defName="RM_LiquidTank", rect="%d,%d,1,1" % (242, tz), limit=3).get("things") or []
                if th:
                    call("jawa/set_thing_props", thing=str(th[0].get("id")), style="RM_LiquidTank_" + L)
                cells = [(239, tz), (240, tz), (241, tz), (244, tz + 1), (245, tz + 1), (246, tz + 1),
                         (242, tz + 2), (242, tz + 3), (243, tz - 1), (243, tz - 2)]
                call("jawa/build_batch", ops=";".join("RM_UniversalPipe:%d,%d" % c for c in cells), faction="player", wipeExisting=False)
                for c in cells:
                    th = call("jawa/list_things", defName="RM_UniversalPipe", rect="%d,%d,1,1" % c, limit=3).get("things") or []
                    if th:
                        call("jawa/set_thing_props", thing=str(th[0].get("id")), style="RM_UniversalPipe_" + L)
            call("rimworld/step_game_ticks", ticks=5)
            print("notes", notes)
            return
        if a[0] != "build":
            sys.exit("build|shoot|things|cam|flow")
        ox, oz = 70, 196
        W, H = 165, 50
        rr = "%d,%d,%d,%d" % (ox - 2, oz - 2, W, H)
        call("jawa/destroy_batch", rects=rr, categories="All")
        call("jawa/set_terrain_batch", ops="Soil:" + rr)
        call("jawa/set_fog", action="unfog", rect=rr)
        call("jawa/set_roof_batch", ops="None:" + rr)
        for i, L in enumerate(LOOKS):
            z0 = oz + 12 * i
            builds, styles, after = [], [], []

            def P(x, z):
                builds.append(("RM_UniversalPipe", x, z))
                styles.append(("RM_UniversalPipe", x, z, "RM_UniversalPipe_" + L))
            # A shapes
            for x in range(0, 5): P(x, 1)
            for z in range(0, 5): P(6, z)
            for c in [(8, 4), (9, 4), (10, 4), (10, 3), (10, 2)]: P(*c)
            for x in range(12, 17): P(x, 2)
            for z in (3, 4): P(14, z)
            for x in range(18, 23): P(x, 2)
            for z in (0, 1, 3, 4): P(20, z)
            P(24, 1)
            P(24, 3); P(25, 3)
            # vanilla conduit + pawn for girth
            for x in range(0, 6):
                builds.append(("PowerConduit", x, 8))
            # B tank W + N, tall tank E
            builds.append(("RM_LiquidTank", 31, 2)); styles.append(("RM_LiquidTank", 31, 2, "RM_LiquidTank_" + L))
            for x in (28, 29, 30): P(x, 2)
            for z in (5, 6): P(31, z)
            builds.append(("RM_LiquidTankTall", 36, 2)); styles.append(("RM_LiquidTankTall", 36, 2, "RM_LiquidTankTall_" + L))
            for x in (38, 39, 40): P(x, 2)
            # C pump 3 sides
            builds.append(("RM_LiquidPump", 46, 2))
            for x in (43, 44, 45): P(x, 2)
            for x in (47, 48, 49): P(x, 2)
            for z in (3, 4): P(46, z)
            # D sprinklers on the pipe
            for x in range(52, 59): P(x, 2)
            for x in (53, 56, 58):
                builds.append(("RM_SprinklerHead", x, 2)); styles.append(("RM_SprinklerHead", x, 2, "RM_SprinklerHead_" + L))
            # E taps beside + end
            for x in range(61, 65): P(x, 2)
            for x in (62, 64): builds.append(("RM_LiquidTap", x, 1))
            builds.append(("RM_LiquidTap", 65, 2))
            # F pole span over a ditch
            for x in (66, 67): P(x, 2)
            builds.append(("RM_PipePole", 68, 2)); styles.append(("RM_PipePole", 68, 2, "RM_PipePole_" + L))
            builds.append(("RM_PipePole", 73, 2)); styles.append(("RM_PipePole", 73, 2, "RM_PipePole_" + L))
            for x in (74, 75, 76): P(x, 2)
            # G pipe under a wall
            for x in range(79, 86): P(x, 2)
            for z in range(0, 5): after.append(("Wall", 82, z))
            # H hoses
            reels = [(88, 1), (88, 6), (108, 1), (108, 6), (130, 1), (130, 6)]
            for rx, rz in reels:
                builds.append(("RM_HoseReel", rx, rz)); styles.append(("RM_HoseReel", rx, rz, "RM_HoseReel_" + L))
            builds.append(("RM_LiquidTank", 102, 1)); styles.append(("RM_LiquidTank", 102, 1, "RM_LiquidTank_" + L))
            builds.append(("RM_LiquidPump", 102, 7))
            for x in range(122, 127): P(x, 1)
            builds.append(("RM_LiquidTank", 122, 6)); styles.append(("RM_LiquidTank", 122, 6, "RM_LiquidTank_" + L))
            ops = ";".join("%s:%d,%d" % (d, ox + x, z0 + z) for d, x, z in builds)
            r = call("jawa/build_batch", ops=ops, faction="player", wipeExisting=False, stuff="Steel")
            print(L, "build survived", r.get("survived"), "failed", (r.get("failed") or [])[:4])
            # dig the ditch under the span
            for x in range(69, 73):
                for z in (1, 2, 3):
                    call("jawa/flowworks_excavation_drive", x=ox + x, z=z0 + z, deepenLevels=4, setFill=-1)
            for d, x, z, st in styles:
                th = call("jawa/list_things", defName=d, rect="%d,%d,1,1" % (ox + x, z0 + z), limit=3).get("things") or []
                if not th:
                    notes.append("%s style: no %s at %s" % (L, d, (x, z)))
                    continue
                rs = call("jawa/set_thing_props", thing=str(th[0].get("id") or th[0].get("thingId")), style=st)
                if "style" not in (rs.get("changed") or []):
                    notes.append("%s style %s not written: %s" % (L, st, json.dumps(rs)[:120]))
            call("jawa/static_call", type=LPROOF, method="ProofLinkPoles",
                 args="%d,%d;%d,%d" % (ox + 68, z0 + 2, ox + 73, z0 + 2))
            call("jawa/spawn_pawn", kindDef="Colonist", x=ox + 7, z=z0 + 8, faction="player", count=1)
            # hoses
            call("rimworld/step_game_ticks", ticks=1)
            g = lambda x, z: (ox + x, z0 + z)  # noqa: E731
            hose("lay:%d,%d,%d,%d" % (g(88, 1) + g(101, 1)))
            hose("lay:%d,%d,%d,%d" % (g(88, 6) + g(102, 7)))
            hose("lay:%d,%d,%d,%d" % (g(108, 1) + g(122, 1)))
            hose("lay:%d,%d,%d,%d" % (g(108, 6) + g(121, 6)))
            hose("lay:%d,%d,%d,%d" % (g(130, 1) + g(144, 1)))
            hose("lay:%d,%d,%d,%d" % (g(130, 6) + g(144, 6)))
            hose("end:%d,%d=nozzle" % g(130, 6))
            call("rimworld/step_game_ticks", ticks=2)
            hose("flow:%d,%d=on" % g(108, 6))
            hose("reelin:%d,%d" % g(130, 1))
            ops = ";".join("%s:%d,%d" % (d, ox + x, z0 + z) for d, x, z in after)
            call("jawa/build_batch", ops=ops, faction="player", wipeExisting=False, stuff="BlocksGranite")
        call("rimworld/step_game_ticks", ticks=120)
        print("notes", json.dumps(notes, indent=0)[:4000])


main()

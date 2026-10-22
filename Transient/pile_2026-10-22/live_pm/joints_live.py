"""BENCH live helper PM 2026-10-22: live rows for REEL_OUTLET_DECIDE_ALWAYS_GOES_WEST, PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID,
HOSE_GIRTH_TUNE_MUCH_THINNER, BLEED_WELL strings, DRILL_PLACEMENT (empty survey), PIT_COVER (partly covered pit walkable).
python.exe joints_live.py <out.json> <phase>     phases: prep reels tank shadow drill cover
Runs on a disposable debug map (never the walkthrough save)."""
import json, os, sys, time, math
sys.path.insert(0, os.path.join("src", "RimMandrake", "FlowWorks", "northstar"))
sys.path.insert(0, os.path.join("src", "RimMandrake", "Utils"))
import proof_hose as PH
import validation_core as V
B = PH.PB()
out, phase = sys.argv[1], sys.argv[2]
doc = json.load(open(out)) if os.path.exists(out) else {"phases": {}}
log = doc["phases"].setdefault(phase, [])
SITE = (10, 10, 110, 60)   # x,z,w,h


def save():
    with open(out + ".tmp", "w") as f:
        json.dump(doc, f, indent=1, default=str)
    os.replace(out + ".tmp", out)


def note(**kw):
    kw["wall"] = time.strftime("%H:%M:%S")
    log.append(kw)
    save()
    print(json.dumps(kw, default=str)[:900], flush=True)


def slim(r):
    return {k: v for k, v in (r or {}).items() if k not in ("operation", "state", "typeIdentity")}


def step(n):
    return (B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 60)) or {}).get("advancedTicks")


def sc(t, m, a=""):
    return slim(B.call("jawa/static_call", type=t, method=m, args=a))


def shot(name, x, z, w, h, pad=2):
    r = B.call("rimworld/screenshot_cell_rect", x=x, z=z, width=w, height=h, paddingCells=pad, fileName=name, includeTargets=False) or {}
    return r.get("path") or slim(r)


def census():
    return B.hp("census")


REELS = [(0, 22, 30), (1, 42, 30), (2, 62, 30), (3, 82, 30)]   # rot (N,E,S,W), reel cell
DIRS = {0: (0, 1), 1: (1, 0), 2: (0, -1), 3: (-1, 0)}
REACH = 8

if phase == "prep":
    r = "%d,%d,%d,%d" % SITE
    note(huge=str(V.clear_huge_plants(B))[:300])
    for tool, kw in (("jawa/destroy_batch", {"rects": r, "categories": "All"}),
                     ("jawa/set_terrain_batch", {"ops": "Soil:" + r}),
                     ("jawa/set_fog", {"action": "unfog", "rect": r}),
                     ("jawa/set_roof_batch", {"ops": "None:" + r})):
        note(tool=tool, res=str(slim(B.call(tool, **kw)))[:300])
    note(survey=slim(B.call("jawa/map_comp_read", comp="SubsurfaceLiquid")).get("values"))

elif phase == "reels":
    res = []
    for rot, x, z in REELS:
        pl = B.hp("place:RM_HoseReel:Scrapper:%d,%d:%d:god" % (x, z, rot))
        res.append({"rot": rot, "place": pl})
    # control: a west-facing reel (the old fixed outlet) laying EAST must loop (the can-fail)
    res.append({"rot": "3ctl", "place": B.hp("place:RM_HoseReel:Scrapper:102,30:3:god")})
    note(placed=res)
    things = slim(B.call("jawa/list_things", defName="RM_HoseReel", rect="%d,%d,%d,%d" % SITE, limit=20))
    note(reelThings=[{k: t.get(k) for k in ("thingId", "id", "x", "z", "rot", "rotation", "position", "label")} for t in things.get("things") or []])
    lays = []
    cen = census()
    for h in cen.get("hoses") or []:
        rx, rz = h["reel"]
        rot = next((r for r, x, z in REELS if (x, z) == (rx, rz)), None)
        if (rx, rz) == (102, 30):
            tx, tz, rot = rx + REACH, rz, "3ctl"
        elif rot is None:
            continue
        else:
            dx, dz = DIRS[rot]
            tx, tz = rx + dx * REACH, rz + dz * REACH
        lays.append({"reel": [rx, rz], "rot": rot, "target": [tx, tz], "lay": B.hp("lay:%d,%d,%d,%d" % (rx, rz, tx, tz))})
    note(lays=lays)
    step(60)
    B.call("rimworld/set_camera_zoom", rootSize=24)
    note(shot=shot("pm_reels_4facings", 12, 18, 100, 24, 1))
    cen = census()
    note(hoses=[{k: h.get(k) for k in ("reel", "far", "laid", "layOk", "layReason", "draw", "freeEnd", "visibleWidth", "meshWidthFlat")}
                for h in cen.get("hoses") or []], defaultLook=cen.get("defaultLook"))
    for rot, x, z in REELS + [("3ctl", 102, 30)]:
        note(rot=rot, closeup=shot("pm_reel_%s" % rot, x - 3, z - 10, 14, 20, 1))

elif phase == "tank":
    # 2x2 tank at 40..41,50..51; pipes on its lower row west and east
    note(build=slim(B.call("jawa/build_batch", ops="RM_LiquidTank:40,50", stuff="Steel", faction="player")))
    ops = ";".join("RM_UniversalPipe:%d,50" % x for x in (35, 36, 37, 38, 39, 42, 43, 44, 45, 46))
    note(pipes=slim(B.call("jawa/build_batch", ops=ops, stuff="Steel", faction="player")))
    step(10)
    note(net=slim(B.call("jawa/pipe_net_info", x=38, z=50)) if True else None)
    note(things=[{k: t.get(k) for k in ("defName", "x", "z", "rot")} for t in
                 (slim(B.call("jawa/list_things", rect="34,48,14,5", limit=30)).get("things") or [])])
    B.call("rimworld/set_camera_zoom", rootSize=8)
    note(shot=shot("pm_pipe_tank_riser", 34, 48, 14, 5, 1))

elif phase == "shadow":
    T = "RimMandrake.FlowWorks.Hose.HoseMath"
    note(alphaEmpty=sc(T, "ShadowAlpha", "0"), alphaFull=sc(T, "ShadowAlpha", "1"),
         widthEmpty=sc(T, "ShadowWidth", "0"), widthFull=sc(T, "ShadowWidth", "1"))

elif phase == "drill":
    note(survey=slim(B.call("jawa/map_comp_read", comp="SubsurfaceLiquid")).get("values"))
    for d in ("RM_LiquidDrill", "RM_LiquidTap", "RM_LiquidTank"):
        note(check=d, res=slim(B.call("jawa/build_check", **{"def": d, "rect": "70,50,1,1", "stuff": "Steel"})))
    note(tapSpawn=slim(B.call("jawa/build_batch", ops="RM_LiquidTap:90,50", stuff="Steel", faction="player")))
    note(tapLabel=slim(B.call("jawa/inspect_string", defName="RM_LiquidTap", rect="85,45,10,10", limit=3)))

elif phase == "cover":
    # pit 3 x 5 (x 60..64, z 46..48), 8 notches = 4 m; planks across the middle row z=47
    for x in range(60, 65):
        for z in (46, 47, 48):
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=8, setFill=-1)
    note(depth=slim(B.call("jawa/flowworks_excavation_rect", x=60, z=46, w=5, h=3, onlyNonZero=False)).get("rows"))
    ops = ";".join("RM_PitCover_PlankLattice:%d,47" % x for x in range(60, 65))
    note(covers=slim(B.call("jawa/build_batch", ops=ops, stuff="WoodLog", faction="player")))
    cols = (B.call("rimworld/list_colonists", currentMapOnly=True) or {}).get("colonists") or []
    free = [c for c in cols if not c.get("downed") and not c.get("drafted")] or cols
    pid = free[0]["pawnId"]
    num = str(free[0]["thingIdNumber"])
    B.call("jawa/set_draft", pawnId=pid, drafted=True)
    # bring him to the west lip by teleport-free walking: order to (56,47)
    note(go1=slim(B.call("jawa/order_pawn", pawnId=pid, x=56, z=47)))
    for i in range(30):
        step(60)
        p = [c for c in (B.call("rimworld/list_colonists", currentMapOnly=True) or {}).get("colonists") or [] if c["pawnId"] == pid][0]
        if (p["position"]["x"], p["position"]["z"]) == (56, 47):
            break
    note(atStart=p["position"], ticks=(i + 1) * 60)
    P = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
    note(pathCovered=sc(P, "ProofPath", "%s;62,47" % num), pathAcross=sc(P, "ProofPath", "%s;67,47" % num),
         pathOpenPit=sc(P, "ProofPath", "%s;62,46" % num))
    note(go2=slim(B.call("jawa/order_pawn", pawnId=pid, x=62, z=47)))
    for i in range(10):
        step(30)
        p = [c for c in (B.call("rimworld/list_colonists", currentMapOnly=True) or {}).get("colonists") or [] if c["pawnId"] == pid][0]
        if (p["position"]["x"], p["position"]["z"]) == (62, 47):
            break
    note(onCover=p["position"], ticks=(i + 1) * 30, job=p.get("job"))
    B.call("rimworld/set_camera_zoom", rootSize=10)
    note(shot=shot("pm_pit_cover_walk", 55, 43, 14, 9, 1))
save()

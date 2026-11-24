"""walk_look.py: his full list, the walk map of visit 1 loaded on the fixed build: cords read, every station captured. python.exe. Saves nothing."""
import os, sys, shutil, json, collections
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA
B = VA.A(); OUT = r"D:\ClaudeWork\rimmandrake\scratch\gss_020_v3\walk"; os.makedirs(OUT, exist_ok=True)
V_ = sys.argv[1]
print(str(B.call("rimworld/load_game_ready", saveName=V_, ignoreModCompatibility=True, allowIncompatibleMods=True) if 0 else B.call("rimworld/load_game_ready", saveName=V_, ignoreModCompatibility=True))[:200])
B.call("rimworld/set_time_speed", speed=0) if False else None
B.probe("poll"); B.probe("rebuild"); B.ticks(30)
c = B.probe("census"); print(json.dumps({k: c.get(k) for k in ("cordEdges", "cordsAcrossNets", "cordEndsWithoutNet", "verticesInUnwalkable", "pieces", "unroutable", "fellBack", "dives", "conduitCells", "decals")}))
selfloops = [k for k in c.get("edgeHashes", {}) if len(set(k.split("|"))) == 1]; print("self loops", selfloops)
a = B.ap("census"); print("spans", a.get("spansUp"), "cut", a.get("spansCut"), "anchors", len(a.get("anchors") or []))
print("joins", json.dumps({k: v for k, v in B.probe("joins").items() if k in ("taken", "offLine", "offSlope", "empty")}))
B.call("jawa/clear_ui")
pts = []
for d in ("PowerConduit", "RM_AerialMast", "RM_AerialLampMast", "WallLamp", "StandingLamp", "Battery"):
    for t in B.call("jawa/list_things", defName=d, limit=2000).get("things") or []: pts.append((t["x"], t["z"]))
W, H = 34, 20
cc = collections.Counter((x // W, z // H) for x, z in pts); print(len(pts))
for i, ((p, q), n) in enumerate(cc.most_common(16)):
    if n < 6: continue
    r = (p * W, q * H, W, H); log = []
    B.call("rimworld/jump_camera_to_cell", x=r[0] + W // 2, z=r[1] + H // 2); V.frame_fit(B, r)
    d = V.shot(B, "walk_%d_%d" % (p, q), r, log, pad=0)
    if d and os.path.exists(str(d)): shutil.copy(str(d), os.path.join(OUT, "w_%02d_%d_%d.png" % (i, p, q)))
    print(i, r, n)

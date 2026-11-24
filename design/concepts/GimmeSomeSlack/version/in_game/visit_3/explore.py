"""explore.py: load his review map copy, find where its conduits stand, and capture each cluster at play zoom. python.exe. Read only: nothing is saved."""
import os, sys, shutil, collections, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA
B = VA.A(); OUT = r"D:\ClaudeWork\rimmandrake\scratch\gss_020_v3\explore"; os.makedirs(OUT, exist_ok=True)
print(str(B.call("rimworld/load_game_ready", saveName="GSS_OWNER_LOOK_20261116"))[:120])
B.probe("poll"); B.probe("rebuild"); B.ticks(5); B.call("jawa/clear_ui"); B.call("jawa/review_label", action="hide")
pts = []
for d in ("PowerConduit", "RM_AerialMast", "WallLamp", "StandingLamp", "Battery"):
    for t in B.call("jawa/list_things", defName=d, limit=2000).get("things") or []:
        pts.append((t["x"], t["z"])) if "x" in t else print(t)
W, H = 34, 20
c = collections.Counter((x // W, z // H) for x, z in pts)
print(len(pts), sorted(c.items()))
for i, ((a, b), n) in enumerate(c.most_common(16)):
    if n < 8: continue
    r = (a * W, b * H, W, H); log = []
    B.call("rimworld/jump_camera_to_cell", x=r[0] + W // 2, z=r[1] + H // 2); V.frame_fit(B, r)
    d = V.shot(B, "explore_%d_%d" % (a, b), r, log, pad=0)
    if d: shutil.copy(str(d), os.path.join(OUT, "e_%02d_%d_%d.png" % (i, a, b)))
print("bends", str(B.probe("bends"))[:600]); print("kinks", str(B.probe("kinks"))[:400])

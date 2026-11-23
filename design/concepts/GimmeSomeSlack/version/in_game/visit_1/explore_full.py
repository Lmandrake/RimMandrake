"""explore_full.py: full list. Loads the walk save, reads the master off/on, the wall lamps' power, and captures every station. python.exe."""
import os, sys, shutil, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, scene_rows as S, human_review as H
from await_lifecycle import await_lifecycle
SAVE = sys.argv[1]; pre = sys.argv[2]
OUT = r"D:\ClaudeWork\rimmandrake\scratch\gss_020_v1\shots"
B = VA.A()
if SAVE != "-":
    print("load", str(B.call("rimworld/load_game_ready", saveName=SAVE))[:150]); print("ready", await_lifecycle(B.call, "map_ready", 240, poll_s=0.5).ok)
B.probe("poll"); B.ticks(300)
_, mem, lamps = S._styles(B, (20, 60, 40, 30))
res = {"lamps": [(l["def"], l.get("look"), str(l.get("drawnPath")).split("/")[-2:], l.get("rot")) for l in lamps.values()]}
def cens():
    c = B.probe("census"); j = B.probe("joins:0,0,400,400")
    return {"invisibleApplied": c.get("invisibleApplied"), "layerVisible": c.get("layerVisible"), "spawnedConduitTexture": c.get("spawnedConduitTexture"),
            "tex": sorted(set((c.get("texPaths") or {}).values()))[:4], "edges": c.get("edges"), "offLine": j.get("offLine"), "offSlope": j.get("offSlope"), "taken": j.get("taken")}
res["on0"] = cens()
B.probe("set:enabled=False"); B.ticks(2); res["off"] = cens()
_, _, l2 = S._styles(B, (20, 60, 40, 30)); res["lamps_off"] = sorted(set(str(l.get("drawnPath")) for l in l2.values()))
B.probe("set:enabled=True"); B.ticks(30); B.probe("rebuild"); B.ticks(2); res["on1"] = cens()
_, _, l3 = S._styles(B, (20, 60, 40, 30)); res["lamps_on"] = sorted(set(str(l.get("drawnPath")) for l in l3.values()))
print(json.dumps(res, default=str)[:3500])
json.dump(res, open(os.path.join(HERE, "evidence", pre + "_master_off_on.json"), "w"), indent=1, default=str)
st = [(str(s["n"]), (s["origin"][0] - 1, s["origin"][1] - 2, s["size"][0] + 2, s["size"][1] + 6)) for s in H.station_list()] + \
     [("32", (20, 60, 32, 11)), ("33", (20, 74, 32, 12)), ("33z", (21, 79, 14, 6)), ("33y", (35, 77, 16, 8))]
for n, r in st:
    V.frame_fit(B, r); log = []
    d = V.shot(B, pre + "_" + n, r, log)
    if d and os.path.exists(str(d)): shutil.copy(str(d), os.path.join(OUT, pre + "_" + n + ".png"))
    else: print("no shot", n, d, log[-1:])

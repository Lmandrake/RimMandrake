"""full_probe.py: his full list: the wire-down plot on the map (after the keeper save; nothing is saved), the stub joins, master off and on. python.exe."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, save_wire_down as WD
B = VA.A()
j = B.probe("joins:"); print("joins", {k: j.get(k) for k in ("taken", "offLine", "offSlope", "empty", "bad")})
def look(tag):
    c = B.probe("census"); print(tag, {k: c.get(k) for k in ("enabled", "invisibleApplied", "spawnedConduitTexture", "cordEdges", "layerVisible", "strands")})
look("on")
B.probe("set:enabled=False"); B.ticks(5); look("off"); print(str(B.call("rimworld/take_screenshot", fileName="gss_v3_master_off").get("path")))
time.sleep(1); B.probe("set:enabled=True"); B.ticks(5); B.probe("rebuild"); look("on again")
WD.stage(B, V); WD.wire_down(B); r = WD.read(B); print("wd", WD.midway(r), r["ends"], r["cords"])

import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
GSS = os.path.join(REPO, "src", "RimMandrake", "GimmeSomeSlack"); sys.path[:0] = [GSS, os.path.join(GSS, "northstar"), os.path.join(REPO, "src", "RimMandrake", "Utils")]
import validation as V, validation_aerial as VA, time
B = VA.A()
c = B.probe("census"); print(json.dumps({k: v for k, v in c.items() if k not in ("polylines",)})[:2500])
xs = [int(v) for k in c["edgeHashes"] for e in k.split("|") for v in e.split(":")[1].split(",")]
x0, x1, z0, z1 = min(xs[::2]), max(xs[::2]), min(xs[1::2]), max(xs[1::2])
R = (x0 - 8, z0 - 8, x1 - x0 + 16, z1 - z0 + 16)
r = B.probe("rect:%d,%d,%d,%d" % R)
print({k: v for k, v in r.items() if k not in ("polylines", "nodes")})
cells = {}
for p in r["polylines"]:
    for x, z in p: cells[(int(x), int(z))] = cells.get((int(x), int(z)), 0) + 1
import collections
for (x, z), n in sorted(cells.items()):
    g = B.call("rimworld/get_cell_info", x=x, z=z)
    s = json.dumps(g)
    things = [t.get("defName") for t in (g.get("things") or (g.get("cell") or {}).get("things") or [])]
    w = (g.get("cell") or g).get("walkable")
    if w is False or any(t in ("Battery", "StandingLamp", "Wall", "GravshipHull") for t in things): print((x, z), n, "walkable", w, things)
print(s[:700])
for p in r["polylines"]: print(len(p), p[0], p[-1])
B.call("jawa/clear_ui"); B.call("rimworld/jump_camera_to_cell", x=(x0 + x1) // 2, z=(z0 + z1) // 2); B.call("rimworld/set_camera_zoom", rootSize=11); time.sleep(1.2)
print(B.call("rimworld/take_screenshot", fileName="gss_v3_gs").get("path"))

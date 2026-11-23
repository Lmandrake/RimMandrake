"""Write a sweep of station-3-like worlds for SelfTest --lab (a folder of worlds). Axes: seed, tangle shape, battery lead,
lamp offsets, wall on/off and place, pile look (strips/boxes), slack scale, cord count. Usage: gen.py OUTDIR [--small]"""
import json, os, sys, itertools
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
small = "--small" in sys.argv
W, H = 30, 16
def world(seed, tw, th, blead, lamp_dz, lamp_dx, wall, pile, slack, cords, look):
    ox, oz = 3, 4
    tx0 = ox + 2 + blead                     # tangle west column
    zc = oz + 3                              # run row
    cells = set()
    for x in range(ox + 1, tx0): cells.add((x, zc))                    # battery lead
    tz0 = zc - (th // 2)
    for x in range(tx0, tx0 + tw):
        for z in range(tz0, tz0 + th): cells.add((x, z))
    xe = tx0 + tw
    sw = xe + 3                                                        # switch after 3 cells of run
    for x in range(xe, sw): cells.add((x, zc))
    for x in (sw + 1, sw + 2, sw + 4, sw + 5): cells.add((x, zc))      # past switch, a gap at sw+3
    wallx = xe + 1 if wall else None
    blocked = [[wallx, z, 1] for z in range(zc - 2, zc + 3)] if wall else []
    m = []
    m.append(dict(id="bat", def_="Battery", kind=1, x=ox, z=zc, w=1, h=2, hookups=[[ox + 1, zc]], cp=None))
    m.append(dict(id="sw", def_="PowerSwitch", kind=4, x=sw, z=zc, w=1, h=1, hookups=[[sw + 1, zc], [sw - 1, zc]], cp=None))
    m.append(dict(id="heat", def_="Heater", kind=2, x=sw + 6, z=zc, w=1, h=1, hookups=[[sw + 5, zc]], cp=[sw + 5, zc]))
    lx = tx0 - 1 + lamp_dx
    lamps = [(lx, zc + lamp_dz, (tx0, tz0 + th - 1)), (sw + 1, zc + 3, (sw + 1, zc)), (sw + 5, zc + 3, (sw + 5, zc))]
    for i, (x, z, hp) in enumerate(lamps):
        m.append(dict(id="lamp%d" % i, def_="StandingLamp", kind=2, x=x, z=z, w=1, h=1, hookups=[list(hp)], cp=list(hp), baseDz=-0.25))
    occ = {(q["x"], q["z"]) for q in m}
    if any(c in occ for c in cells): return None
    machines = [{"id": q["id"], "def": q["def_"], "baseDz": q.get("baseDz", 0), "kind": q["kind"], "x": q["x"], "z": q["z"], "w": q["w"], "h": q["h"],
                 "hookups": q["hookups"], "links": [], "insets": [0, 0, 0, 0], "connectParent": q["cp"], "parentDraw": "ConduitCell" if q["cp"] else None,
                 "hasHookup": True, "hasLink": False} for q in m]
    conduit = sorted(cells)
    gap_far = {(sw + 4, zc), (sw + 5, zc)}
    live = [list(c) for c in conduit if c not in gap_far]
    allc = conduit + [(sw, zc)]
    return {"w": W, "h": H, "conduit": [list(c) for c in conduit], "blocked": blocked, "doors": [], "buried": [], "busy": [list(c) for c in conduit],
            "furniture": [], "costs": [], "connectParentData": True, "unhooked": [], "machines": machines, "live": live,
            "strips": [list(c) for c in allc] if pile == "strips" else [], "boxes": [list(c) for c in allc] if pile == "boxes" else [],
            "looks": [[c[0], c[1], look] for c in allc],
            "opt": {"boot": 0.102, "tangles": True, "needless": True, "tangleMin": 9, "strips": pile == "strips", "dive": True, "slide": True, "seed": seed,
                    "slack": slack, "maxExtra": 16, "cordsMax": cords, "straight": []}}
axes = dict(seed=range(1, 4 if small else 7), shape=[(3, 3), (4, 3), (3, 4), (4, 4)], blead=[1, 2, 4], lamp=[(3, 0), (2, 2), (4, 3)],
            wall=[True, False], pile=[("strips", "Modern"), ("boxes", "Scrapper")], slack=[0.6, 1.0, 1.6], cords=[1, 2])
if small:
    axes.update(blead=[1, 3], lamp=[(3, 0), (2, 2)], slack=[1.0], cords=[1])
n = 0
for seed, (tw, th), blead, (ldz, ldx), wall, (pile, look), slack, cords in itertools.product(*axes.values()):
    wd = world(seed, tw, th, blead, ldz, ldx, wall, pile, slack, cords, look)
    if wd is None: continue
    name = "s%d_t%dx%d_b%d_l%d%d_w%d_%s_k%s_c%d" % (seed, tw, th, blead, ldz, ldx, int(wall), pile, str(slack).replace(".", ""), cords)
    json.dump(wd, open(os.path.join(out, name + ".json"), "w")); n += 1
print(n, "worlds ->", out)

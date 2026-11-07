#!/usr/bin/env python3
"""Doorway layouts for the shape lab: every way a player runs conduit through or past a door, on several seeds.

    python3 ralph/live/lab_doors.py gen  DIR            write the worlds
    python3 ralph/live/lab_doors.py read DIR OUTDIR     count the lines reaching each doorway and conduit end

Lines at a point = how many times the laid cords cross a ring round it. A cord ending there is one line; a cord that leaves and comes back is three.
"""
import json, math, os, sys

W, H = 60, 40
OPT = {"tangles": True, "needless": True, "tangleMin": 9, "strips": True, "dive": True, "slide": True, "slack": 1, "maxExtra": 16, "cordsMax": 1, "straight": []}
BAT = (10, 18)


def world(conduit, doors, walls, seed, strips=True, machines=None):
    blocked = [[x, z, 1] for x, z in walls if (x, z) not in doors]
    c = sorted(set(conduit))
    ms = machines if machines is not None else [{"id": "bat", "kind": 1, "x": BAT[0], "z": BAT[1], "w": 1, "h": 2, "hookups": [[BAT[0] + 1, BAT[1]]], "links": [], "insets": [0, 0, 0, 0]}]
    o = dict(OPT, seed=seed, strips=strips)
    return {"w": W, "h": H, "conduit": [list(q) for q in c], "blocked": blocked, "doors": [list(q) for q in doors], "buried": [], "busy": [], "machines": ms, "live": [list(q) for q in c],
            "strips": [list(q) for q in c] if strips else [], "boxes": [], "opt": o}


def line(x0, z0, x1, z1):
    if x0 == x1:
        return [(x0, z) for z in range(min(z0, z1), max(z0, z1) + 1)]
    return [(x, z0) for x in range(min(x0, x1), max(x0, x1) + 1)]


def perim(x0, z0, x1, z1):
    return set(line(x0, z0, x1, z0) + line(x0, z1, x1, z1) + line(x0, z0, x0, z1) + line(x1, z0, x1, z1))


ROOM = perim(5, 12, 20, 26)
DOOR = (20, 18)   # east wall, level with the battery's hookup row
INSIDE = line(11, 18, 19, 18)


def layouts():
    out = {}
    for d in (1, 2, 3, 4, 6, 8, 12):
        out["through_%d" % d] = (INSIDE + [DOOR] + line(21, 18, 20 + d, 18), [DOOR], ROOM)
    for d in (2, 4, 7):
        out["bend_%d" % d] = (INSIDE + [DOOR] + line(21, 18, 20 + d, 18) + line(20 + d, 18, 20 + d, 18 + d), [DOOR], ROOM)
    # ends under the door itself
    out["ends_at_door"] = (INSIDE + [DOOR], [DOOR], ROOM)
    # in the wall both sides of the door, a branch out to an end
    for d in (1, 3, 6):
        wallrun = line(20, 14, 20, 17) + line(20, 19, 20, 23)
        out["inwall_branch_%d" % d] = (wallrun + [DOOR] + line(21, 18, 20 + d, 18) + INSIDE, [DOOR], ROOM)
        out["inwall_noinside_%d" % d] = (wallrun + [DOOR] + line(21, 18, 20 + d, 18) + line(11, 15, 19, 15), [DOOR], ROOM)
    # along the inside of the wall past the door, a branch through it
    for d in (2, 5):
        out["along_branch_%d" % d] = (line(19, 13, 19, 25) + line(11, 18, 18, 18) + [DOOR] + line(21, 18, 20 + d, 18), [DOOR], ROOM)
    # outside: a run along the wall beside the door, the door's cord joins it
    for d in (2, 5):
        out["outside_tee_%d" % d] = (INSIDE + [DOOR] + line(21, 18 - d, 21, 18 + d), [DOOR], ROOM)
    # double door, conduit through one leaf; a run through two doors in a row
    dd = [DOOR, (20, 19)]
    out["double_door"] = (INSIDE + [DOOR] + line(21, 18, 24, 18), dd, ROOM)
    r2 = ROOM | perim(20, 12, 30, 26)
    d2 = [DOOR, (30, 18)]
    out["two_doors"] = (INSIDE + [DOOR] + line(21, 18, 29, 18) + [(30, 18)] + line(31, 18, 34, 18), d2, r2)
    # a door with no room behind it: a door in a short wall, conduit passing
    return out


def gen(d):
    os.makedirs(d, exist_ok=True)
    n = 0
    for name, (c, doors, walls) in layouts().items():
        for seed in range(1, 7):
            json.dump(world(c, doors, walls, seed), open(os.path.join(d, "%s_s%d.json" % (name, seed)), "w"))
            n += 1
    print(n, "worlds in", d)


def crossings(p, r, strands, skip=None):
    """How many times cords cross the ring of radius r round p, sampling finely. Per strand."""
    out = []
    for s in strands:
        cnt = 0
        prev = None
        for i in range(1, len(s)):
            ax, az = s[i - 1]; bx, bz = s[i]
            L = math.hypot(bx - ax, bz - az)
            k = max(1, int(L / 0.05))
            for j in range(k + 1):
                t = j / k
                q = math.hypot(ax + (bx - ax) * t - p[0], az + (bz - az) * t - p[1]) <= r
                if prev is not None and q != prev:
                    cnt += 1
                prev = q
        out.append(cnt)
    return out


def read(wd, od, r=1.5):
    rows = []
    for fn in sorted(os.listdir(od)):
        if not fn.endswith(".out.json"):
            continue
        name = fn[:-9]
        Wd = json.load(open(os.path.join(wd, name + ".json")))
        L = json.load(open(os.path.join(od, fn)))
        pieces = L["pieces"]
        strands = [s for p in pieces for s in p["strands"]]
        for dx, dz in Wd["doors"]:
            c = crossings((dx + 0.5, dz + 0.5), r, strands)
            rows.append(dict(world=name, what="door", at=[dx, dz], lines=sum(c), per=[v for v in c if v]))
        ends = {}
        for p in pieces:
            for s in p["strands"]:
                for q in (s[0], s[-1]):
                    ends.setdefault((round(q[0], 1), round(q[1], 1)), []).append(1)
        for (x, z), own in ends.items():
            c = crossings((x, z), r, strands)
            lines = sum(c)
            rows.append(dict(world=name, what="end", at=[x, z], own=len(own), lines=lines, extra=lines - len(own), per=[v for v in c if v]))
    return rows


def main():
    if sys.argv[1] == "gen":
        gen(sys.argv[2])
        return
    rows = read(sys.argv[2], sys.argv[3])
    by = {}
    for q in rows:
        base = q["world"].rsplit("_s", 1)[0]
        if q["what"] == "door":
            by.setdefault(base, []).append(q["lines"])
    print("lines at the door (a plain pass through a door is 2)")
    for k, v in sorted(by.items()):
        print("  %-22s %s" % (k, v))
    ex = [q for q in rows if q["what"] == "end"]
    tot = len(ex)
    bad = [q for q in ex if q["extra"] > 0]
    print("ends %d, with more lines than cords ending there %d" % (tot, len(bad)))
    for q in sorted(bad, key=lambda q: -q["extra"])[:12]:
        print("  ", q["world"], q["at"], "own", q["own"], "lines", q["lines"], "per", q["per"])


if __name__ == "__main__":
    main()

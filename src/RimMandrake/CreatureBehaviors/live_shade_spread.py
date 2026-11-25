#!/usr/bin/env python3
"""Live test of RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL: a wild herd that dashes out of the sun spreads
over the shade patch instead of resting in a heap on one cell, and a heap already in the save breaks up.

Run on the machine that hosts the game, with that game's environment:
    eval "$(python3 src/RimMandrake/Utils/game_instance.py env Steve1)"
    python3 src/RimMandrake/CreatureBehaviors/live_shade_spread.py --save <fixture save name> --out <new save name>

It loads the fixture (a hot, sunny Pyrelands map on the pyrelands tier), spawns six wild ullai in a group at --cell,
plays --ticks ticks, prints where every wild animal stands and what it does, and saves under --out. The verdict is
the acceptance script on that save (no cell holds three or more wild animals):
    python3 infrastructure/state/acceptance/RIMMANDRAKE_SPREAD_SHADE_DASH_SEVEN_ANIMALS_ON_ONE_CELL.py <out>.rws
The line `dashed` (read from a pawn_census trace every --every ticks) says whether the herd really ran for shade; a run
where none dashed is COULD NOT LOOK for this claim (a cool or dark map), whatever the acceptance script says.
Measured 2026-11-25 on Steve1 (fixture PYRELANDS_0.1.0_VISIT9_WALK_SIGNED, --cell 68,33, 2500 ticks): red on the parent
of the least-load fix (four ullai resting on (74,18), a three-cell sliver), green on the fix.
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path[:0] = [os.path.join(ROOT, "src", "RimMandrake", "Utils"), os.path.join(ROOT, "src", "RimMandrake", "Pyrelands")]


def wild(s):
    r = s.call("jawa/list_pawns") or {}
    rows = r.get("pawns") if isinstance(r, dict) else r
    out = []
    for p in rows or []:
        fac = p.get("faction")
        if fac in (None, "", "None", "none") and (p.get("animal") or p.get("isAnimal") or p.get("race") or p.get("kind")):
            out.append(p)
    return out, rows


def cell_of(p):
    pos = p.get("position") or p.get("pos") or p.get("cell")
    if isinstance(pos, dict):
        return (pos.get("x"), pos.get("z"))
    if isinstance(pos, (list, tuple)):
        return tuple(pos[:1]) + tuple(pos[-1:])
    return (p.get("x"), p.get("z"))


def job_of(p):
    return p.get("job") or p.get("curJob") or p.get("jobDef")


def census(label, s, herd_ids):
    animals, raw = wild(s)
    cells = collections.defaultdict(list)
    for p in animals:
        cells[cell_of(p)].append(p.get("kindDef") or p.get("kind") or p.get("def"))
    heaps = {str(c): v for c, v in cells.items() if len(v) >= 3}
    herd = [p for p in raw or [] if (p.get("thingId") or p.get("id")) in herd_ids]
    print("%s: %d wild animals; heaps (3+ on a cell): %s" % (label, len(animals), heaps or "none"), flush=True)
    print("%s: herd %s" % (label, [(cell_of(p), job_of(p)) for p in herd]), flush=True)
    return heaps, herd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cell", default="68,33")
    ap.add_argument("--kind", default="RM_Ullai")
    ap.add_argument("--ticks", type=int, default=2500)
    ap.add_argument("--every", type=int, default=30)
    a = ap.parse_args()
    import northstar_site as N
    from northstar_driver.session import FastSession
    with FastSession(strict=False, focus=False) as s:
        scene(N, s, a)


def scene(N, s, a):
    print("load:", str(s.call("rimworld/load_game", saveName=a.save))[:200], flush=True)
    N._wait_state(s, "Playing", 300)
    time.sleep(10)
    mi = s.call("jawa/map_info") or {}
    print("map:", json.dumps({k: mi.get(k) for k in ("biome", "sizeX", "sizeZ", "tile", "outdoorTemp", "hour", "temperature")}), flush=True)
    sample = (s.call("jawa/list_pawns") or {})
    rows = sample.get("pawns") if isinstance(sample, dict) else sample
    print("list_pawns row keys:", sorted((rows or [{}])[0].keys()), flush=True)
    census("before", s, set())
    x, z = (int(v) for v in a.cell.split(","))
    sp = s.call("jawa/spawn_pawn", kindDef=a.kind, x=x, z=z, faction="none", count=6) or {}
    print("spawn:", json.dumps(sp)[:600], flush=True)
    ids = set()
    for p in (sp.get("pawns") or sp.get("spawned") or []) if isinstance(sp, dict) else []:
        ids.add(p.get("thingId") or p.get("id") if isinstance(p, dict) else p)
    if isinstance(sp, dict) and sp.get("thingId"):
        ids.add(sp["thingId"])
    hist = collections.defaultdict(list)    # id -> [(tick, cell, job)] on every change
    first = True
    left = a.ticks
    while left > 0:
        step = min(left, a.every)
        s.call("jawa/safe_advance", action="start", ticks=step)
        left -= step
        c = s.call("jawa/pawn_census", includeDead=False, limit=500) or {}
        rows = c.get("pawns") if isinstance(c, dict) else c
        if first:
            print("pawn_census row keys:", sorted((rows or [{}])[0].keys()), flush=True)
            first = False
        for p in rows or []:
            if p.get("faction") not in (None, "", "None", "none"):
                continue
            pid = p.get("id") or p.get("thingId")
            entry = (cell_of(p), str(job_of(p)))
            if not hist[pid] or hist[pid][-1][1:] != entry:
                hist[pid].append((a.ticks - left,) + entry)
    heaps, _ = census("t+%d" % a.ticks, s, ids)
    dashed = sum(1 for i in ids if any("RM_ShadeDash" in e[2] for e in hist.get(i, [])))
    print("dashed: %d of %d herd members ran RM_ShadeDash during the run (pawn_census trace)" % (dashed, len(ids)), flush=True)
    animals, _ = wild(s)
    at = collections.defaultdict(list)
    for p in animals:
        at[cell_of(p)].append(p.get("id") or p.get("thingId"))
    for cell, members in at.items():
        if len(members) >= 3:
            print("HEAP %s:" % (cell,), flush=True)
            for m in members:
                print("   %s %s" % (m, hist.get(m, [])[-8:]), flush=True)
    print("save:", str(s.call("rimworld/save_game", saveName=a.out))[:200], flush=True)
    print("VERDICT-HINT: heaps=%d dashed=%d" % (len(heaps), dashed), flush=True)


if __name__ == "__main__":
    main()

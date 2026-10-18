"""lake_floor_stage.py -- stage P11 lake floors (LAKE_FLOORS_BUILD_MOUNTAINS_RUN_DEEP) for the owner to LOOK at: found a map
on a world tile with natural lakes, photograph each lake full, draw it down (ProofSetBodyFraction), photograph it again,
and write captioned panels + index.html under Transient/fw_scenes/lake_floors/live/.

    python.exe src/RimMandrake/FlowWorks/northstar/lake_floor_stage.py --tile 24575 --name mountain [--frac 0.35] [--max 6]

Needs a Playing game (any map: the world is read from it) and the bridge held. The new map stays loaded and current.
Measured per lake: squares, deepest floor (max hole of ProofReadout over the lake's squares), litres full and drawn
down, the floor's terrain census after the draw-down (ProofPondDepth). Nothing here is a verdict: the owner judges.
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
for _p in (os.path.join(REPO, "src", "RimMandrake", "Utils"), os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUT = os.path.join(REPO, "Transient", "fw_scenes", "lake_floors", "live")
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PROMO = "RimMandrake.FlowWorks.RM_PromotionProofs"
STILL = ("WaterDeep", "WaterShallow", "WaterChestDeep", "RM_WaterChestDeepStill", "Marsh")


def bodies(terr, size, min_cells=6):
    """Connected clusters of still natural water not touching the map edge, largest first."""
    W, H = size
    water = {k for k, t in terr.items() if t in STILL or (t.startswith("RM_Water") and "Moving" not in t)}
    seen, out = set(), []
    for c in water:
        if c in seen:
            continue
        q, comp, edge = collections.deque([c]), [], False
        seen.add(c)
        while q:
            x, z = q.popleft()
            comp.append((x, z))
            if x in (0, W - 1) or z in (0, H - 1):
                edge = True
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in water and n not in seen:
                    seen.add(n)
                    q.append(n)
        if len(comp) >= min_cells and not edge:
            out.append(comp)
    return sorted(out, key=len, reverse=True)


def parse_ro(t):
    """ProofReadout -> (hole metres, litres) or None."""
    try:
        hole = float(t.split("Hole ", 1)[1].split(" m", 1)[0])
        litres = int(t.rsplit("(", 1)[1].split(" L", 1)[0].replace(",", ""))
        return hole, litres
    except (IndexError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tile", type=int, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--frac", type=float, default=0.35)
    ap.add_argument("--max", type=int, default=6)
    a = ap.parse_args()
    import fw_walk_common as C  # noqa: E402
    import bland_world as BW  # noqa: E402
    wa = argparse.Namespace(mock=False, pace=0.0, no_shots=False, mock_fail=None)
    w = C.make_walk(wa, OUT)
    s = w.B
    res = {"tile": a.tile, "name": a.name, "frac": a.frac, "lakes": []}
    cf = w.call("jawa/colony_found", tile=a.tile, faction="Player", name="LakeFloors_%s" % a.name)
    BW.close_naming_dialogs(s)
    g = w.call("jawa/world_tile_map_generate", tile=a.tile, suggestedMapParent="Settlement") or {}
    BW.close_naming_dialogs(s)
    mid = g.get("mapId")
    cm = w.call("jawa/set_current_map", mapId=mid) or {}
    mi = w.call("jawa/map_info") or {}
    res.update(found=str(cf)[:160], mapId=mid, setCurrent=cm.get("success"), mapTile=mi.get("tile"), biome=mi.get("mapBiome"))
    w.say("map %s tile %s biome %s (set current %s)" % (mid, mi.get("tile"), mi.get("mapBiome"), cm.get("success")))
    if mi.get("tile") != a.tile:
        w.say("NOT ON THE TILE: %s" % mi)
        return 2
    w.call("jawa/quiet_site", action="apply", clearThreats=True, proximityLetters=True)
    w.call("jawa/kill_hostiles")
    w.call("jawa/debug_settings", action="set", field="enableStoryteller", value=False)
    w.call("rimworld/set_god_mode", enabled=True)
    w.call("jawa/set_fog", action="unfogAll")
    # daylight from the CLOCK (rimworld-live-review 8b): jump TicksGame to the next local noon (nothing simulated)
    da = w.call("jawa/time_date_at") or {}
    ck = w.call("jawa/time_clock") or {}
    lon, tabs = float(da.get("longitude") or 0.0), int(ck.get("ticksAbs") or 0)
    local = (tabs + int(lon / 360.0 * 60000)) % 60000
    delta = (30000 - local) % 60000
    if delta:
        w.call("jawa/time_set_ticks", ticks=int(ck.get("ticksGame") or 0) + delta, timeException=True,
               why="lake floor review shots at local noon (P11 staging)")
    res["clock"] = {"longitude": lon, "localHourBefore": round(local / 2500.0, 2), "jumped": delta}
    tw = w.call("jawa/world_tile_get", tiles=str(a.tile)) or {}
    trow = (tw.get("tiles") or [{}])[0]
    res["hilliness"] = trow.get("hilliness")
    size = C.map_size(w)
    terr = C.read_terrain(w, size)
    bs = bodies(terr or {}, size)[:a.max]
    w.say("hilliness %s; %d still-water bodies off the edge (taking %d)" % (trow.get("hilliness"), len(bodies(terr or {}, size)), len(bs)))
    groups = []
    for n, cells in enumerate(bs, 1):
        c0 = max(cells, key=lambda c: sum((c[0] + dx, c[1] + dz) in set(cells) for dx in (-1, 0, 1) for dz in (-1, 0, 1)))
        span = max(max(c[0] for c in cells) - min(c[0] for c in cells), max(c[1] for c in cells) - min(c[1] for c in cells))
        side = max(24, span + 12)
        rect = C.centroid_rect(cells, side, int(side * 0.6) + 6, size)
        br = w.call("jawa/flowworks_body_report", x=c0[0], z=c0[1], classify=True) or {}
        full = [parse_ro(w.proof(NSP, "ProofReadout", "%d,%d" % c)[1]) for c in cells]
        full = [f for f in full if f]
        deepest = max((f[0] for f in full), default=None)
        holes = collections.Counter(f[0] for f in full)
        l_full = sum(f[1] for f in full)
        img_full = C.snap(w, "%s_lake%d_full" % (a.name, n), rect)
        ok, setr = w.proof(NSP, "ProofSetBodyFraction", "%d;%d;%.3f" % (c0[0], c0[1], a.frac))
        w.ticks(300)
        low = [parse_ro(w.proof(NSP, "ProofReadout", "%d,%d" % c)[1]) for c in cells]
        low = [f for f in low if f]
        l_low = sum(f[1] for f in low)
        ok2, census = w.proof(PROMO, "ProofPondDepth", "%d,%d" % c0)
        img_low = C.snap(w, "%s_lake%d_drawn" % (a.name, n), rect)
        cap = ["%d squares; deepest floor %s m; floor depths (m: squares) %s" % (len(cells), deepest,
               ", ".join("%g: %d" % kv for kv in sorted(holes.items()))),
               "full %s L -> drawn down to %d%%: %s L (%s)" % ("{:,}".format(l_full), round(a.frac * 100), "{:,}".format(l_low), setr[:60]),
               "after the draw-down: %s" % census[:200]]
        lake = dict(n=n, centre=c0, squares=len(cells), deepest=deepest, holes=dict(holes), litresFull=l_full, litresLow=l_low,
                    body=str(br)[:300], set=setr, census=census, rect=rect)
        res["lakes"].append(lake)
        imgs = []
        for img, label in ((img_full, "full"), (img_low, "drawn down")):
            if img:
                dst = os.path.join(OUT, "annotated", os.path.basename(img).replace(".png", "_panel.png"))
                C.label_image(img, dst, "%s map, lake %d: %s" % (a.name, n, label),
                              "tile %s, %s, %s" % (a.tile, mi.get("mapBiome"), trow.get("hilliness")), cap)
                imgs.append((os.path.relpath(dst, OUT).replace(os.sep, "/"), label))
        groups.append(dict(id="%s_lake%d" % (a.name, n), title="%s map (%s), lake %d" % (a.name, trow.get("hilliness"), n),
                           looking_at="A natural lake on a freshly made map, first full, then drawn down to %d%% of its water so "
                                      "the floor P11 recorded at map creation shows." % round(a.frac * 100),
                           check=["Does the floor look like a lake bed for this terrain (flat land: shallow; mountains: deeper, rougher)?",
                                  "Is there a shore shelf and a way out on every side?"],
                           passif="the drawn-down lake reads as a believable bed", fails="it reads as a flat-bottomed box or a pit",
                           images=imgs, readings=[("MEASURED", c) for c in cap], notes=[], pre=json.dumps(lake, default=str)[:1500]))
        w.say("lake %d: %s" % (n, " | ".join(cap)))
    with open(os.path.join(OUT, "%s_result.json" % a.name), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    C.write_index(os.path.join(OUT, "index.html"), "P11 lake floors, live (FlowWorks 71aaadd97)",
                  "Flat and mountainous maps, each lake photographed full and drawn down. Captions are measured: floor depth from "
                  "the game's own readout per square, litres, and the floor terrain census.", groups, accumulate=True)
    w.call("jawa/debug_settings", action="set", field="enableStoryteller", value=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

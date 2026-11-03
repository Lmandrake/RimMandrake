#!/usr/bin/env python3
"""live_kit_art.py - live clause A2 of GELATINOUSSLIME_KIT_ART_1: a Slime map draws no tortoise and no dandelion.

    python3 src/RimMandrake/GelatinousSlime/live_kit_art.py             # WSL: stages a Slime map, re-runs under python.exe
    python3 src/RimMandrake/GelatinousSlime/live_kit_art.py --current   # read the CURRENT map only (must be Slime)
    python.exe ...\\live_kit_art.py --inner --out <json> [--current]    # the bridge half (Windows side)

Staging (default): a FRESH scratch vanilla quicktest world, a 2-ring land patch re-tiled to RM_GelatinousSlime with the
Slime's measured tile values (design/Jawa/worldbuilding/biomes/the_slime.md §0: temp median 13.4 C, elevation median 3 m,
flat, dry), centre mutators stripped, colony_found + world_tile_map_generate, then the map made current. Recipe:
Utils/modcheck/biome_site.py, as LeaningScrub/northstar/wildlife_mapgen_live.py uses it. Never Ash'karr, never a world a
player receives (CLAUDE.md worldgen ban); nothing is saved. Before 2026-11-03 this read whatever map was current, and the
live tier left a Rot map up: two runs measured nothing.

On that map (read only: jawa/map_info, jawa/thing_graphic, jawa/thing_explain):
  * every thing (one thing_graphic rect read, complete list required) has no graphicPath, resolvedPath or variant path
    naming Tortoise or Dandelion, and no RM_ thing draws BadTex;
  * at least one kit plant (slime grass, bellows, thumbstalk or readerbloom) is present, so the read is not blind;
  * every RM_Gelatid on the map has no appearance texPath naming Tortoise (thing_explain lists the body AND desiccated
    graphic paths the def configures).
Exit 0 holds, 1 a stand-in is drawn, 2 UNMEASURED (no bridge, wrong load, wrong map, truncated read, nothing of ours).
Callers hold the bridge lock; this never takes it.
"""
import json
import os
import subprocess
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.normpath(os.path.join(HERE, "..", "Utils"))
MODCHECK = os.path.join(UTILS, "modcheck")
SCRATCH = "/mnt/d/ClaudeWork/rimmandrake/scratch/slime_kit_art"
TIMEOUT = 530
FORBIDDEN = ("tortoise", "dandelion")
KIT_PLANTS = {"RM_Plant_SlimeGrass", "RM_Plant_Bellows", "RM_Plant_Thumbstalk", "RM_Plant_Readerbloom"}
BIOME = "RM_GelatinousSlime"
SPEC = types.SimpleNamespace(       # the fields biome_site.choose_tile / retile read
    BIOME=BIOME, LAT_MAX=45.0, MAP_SIZE=120,
    TILE={"temperature": 13.4, "rainfall": 0.0, "elevation": 3.0, "hilliness": "Flat", "swampiness": 0.0})


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)


def judge(things, explain):
    """(fails, kit, gelatid ids, unread gelatids) from a complete thing_graphic list; explain(id) -> thing_explain reply."""
    fails = []
    for t in things:
        hits = [s for s in strings({k: t.get(k) for k in ("graphicPath", "resolvedPath", "variantPath",
                                                           "variantPaths", "textureName")})
                if any(w in s.lower() for w in FORBIDDEN)]
        if hits:
            fails.append(f"{t.get('defName')} {t.get('id')} draws {hits[0]}")
        if str(t.get("defName", "")).startswith("RM_") and t.get("badTex"):
            fails.append(f"{t.get('defName')} {t.get('id')} draws BadTex")
    kit = sorted({t.get("defName") for t in things} & KIT_PLANTS)
    gels = [t.get("id") for t in things if t.get("defName") == "RM_Gelatid"]
    blind = []
    for gid in gels:
        ex = explain(gid) or {}
        paths = list(strings(ex.get("appearance")))
        if ex.get("success") is False or not paths:   # an unread appearance never counts as clean
            blind.append(f"RM_Gelatid {gid} appearance unread: {str(ex)[:150]}")
            continue
        for s in paths:
            if any(w in s.lower() for w in FORBIDDEN):
                fails.append(f"RM_Gelatid {gid} appearance names {s}")
                break
    return fails, kit, gels, blind


def verdict(things, fails, kit, gels, blind=()):
    lines = [f"map things read {len(things)}; kit plants present {kit}; gelatids {len(gels)}"]
    lines += ["FAIL " + f for f in fails]
    if fails:
        return 1, lines
    if blind:
        return 2, lines + ["UNMEASURED: " + b for b in blind]
    if not kit:
        return 2, lines + ["UNMEASURED: no kit plant on the map; the read cannot speak for the kit"]
    return 0, lines + ["HOLDS"]


def stage(s, rec, work):
    import biome_site as B
    NS = B.pyre()
    mods, retired = B.running_retired(s.call)
    lack = B.missing_dlc(mods)
    if retired or lack:
        raise B.SiteError("UNMEASURED: wrong load (retired %s, DLC missing %s)" % (retired, lack))
    rec["world"] = NS.fresh_quicktest_world(s)
    rec["colonyTile"] = s.call("jawa/map_info").get("tile")
    rec["pick"] = B.choose_tile(s, SPEC, work, rec["colonyTile"])
    centre = rec["pick"]["centre"]
    rec["retiled"] = B.retile(s, SPEC, rec["pick"]["patch"])
    NS.strip_mutators(s, centre)
    g = NS.generate(s, centre, SPEC.MAP_SIZE)
    rec["mapId"] = g["mapId"]
    s.call("jawa/set_current_map", mapId=g["mapId"])


def inner(out_path, current):
    for p in (MODCHECK, UTILS):
        if p not in sys.path:
            sys.path.insert(0, p)
    from northstar_driver.session import FastSession
    rec = {"item": "GELATINOUSSLIME_KIT_ART_1", "clause": "A2", "staged": not current,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rc, lines = 2, ["UNMEASURED: did not reach the read"]
    try:
        with FastSession(strict=False, focus=False) as s:   # never focus the game (live-tier rule)
            if not current:
                stage(s, rec, os.path.join(os.path.dirname(out_path), "slime_kit_art_site"))
            mi = s.call("jawa/map_info")
            rec["map"] = {k: mi.get(k) for k in ("mapId", "mapBiome", "tile", "sizeX", "sizeZ")}
            if mi.get("mapBiome") != BIOME or (rec.get("mapId") is not None and mi.get("mapId") != rec["mapId"]):
                raise RuntimeError("UNMEASURED: current map %s biome %s is not the %s map %s" % (
                    mi.get("mapId"), mi.get("mapBiome"), BIOME, rec.get("mapId")))
            g = s.call("jawa/thing_graphic", rect="0,0,1000,1000", limit=100000)
            if not g.get("success") or not g.get("isCompleteList"):
                raise RuntimeError("UNMEASURED: thing_graphic success=%s complete=%s" % (
                    g.get("success"), g.get("isCompleteList")))
            things = g.get("things") or []
            fails, kit, gels, blind = judge(things, lambda gid: s.call("jawa/thing_explain", id=gid))
            rc, lines = verdict(things, fails, kit, gels, blind)
            rec.update({"things": len(things), "kit": kit, "gelatids": len(gels), "fails": fails, "blind": blind})
    except Exception as ex:   # every failure is UNMEASURED with its reason on disk, never a silent pass
        msg = str(ex)[:400]
        if rc != 1:
            rc, lines = 2, [msg if msg.startswith("UNMEASURED") else "UNMEASURED: %s: %s" % (type(ex).__name__, msg)]
    rec["rc"], rec["lines"] = rc, lines
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True, default=str)
    print("\n".join(lines))
    return rc


def win(path):
    out = subprocess.run(["wslpath", "-w", path], capture_output=True, text=True, timeout=20).stdout.strip()
    if not out:
        raise SystemExit("wslpath gave nothing for %s" % path)
    return out


def outer(current):
    os.makedirs(SCRATCH, exist_ok=True)
    out = os.path.join(SCRATCH, "a2_%d_%d.json" % (os.getpid(), time.time_ns()))
    argv = ["python.exe", win(os.path.abspath(__file__)), "--inner", "--out", win(out)] + (["--current"] if current else [])
    print("$ " + " ".join(argv), flush=True)
    try:
        rc = subprocess.run(argv, stdin=subprocess.DEVNULL, timeout=TIMEOUT).returncode
    except (OSError, subprocess.TimeoutExpired) as ex:
        print("UNMEASURED: bridge half did not finish: %s" % ex)
        return 2
    if not os.path.exists(out):
        print("UNMEASURED: the bridge half wrote no %s (exit %d)" % (out, rc))
        return 2
    with open(out, encoding="utf-8") as fh:
        rec = json.load(fh)
    print("evidence: %s" % out)
    return rec.get("rc", 2) if rc in (0, 1, 2) and rc == rec.get("rc") else 2


def main(argv):
    current = "--current" in argv
    if "--inner" in argv:
        out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(os.getcwd(), "slime_kit_art_a2.json")
        return inner(out, current)
    return outer(current)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""BIOME_ENRICHMENT_DESERT_WASTELAND_1 - the tile-mutator plan that thickens the Long Shade (ex-Desert)
and the Wasteland, applied ONCE at the terminal world painting (BIOME_PAINT_ONCE_AT_THE_END_1).

Owner ruling 2026-09-20 (option b): raise how often the game's OWN existing mutators that pass
`TileMutatorDef.IsValidTile` for these biomes appear; that counts as building the sheets' kit
("the wide gaps"). No new TileMutatorDef, no defName standing in for a sheet's narrative category,
none of structure_injection_roster.md's PROMISE mutators (arc-gated; "Placement stays the owner's
hand"). The dune sea (RM_Stillsand) stays barren by rule and is never touched.

What it reads (offline, no game):
  * the canonical start save (canon.yml planet.start_savegame, committed under world/): per-tile
    biome, hilliness, elevation, mutators, settlements, landmarks;
  * the TileMutatorDef capture of the def dump: each candidate's biome/hilliness/coast/temperature/
    pollution gates, so legality is read, never assumed;
  * world/ASHKARR_WORLDMAP_tiles.csv for lat/lon (geometry only) and the 2026-10-20 parity links
    plan for road tiles (a priority signal, not a gate).

The biomes are selected by TILE SET, not by a defName, because the save's biome hashes drift with
the mod list (RUT_Wasteland's tiles read as an unresolved hash on the 2026-11-02 capture). The
tile set is the save's tiles whose biome is the one the frozen CSV calls RUT_Desert / RUT_Wasteland;
the plan records both the save's biome name and the successor defName (RM_LongShade, RM_Wastes).

Selection rule (deterministic, one world, no variants): only tiles that carry NO mutator today;
never a settlement, landmark or water tile; candidates per tile chosen by hilliness from the kit
map below, filtered by every gate the def declares; tiles ranked by great-circle distance to the
nearest road tile (the item: "read thin where caravans travel most"), ties by tile id. The quota
stops at TARGET_ZERO_SHARE: the bare tiles that remain are the ones farthest from any road, which
is where desert.md's "wide gaps" are supposed to be.

    python3 src/RimMandrake/Utils/desert_wasteland_enrichment_plan.py            # write the plan
    python3 src/RimMandrake/Utils/desert_wasteland_enrichment_plan.py --check    # rebuild, diff, exit 1 on drift
"""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

SAVE = os.path.join(REPO, "world", "ASHKARR_DEV_START_2026-10-20_PARITY_QUIET_R3.rws")
TILES_CSV = os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv")
LINKS_CSV = os.path.join(REPO, "world", "ASHKARR_PARITY_U4_links_mouthfirst_2026-10-20.csv")
PLAN = os.path.join(REPO, "world", "ASHKARR_DESERT_WASTELAND_ENRICHMENT_plan.json")

ITEM = "BIOME_ENRICHMENT_DESERT_WASTELAND_1"
TARGET_ZERO_SHARE = 0.30   # LeaningScrub 0.28, the NightsideIce band 0.31 on the same save: ordinary, not dense
START_TILE = 17007          # the player start (CANONICAL_SAVE.md); never mutated by this plan

# Hilliness byte in the save: 1 Flat, 2 SmallHills, 3 LargeHills, 4 Mountainous.
HILL_NAMES = {0: "Undefined", 1: "Flat", 2: "SmallHills", 3: "LargeHills", 4: "Mountainous", 5: "Impassable"}
HILL_ORDER = {n: i for i, n in HILL_NAMES.items()}

# The kit, sheet line -> existing mutator. Each list is the per-tile rotation for that hilliness class.
KIT = {
    "RUT_Desert": {
        "successor": "RM_LongShade",
        "sheet": "design/Jawa/worldbuilding/biomes/desert.md",
        "why": {
            "Caves": "8. 'Rock shelters and crevice dwellings in the hills'; 7. 'Crevice shelter'",
            "Junkyard": "8. 'Shade patches are ... middens ... bones, debris and wreckage'",
            "AncientRuins": "8. 'archaeology accumulates in them. For a Jawa, the shade is the dig site'",
            "MineralRich": "7. 'Desert pavement stone, wind-stripped and flat' (the owner's ruling names MineralRich)",
        },
        "by_hill": {1: ["Junkyard", "AncientRuins", "Junkyard", "MineralRich"],
                    2: ["Caves", "AncientRuins", "Junkyard", "MineralRich"],
                    3: ["Caves", "Caves", "MineralRich"],
                    4: ["Caves", "MineralRich"]},
    },
    "RUT_Wasteland": {
        "successor": "RM_Wastes",
        "sheet": "design/Jawa/worldbuilding/biomes/wastes.md",
        "why": {
            "Junkyard": "8. the Junkers' dump; 7. 'ruined vehicles of past attempts, crashed ships'",
            "Stockpile": "8. palette 'War ground: buried arsenals'; 7. 'War salvage priced in dose'",
            "AncientRuins": "8. palette 'Terminator pockets: the oldest battle ruins'; 'The buried crimes'",
            "MineralRich": "7. 'Salt, glass, brine minerals'; 'Plant-vault ore - the cursed prize'",
            "Caves": "8. 'Rib-vaults and the other dead sarlacc throats (bunker, vault, dungeon)'",
        },
        "by_hill": {1: ["Junkyard", "Stockpile", "AncientRuins", "MineralRich"],
                    2: ["Stockpile", "MineralRich", "Junkyard", "Caves"],
                    3: ["Caves", "MineralRich", "AncientRuins"],
                    4: ["Caves", "MineralRich"]},
    },
}
NEVER = ("RUT_ExtremeDesert",)
GATE_FIELDS = ("biomeWhitelist", "biomeBlacklist", "minHilliness", "maxHilliness", "coastSidesRange",
               "averageTemperatureRange", "pollutionRange", "categories")   # the dune sea: barren by rule


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def mutator_defs():
    import worldmap
    path = os.path.join(worldmap.DEFAULT_DUMP, "TileMutatorDef.json")
    with open(path, encoding="utf-8-sig") as f:
        d = json.load(f)
    rows = d.get("defs", d) if isinstance(d, dict) else d
    rows = rows if isinstance(rows, list) else list(rows.values())
    return {r["defName"]: r for r in rows}


def gate_refusal(defrow, target_biome, hill, temp_c, pollution, other_names=()):
    """Why IsValidTile's declared gates refuse this tile, or None. target_biome is the def the tile will wear
    when the plan is applied (the successor): a whitelist must name IT - a legacy name on the list proves
    nothing. other_names (the save's and the CSV's names for the same tiles) only make a blacklist stricter."""
    f = defrow["fields"]
    wl, bl = f.get("biomeWhitelist") or [], f.get("biomeBlacklist") or []
    if wl and target_biome not in wl:
        return "biomeWhitelist %s" % wl
    if any(b in bl for b in (target_biome,) + tuple(other_names)):
        return "biomeBlacklist"
    lo, hi = f.get("minHilliness", "Undefined"), f.get("maxHilliness", "Undefined")
    if lo != "Undefined" and hill < HILL_ORDER[lo]:
        return "minHilliness " + lo
    if hi != "Undefined" and hill > HILL_ORDER[hi]:
        return "maxHilliness " + hi
    cs = f.get("coastSidesRange") or {}
    if cs.get("min", -1) != -1 or cs.get("max", -1) != -1:
        return "coastSidesRange set (not measurable offline; never planned)"
    t = f.get("averageTemperatureRange") or {}
    if not (t.get("min", -1e38) <= temp_c <= t.get("max", 1e38)):
        return "averageTemperatureRange"
    p = f.get("pollutionRange") or {}
    if not (p.get("min", 0) <= pollution <= p.get("max", 1e38)):
        return "pollutionRange"
    return None


def latlon():
    out = {}
    with open(TILES_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            out[int(r["tile"])] = (math.radians(float(r["lat"])), math.radians(float(r["lon"])), r["biome"])
    return out


def road_tiles():
    s = set()
    with open(LINKS_CSV, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["kind"] == "road":
                s.add(int(r["a"]))
                s.add(int(r["b"]))
    return s


def arc(a, b):
    (la1, lo1), (la2, lo2) = a, b
    c = math.sin(la1) * math.sin(la2) + math.cos(la1) * math.cos(la2) * math.cos(lo1 - lo2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def build():
    import worldmap
    g = worldmap.WorldGrid(SAVE)
    names = g.biome_names()
    defs = mutator_defs()
    by_hash = {r["shortHash"]: n for n, r in defs.items()}
    per = collections.defaultdict(list)
    for t, h in g.mutator_entries():
        per[t].append(by_hash.get(h, "?%d" % h))
    objs = worldmap.WorldObjects(SAVE)
    blocked = {s["tile"] for s in objs.settlements()} | {l["tile"] for l in objs.landmarks()} | {START_TILE}
    geo = latlon()
    roads = road_tiles()
    road_pts = [geo[t][:2] for t in sorted(roads) if t in geo]

    # biome identity by tile set: the save name worn by the CSV's tiles of that biome, measured 1:1
    csv_to_save = collections.defaultdict(collections.Counter)
    for t, (_, _, b) in geo.items():
        csv_to_save[b][names[t]] += 1

    plan = {"item": ITEM, "what": __doc__.strip().splitlines()[0],
            "ruling": "owner 2026-09-20, option (b): raise density of existing mutators that pass IsValidTile",
            "apply": ("At the terminal world painting (BIOME_PAINT_ONCE_AT_THE_END_1), on the canonical start save, "
                      "for each biome and def: jawa/world_mutators_set {action:add, mutators:<def>, tiles:<csv>} in "
                      "batches, then jawa/world_commit, then read back with jawa/world_mutators_get (limit<=100 rows "
                      "per call) - never the write's return value. Before applying, rebuild with --check on the save "
                      "being painted: a tile that is no longer this biome, or no longer bare, drops out."),
            "inputs": {"save": os.path.relpath(SAVE, REPO), "save_sha256": sha256(SAVE),
                       "tiles_csv": os.path.relpath(TILES_CSV, REPO), "links_csv": os.path.relpath(LINKS_CSV, REPO),
                       "mutator_capture": os.path.basename(os.path.dirname(os.path.dirname(
                           os.path.join(worldmap.DEFAULT_DUMP, "x"))))},
            "target_zero_share": TARGET_ZERO_SHARE, "never": list(NEVER), "biomes": {},
            "gates": {d: dict({k: defs[d]["fields"].get(k) for k in GATE_FIELDS}, modName=defs[d]["modName"])
                      for d in sorted({d for k in KIT.values() for r in k["by_hill"].values() for d in r})}}

    for csv_name in sorted(KIT):
        kit = KIT[csv_name]
        (save_name, n_match), = csv_to_save[csv_name].most_common(1)
        tiles = [t for t in range(g.tiles) if names[t] == save_name]
        if n_match != len(tiles) or n_match != sum(csv_to_save[csv_name].values()):
            raise SystemExit("%s: CSV tiles and save tiles are not one set (%d vs %d) - re-export the record first"
                             % (csv_name, n_match, len(tiles)))
        bare = [t for t in tiles if not per.get(t)]
        aliases = (save_name, csv_name)
        cand, refused = [], collections.Counter()
        for t in bare:
            if t in blocked or g.arrays["tileElevation"][t] - 8192 <= 0:
                continue
            hill = g.arrays["tileHilliness"][t]
            rot = kit["by_hill"].get(hill)
            if not rot:
                refused["hilliness %s not in kit" % HILL_NAMES.get(hill, hill)] += 1
                continue
            temp_c = g.get("tileTemperature", t)
            pol = g.arrays["tilePollution"][t] / 65535.0
            legal = []
            for d in rot:
                why = gate_refusal(defs[d], kit["successor"], hill, temp_c, pol, aliases)
                if why:
                    refused["%s: %s" % (d, why)] += 1
                else:
                    legal.append(d)
            if legal:
                dist = min(arc(geo[t][:2], p) for p in road_pts) if road_pts else 0.0
                cand.append((round(dist, 4), t, hill, legal))
        cand.sort()
        need = len(bare) - int(math.floor(TARGET_ZERO_SHARE * len(tiles)))
        take = cand[:max(0, need)]
        adds = collections.defaultdict(list)
        turn = collections.Counter()
        for dist, t, hill, legal in take:
            d = legal[turn[hill] % len(legal)]
            turn[hill] += 1
            adds[d].append(t)
        after_zero = len(bare) - len(take)
        plan["biomes"][kit["successor"]] = {
            "csv_biome": csv_name, "save_biome": save_name, "sheet": kit["sheet"], "tiles": len(tiles),
            "zero_before": len(bare), "zero_share_before": round(len(bare) / len(tiles), 4),
            "zero_after": after_zero, "zero_share_after": round(after_zero / len(tiles), 4),
            "save_biome_hash": g.arrays["tileBiome"][tiles[0]], "eligible": len(cand), "shortfall": max(0, need - len(cand)),
            "max_road_distance_deg": take[-1][0] if take else None,
            "refusals": dict(sorted(refused.items())),
            "why": kit["why"],
            "adds": {d: sorted(ts) for d, ts in sorted(adds.items())},
        }
    for nb in NEVER:
        save_name = csv_to_save[nb].most_common(1)[0][0] if csv_to_save.get(nb) else None
        plan["never_touched"] = {nb: save_name}
    return plan


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="rebuild and compare with the committed plan; exit 1 on drift")
    a = ap.parse_args(argv)
    plan = build()
    text = json.dumps(plan, indent=1, sort_keys=True) + "\n"
    if a.check:
        with open(PLAN, encoding="utf-8") as f:
            same = f.read() == text
        print("PLAN CURRENT" if same else "PLAN DRIFT: rebuild with no --check and review the diff")
        return 0 if same else 1
    with open(PLAN, "w", encoding="utf-8") as f:
        f.write(text)
    for b, r in plan["biomes"].items():
        print("%s: %d tiles, zero %.1f%% -> %.1f%%, adds %s" % (
            b, r["tiles"], 100 * r["zero_share_before"], 100 * r["zero_share_after"],
            {d: len(t) for d, t in r["adds"].items()}))
    print("wrote", os.path.relpath(PLAN, REPO))
    return 0


if __name__ == "__main__":
    sys.exit(main())

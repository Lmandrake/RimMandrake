#!/usr/bin/env python3
"""Selftest for BIOME_ENRICHMENT_DESERT_WASTELAND_1's committed plan
(world/ASHKARR_DESERT_WASTELAND_ENRICHMENT_plan.json), checked against the canonical save it names.

Proves, offline: the plan is built from that exact save (sha256); every planned tile is a land tile of
the named biome (raw biome hash), bare today, not a settlement/landmark/start tile, planned once; every
def is an existing in-use, non-PROMISE mutator whose declared gates pass that tile (gates frozen in the
plan and, when the def capture is readable, equal to it); the dune sea gets nothing; each biome's
zero-mutator share after the plan is at or under the generator's target, and each successor's tiles are
exactly the CSV record's tiles of its legacy biome. Then it feeds the same checker four
broken plans and requires each to be caught, so a green run means the checker can see.
"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import desert_wasteland_enrichment_plan as P   # noqa: E402
import worldmap                                 # noqa: E402


def load_world():
    g = worldmap.WorldGrid(P.SAVE)
    muts = {}
    for t, h in g.mutator_entries():
        muts.setdefault(t, set()).add(h)
    objs = worldmap.WorldObjects(P.SAVE)
    blocked = {s["tile"] for s in objs.settlements()} | {l["tile"] for l in objs.landmarks()} | {P.START_TILE}
    return g, muts, blocked


def problems(plan, g, muts, blocked, dune_tiles, csv_sets, live_defs=None):
    """csv_sets: CSV biome name -> its tile set, read from the frozen CSV record, independent of the plan."""
    out = []
    raw_b = g.arrays["tileBiome"]
    if plan.get("target_zero_share") != P.TARGET_ZERO_SHARE:
        out.append("plan target %r is not the generator's %r" % (plan.get("target_zero_share"), P.TARGET_ZERO_SHARE))
    want = {k["successor"]: c for c, k in P.KIT.items()}
    in_use = {h for hs in muts.values() for h in hs}
    seen = set()
    for name, b in plan["biomes"].items():
        h = b["save_biome_hash"]
        tiles = [t for t in range(g.tiles) if raw_b[t] == h]
        if b["csv_biome"] != want.get(name):
            out.append("%s: csv_biome %r, expected %r" % (name, b["csv_biome"], want.get(name)))
        if set(tiles) != csv_sets.get(want.get(name), set()):
            out.append("%s: the save's hash-%d tiles are not the CSV's %s tiles" % (name, h, want.get(name)))
        bare = [t for t in tiles if t not in muts]
        if len(tiles) != b["tiles"] or len(bare) != b["zero_before"]:
            out.append("%s: save has %d tiles / %d bare, plan says %d / %d" % (name, len(tiles), len(bare),
                                                                             b["tiles"], b["zero_before"]))
        n_add = 0
        for d, ts in b["adds"].items():
            gate = plan["gates"].get(d)
            if gate is None:
                out.append("%s: no frozen gate" % d)
                continue
            if d.startswith(("RUT_", "RSW_", "RM_")):
                out.append("%s: our own/PROMISE def - the ruling allows only the game's existing mutators" % d)
            if live_defs is not None:
                live = live_defs.get(d)
                if live is None:
                    out.append("%s: not in the def capture" % d)
                else:
                    if {k: live["fields"].get(k) for k in P.GATE_FIELDS} != {k: gate.get(k) for k in P.GATE_FIELDS}:
                        out.append("%s: frozen gates differ from the capture" % d)
                    if live["shortHash"] not in in_use:
                        out.append("%s: not in use anywhere on the save (not an existing mutator)" % d)
            aliases = (b["save_biome"], b["csv_biome"])
            for t in ts:
                n_add += 1
                if t in seen:
                    out.append("tile %d planned twice" % t)
                seen.add(t)
                if raw_b[t] != h:
                    out.append("tile %d is not %s in the save" % (t, name))
                if t in muts:
                    out.append("tile %d already carries a mutator" % t)
                if t in blocked:
                    out.append("tile %d is a settlement/landmark/start tile" % t)
                if t in dune_tiles:
                    out.append("tile %d is dune sea (barren by rule)" % t)
                if g.arrays["tileElevation"][t] - 8192 <= 0:
                    out.append("tile %d is water" % t)
                why = P.gate_refusal({"fields": gate}, name, g.arrays["tileHilliness"][t],
                                     g.get("tileTemperature", t), g.arrays["tilePollution"][t] / 65535.0, aliases)
                if why:
                    out.append("tile %d: %s refused (%s)" % (t, d, why))
        after = len(bare) - n_add
        if after != b["zero_after"] or after / max(1, len(tiles)) > P.TARGET_ZERO_SHARE + 1e-9:
            out.append("%s: %d bare after (%.3f) vs plan %d, target %.2f" % (
                name, after, after / max(1, len(tiles)), b["zero_after"], plan["target_zero_share"]))
    return out


def main():
    with open(P.PLAN, encoding="utf-8") as f:
        plan = json.load(f)
    h = hashlib.sha256()
    with open(P.SAVE, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    fails = []
    if h.hexdigest() != plan["inputs"]["save_sha256"]:
        fails.append("save sha256 differs from the plan's input")
    g, muts, blocked = load_world()
    geo = P.latlon()
    dune = {t for t, (_, _, b) in geo.items() if b in P.NEVER}
    csv_sets = {}
    for t, (_, _, b) in geo.items():
        csv_sets.setdefault(b, set()).add(t)
    if not dune:
        fails.append("no dune-sea tiles found: the barren check would be blind")
    try:
        live = P.mutator_defs()
    except OSError as e:   # existence and in-use are unverifiable without it: not a pass
        fails.append("def capture unreadable (%s): cannot prove each def exists and is in use" % e)
        live = None
    if set(plan["biomes"]) != {"RM_LongShade", "RM_Wastes"}:
        fails.append("plan biomes %s" % sorted(plan["biomes"]))
    fails += problems(plan, g, muts, blocked, dune, csv_sets, live)

    # the checker must see: four broken plans, each caught by its own check
    some = next(iter(plan["biomes"].values()))
    bad1 = copy.deepcopy(plan)
    next(iter(bad1["biomes"].values()))["adds"].setdefault("Caves", []).append(sorted(dune)[0])
    bad2 = copy.deepcopy(plan)
    b2 = bad2["biomes"]["RM_LongShade"]
    b2["adds"]["Oasis"] = [b2["adds"]["Caves"].pop()]
    bad2["gates"]["Oasis"] = dict(bad2["gates"]["Caves"], biomeWhitelist=["Desert", "RUT_Desert"])  # legacy name only
    bad3 = copy.deepcopy(plan)
    victim = next(t for t in range(g.tiles) if g.arrays["tileBiome"][t] == some["save_biome_hash"] and t in muts)
    next(iter(bad3["biomes"].values()))["adds"]["Junkyard"].append(victim)
    bad4 = copy.deepcopy(plan)
    bad4["target_zero_share"] = 0.9
    for label, bad, needle in (("dune-sea tile", bad1, "is dune sea"), ("whitelist refusal", bad2, "Oasis refused"),
                               ("already-mutated tile", bad3, "already carries a mutator"),
                               ("relaxed target", bad4, "is not the generator's")):
        if not any(needle in p for p in problems(bad, g, muts, blocked, dune, csv_sets, None)):
            fails.append("blind: a plan with a %s was not caught by its own check" % label)

    for name, b in plan["biomes"].items():
        print("%s: %d tiles, bare %.1f%% -> %.1f%%, adds %d" % (name, b["tiles"], 100 * b["zero_share_before"],
                                                                 100 * b["zero_share_after"],
                                                                 sum(len(v) for v in b["adds"].values())))
    for f in fails[:40]:
        print("FAIL", f)
    print("RESULT", "FAIL %d" % len(fails) if fails else "PASS")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

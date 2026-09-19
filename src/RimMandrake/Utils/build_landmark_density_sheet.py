#!/usr/bin/env python3
"""build_landmark_density_sheet.py — the 8 dense biomes' landmark pairings, for a ruling.

BIOME_LANDMARK_REFINEMENT_1. The owner picked "Review sheet" at the 2026-09-18
card: BENCH builds one sheet over the 8 dense biomes (landmark roster + density,
keep/thin/enrich per row) and he rules on it.

WHAT IS ACTUALLY BEING RULED ON. The first pass (world/_dense_biomes.py, commit
64eb8f3e6) is 40 lines with two constants doing all the work:

    DENS = 26                       -> ~26% of every eligible tile, SAME in all 8
    pal[h(t,'d') % len(pal)]        -> an EVEN split across that biome's palette

Nobody chose 26%, and nobody chose an even split. A 3-def palette therefore gives
~1/3 each and a 2-def palette ~1/2 each, in every biome, regardless of what the
biome is for. That uniformity is the draft this item calls "not curated to each
sheet's flagship", and it is what these rows ask him to break.

DATA, all MEASURED 2026-09-19:
  world/dense_biomes_plan.json      561 placements, the only readable record of
                                    the pass (the .rws holds the live truth)
  world/ASHKARR_WORLDMAP_tiles.csv  frozen canonical tiles, sha256:9fad8198,
                                    21,872 rows — for tile->biome and water
  the live def dump                 mods=621/fedd946a33bb7137, captured
                                    2026-09-19T16:54Z — for each landmark's
                                    mutatorChances, i.e. what it actually DOES

⚠️ world/ASHKARR_WORLDMAP_landmarks.csv is NOT used and must not be: it is dated
2026-08-23, sixteen days BEFORE this pass, and its def mix (Dunes 36, Cliffs 27,
Valley 21) is a different lineage entirely. The frozen marker sits on tiles.csv
alone; its siblings are not the same vintage.

    python3 build_landmark_density_sheet.py            # dry run, writes nothing
    python3 build_landmark_density_sheet.py --apply
"""

import argparse
import collections
import csv
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL = Path.home() / ".claude" / "skills" / "review-sheets"
TEMPLATE = SKILL / "assets" / "sheet_template.html"
MEASURE = Path.home() / ".claude" / "skills" / "measuring-large-artifacts" / "bin" / "measure"

TILES = REPO_ROOT / "world" / "ASHKARR_WORLDMAP_tiles.csv"
PLAN = REPO_ROOT / "world" / "dense_biomes_plan.json"
OUT_HTML = REPO_ROOT / "Transient" / "landmark_density_2026-09-19.html"
OUT_DEC = REPO_ROOT / "Transient" / "landmark_density_2026-09-19.decisions.json"

# The 8 dense biomes, as the first pass keyed them (donor defNames) and as the
# frozen record names them now. The biome switch RENAMED the defs; it did not
# move which tiles are which biome, so the campaign name is the stable key.
BIOMES = [
    # campaign name,      biome def now,        palette the first pass gave it
    ("The Cracked Lands", "RUT_CrackedLands", ["DryLake", "VEE_DryRiver", "Valley"]),
    ("The Greentide", "RUT_Greentide", ["VEE_Cenotes", "Valley", "Oasis"]),
    ("Weeping Stones", "RUT_WeepingStones", ["Oasis", "VEE_Cenotes"]),
    ("The Pyrelands", "ZBiome_Grasslands", ["TerraformingScar", "Ruins", "VEE_DryRiver"]),
    ("The Contagion", "RUT_Contagion", ["TerraformingScar", "Ruins", "AncientGarrison"]),
    ("The Webwork", "RUT_Webwork", ["Cavern", "Valley", "VEE_SerpentineCanyons"]),
    ("The Slime", "RUT_Slime", ["VEE_Cenotes", "Cavern"]),
    ("The Scarlands", "RUT_Scarlands", ["Ruins", "AncientGarrison", "TerraformingScar"]),
]
BIOME_NAME = {d: n for n, d, _ in BIOMES}
PALETTE = {d: p for _, d, p in BIOMES}

# Each biome's flagship, from its own prose sheet under
# design/Jawa/worldbuilding/biomes/ — the thing the landmarks should be serving.
FLAGSHIP = {
    "The Cracked Lands": "the flood that dried — a cracked basin floor",
    "The Greentide": "river-jungle, the one wet place",
    "Weeping Stones": "the dew engine: stone that sweats water",
    "The Pyrelands": "fire-scarred grassland",
    "The Contagion": "the weapon site that made the plague",
    "The Webwork": "dense silk jungle",
    "The Slime": "the gelatinous superorganism, and its pits",
    "The Scarlands": "the Rakatan last stand, a battlefield",
}

# Mutators whose presence is a design question on a DESERT world (owner's rule:
# Ash'karr stays desert — local features, not repaints).
WET_MUTATORS = {"WildTropicalPlants", "PlantGrove", "Fertile", "WildPlants",
                "VEE_PlantLife_Overgrown", "ArcheanTrees", "Marshy", "WetClimate", "Muddy"}
# A marker earns its place only if it is RARE — at 77% coverage it is wallpaper and
# it destroys the markers beside it. So the contested mark is spent on a real wet
# ROLL, not a trace one: a landmark that rolls tropical growth a quarter of the time
# is a question, one that rolls Muddy at 0.05 is not.
WET_CONTEST_FLOOR = 0.2

DRIFT_GROUP = "⚠ Drifted here — nobody placed these"


def landmark_effects():
    """defName -> (top non-required mutators by chance, wet-mutator chances).

    Read from the live def dump, which is post-patch and carries the fingerprint
    of the mod set it was captured against — not from the donor XML on disk."""
    names = sorted({d for _, _, pal in BIOMES for d in pal})
    quoted = ",".join(f"'{n}'" for n in names)
    out = subprocess.run(
        [str(MEASURE), "sql",
         f"SELECT def_name, json FROM defs WHERE def_type='LandmarkDef' "
         f"AND def_name IN ({quoted})"],
        capture_output=True, text=True, cwd=REPO_ROOT).stdout

    effects = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        name, _, blob = line.partition("\t")
        try:
            rec = json.loads(blob)
        except ValueError:
            continue
        chances = rec.get("fields", {}).get("mutatorChances") or []
        rolls = collections.defaultdict(float)
        for mc in chances:
            if mc.get("required"):
                continue          # the landmark's own mutator, always applied
            rolls[mc["mutator"]] = max(rolls[mc["mutator"]], float(mc.get("chance") or 0))
        top = sorted(rolls.items(), key=lambda kv: -kv[1])[:4]
        wet = {k: v for k, v in rolls.items()
               if k in WET_MUTATORS and v >= WET_CONTEST_FLOOR}
        effects[name] = (top, wet)
    missing = [n for n in names if n not in effects]
    if missing:
        raise SystemExit(f"UNMEASURED: no LandmarkDef record for {missing} — "
                         f"refusing to describe a landmark I could not read.")
    return effects


def measured_rows():
    """(biome def, landmark) -> count, plus each biome's tile total."""
    tile_biome, tile_water = {}, {}
    with TILES.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            tile_biome[int(r["tile"])] = r["biome"]
            tile_water[int(r["tile"])] = r["water"]
    totals = collections.Counter(tile_biome.values())
    placed = collections.defaultdict(collections.Counter)
    water_hits = collections.defaultdict(list)
    for e in json.loads(PLAN.read_text(encoding="utf-8")):
        t, d = int(e["tile"]), e["def"]
        b = tile_biome[t]
        placed[b][d] += 1
        if tile_water[t] not in ("0", "", None):
            water_hits[(b, d)].append(t)
    return placed, totals, water_hits


def build(apply_it):
    effects = landmark_effects()
    placed, totals, water_hits = measured_rows()

    items, prefill = [], {}
    for bdef, counts in placed.items():
        biome = BIOME_NAME.get(bdef, bdef)
        pal = PALETTE.get(bdef, [])
        total = totals[bdef]
        n_biome = sum(counts.values())
        for lm, n in counts.most_common():
            drifted = lm not in pal
            on_water = water_hits.get((bdef, lm), [])
            share = n / n_biome * 100 if n_biome else 0
            dens = n / total * 100 if total else 0

            if lm in effects:
                top, wet = effects[lm]
                does = ", ".join(f"{k} {v:g}" for k, v in top) or "no optional mutators"
            else:
                top, wet, does = [], {}, "UNMEASURED"

            if on_water:
                effect = (f"{n} on WATER tiles in the open sea. A {lm} in the sea is "
                          f"wrong however the density is ruled — this is a defect, not "
                          f"a taste call. Arrived when the biome switch moved these "
                          f"tiles out of the biome that was given this landmark.")
                pre, contested = "cut", False
            elif drifted:
                effect = (f"{n} sitting in {biome}, which was NEVER given {lm} — its "
                          f"palette is {', '.join(pal)}. These drifted in when the biome "
                          f"switch renamed the tiles under them. Rolls: {does}.")
                pre, contested = "cut", False
            elif wet:
                effect = (f"{n} tiles ({share:.0f}% of this biome's landmarks, {dens:.0f}% "
                          f"of its tiles). Rolls WET plant mutators on a desert world — "
                          f"{', '.join(f'{k} {v:g}' for k, v in sorted(wet.items(), key=lambda kv: -kv[1])[:3])}. "
                          f"Also: {does}.")
                pre, contested = "keep", True
            else:
                effect = (f"{n} tiles ({share:.0f}% of this biome's landmarks, {dens:.0f}% "
                          f"of its tiles). Rolls: {does}.")
                pre, contested = "keep", False

            # Every drifted/on-water row goes in ONE group, so he can settle the
            # whole defect class in a single motion instead of meeting it six times
            # scattered through six biomes.
            group = (DRIFT_GROUP if (drifted or on_water)
                     else f"{biome} — {FLAGSHIP.get(biome, '')}")
            items.append({
                "id": f"{bdef}__{lm}",
                "group": group,
                "label": f"{lm} in {biome}",
                "effect": effect,
                "prefill": pre,
                "contested": contested,
                "meta": {"tiles": str(n),
                         "of biome": f"{dens:.0f}%",
                         **({"DRIFTED": "not in this biome's palette"} if drifted else {}),
                         **({"ON WATER": f"{len(on_water)} tiles"} if on_water else {})},
            })
            prefill[items[-1]["id"]] = {"decision": pre, "prefill": pre, "note": ""}

    items.sort(key=lambda it: (it["group"], -int(it["meta"]["tiles"])))

    config = {
        "sheetId": "landmark_density_2026-09-19",
        "title": "Landmarks on the 8 dense biomes",
        "subtitle": f"{len(items)} biome×landmark pairings · 561 placements MEASURED",
        "briefHtml": (
            "<p>Every landmark on these 8 biomes was placed by a 40-line script with "
            "<b>two constants</b>: <code>DENS=26</code>, so ~26% of eligible tiles in "
            "<i>every</i> biome, and an <b>even split</b> across that biome's 2-3 def "
            "palette. Nobody chose either number. That is what this sheet asks you to "
            "break — per biome, and per landmark within it.</p>"
            "<p>Each row says what the landmark actually <b>does</b> when a map is "
            "generated on it: its optional <code>mutatorChances</code>, read from "
            "today's def dump, not from the donor XML.</p>"
            "<p><b>Two things are defects rather than taste</b>, pre-filled CUT: four "
            "landmarks now sit on open-sea water tiles, and two Caverns sit in a biome "
            "that was never given Caverns. Both arrived when the biome switch renamed "
            "tiles underneath already-placed landmarks.</p>"
            "<p>Contested rows roll <b>wet plant mutators on a desert world</b> — "
            "tropical growth, groves, fertility. That may be exactly right for a "
            "cenote, or it may be the desert rule leaking. Your call.</p>"),
        "criterion": ("Grouped by biome and sorted by tile count — which ranks how MUCH of "
                      "each biome a landmark occupies, not whether it belongs there. Only "
                      "you can rank belonging, and the flagship in each group header is "
                      "what I think it should be serving."),
        "invented": [
            "The 26% density and the even palette split were a script constant, not a "
            "design. Treating them as the thing to rule on is my framing of this item.",
            "Each group header names that biome's flagship, taken from its own prose "
            "sheet. If a flagship is wrong, the rows under it are judged against the "
            "wrong target.",
            "I call wet plant mutators on a desert world a question worth raising, from "
            "your 'Ash'karr stays desert' rule. You have never ruled on these landmarks.",
            "CUT pre-fills on the 6 drifted/on-water rows are my call, not yours.",
        ],
        "posture": {
            "mode": "whitelist",
            "explain": ("Default is KEEP: a row you leave alone keeps the landmark at the "
                        "density it has now. Nothing is removed by not deciding."),
        },
        "options": [
            {"key": "keep", "label": "Keep as is", "hotkey": "1", "color": "#5ac37f", "counts": "in"},
            {"key": "thin", "label": "Thin", "hotkey": "2", "color": "#e8b64c", "counts": "in"},
            {"key": "enrich", "label": "Enrich", "hotkey": "3", "color": "#6aa6e8", "counts": "in"},
            {"key": "cut", "label": "Cut from this biome", "hotkey": "4", "color": "#e06c6c", "counts": "out"},
        ],
        "groupLabel": "biome",
        "media": False,
        "decisionsFile": OUT_DEC.name,
        "decisionsPath": str(OUT_DEC),
        "sheetPath": str(OUT_HTML),
    }

    if not apply_it:
        print(f"Dry run — would write:\n  {OUT_HTML}\n  {OUT_DEC}\n")
        for it in items:
            flag = "WATER" if "ON WATER" in it["meta"] else ("DRIFT" if "DRIFTED" in it["meta"] else "     ")
            print(f"  [{it['prefill']:6}] {flag} {it['label'][:48]:48} {it['meta']['tiles']:>4} tiles")
        n_cont = sum(1 for it in items if it["contested"])
        print(f"\n{len(items)} rows · contested {n_cont} ({n_cont/len(items)*100:.0f}%) "
              f"· cut pre-filled {sum(1 for it in items if it['prefill']=='cut')}")
        return 0

    html = TEMPLATE.read_text(encoding="utf-8")
    html = replace_block(html, "CONFIG", json.dumps(config, indent=2))
    html = replace_block(html, "ITEMS", json.dumps(items, indent=1))
    OUT_HTML.write_text(html, encoding="utf-8")
    OUT_DEC.write_text(json.dumps({
        "sheetId": config["sheetId"], "posture": "whitelist",
        "decidedCount": 0, "decisions": prefill, "frozen": False,
    }, indent=2), encoding="utf-8")
    print(f"wrote {OUT_HTML}\nwrote {OUT_DEC}\n{len(items)} rows")
    return 0


def replace_block(html, block_id, payload):
    open_tag = f'<script id="{block_id}" type="application/json">'
    i = html.index(open_tag) + len(open_tag)
    j = html.index("</script>", i)
    return html[:i] + "\n" + payload + "\n" + html[j:]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for p in (TEMPLATE, TILES, PLAN, MEASURE):
        if not p.exists():
            print(f"missing: {p}", file=sys.stderr)
            return 2
    return build(args.apply)


if __name__ == "__main__":
    sys.exit(main())

# CONTAGION_BIOME_PLACEMENT_1 — move the Contagion to the peaks above the green

Owner ruling 2026-09-06 (`the_contagion.md` §0): the Contagion (`AB_OcularForest`) lives on
the high tiles above the green valleys and **takes NO green squares** (CypreJungle,
Feralisk jungle, Desert Oasis and kin are precious and get their own definitions).

## spec
- MEASURED candidate bands (non-green, dayside arc < 75):
  - Scald Spine's 38 non-green tiles (Volcano 18, ZBiome_Badlands 13, LavaField 7; elev
    median 1,170 m) — the core, under the perpetual scald thunderstorm.
  - For presence, at the owner's option: Ashfall Range 35 tiles ≥ 1,200 m (11 ≥ 1,500);
    Dew Horn 137 tiles ≥ 1,200 m (70 ≥ 1,500; the wettest non-green highs, rain median 103).
- Produce the exact tile list from those bands; put it to the owner as a rendered
  worldview before painting (patch-a-curated-artifact rule: diff to a temp path first).
- The donor's 3 current Ashfall Range tiles (15045-class strays are NOT these; these are
  tiles at lat −2.0/−0.7/−1.4, lon 63.1/63.2/64.3) either fold into the new set or dissolve
  into their desert neighbors.
- Re-biome via world tools + `world_commit`; re-freeze the savegame; back up Saves first.
- 🔴 Anti-bullseye: the Contagion is a point-set on peaks, never a ring.

## verify
CSV re-count: Contagion tiles == the ruled list, zero on former green tiles; savegame
re-frozen; a `worldview.py` render reviewed by the owner.

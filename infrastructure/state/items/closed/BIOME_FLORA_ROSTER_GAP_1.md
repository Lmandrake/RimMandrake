# BIOME_FLORA_ROSTER_GAP_1 — biome_flora.py's own `--check` finds 10 stale/missing biome entries

Discovered 2026-09-07 (FOUNDRY, this window) while reviewing `design/Jawa/mods/biome_flora.py`
for the standing code-review loop. The file's own authoritative `--check` (not a guess —
run live) currently reports:

```
🔴 BIOME NOT ON THE MAP: HorrorWastes
🔴 BIOME NOT ON THE MAP: BMT_CrystalCaverns
🔴 PLACED BIOME WITH NO ROSTER: BiomeCypreJungle (227 tiles)
🔴 PLACED BIOME WITH NO ROSTER: BiomeGRimond (1328 tiles)
🔴 PLACED BIOME WITH NO ROSTER: COMIGO_GreaterSwamp_Tropical (43 tiles)
🔴 PLACED BIOME WITH NO ROSTER: RUT_GreySea (381 tiles)
🔴 PLACED BIOME WITH NO ROSTER: RUT_NightsideIce (802 tiles)
🔴 PLACED BIOME WITH NO ROSTER: RUT_PropaneLake (57 tiles)
🔴 PLACED BIOME WITH NO ROSTER: RUT_TheScald (312 tiles)
🔴 PLACED BIOME WITH NO ROSTER: RUT_TwilightSea (436 tiles)

10 problem(s) — nothing written.
```

**This is not a code bug** — `biome_flora.py` is doing exactly what it's designed to do
(refuse to write a patch when its `FAMILIES` data disagrees with the current world). The
code itself is reviewed clean; this item tracks the DATA gap the check surfaced.

## spec
- **Two stale entries to remove/reconcile**: `HorrorWastes` (dissolved into other biomes
  per `HORRORWASTES_BIOME_DISSOLVE_1`) and `BMT_CrystalCaverns` (no longer a worldmap
  biome per `the_lantern_deeps.md`'s owner ruling — it's now the Lantern Deeps' injected
  cave-map layer, `LANTERN_DEEPS_INJECTION_1`). Both rulings landed after
  `biome_flora.py`'s `FAMILIES` dict was last authored/updated — this is the
  "unblocking/propagation sweep" those two rulings owed and never got.
- **8 placed biomes with zero flora roster**, all fairly recent additions from the
  liquid-biomes/naming work: `BiomeCypreJungle`, `BiomeGRimond` ("Blue Desert"),
  `COMIGO_GreaterSwamp_Tropical`, `RUT_GreySea`, `RUT_NightsideIce`, `RUT_PropaneLake`,
  `RUT_TheScald`, `RUT_TwilightSea`. Several of these already have their own "Roster"
  owed-lines in their biome sheets (e.g. `the_scald.md`'s "rides the full assignment
  pass: the four sorts into `RUT_TheScald`'s waiting empty `wildAnimals`") — this item
  is the FLORA half of that same debt, surfaced mechanically rather than by memory.
  Until assigned, these biomes have no flora entry through this pipeline (donor
  defaults may still apply at the def level, but nothing here shapes them).
- Fix: update `FAMILIES` in `design/Jawa/mods/biome_flora.py` — drop the two dead
  entries (or replace with a superseding note per the doc's own "DELIBERATELY UNPLACED"
  convention), assign rosters for the 8 live-but-uncovered biomes (following the file's
  own rules: no plant crosses a family, head-and-tail shaping, `PLANTLESS`/`DENSITY`
  exceptions only where already ruled). This is content-authoring work (which plants go
  where), not mechanical — needs the same kind of judgment call the original 8-family
  assignment pass used, ideally with the owner's steer per
  `[[biome-sheets-are-a-conversation-loop]]`-style engagement rather than a solo guess.

## verify
`python3 design/Jawa/mods/biome_flora.py --check` reports 0 problems; `--write` produces
a patch covering all 24 (or however many then-current) placed biomes with no stale
entries; `--doc` regenerates `biome_flora_rosters.md` cleanly.

## closed 2026-09-09 (BENCH, assignment pass)
FAMILIES rewritten from the rosters at `32f9d25d`: --check 0 problems, 5 families
(connected components of plant-sharing — the 8-family shape was unsatisfiable under
"no plant crosses a family" with the rosters' shared plants), 23 biomes, 143 plants,
199 assignments; stale HorrorWastes/BMT_CrystalCaverns keys gone; --write and --doc
both regenerate clean. A follow-on normalization wave (flammability + grow temps) is
running under BIOME_FAUNA_ASSIGNMENT_SITTING_1 but this item's own criteria are met.

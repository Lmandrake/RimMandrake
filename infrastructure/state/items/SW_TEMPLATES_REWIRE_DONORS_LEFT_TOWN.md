## spec
Found by the offline bar `template_defs_resolve` in `src/RimStarWars/StructureInjectionsSW/validation.py`
(NORTHSTAR_PARTIAL_GAPS_FILL_1). In `src/RimStarWars/StructureInjectionsSW/Templates/*.txt` (rimplace exports of
`design/Jawa/templates/*.lua`) these THING defNames resolve in the 2026-08-29 def capture but in none of the
2026-10-28..2026-11-02 captures (317-mod list), so each line places nothing today:

- `BanthaHorn` x29, `Leather_Bantha` x19 (bantha_graveyard) — donor `mlie.starwarsanimalcollection`, absorbed:
  `RSW_BanthaHorn` / `RSW_Leather_Bantha` exist in `mandrake.rsw.swbestiary`.
- `KraytDragonHorn` x5 (krayt_graveyard) — same donor; `RSW_KraytHorn` exists, check it is the same trophy.
- `LargeFossilTrophy`, `MediumFossilTrophy` (hunting_lodge) — `zacharyfoster.mineralssparkle`, gone.
- `QE_Sign` (garrison_tiny, mining_site) — `hailuan.customquestframework`, gone.

Also: `RSW_BeastNest_Large` (Defs/BeastLairs, the 3x3 lair dressing of structure_procedural_spec.md §9) ships
but no template places it and no patch names it; `beast_lair.lua` should place it (`KNOWN_UNPLACED`).

Retarget in the .lua, re-export the .txt with rimplace, delete the names from `KNOWN_UNRESOLVED` in validation.py
(the bar fails on a stale entry), and restore a live `TEMPLATE_CHECKS` marker for bantha_graveyard's horns and
hunting_lodge's trophies.

## criteria
`python3 src/RimStarWars/StructureInjectionsSW/validation.py` prints `STATIC: PASS` with `KNOWN_UNRESOLVED` and `KNOWN_UNPLACED` empty.

# BENCH saved-site tooling: Contagion + LeaningScrub (offline only)

2026-10-16. Copies the Cauldron pattern (e1e5a6ff3a). No live game, no bridge, no ModsConfig, no FOUNDRY build files.

## 0. Shared recipe
NEW `src/RimMandrake/Utils/modcheck/biome_site.py`: Cauldron's steps parameterised by a site_spec module plus a
biome `probe(call, phase, saved)`; save-phase problems stop the build before anything is written, reload-phase
problems register loadVerified False. Cauldron keeps its own copy (folding it in is a mechanical follow-up).

## 1. Contagion site
DONE offline. `Contagion/site_spec.py` (RM_TestSite_contagion_v1, danger, 250, tile 25 C/60 mm/1387 m/Flat --
test values, not the 32 C median or the peaks; 23 natives = BiomeDef roster; food at (125,145) off every pad) +
`Contagion/prep_site.py` (probe: ContagionSky BurnActive False at save and reload).
Gap: `Contagion/northstar_site.py` preflight refuses an RM_Contagion map; the arm split is owed before the driver runs here.

## 2. LeaningScrub site (LEANING_SCRUB_SITE_BUILD_LEANS_ONE_WAY)
DONE offline. `LeaningScrub/site_spec.py` (RM_TestSite_leaningscrub_v1, danger, 250, tile 19.7 C/0 mm/15 m/Flat;
8 non-predator natives) + `LeaningScrub/prep_site.py` (probe: Downwind read locks the heading before the save; the
reload must read the same headingDegrees without asking Downwind).

## 3. test_site_saves.py entries + preflight
`SITES["contagion"]`, `SITES["leaningscrub"]` (builder key). `biome_preflight.o_site` now PASSes only on
loadVerified True (was: any registry row). Both preflights: O-SITE UNMEASURED "declared, not built yet".

## 4. Items
FILED `CONTAGION_SITE_BUILD_SKY_STAYS_CALM` (--for BENCH, needs bridge). Prose notes appended to both items.

## Selftests
GREEN 5/5: selftest_contagion_site, selftest_leaningscrub_site, selftest_cauldron_site, selftest_test_site_saves,
selftest_biome_preflight.

## Left for the live round
- `test_site_saves.py build contagion` / `build leaningscrub`, then `load` each (biomes_sprint, bridge held).
  jawa/map_comp_read and the shared recipe are UNPROVEN live.
- Contagion: split northstar_site.py's arms (on-Contagion preflight) before the driver runs on the site.
- LeaningScrub: FOUNDRY's Lean components in validation.py, then the driver on the site.

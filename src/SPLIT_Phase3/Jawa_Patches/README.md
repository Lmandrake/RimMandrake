# Jawa Patches — SPLIT, superseded 2026-09-04

This mod no longer exists. JAWA_PATCHES_SPLIT_1 (owner-confirmed tiers,
2026-09-01) split its 95 Patches/Defs files plus textures/languages into:

- `src/RimMandrake/MandrakePatches`  (mandrake.rm.patches)  — game-generic fixes
- `src/RimStarWars/StarWarsPatches`  (mandrake.rsw.patches) — SW content fixes + parked SW animal art
- `src/RimUtinni/UtinniPatches`      (mandrake.rut.patches) — the campaign layer

Per-file record: `infrastructure/state/jawa_patches_split_map.csv`.
The ❄️ frozen Jawa eye-glow doctrine moved to `src/RimStarWars/StarWarsRaces/README.md`
(its values live in that mod's GeneDefs).

The DEPLOYED copy of mandrake.jawa.patches stays in the game's Mods folder until
the next full-list load proves the three successors (COLD_LOAD_RUN_SHEET_3);
then delete it and drop its ModsConfig entry.

# DEAD_OR_INERT_SETTINGS_1 — settings the def lints found unwired: wire or delete per mod

From the 2026-10-07 lint wave (FOUNDRY handoff 202610080208). A Mod Settings control that changes nothing breaks the "every mod ships superb Mod Settings" rule.

## spec

Per mod: wire the setting to the mechanic its label promises, or delete it (field, Scribe, UI) when nothing should read it.

## built 2026-10-08 (c76c4119c)

- Scarlands: `biomeRarityFactor` applied by a postfix on `BiomeWorker_Scarlands.GetScore` for RM_Warscar only (0 never; below 1 a tile-seeded chance; above 1 a score multiplier, PROVISIONAL). Cross-biome opt-in wired like TheRot's (`RM_WarscarSettings.Governs/Coverage`): wreck-lichen seeding (scaled by intensity) and the settling-dust calm run on opted-in maps; the UI is real now.
- EmpirePursuit: `ionVolleyIntervalHours` has a slider (1-24 h).

## still open (not obvious, left for their own items)

- TerminalBiomes: `crossBiome*` (4) and `twilightChainAvailability`, `twilightSuulkPressureScalingEnabled`, `twilightChartsAgeEnabled` gate features other items still owe.
- Wasteland: `brineDepositsEnabled` needs the brine GenStep it promises.

## criteria

- A1 (L0): `lint_scarlands_defs.py` and `lint_empirepursuit_defs.py` report 0 settings WARN.
- A2 (L2): with the Warscar cross-biome opt-in on for one biome, a new map of that biome seeds wreck-lichen beside ruins; rarity 0 leaves no RM_Warscar tile on a generated planet.

## NEXT

Decide TerminalBiomes and Wasteland when their owning features land.

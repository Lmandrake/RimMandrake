# Review batch 5 — 2026-10-06 (FOUNDRY, offline)

Engine facts checked against RimSage (decompiled 1.6): GenStep_Scatterer, GenStep_ScatterThings.CanScatterAt,
GenSpawn.CanSpawnAt / WouldWipeAnythingWith, BiomeAnimalRecord, Listing, Building_SteamGeyser.

## RM_GenStep_WreckField.cs — CLEAN (marked)
- XML row loader matches BiomeAnimalRecord's element-name-as-key form exactly.
- Generate/CanScatterAt/terrain validation mirror GenStep_ScatterThings; seeded via SeedPart; Rand use deterministic.
- Count: own range overrides class, density setting multiplies both paths; ShouldSkipMap carries FieldActive.
- Note (not a bug): cluster pieces are not added to usedSpots, so a later anchor can sit within minSpacing of a
  cluster piece (not of its anchor). `misses < 3` is total, not consecutive; more lenient than vanilla's stop-at-first.
- Latent: an alias equal to its own settingsKey would recurse (FieldActive -> Enabled(key) -> FieldActive). None today.

## RM_WreckageMod.cs — CLEAN (marked)
- disabledFields null-safe; per-field checkbox list from GenStepDefs; scribe keys unchanged.

## RM_WreckWeathering.cs — already CLEAN at 58351a233 (hash matches), not re-reviewed.

## RM_TerminalBiomesMod.cs — FIXED (not marked; edited)
- Settings screen: `Listing_Standard` lacked `maxOneColumn = true`. Default content ~2100px vs the 1600px first-frame
  view guess, so overflow wrapped into an off-screen second column (Listing.NewColumnIfNeeded), CurHeight reset, and
  lastListHeight then SHRANK every frame — the lower sections (channel current / cross-biome / Grey Sea) were
  unreachable. Same bug as Webwork's cfdba9344. One-line fix; rebuilt (winbuild OK, srchash says +dirty until committed).
- S6 retirement: no C# caller of the old bool remains; dropping the scribe key is harmless; "Scald" bare gate
  registered here, "Scald.S6" alias registered later by RM_WreckFieldStartup (replaces). Scald maps still get the field
  via extraGenSteps on RM_TheScald/RUT_TheScald.
- FINDING (derived file, not edited): `src/RimMandrake/Utils/modcheck/required_checks.json` still lists
  `flip_scaldS6WreckSalvageEnabled` and `scald_wreck_salvage` with toggle `scaldS6WreckSalvageEnabled` (stale
  script_sha) — regenerate from validation.py.

## RM_TerminalBiomesScaldKit.cs — CLEAN (marked)
- Skipping base.Tick is safe: Building_SteamGeyser.Tick never calls base (no comps ticked either way).

## RM_WebworkMod.cs — CLEAN (marked). Scroll fix present and correct.

## RM_FeverWoodMod.cs — CLEAN (marked)
- Scroll lacks maxOneColumn but content (~1650px, no conditional rows) fits its 2000px initial view; min>max sliders are
  clamped by consumers (TwoFrontLure, TentacleWatch). Latent only if rows are added past 2000px.

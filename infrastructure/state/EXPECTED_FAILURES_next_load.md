# Expected-failure signatures — next load(s), 2026-09-19 overnight BELT pass

Written BEFORE any restart, per `rimworld-load-round` §3. Seven touched
assemblies ride the same minimal-list batch; each has its own distinguishing
signature so a `TypeLoadException`/Harmony patch failure/crash can be
attributed to the right one rather than guessed after the fact.

| # | assembly (DLL) | new symbol(s) that must appear/behave | distinguishing failure signature to grep for |
|---|---|---|---|
| 1 | JawaBench.BridgeTools (companion) | `jawa/do_bill_now`, `jawa/droid_format_tier`, finalize-sequence fix in `jawa/world_tile_map_generate` | Exception text containing `JawaBenchTerrainTools` / `RimBridgeServer` at startup; OR the two new tool names absent from `--list-tools` |
| 2 | JawaRules.dll | `Patch_RedressPawn_ForceKind` (Harmony postfix on `PawnGenerator.RedressPawn`) | `Patch_RedressPawn_ForceKind` or `JawaRules` in a Harmony-patch-failed or TypeLoadException line |
| 3 | RimMandrakeFlowWorks.dll | `CompPitFitting.CanSwim`, `RM_GenStep_LiquidShores`, `RM_WorldComponent_LiquidTags` | `RimMandrakeFlowWorks` / `CompPitFitting` / `RM_GenStep_LiquidShores` / `RM_WorldComponent_LiquidTags` in a crash, ConfigError, or missing-type line |
| 4 | RimMandrakeNinefold.dll | `GetLoudness`/`GetLoudnessRank`/`GetFront`/`ReckonFrontAtLanding` on `GameComponent_Ninefold`, `Patch_GravshipLanded` postfix | `RimMandrakeNinefold` / `GameComponent_Ninefold` / `Patch_GravshipLanded` in a crash or Harmony-patch-failed line |
| 5 | RimMandrake.CreatureBehaviors.dll | `RM_Hediff_Grappled`, fluid-sac/poison comp, Soulchime stun/soothe/armor comp | `RimMandrake.CreatureBehaviors` / `RM_Hediff_Grappled` / `RM_CompProperties_FluidSacs` / `RM_CompProperties_ProximityPsychicStun` in a crash or ConfigError line |
| 6 | RimMandrakeProperty.dll | `FloatMenuOptionProvider_Bribe`, `HirePlacelessUtility`, Pickpocket csproj-registration fix | `RimMandrakeProperty` / `FloatMenuOptionProvider_Bribe` / `FloatMenuOptionProvider_HirePlaceless` / `PickpocketUtility` in a crash, TypeLoadException, or "type not found" line |
| 7 | FireEcologyHook.dll (Pyrelands) | `WildPlantAllowlist` Harmony postfix on `WildPlantSpawner.CalculatePlantsWhichCanGrowAt` | `FireEcologyHook` / `WildPlantAllowlist` in a Harmony-patch-failed or crash line |

## Baseline (no signal = pass)

A CLEAN load shows **none** of the seven signature strings above anywhere in
`Player.log`, and `--list-tools` includes `jawa/do_bill_now` and
`jawa/droid_format_tier`. Any signature string present attributes the failure
to that row and only that row — do not batch-blame.

## RESULT — Phase 1 minimal-list sweep, 2026-09-19 (CLEAN)

Ran via `loadsweep/sweep_load.sh` on the 9-mod loadsweep BASE +
`overnight_batch.txt` (the 6 custom mod packageIds; the companion DLL loads
automatically with `brrainz.rimbridgeserver`, not a Mods-folder entry) = 15
active mods. Bridge up in 18s. `recovery_hits=0`, `patch_failed=0`,
`typeload=0`. Zero hits on any of the 7 signature strings above except
`JawaRules`, which appeared 6 times as its own **armed** log lines — including
`pawnkind-redress-fix: armed; KCSG_PAWNKIND_COLONIST_FALLBACK_1 — a redressed
world pawn is forced onto the requested kind and xenotype even when ChangeKind
was blocked`, confirming `Patch_RedressPawn_ForceKind` registered successfully.
114 config errors / 57 crossref errors present, but 100% attributable to
pre-existing FlowWorks liquid-authoring notes and other mods' missing
dependencies on the minimal list — none touch any of the 7 rows above.
`jawa/do_bill_now` and `jawa/droid_format_tier` both confirmed present in
`--list-tools`. **All 7 assemblies: CLEAN on the minimal-list signal.**

## RESULT — Phase 2 full-list load: BLOCKED by an unrelated pre-existing crash

4 consecutive full-list launch attempts (with and without `mandrake.rut.longhunger`
inserted) all hit the SAME `AlphaGenes_GeneDefGenerator_ImpliedGeneDefs_Patch`
NullReferenceException during `DefGenerator.GenerateImpliedDefs_PreResolve`,
before Playing was ever reached. **Confirmed unrelated to all 7 touched
assemblies and to LongHunger** — reproduces identically on the plain
`FULL.LATEST` list with LongHunger absent. Filed as `FULL_LOAD_ALPHAGENES_NRE_1`
with a strong lead (bisect `df261b2bc` ROT_FLORA_FAUNA_VERDICTS_1's 48-species
rename/resize pass, landed the same session, touches exactly the content class
implicated). This blocks every full-list-only item below from being directly
observed tonight — see each item's own note for what Phase 1 could still
confirm indirectly (assembly loads clean) versus what remains genuinely
unverified.

## Full-list-only decision strings (Phase 2)

Written per named item, read off each item's own file, before the full-list
load:

- `BIOME_CONFIGERRORS_NRE_1`: grep `Player.log` for `NullReferenceException` +
  `ConfigErrors` on the 5 named biomes (see item file for the list). Expect
  ABSENT (prior pass: "looks resolved").
- `FULL_LOAD_RESIDUE_TRIAGE_1`: grep for the aquatic Juv lifeStageAges config
  error pattern (42 lines previously). Expect ABSENT after the `Inherit="False"`
  fix.
- `MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1`: LongHunger's own first-load criteria
  — grep for LongHunger's defNames loading clean alongside the donor sandworm
  mod, 0 config errors attributable to it.
- `WORLDMAP_LIQUID_TAGS_1` / `AQUATIC_WATER_BREATHING_GENE_1`: grep for
  `Config error in RM_` on any FlowWorks liquid-tag/gene def. Expect 0.
- `KCSG_PAWNKIND_COLONIST_FALLBACK_1`: confirm JawaRules assembly loads clean
  (no signature-2 hit); full KCSG placement repro deferred if time-limited.
- `PYRELANDS_FLORA_LEAK_1`: spawn/generate a Pyrelands map, grep spawned flora
  for `AB_SessileMechanoid` / `AB_GiantStikehr`. Expect 0 occurrences.
- `DEEPS_FAUNA_MECHANICS_1` / `SETTLEMENT_VERBS_WAVE_1`: confirm assemblies
  load clean (signatures 5 and 6 absent); quick spawn-and-poke if time allows.
- `BRIDGE_MAPGEN_STALE_FINALIZE_1`: `do_bill_now`/`droid_format_tier` present
  in `--list-tools`; a map-finalize call renders correctly (visual/read-back
  check, not just `success: true`).

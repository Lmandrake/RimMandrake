# Expected-failure signatures — MODLIST_RESTORE_AND_BATCH_DEPLOY_1, 2026-09-09 (FOUNDRY)

Written BEFORE launch per load-round §2/§3. Five assemblies ride this load under
the owner's batching waiver; each fails in a distinguishable place.

## Assemblies riding this load

1. **RimMandrakeMovingDunes.dll** (`mandrake.rm.movingdunes`) — brand new mod,
   never loaded before. Fails as: `TypeLoadException` / `Could not find class`
   naming `RimMandrake.MovingDunes.*`, `DuneMaterialDef`, or a discarded
   `DuneMaterialDef` def block; or a red error naming
   `RM_MD_`/`BuriedCache`/`MovingDunes` from `Patches/BiomeBindings.xml`
   (`PatchOperationAddModExtension`, unguarded — 2 matches predicted, in Core
   `Biomes_WarmArid.xml` and GRiNDTerra `Biomes_NewArid.xml`).
2. **RiverSteamHook.dll** (`mandrake.rm.manywaters`) — rebuilt, and the mod has
   never been in the live list. Fails as: errors naming `RiverSteamHook`, or
   discarded defs naming `RM_ColoredWater*` / `RM_DeepSand` / `RM_ColoredSteam`.
3. **RimMandrakeOracle.dll** (`mandrake.rm.oracle`) — already on disk, mod never
   enabled. Fails as: errors naming `RimMandrake.Oracle`, `OracleClient`,
   `OracleHttpClient`, or a Mod-settings `Could not find class`.
4. **RimMandrakeFluidCanals.dll** (`mandrake.rm.fluidcanals`) — already on disk,
   mod never enabled. Fails as: errors naming `RimMandrake.FluidCanals`,
   `RM_FluidCanal*`, or a `DesignationCategoryDef` failure from
   `FluidCanal_OrdersPatch.xml` (1 match predicted, Core `DesignationCategories.xml`).
5. **JawaBench.BridgeTools.dll** (companion, `RimWorld/BridgeTools/JawaBench/`) —
   redeployed with `--gm` (317 tools) carrying the `WORLD_FEATURE_LABELS_OVERSIZED_1`
   `maxDrawSizeInTiles` fix. Fails as: bridge tool count != 317, a missing
   `Bridge token:` line, or `[JawaBench]` load errors. Note this one is NOT in
   `ModsConfig.xml` at all — it is discovered by RimBridgeServer at bridge start.

## Load decision strings

| item | expected-PRESENT | expected-ABSENT / at-baseline |
|---|---|---|
| the load itself | `Bridge token:` in Player.log; `activeMods` = **582** | `Resetting mods config and trying again` / `Recovered from incompatible or corrupted mods` |
| the 7 restored C# types | zero `Could not find type named RimMandrake.` lines | any of the 7 recurring — the stale-DLL deploy did not take |
| the 4 new mods | `Adding mandrake.rm.manywaters(`, `...movingdunes(`, `...fluidcanals(`, `...oracle(` | any `Could not find class` naming their namespaces |
| Wave 1 retirement (13) | — | any `Could not load reference to` naming `KibbleDispenser` above the 3 known bookkeeping-roster tokens |
| 3 droid mods restored | `Adding neronix17.asimov(`, `neronix17.outerrim.droiddepot(`, `mandrake.rsw.msedroidfix(` | `Could not resolve cross-reference` naming droid defs |
| WORLD_FEATURE_LABELS | (post-load) `jawa/world_features_get` max `maxDrawSizeInTiles` ≈ **61** (was 99.6) | — |
| overall | `harvest_log.py` exits without REFUSING | no new `^Config error in` / `Could not resolve cross-reference` above the last known-good baseline |

**False pass to watch for**: the bridge answering is NOT proof of a load — an
idle vanilla main menu answers too. The load is only real when `harvest_log.py`
runs without refusing AND `activeMods` reads 581.

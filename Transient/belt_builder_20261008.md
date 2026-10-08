# FOUNDRY belt offline content builder — 2026-10-08

Offline only (no bridge, no game). One section per item, appended as each lands.

## MOVINGDUNES_WATER_BANKS_SAND_1

Built at `01108c97c`. `RM_DuneKernel.RunTransport`: a hop meeting a non-holding cell (water/space, `IDuneField.CanHoldSand`, `MapDuneField` reads terrain `holdSnowOrSand`) lands on the cell before it like a wall lee. `Batch.WaterBanked` counts it; `Batch.CapOverflow` split out so `DepositError` is nudge-only (exactly 0 with nudge off). Fuzz: ledger identity extended, no slab on water, lake-shore unit (mass exact, shore grows), blind check on water banks. Mutation: deleting the shore line turns 5/5 seeds red. DLL+srchash rebuilt. run_selftests 281/281. Design doc updated. Owes A2 L2 live.

## WARCASKET_DEPENDENCY_DOWNLOAD_URL_1

Built at `e97afd219` (sha on origin may differ after landing; see final list). Decompiled `ModMetaData` drops any dependency without a non-empty downloadUrl/steamWorkshopUrl; 73 entries across 51 About.xml were inert (empty `<steamWorkshopUrl />` counts as none). All fixed: our mods point at the repo, third-party at Steam ids read from the installed workshop folders. Guard `src/RimMandrake/Utils/selftest_about_dependency_urls.py` (199 entries, sanity floor 50). A2 log read owed.

## DEAD_OR_INERT_SETTINGS (Scarlands, EmpirePursuit)

- Scarlands: `biomeRarityFactor` now applied by a Harmony postfix on `BiomeWorker_Scarlands.GetScore` for RM_Warscar only (0 never, <1 tile-seeded chance, >1 score multiplier PROVISIONAL). Cross-biome opt-in wired like TheRot's: `RM_WarscarSettings.Governs/Coverage`; wreck-lichen seeding (scaled by intensity) and the settling-dust calm run on opted-in maps; UI now real. Stale "ships no bespoke mechanic" header comment rewritten. Lint 4 WARN -> 0.
- EmpirePursuit: `ionVolleyIntervalHours` got its slider (1-24 h) and keyed string. Lint 1 WARN -> 0.
- Left alone (not obvious): TerminalBiomes crossBiome* + 3 twilight settings (their features are owed by other items), Wasteland `brineDepositsEnabled` (needs a GenStep).
- run_selftests: my mods green; 5 failures are in peers' uncommitted in-flight mods (SeaShores, RaidRedesigner, TitanicCreatures build, ledger_lint on a dirty OWNER shard).

## MODCHECK_ACCEPTANCE_MAPPING_TABLE_1

Already built at `69378ce3b` (tables + `acceptance_map.py` + selftest reproducing the Greentide/PyrelandsMechanics run JSONs, unmapped never recorded). Selftest GREEN today; recorded implemented, all three L0 attested, item moved to closed/.

## BRIDGE_KILL_HOSTILES_TOOL_1 + TILE_TEMP_CACHE_RESET_TOOL_1

Built at `ac8b24b82`, NOT deployed (companion deploys only with the game closed: `build.py --gm --apply`). `jawa/kill_hostiles` (GenHostility, filters, dryRun, corpse cleanup, survivor control). `jawa/world_tile_cache_reset` (nulls the five Tile caches by reflection, refuses if any field fails to resolve, verifies null). `jawa/get_defs` renders System.Type values by name (fixes 'RuntimeType' for specialDesignatorClasses). world_cache_audit's "no cache-clearing tool" text corrected. selftest_tool_metadata 377 tools == source. A3 (skill doc) left for a curation session.

## BRIDGE_LOCK_CROSS_CLONE_RACE_1

Shared cross-clone lock file on D:\ (outside git) checked by `bridge take`, touched by the holder's events, cleared on release; `modset_builder --apply/--restore` refuses a window that does not hold the bridge (override `--not-my-bridge`). Ad-hoc kill scripts not gated (named in the item). selftest_cli 44/44, selftest_model 71/71, new selftest_bridge_gate 6/6.

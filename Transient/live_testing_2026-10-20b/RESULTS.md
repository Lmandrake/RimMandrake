# Wave 3 (374) + post-380 builds — one cold load (FOUNDRY helper, 2026-10-20b)

Authority: owner authorizes game down/up + bridge (CLAUDE.md: holding the bridge is blanket authorization).
Prep: `design/RimMandrake/world_remake_2026-10-19/14_wave3_prep.md` §4. Base: HEAD 24d8a70b6 (== origin/main).

## Status
- [x] 1 bridge take (04:31Z)
- [x] 2 backups (ModsConfig, Cherry Picker, Player.log)
- [x] 3 deploy plans (flat + --compose biomes), assemblies checked
- [x] 4 game down; apply; JawaBench build --gm --apply; stale RUT_FuelSnows removed
- [x] 5 ModsConfig 374 swap (launched 04:42Z)
- [ ] 6 cold load + baseline compare vs Wave 2 load #3
- [ ] 7 live checks (Cauldron rows, Ummisk, Auroral Umbra, acceptance L1)
- [ ] 8 FULL.LATEST (only if clean), release, commit, publish

## Transaction
- `git pull --rebase`: HEAD 24d8a70b6 == origin/main; `src/` clean (only an untracked GSS proof json).
- Game build before launch: `Version.txt` 1.6.4871 rev590, appmanifest buildid 23969874, StateFlags 4, TargetBuildID 0
  — **unchanged** from the Wave 2 load (coordinator flagged a possible Steam update; none on disk). The Steam "Cloud Error"
  label at the 21:37 PDT exit is a Steam connectivity blip (CompleteAppUploadBatch No Connection), not a mod issue.
- Backups: live ModsConfig (380, sha == FULL.LATEST) → `infrastructure/state/modlists/ModsConfig.LIVE_BACKUP_20261020_pre_wave3.xml`;
  Cherry Picker SHIP (== live) → `CherryPicker.SHIP_pre_wave3.xml`; last 380 Player.log → `playerlog_pre_shutdown_380.txt`.
- Committed DLLs vs sources (`dll_source_stamp.py check`): MATCH for Cauldron (rhossak A6 sleep-hold, 8c20f7577),
  TheForge (Ummisk), WeatherSuiteHook (aurora piece, 3056163ac).
- Game killed by PID 15668 (stamped going-down, down).
- Flat deploy (`deploy_apply_all.txt`), all VERIFIED: PawnFlavor `Defs/Founders/Backstories_Founders.xml` (RUT_Jawa_Founder*),
  UtinniPatches 9 (RUT_Umbra, RUT_PropaneRain, RUT_UmbraRename_Aliases, PropaneLakeFauna, ExplosiveGrowth roster, 4 patches)
  and **`Defs/BiomeDefs/RUT_FuelSnows.xml` pruned** (repo-deleted; the game's BiomeDefs folder now holds RUT_Umbra.xml only),
  WeatherSuiteHook.dll, 1 SWBestiary texture. Game-only `UtinniPatches/Defs/IdeoSymbolDefs_placeholder` kept (no --prune).
- `--compose biomes --apply` (`deploy_apply_biomes.txt`) VERIFIED: Cauldron DLL, `RM_Ummisk.xml` (frostbite fix cbcba6fa8),
  TerminalBiomes DonorPorts, Pyrelands/Wasteland defs + 4 committed textures. AB_TinkleGrass stand-ins kept.
- JawaBench `build.py --gm --apply` (`jawabench_apply.txt`): 0 warnings, fire_incident/send_letter in DLL, closure scan clean.
- Gravship S10b files (625d09480: `Gravship_v2_ring_2026-09-12.paint.xml`, `ship_remap_S10b.json`) are design/tool inputs,
  not mod files: nothing to deploy.
- Cherry Picker: `WAVE3_CANDIDATE` byte-identical to SHIP (cmp); `--status` LIVE == SHIP 1,747 (15ba0497): no swap.
- Live ModsConfig = `ModsConfig.FULL.WAVE3_374_2026-10-20.xml`: parsed 374, 0 dupes, sha c54e9e8b equal.
- Companion TEST grant renewed 06:30Z → `2026-10-20T09:30:00Z` (old: `companion_profile_before.json`).

## Cold load (374)
- **READY in 771 s** (380: 806 s), pid 5304 (`launch_receipt.txt`). Game build in the log: RimWorld 1.6.4871 rev591, the
  same string as the Wave 2 log (Version.txt says rev590 in both cases): no Steam update.
- Harvest (`harvest_menu.txt` vs Wave 2 load #3 `harvest_menu3.json`): running **374**, expected-list missing 0 / extra 0,
  retired packageIds loaded: none.
  - Exceptions 3, the same three pre-existing (CannibalPirate / PirateYttakin ConfigErrors, `brtrue`); **ours 0, 0 new
    signatures**. First exception = the same CannibalPirate ConfigErrors line as the 380 load.
  - Xref ours 0; texture misses ours 0; **config errors 13 (380: 14), ours 0**: the Ummisk frostbite error is gone (cbcba6fa8).
  - **Patch failures 3, ours 0** (the three Intimacy GenderWorks removes, pre-existing); none names CameraSecurity /
    WatchTelescope, so the ResearchRetag guards hold with Real FoW gone.
  - Scribe 'Could not load reference' 7 at the menu: the user's custom xenotype files (`Xenotypes/Dark Troll.xtp` etc.)
    naming retired Alpha Genes AG_*; the 380 log has the same 7 (harvest's "7 vs 0 RED" compares against an old baseline).
  - No line names Ummisk, PerpetualAurora, RUT_Umbra, RUT_PropaneRain, RUT_FuelSnows or the founders.
  - The tool's VERDICT reads "FAIL: exceptions 3" exactly as on the 380 load (pre-existing third-party), so the load is
    judged clean by the baseline rule (0 ours, 0 new).
- Def dump `DefDump/captures/2026-10-20T04-52-08Z` (374 mods; the marker was still armed). `selftest_researchretag.py`: only
  the known techprint-gate row FAILs (RG_/VFEI2_). Then `mlie.nwnrealfogofwar` removed from ResearchRetag `forceLoadAfter`
  and deployed (VERIFIED); takes effect next load.
- CAI 5000 settings (read from `Config/Mod_3673768803_CombatAIMod.xml`): `FogOfWar_Enabled=False`,
  `FogOfWar_DisableOnPlayerMap=True`. Code default still UNMEASURED.
- Save census (`def_census.txt`, 374 index): `RM_TestSite_calm_v1_AREAFIX2` 0 unresolved thing defs, 85 other refs / 20 defs
  (== Wave 2): no GravTide/RimTek/Real FoW residue. Canonical start save: 167 unresolved things / 44 defs (the known Wave 1
  pre-edit debt).
- AREAFIX2 loaded in 32 s ("unverified" = the same site-tile mismatch vs calm_v2 as Wave 2: harness).

## Live checks
- `ModsConfig.FULL.LATEST.xml` = the 374 list (load clean by the baseline rule); the 380 copy is `ModsConfig.FULL.PRE_WAVE3_380.xml`.
- **Cauldron rhossak + grove** (`run_live_suite.py Cauldron --chains=rhossak,grove` on AREAFIX2; `cauldron_rhossak.txt`,
  `cauldron_rhossak2.txt`): A1 `rhossak_binds_to_thornwood` PASS, A2 `rhossak_stays_by_its_tree` PASS (both runs);
  **A5 `rhossak_grove_site_ready` PASS, `rhossak_sprouts_while_asleep` PASS, A6 `three_rhossak_root_a_grove` PASS (the
  sleep-hold fix works live), A7 `galled_rhossak_drops_meat` PASS.**
- **A3 `rhossak_bind_off_unbinds` still FAIL, now with the bridge fix live** (typeIdentity `GenTypes(cached)`,
  copiesInAppDomain 1): the Prepatcher-twin HARNESS theory (8c20f7577) is disproved. Split probes (`rhossak_a3_probe*.py/.txt`):
  - a rhossak spawned with the setting already OFF: no bind line at t0 and +300, comp boundTree null — the off path works for it;
  - a rhossak bound while ON, then switched OFF: comp boundTree null at +300, yet `GetInspectString` still says "Bound to
    twisting thornwood"; in probe3 still there after +3000 ticks and 4 reads; in probe2 gone at +2800 (inconsistent).
  - Vanilla `InspectStringPartsFromComps` has no cache (RimSage); Harmony on `Pawn`/`ThingWithComps.GetInspectString` is
    postfixes only (`harmony_Verse.*.json`); "Bound to" exists only at `RM_CompRhossakGrove.cs:239`, which needs the static
    true AND a valid boundTree. Mechanism UNRESOLVED. The false HARNESS comment in `Cauldron/validation.py` was corrected.

## Rollback
380 list = `ModsConfig.LIVE_BACKUP_20261020_pre_wave3.xml` (== FULL.LATEST at start); Cherry Picker unchanged.

## End state

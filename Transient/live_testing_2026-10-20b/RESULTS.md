# Wave 3 (374) + post-380 builds — one cold load (FOUNDRY helper, 2026-10-20b)

Authority: owner authorizes game down/up + bridge (CLAUDE.md: holding the bridge is blanket authorization).
Prep: `design/RimMandrake/world_remake_2026-10-19/14_wave3_prep.md` §4. Base: HEAD 24d8a70b6 (== origin/main).

## Status
- [x] 1 bridge take (04:31Z)
- [x] 2 backups (ModsConfig, Cherry Picker, Player.log)
- [x] 3 deploy plans (flat + --compose biomes), assemblies checked
- [x] 4 game down; apply; JawaBench build --gm --apply; stale RUT_FuelSnows removed
- [x] 5 ModsConfig 374 swap (launched 04:42Z)
- [x] 6 cold load + baseline compare vs Wave 2 load #3 (clean: 0 ours, 0 new)
- [x] 7 live checks (Cauldron rows, Ummisk, Auroral Umbra, acceptance L1)
- [x] 8 FULL.LATEST = 374, release, commit, publish

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

- **Cauldron yield + water** (`cauldron_yield_water.txt`): all 10 rows PASS, incl. the previously UNMEASURED
  `yield_factor_scales`, `yield_toggle_off`, `water_letter_arrives`, `water_letter_cooldown` (e9d3ca356 harness fixes work).
  `CAULDRON_YIELD_LIVE_RERUN_1` verified and closed.
- **Ummisk** (`ummisk_probe.py/.txt`, AREAFIX2 with a painted 6x6 LavaDeep pool): A1 no Ummisk error in the log (L1 pass);
  A2 an ummisk spawned 30 cells away walked to the pool and read on a lava-edge cell 10/10 times over 5000 ticks (pass);
  the edge-spawned one died to a roof collapse caused by the probe's own `destroy_batch` clearing (SITE; `damage_log`).
  A4 `pawn_need` list empty (no Food/Rest), gender None, Cut 500 on `RM_UmmiskDome` -> dead (pass).
  A3 steam puff is a fleck (no state to read): UNMEASURED.
- **Auroral Umbra** (tile 116138 set to RUT_Umbra at -60 C, fresh Settlement map, defenders killed, 3 colonists; night):
  - A2 **FAIL (mod)**: permanent `RM_WS_DarkAurora` is there (and Mod Settings off removes it within 2600 ticks, on restores
    it), but the ground stays **Dark (0%)**: `CurSkyGlow` 0.0 with `perpetualAuroraGlow` 0.35 (`umbra_aurora_a.png`,
    `umbra_aurora_b.png`: night map, faint blue cast only). Mechanism (RimSage): `SkyManager.CurrentSkyTarget` folds every
    GameCondition SkyTarget in with `SkyTarget.LerpDarken` (glow = min), so a condition can only darken; `GlowFloor` never
    brightens anything. Note filed on the item. (The first try on tile 116137 was daytime and then culled as a non-home map.)
  - A3 pass: 40 `weather_roll_next` rolls = Clear 29, RUT_PropaneRain 11, snow 0; under locked propane rain a pool fire grew
    1 -> 18 cells in 2000 ticks (not put out).
  - A4 pass: RM_PropaneShallow on both fresh maps (694 cells on map 1); 0 fires before ignition; snow cells refuse fire.
  - A5 pass: `CANONICAL_ASHKARR_START_2026-09-12` loads (138 s, read only, never saved): RUT_Umbra 2,531 tiles, 0 log lines
    name RUT_FuelSnows; Scribe 'Could not load reference' 6,374 (6,287 ThingDef: the known Wave 1 pre-edit debt).
  - Harness noise: the bridge-made Settlement at tile 116137 had no faction, so the world view logged 1,318 "Error while
    drawing Settlement (tile=116137)" NREs until it was culled (ours to avoid: generate with a non-Settlement parent).
- **Acceptance L1** (`acceptance_list.txt`, 109 L1 items): `NONSW_XENOTYPES_SCOPE_1` A1-A4 pass (KAR_Orc CUT live; dump
  AFTER the patch, 0 refs on 219 xenotypeSets; no red error names the 11; `validate_patch` on the 374 list 0 errors) — item
  validated and moved to closed. Its selftest's SHIP row still fails on BX_Beliar/DV_Avaloi/DV_Brawnum/DV_Buzzer/HBX_Highborn,
  whose mods Wave 2 retired: a stale expectation in `selftest_xenotype_cut_nonsw.py`, not the patch.
- Session log delta (`playerlog_session_delta.txt`): apart from the Settlement-draw harness noise, the AREAFIX2 load's
  pre-existing SaveableFromNode classes and the pre-existing InputLegacyModule line; 0 exceptions from our mods' runtime.

## Rollback
380 list = `ModsConfig.LIVE_BACKUP_20261020_pre_wave3.xml` (== FULL.LATEST at start); Cherry Picker unchanged.

## End state
Game UP on the 374 list, main menu, healthy (canonical save never saved). Cherry Picker 1,747. FULL.LATEST = 374.
Bridge released. Companion TEST grant expires 2026-10-20T09:30Z. Pointers:
- `RHOSSAK_MIGRATE_ROOTS_TAKE_HOLD` — A1 A2 A5 A6 A7 pass, A3 FAIL with the bridge fix live; NEXT: log, from inside `CompInspectStringExtra`, the static and boundTree it sees for a rhossak bound-then-switched-off (the comp tick reads null, the pane still says Bound).
- `AURORAL_UMBRA_RENAME_BACK_TO_DARK` — A3 A4 A5 pass, A2 FAIL (LerpDarken); NEXT: light the Umbra through a non-darkening sky route (CurrentSkyTarget postfix gated on the permanent condition, or CompAffectsSky lerpDarken=false) and re-run A2.
- `FORGE_SNAILHOLE_FILL_EMPTY_SHELL_LEFT_BEHIND` — A1 A2 A4 L1 pass, A3 UNMEASURED; NEXT: watch the steam puff with the owner (or add a fleck counter) and toggle "Ummisk steam cushion".
- `NONSW_XENOTYPES_SCOPE_1` selftest — SHIP row stale after Wave 2; NEXT: make `selftest_xenotype_cut_nonsw.py` require SHIP keys only for CUT_DEF names present in the live dump.
- ResearchRetag `forceLoadAfter` minus Real FoW is deployed; NEXT: at the next cold load, confirm ResearchRetag `retag_rows_vs_dump` 5/5 on a map.

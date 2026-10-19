# Retirement Wave 1 — deployment transaction and cold load (FOUNDRY, 2026-10-19)

Authority: owner by card 2026-10-19, "Yes, and also deploy the 39-mod retirement"; ruling 2026-10-10.

## Transaction
- Dependency closure (`closure.py` -> `closure.json`): 0 retained active mods hard-depend (About.xml
  modDependencies, incl. v1.6 by-version) on any of the 39. 13 loadAfter edges only (order, not a stop).
  5 hard edges are inside the wave (FancyRats+, VSR/Alpha Skills -> VSE, AURVL -> AURAD, Sandworm -> ChezhouLib).
  Kept because dependent: none.
- Pyrinth swap: `mandrake.rm.pyrinth` replaces `det.epochspyrinth` at the donor's list position (already deployed, in sync).
  Every DV_ name our src uses that is not in rm.pyrinth belongs to retained Det mods (Keshig/Buzzer/Avaloi...).
  Lantern Deeps guards re-pointed (scatter `MayRequireAnyOf`, gate FindMod both names, loadAfter) — f037c9a37.
- Removed list: `wave1_removed_39.txt`. New list 536 - 39 + 1 = 498: `ModsConfig.FULL.WAVE1_498_2026-10-19.xml`
  (= `infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`). World-generation mods kept (Alien Worlds +
  Tidally Locked, Deep Orbit, My Little Planet, Sensible Factions).
- Cherry Picker: SHIP minus the 140 wave keys (`cp_wave1_keys_140.txt`) = 2,329 keys, swapped live.
  Live had 2,134; every live-only key was a wave or retired-donor def (0 surviving defs un-cut).
- Deploys: composed Baroque Biomes (97 files, committed changes incl. the guards), UtinniPatches (2 XML: stale
  RUT_TheForge still named the dropped RM_TinkleGrass).

## Cold load (498)
- READY in 962 s (`launch_receipt.txt`). Running mods 498, none of the 39 (`running_mods_menu.json`).
- Menu log: 5 exception events, all pre-existing on the 536 list (CannibalPirate/PirateYttakin ConfigErrors,
  '-1§Vanilla', Sandstone dup key, brtrue) — first: `Exception in ConfigErrors() of CannibalPirate`.
  Ours 0. Texture misses ours 0. Xref 1: `RM_TinkleGrass` (stale UtinniPatches game copy; fixed by deploy,
  takes effect next start). Config errors 21 (ours 0), patch failures 4 (ours 0) — same as the 536 baseline.
- Save: `RM_TestSite_calm_v1_AREAFIX2` after `save_class_census` (0 fatal) and `save_def_census` (0 thing defs).
  Loaded in 40 s; 13 load exceptions, all classes seen on the 536 list (abstract-component skips, Worldbuilder
  cross-ref NRE, SurfaceLayer FastTileFinder NRE, RimFridge LoadedGame NRE). VEF new-faction dialogs closed.
- 10,228 ticks at speed: 0 exceptions; spam is the pre-existing Beer/Intimacy warnings (6,185 Beer lines in the
  536 run). No error storm.

## Rollback
`ModsConfig.LIVE_BACKUP_20261019_pre_wave1.xml` (536) and `ModsConfig.FULL.PRE_WAVE1.xml` (old FULL.LATEST, 542 —
stale); Cherry Picker `CherryPicker.PRESWAP.20261019_153159.xml`. Not used.

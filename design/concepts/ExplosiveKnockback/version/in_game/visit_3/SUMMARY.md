# ExplosiveKnockback 0.2.0: in-game acceptance, visit 3

Detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_VISIT_THREE, 2026-11-26 05:11 to 06:30 PST, on
ArchBig, tier explosiveknockback_visit (26 mods, all five DLC). Builds: the committed release DLL for the nine `scene.py accept`
checks (identities `ident_release.json`, `ident_release2.json`); a proof build of 9931b028e1 (RmProofs=true, built to
`D:\ClaudeWork\rimmandrake\build\EK_v3_proof`) for sc_save_in_air, sc_walk_frames and the walk save (`ident_proof.json`).
The release DLL is deployed on ArchBig at the end. Drivers: `scripts/` (copied from visit 2; `walk_save.py` now labels each
station through `look_changed_labels`).

## Result

16 of 16 checks that the change since visit 2 touches read PASS in their last row [measured]:
- 5 runner checks (sc_pawn_arc, sc_open_storage, sc_cauldron_gas, sc_pit_fetch, sc_killed_thrown) PASS on Steve1 at the
  current mod source 0b0a0511e0 (testq rows already in `rows.jsonl` when this visit opened; `rerun_relation.py` counts them).
- 9 scene checks on the release DLL, ArchBig: sc_lookup_sources, sc_pawn_arc_carried_thing, sc_pawn_arc_bruise_sizes (after
  a check repair), sc_pawn_land_on_pawn_sizes, sc_pawn_arc_sandbag_no_contact, sc_storeroom_mortar_rebound_legs,
  sc_settings_sweep_show_switches, sc_blast_show, sc_gas_chain_pawn_on_cover.
- sc_save_in_air (5 of 5 claims) and sc_walk_frames (mod-on p99 21.9 ms against mod-off 22.5 ms, 21 arms each) on the proof
  build, AridShrubland quicktest.
The other 49 stage-6 checks keep their PASS from visit 2 (untouched by the change).

## What failed and what was done

- **sc_pawn_arc_bruise_sizes run 1**: V_HEDIFF small read None. The squirrel took 6.68 from the thrown colonist and died (its
  corpse is in the scene's `small_after.png`), and a dead pawn no longer reads through its alias. The scene's docstring allows
  the death, and V_SMALL already counted a dead squirrel. Class HARNESS (the check was wrong, not the mod). Repaired at
  9931b028e1: V_HEDIFF counts a corpse of the lane's kind in the lane together with the journal's bruise, and V_SMALL now needs
  that corpse (it had read "unreadable" as "dead"). Planted `--plant no_bruise`: FAIL, 6 rows
  (`evidence/sc_pawn_arc_bruise_sizes_plant_no_bruise.txt`). Real build: PASS 12 of 12. In this run the squirrel survived, so
  the new corpse branch was not exercised live [measured]. `maturation.py red-seen` is not the record for this check:
  the judge certificate reads offline deciders only, and red-seen cannot run an accept check (next item). The planted
  reading is on the row's `repair` field.
- **Pipeline defect fixed, test first** (RIMMANDRAKE_REFUSE_RED_SEEN_ON_SCENE_ACCEPT_TREE_NOT_CLEAN_READS_RED, a34984d90c):
  `scene.py accept` exits 0 on a scene that prints FAIL, and refuses a tree that differs from its commit (exit 3). So
  `maturation.py red-seen` would have recorded any planted fault on a scene check as red without running the scene.
  red-seen now refuses an accept command and names the `--plant` route. selftest_red_seen: red on the parent (a false red
  was recorded), 19/19 green after; selftest_red_seen_owner and selftest_asks_on_empty_game green.
- **sc_gas_chain_pawn_on_cover**: refused WRONG_BUILD twice before it ran (COULD NOT LOOK rows). The first refusal was
  FlowWorks, whose committed DLL moved on origin/main (d319937af5); I redeployed FlowWorks. The second was the proof DLL,
  because accept runs only on the committed release. After the release DLL was redeployed and the game restarted: PASS 11
  of 11.

## The owed cases

- **RIMMANDRAKE_REPAIR_KNOCKBACK_JOLT_CHECK_LOCAL_WILD**: sc_killed_thrown PASS on the current source (Steve1 row);
  sc_storeroom_mortar is untouched since visit 2's PASS on the fixed build.
- **C# plants** (PF_PROOF_ADDEXT_DROPS_CHAIN, PF_PROOF_RUNRESTORE_NOOP, PF_PROOF_PLACEFAULT_IGNORED,
  PF_LANDING_BRUISE_SWAPPED, PF_HOOK_BLAST_POWER_DROPPED) and **PF_RUNNER_GATE_REMOVED**: read in visit 2
  (`../visit_2/planted_rows.jsonl`, `../visit_2/SUMMARY.md`). The files they plant into (the mod's C# and the runner)
  are unchanged since then, except RM_KnockbackProof.cs's staging, and that staging change touches none of the planted
  lines. Visit 2's readings, with each "would have", stand: the restore pair was seen (settings leak FAILs).
  PLACEFAULT_IGNORED was not seen live (T_PROOFGATE S1 catches it offline). BLAST_POWER_DROPPED and
  LANDING_BRUISE_SWAPPED were seen after visit 2's check repairs. RUNNER_GATE_REMOVED was red ("Type not found"), never
  a false pass.
- **PF_SCENE_* plants** (20): one by one in visit 2 (`../visit_2/planted_scene_rows.jsonl`, each with its `would_have`).
  This visit changed one of the scene files, scene_pawn_arc_bruise_sizes.py. Its two plant lines (L98 journal mark, L173
  tick filter) are unchanged, and visit 2 saw both: the deciding line read FAIL. The others' files are unchanged.
- **PF_SELFTEST_* plants** (proofgate L57, L36; restore L55): they plant into offline test files that no in-game check
  runs, so no in-game check could see them (visit 2).
- **Lane 1 not_kernel rows** (35): each names a scene whose last row reads PASS, either in this visit (touched checks) or
  in visit 2 (untouched).
- **unrun.jsonl map_agreement**: PASS in visit 2 on a fresh case export (125 of 125); `maturation.py next` reads unrun_run
  as passing.

## The walk save

`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_V020_VISIT3_WALK_20261126.rws`
(ArchBig). Staged on the proof build, tier explosiveknockback_visit, fresh AridShrubland quicktest: 16 stations, each AFTER
at z 12 with its START twin at z 42. Every sign carries "[NEW SINCE YOUR LAST LOOK]", because no earlier look is recorded
(`look_cells/EK_V020_VISIT3_WALK_20261126.json`). `walk_twins.py check`: ok, 32 signs, 16 aftermath, each with its START
twin. All 16 station verdicts PASS. The save then loaded on the release DLL (the walk build) with no error line after its
load line [measured, 06:08]. The Saves folder was backed up first to `D:\ClaudeWork\backups\archbig_saves_20261126_ek_v3`.
Captures `screenshots/walk_g1..4_after.jpg` and `walk_g1..4_start.jpg` were looked at; so was a sheet of the blast show
(`screenshots/blast_show_sheet.jpg`).

## Beyond the checks

`strange.jsonl`: 10 rows, all explained, 0 open. They cover the dead squirrel (check repaired) and the advisory judge's
COULD NOT LOOK on carried_thing. They cover the accept/red-seen defect (fixed) and the two WRONG_BUILD refusals. They also
cover the open_storage floor control, the gas lane's walk before the shove, the soot-watcher Muffalo (RSW look)
crossing the he_tile frames, and the game-build reading rev590 against rev591.

The blast show's art-judge keep: the scene's program rows decide its eight parts (PASS). This visit ran no art judge on
its captures, because the brief starts no helpers. The textures were judged on 2026-11-24
(`version/art/blast_show_art_verdict_2026-11-24.json`), and the show's source is unchanged since visit 2.

## Exit

```
ingame_rows: {sc_pawn_arc: pass, sc_open_storage: pass, sc_cauldron_gas: pass, sc_pit_fetch: pass, sc_killed_thrown: pass, sc_pawn_arc_carried_thing: pass, sc_pawn_arc_bruise_sizes: pass, sc_pawn_land_on_pawn_sizes: pass, sc_lookup_sources: pass, sc_pawn_arc_sandbag_no_contact: pass, sc_gas_chain_pawn_on_cover: pass, sc_storeroom_mortar_rebound_legs: pass, sc_blast_show: pass, sc_settings_sweep_show_switches: pass, sc_save_in_air: pass, sc_walk_frames: pass}
strange_open: 0
savegame: C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves\EK_V020_VISIT3_WALK_20261126.rws
exit_met: true
```

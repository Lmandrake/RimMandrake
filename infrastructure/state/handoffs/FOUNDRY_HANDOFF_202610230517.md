# FOUNDRY_HANDOFF_202610230517 — READ FIRST on wake

Follows `FOUNDRY_HANDOFF_202610230308`. Everything below is committed and pushed unless a line says otherwise.

## The one thing to carry forward

The RimPulse fixes are built and published but NOT LIVE: the daemon (rm-pulse.service) still runs pulse.py from /home/mandrake/rm/bench, so the owner's widget still shows the old pills. Until `RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE` lands, nothing he sees has changed. His order (2026-10-22): "Prioritize RimPulse, then anything to support the mods we're pushing to complete. Keep the subagents full [cap: reduced to 2 by him]. If you truly run out, then dirty code review and additional backlog." Order ends when he next writes; he is handing off to another account. (filed: lessons)

## What the owner should see

- Scald: it was never at arc 0-30; his own 2026-08-16 ruling put it at ~35 deg and the tiles are there. He confirmed: leave tiles, fix sheet + temperature. Sheet fixed (c27b0ba5c); the 7.8 C temperature stamp is `world/repaint_2026-10-21/scald_temperature.csv`, applied only at the final repaint.
- Cards answered 2026-10-22: Scald (leave, fix), VEE leftovers (port all to our own mod), RimPulse surface (keep widget, fix defects only), Deadlife vents (drop). All recorded on the ledger and closed.
- RimPulse red pills ('BENCH 19:40', 'RIMPULSE 19:11') were REAL OOM kills: rm-pulse at its old 256M cap (now 768M) and a ~4 GB python in the BENCH tool cgroup (not page cache). Fixed in code, not live (above).
- The Windows widget has never been looked at since the fixes; headless browser cannot run in WSL (lesson filed).

## What is half-done, and where it stops

- `RIMPULSE_DEPLOY_FIX_RUNS_THE_BENCH_CLONE` — proposed, top priority; NEXT: point rm-pulse.service and the digest/health units at a dedicated origin/main checkout (never edit the BENCH working tree), restart, then `curl -s http://127.0.0.1:8765/api/now` and a Windows screenshot, and `rimflow verify` the owed checks on the six built RimPulse items.
- `RIMPULSE_DIGEST_REBUILD_THREE_QUESTIONS` — proposed; NEXT: claim after the deploy is live, then LOOKS_BUILD_UNREAD_NEVER_LISTED, ALERTS_FIX_TELEMETRY_CRIES_WOLF, STATE_FIX_TWO_WRITERS_ONE_FILE, FAILURES_BUILD_ONLY_THE_STUCK in that order.
- `RIMPULSE_*` dirty code — pulse_core.py, pulse.py, widget/index.html, selftest_pulse.py are DIRTY; NEXT: a second genuine full-file review each, mark-clean only if it finds nothing.
- `VEE_FLORA_VENTS_BUILD_XML_FIRST` — released, prep note on item; NEXT: create src/RimMandrake/TileFeatures (mandrake.rm.tilefeatures) and port flora, weather, vent defs (Deadlife dropped); VEE source XML is workshop folder 3656316229.
- `VEE_LANDFORMS_BUILD_CRATERS_AND_COMPANY` — not started; NEXT: claim after TileFeatures exists, biggest landforms first (Cenotes, SaltPlains, DryRiver).
- `VEE_LANDMARKS_MIGRATE_KEEP_THE_ICONS` — not started; NEXT: re-point LandmarkIcons.xml to the new RM_ landmark defs.
- `VEE_WORLD_RENAME_ONE_STAMP_AT_END` and `VEE_MOD_RETIRE_LAST_ONE_OUT` — proposed; NEXT: wait for all VEE ports, then need bridge / game up.
- Built offline, live checks owed (one bridge sitting, BENCH holds the bridge): `DEEP_DRILL_HOME_BIOME_1`, `SCALD_MECHANICS_1`, `EXPLOSIVE_PLANT_GROWTH_1`, VEE solar and ore ports (be3f91198, 2ad92f40e); NEXT: sweep with `rimflow next --acceptance --seat FOUNDRY` when the bridge is free.
- `PYRELANDS_SHIP_READINESS_1` — doing, helper stopped at launch (owner cut cap to 2), nothing changed; NEXT: claim and do the offline review/art/settings remainder.
- `DIRTY_CODE_REVIEW_STANDING_LOOP_1` — no dirty .cs/.py left; 107 XML DIRTY by design; NEXT: only if the queue runs dry.
- Order not saved by earlier handoff pointers: `GPT_REVIEW_BIOMESCOMPOSITE_UNTRIAGED_1`, `NEXT_BRIDGE_SITTING_ALL_LIVE_CRITERIA_OWED`, `WORLD_REMAKE_TILE_PICKS`, `GREENTIDE_ANTS_NAME_ART_SOUNDS` are not in the ledger; NEXT: re-read the 2026-10-23 handoff fb15b7d04 and file or close each.

## Traps learned

- A pill showing only a seat and time hides the cause; the cause was in a clipped row (filed: RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE).
- `pulse.py metrics` reads only the last 8 MB so it says "no acks yet" (filed: lesson, RIMPULSE_METRICS_FIX_253MB_OF_ECHOES).
- A `git add` can vanish from the shared clone's index before the commit: put paths on the commit itself (filed: lesson 2026-10-23).
- `rimflow close --sha` of a commit that `./publish` later rebases names a dead hash; close only after publishing (filed: lesson).
- A biome sheet's stated place can be a copy error, measure the tiles first (filed: lesson 20261023T043948Z).
- Hook refuses committing the ledger shard together with other paths; commit the shard alone. (filed: lessons)

## Commits

```
ce8a4bda5 Ledger + code-review shards at BENCH wrap-up
fca025bc6 reel_intake_geometry: inner loop no longer shadows the rotation k; 2-space block re-indented, unused enumerates dropped; output unchanged (--check OK)
41e1a6f8f pipe_levelling_perf_proof: LAYOUT doc said both reels are built West; rig_ops faces each at its lip (West, East)
ccaa90ba1 HoseProbe: RelayEnd's Round-7 summary back on RelayEnd (WallCrossJson had two, RelayEnd none); HoseWallSeamChecks S4 header said west-facing reels, the sweep rolls every facing. Comment-only; FlowWorks SelfTest 840/840, hose 182/182 + 403/403; DLL rebuilt (HOSEPROBE_SUMMARY_FIX_WANDERED_OFF)
9250d9f1c Ladder art source: gen_a8 rebuilds A7's north itself (it read OUTDIR/optA7_north.png, failing unless gen_a7 ran first; output byte-identical, = installed art); dead sh_n / THICK=5 / duplicate cx removed. Ledger shard carries two filed review items plus peers' pending events.
542a7899e Code review: 40 files changed tonight marked clean (full or diff-scoped); progress in review_tonight.md
8f836efb6 Review fixes: proof_hose HW1 reads an unanswered census as HARNESS, not 'no laid hose' SITE; Rites validation no longer claims set_setting refuses static fields (BRIDGE_STATIC_SETTINGS_FIELDS_1 fixed that)
4426b0715 Review fixes: DeepDrill validation drops unused REPO; DivingInteraction validation docstring/toggle-count comment were stale, temperature check no longer TypeErrors on a missing hatch row
1e65643aa Transient: pin review_tonight.md (code review progress skeleton)
ce8c095ce selftest_tank_art_edges: measure Modern tall/IBC/XTall body under the hose fittings (TANK_FLANGE_FIX_HOVERS_MID_PIPE) Fittings reach the canvas edge and bury the wall; the outline comes from modern_port_fittings' base, pinned pixel-equal to the installed PNG. Table unchanged (0 insets were the fittings, not the tank), so no DLL rebuild.
ae1da74c4 Ledger: VEE_FLORA_VENTS_BUILD_XML_FIRST prep note, lease released
ef02a5ba1 Ledger: note RimPulse L1 checks wait on the deploy item
f35ddc1d7 Ledger: six RimPulse defect items implemented
490c8ccee RimPulse review fixes: a recovered occurrence stays recovered when its window later closes; digest lists recovered incidents; services light
bc123a9e3 Ledger: VEE_DEEP_ORES_MIGRATE_RICH_AND_POOR built
6b37f4270 lesson: staged new files can vanish from a shared clone's index
ca5da3784 Settings screens selftest: register SolarMirrors' new 'Solar panels' group (scope Now: read every power tick)
be3f91198 DeepDrill: DLL built from committed source (tile resource ports)
df5bc20e2 DeepDrill: port VEE deep-ore rich/devoid, mineral devoid, spacer component deposits (RM_ mutators)
5e87aea8d Ledger: hose snapshot built, fitting gate done, 3 art findings filed
... 79 more: git log --oneline fb15b7d04..HEAD
```

## Tree state at wrap

- upstream: origin/main, pushed

Uncommitted (replace each marker below with whose it is — yours, another agent's, generated):

```
?? Transient/fw_scenes/live/S1_20261017T084726.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_20261017T084802.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_20261017T092155.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_20261017T110253.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_p00.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_p03.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_p10.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S1_p14.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_20261017T084824.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_20261017T092355.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_20261017T110404.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_p00.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_p10.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_p30.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S2_p60.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S3A_p20.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S3B_p06.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S3B_p16.png   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S3_20261017T084854.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
?? Transient/fw_scenes/live/S3_20261017T084938.txt   pre-crash FlowWorks scene capture 2026-10-17 (Transient, unpinned, not mine)
... 167 more uncommitted paths (by top-level dir: Transient 167): git status --short
```


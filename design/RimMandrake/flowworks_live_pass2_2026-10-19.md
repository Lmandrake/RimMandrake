# FlowWorks live pass 2: re-run only what changed (BENCH helper, 2026-10-19)

Runs AFTER the current driver finishes (it is on `flowworks_hugethings`, then does the world-map repair on FULL).
Pattern and gates: `design/RimMandrake/flowworks_session_runbook_2026-10-18.md` (section letters below refer to it).
Written OFFLINE 2026-10-19 00:40 PDT; every flag below was checked by `--help`, `--dry-run` or `--mock` as noted.
Repo-relative paths are under `/home/mandrake/rm/bench`. **M** = measured, **E** = estimated.
Plain `python3` = WSL (offline/plan); `python.exe` = Windows (anything touching the bridge), run from the repo root.

## 0. What pass 2 covers (and why it is not a full re-run)

| script / rows | why re-run | fixed at |
|---|---|---|
| `live_session.py` B4: `B4_cover_120`, `B4_cover_220` (UNMEASURED), `B4_cover_40` (rode with them), `B4_grenade_no_blast_cover` (FAIL), `B4_access_rescue_ladder_queued` (FAIL), `B4_dehydration_rate` (FAIL), `B4_reservoir_fish_rolled` / `_catch` / `B4_access_jump_pack_in_no_fall` / `B4_rail_unrailed_control` / `B4_dig_cost_notch16` (UNMEASURED) | covers read "gave way" off the cover, not ProofClimb's deck-blind depth (ledger `PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON`); the other B4 rows come free with the block (B4 is one shared clock, not row-selectable) | `58e64eb436` (script) |
| `proof_hose.py` realflow block: `NS_hose_carries_real_units`, `NS_hose_far_end_pump`, `NS_relay_chain_carries`, `NS_tank_feeds_hose`, `NS_tank_does_not_bridge_pipe_runs`, `NS_external_pipe_is_visual_only` | hose first fill counted, source tank set Empty (`HOSE_REALFLOW_DIAGNOSE_SHORT_POUR_DRY_TANK`); V tank moved inside the plot, unbuilt tank reads UNMEASURED SITE | `f93867b198`, `e27fbb60d5` (script) |
| `live_session.py` B1 `validation_v2`: `S3_classification`, `P3f_forced_entry_falls`, `P4f_ladder_frees_forced` (FAIL) | all HARNESS (`FLOWWORKS_V2_DIAGNOSE_THREE_NEW_REDS`): W4 is a 40-cell EDGE body, limitless by the wetness-cut ruling (`392300ef0d`); ProofForcedFlyer launched an unstunned PawnFlyer = a jump, which lands safely by `pitJumpLandsSafe` (`0bed9b5796`). Proof now throws `PawnFlyer_Stun` (needs the new DLL deployed) | `3665fb781b` (DLL + script) |
| `live_session.py` B7 `B7_reload_A2/A3/save_reload_pockets_iden` (FAIL, `pocket_covers`) | UNTRACED: the run kept no strings. B7 now records before/after/settled per differing key (`RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS`); re-run for evidence, ~8 s, needs B4's covers zone | `3665fb781b` (script) |
| `liquid_checks.py` `L5_colonists_clean_spill` (UNMEASURED SITE) | HARNESS: precondition wanted Cleaning priority read back 1; vanilla stores 3 with manual priorities off (filth 9 -> 0 in 750 ticks was read UNMEASURED) | `3665fb781b` (script) |
| `live_session.py` B4 `B4_access_jump_pack_in_no_fall` (UNMEASURED) | HARNESS: the verb list was read at the reply's top level; it sits under `result` (JawaBenchAbilityTools). Now cast by verb id | `3665fb781b` (script) |
| `climb_proof.py` `CLIMB_raider_never_crosses_ramped_moat`, `CLIMB_hauler_fetches_ramped_floor` (were OWED "needs ramps") | ramps exist (`RM_PitRamp`, `CLIMB_ramp_frees_and_retraps` PASS in pass 1): scene F = a 3x3 island in a sheer D 4 moat ramped out on its far side, a hostile Pirate on each, `jawa/flowworks_pit_report` canReachMapEdge (the moat raider is the can-say-True control); scene G = a sheer D 4 pit, 10 Jade on its floor, a Hauling-only colonist + Jade-only stockpile: 600 ticks sealed, then a ramp, up to 3000 ticks to the stockpile. Ledger `CLIMB_RAMP_ROWS_BUILD_STAIRS_ARRIVED_EARLY` | HARNESS rows, this commit |
| `live_session.py` B2 `B2_readout_sea_never_dry` (UNMEASURED SITE) | the painted lake was mid-map, so LIMITED by design; the readout zone now sits flush with the east map edge (`(228,15,22,16)` on 250x250, clear of the 216-wide owner zone) and the lake is painted to column W-1, read back; `stickyLimitlessEnabled` off or paint short of the edge reads UNMEASURED SITE, an edge lake reading limited is FAIL MOD | this commit |
| `live_session.py` B5 `B5_ice_freeze_thaw` (UNMEASURED SITE, 1.4 C) | vanilla `FreezeManager` freezes no water above -7 C, and ColdSnap is only -20 C. Now ColdSnap + DeepFreeze (both `GameCondition_ColdSnap`, summed by `AggregateTemperatureOffset`: -40 C at full after the 12,000-tick ramp), four canals (56 squares), up to 24,000 ticks; the row is judged only once the canal read <= -7 C, and "no ice" is FAIL only when >= 4.6 freeze rolls were expected (P(no ice) < 1 %) | this commit |
| `live_session.py` B6 `B6_flood_canal_kept` (UNMEASURED SITE) | `SeasonalFlood` seeds only at river banks and spreads <= 12 squares from them (nothing on a riverless map). Now `jawa/weather_set TorrentialRain lockWeather` (Odyssey): `TorrentialRainFlood` seeds from every unroofed freshwater body's bank squares, the dug canal included, after its 4,000-tick start delay; then back to B0's locked Clear (OnWeatherEnd destroys the flood), recession polled | this commit |
| `suspension_bridge_proof.py`, whole file (all sections) | first real run 12 PASS / 12 FAIL / 10 UNMEASURED (`Transient/suspension_live/suspension_bridge_proof_20261019c.json`) ran on DLL `23979d509b` (lacks `a01c76fe25` underpass reach) and defs without `CompProperties_Styleable`. Ledger `SUSPENSION_LIVE_DIAGNOSE_FIRST_REAL_RUN`, `UNDERPASS_REACH_VERIFY_WALK_UNDER_FOR_REAL` | `d99eab7349` defs + harness; DLL `a01c76fe25` and later |

**Leftovers from the newest full run** (`Transient/live_session/20261018T233414/session.json`, 179 rows: 121 PASS / 19 FAIL / 38 UNMEASURED,
total_s 1165.6 M). Re-read the newest `session.json` under `Transient/live_session/` when pass 2 starts; the current driver may have
written a later one. Not in pass 2 on purpose (need a decision, not a re-run):
- B2 `B2_dialog_*` FAIL (dialog empty below Reset all): `FLOWWORKS_SETTINGS_MEND_EMPTY_BELOW_RESET`, landed `4285565110`; re-check needs the deployed DLL (step 1 here) and one dialog look, add to optional step 6b.
- B3 triaged 2026-10-19 (`Transient/pass1_reds/NOTES.md`); `rc 1` is only "not green", never a crash. Left out because a re-run repeats them:
  `sprinkler_live` draws/dries/walls UNMEASURED SITE (the soak read is `ExplosiveGrowthAPI.IsSoaked`; ExplosiveGrowth is not in the `flowworks`
  tier: run on `fw_gss_sitting`); `liquid_checks` L4 SITE (no gravship fixture), L6 goodwill needs `--theft-day` (~60,000 ticks);
  `thirst_live` T1 needs three mod lists; `trench_cover_proof` UNMEASURED rows are OWED by the script itself; climb's two ramp rows,
  B2 sea, B5 ice and B6 flood are fixed and re-run as F4/F5 below.
- B9 owner-eyes rows (`B9_staged_*`) are UNMEASURED by design. Thirst T15/T16/T27 need the Biomes tier (`fw_gss_sitting`), not this pass.

## 1. Preconditions (offline checks, recorded now)

1. **DLL source stamp: run `python3 src/RimMandrake/Utils/dll_source_stamp.py check` right before deploying** (it hashes COMMITTED
   blobs, so a dirty worktree does not matter). FlowWorks DLLs keep landing (the deck-over-pawns fix, the PawnFlyer_Stun proof), so
   this doc cites no stamp sha. If it prints anything but `MATCH src/RimMandrake/FlowWorks/Assemblies/RimMandrakeFlowWorks.dll`
   (someone committed Source without a rebuild), rebuild from a clean HEAD export
   (UNTESTED, plan only; winbuild stages from the clone it is run in and `--dry-run` shows the staging):
   ```
   rm -rf /home/mandrake/.seat-tmp/BENCH/headexport; mkdir -p /home/mandrake/.seat-tmp/BENCH/headexport
   git -C /home/mandrake/rm/bench archive HEAD src | tar -x -C /home/mandrake/.seat-tmp/BENCH/headexport
   cd /home/mandrake/.seat-tmp/BENCH/headexport && python3 src/RimMandrake/Utils/winbuild.py FlowWorks --dry-run
   cd /home/mandrake/.seat-tmp/BENCH/headexport && python3 src/RimMandrake/Utils/winbuild.py FlowWorks
   ```
   then copy `Assemblies/RimMandrakeFlowWorks.dll` + `.srchash` back, `dll_source_stamp.py check` must say MATCH, commit both by path, push.
2. **Deploy plan for FlowWorks, recorded 2026-10-19 00:40 (plan only, nothing written):** 142 files HELD (`src/DEPLOY_HOLD.txt`, left as-is);
   `MayRequire: rewrote 5 folded-id/name guard(s) in 2 file(s) of FlowWorks (deployed copy only)`; drift =
   4 added `Textures/StandIn/Things/Item/Chunk/ChunkStone/RockLow{A,B,C,D}.png`, 4 changed `Assemblies/RimMandrakeFlowWorks.dll`,
   `Assemblies/RimMandrakeFlowWorks.dll.srchash`, `Defs/Canals/ThingDefs/FlowWorks_MapControls.xml`, `Defs/Pits/ThingDefs/RM_SuspensionBridges.xml`
   ("Drift found. Re-run with --apply"). `RM_SuspensionBridges.xml` carries the Styleable comp, so the deploy is REQUIRED for the suspension LOOK rows.
   The DLL is a game-CLOSED write. If the current driver already applied FlowWorks (check the plan again), the plan reads "no drift": skip step 2.
3. Bridge: `python3 src/RimMandrake/rimflow/cli.py bridge who` must say free (the current driver releases it). Game must be DOWN for steps 2-3.

## 2. Ordered commands

### A. Take the game (runbook A)
```
python3 src/RimMandrake/rimflow/cli.py bridge who
python3 src/RimMandrake/rimflow/cli.py bridge take --for "FlowWorks live pass 2 (changed rows only)"
./game                                                    # must say DOWN (the driver's FULL-list repair may have left it up: STOP, owner/driver closes it)
./game --why "BENCH pass 2 deploying" deploying
```
### B. Deploy (game DOWN)
```
python3 src/RimMandrake/Utils/dll_source_stamp.py check | grep -i flowworks      # MATCH, else rebuild (1.1)
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks               # expect the 8 drift lines above
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply
python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks               # must now say no drift (held lines are fine)
```
Do NOT apply HugeThings / UtinniPatches / companion here (pass 1 owns them; `jawa/fishing` needs the companion, so `B4_reservoir_catch` stays UNMEASURED unless the driver deployed it: check `bridgetools/build.py --gm` plan, apply only if it differs AND the game is down).
### C. Tier `flowworks` (11 mods; NOT `modlist_swap --minimal`)
```
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks
python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply          # backs up the live list (md5) and records the restore marker
python3 src/RimMandrake/Utils/modlist_swap.py --status
```
`--status` should show LIVE = the tier; FULL md5 `a40bedf57526453008d2269039f9f1cd` unchanged (if the world-map repair re-captured FULL, use the md5 the status prints for FULL and record it).
### D. Launch and gate (runbook D, 2.L)
```
powershell.exe -NoProfile -Command "Start-Process 'steam://rungameid/294100'"
./game --why "BENCH launch flowworks tier pass 2" loading
```
Wait for `Bridge token:` in Player.log newer than the launch (M 44-70 s cold load, 11 mods). Then the first-exception gate:
`grep -n -m3 -E "Exception|Error while|Could not|Resetting mods config" "/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"`
(stop on a FlowWorks exception, `Resetting mods config`, or an unresolved cross-reference naming our mods); `./game --why "tier loaded" up`.
Copy Player.log to `Transient/live_session/pass2_<stamp>/Player.log.copy`.
### E. Preflight and a map
```
python3 src/RimMandrake/Utils/preflight_bridge.py --tier quicktest --modset flowworks --purpose test --live --all --no-archive
python3 src/RimMandrake/Utils/modcheck/test_site_saves.py load calm                # or rimworld/start_debug_game_ready (fresh Playing quicktest map)
```
Expect O09/O13 (companion / FlowWorks drift) clear after step B. O10 (`0Harmony.dll` changed) may still need a human `--accept-deps`.
### F. The re-runs (F1-F5) (one map each where noted; all on the SAME launch)
**F1. live_session B1 + B4 + B7 (v2 re-check, pit covers + the shared-clock rows, reload evidence).** `--only` makes it a PARTIAL run, never recordable as a full pass: the verify lines it
writes are for reading, and the ledger `verify` for `SUSPENSION_BASE_REWIRE_COVERS_STEP_OUT` (cover rows) is what this discharges.
Flag check, run 2026-10-19: `python3 src/RimMandrake/FlowWorks/northstar/live_session.py --dry-run --only B0,B1,B4,B7` rc 0, prints the zone
table, `B1   validation_v2 --live --current-map ~14000 ticks ~ 280 s`, `B4   shared clock: ... ~ 8500 ticks ~ 178 s`,
`B7   one save + one load: snapshot rows ~ 0 ticks ~ 40 s`, `ESTIMATED wall for the selected blocks: 498 s (...)`, `DRY RUN: no bridge touched.`
B1 runs first on purpose (it clears the whole map); B7 needs B4's covers zone, so they share this one run.
```
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/live_session.py --only B0,B1,B4,B7 --no-owner-save --player-log <pass2 Player.log.copy> --out-dir Transient/live_session/pass2_<stamp>
```
M (run 20261018T233414): B0 0.9 s, B1 285.8 s, B4 187.2 s (7000 ticks), B7 8.1 s. Rows to read: `validation_v2:*` (want 61/0/0;
a P3f "did not launch a thrown flyer" UNMEASURED means the deployed DLL predates `3665fb781b`), `B7_reload_*` (`detail.pairs` /
`settledSame`: write them into `RELOAD_POCKETS_DIAGNOSE_KEPT_NO_RECEIPTS`), `B4_access_jump_pack_in_no_fall`, `B4_cover_40/120/220` (read each criterion in the row; ledger item says 120/220 kg covers gave way under one ~60 kg colonist), `B4_grenade_no_blast_cover`, `B4_access_rescue_ladder_queued`, `B4_dehydration_rate`.
**F1b. liquid_checks L5 only, same map as F1** (zone `l5` = `51,107` from the plan table; disjoint from every B4 zone, checked):
```
python.exe src/RimMandrake/FlowWorks/northstar/liquid_checks.py Transient/live_session/pass2_<stamp>/liquid_checks_L5.json --only L5 --origin-l5 51,107 2>&1 | tr -d '\r' | tee Transient/live_session/pass2_<stamp>/liquid_checks_L5.log
```
Rows: `L5_switched_off_hose_spills` then `L5_colonists_clean_spill` (M: 56 s for L2,L4,L5,L6 together; L5 alone E ~25 s).
**F2. proof_hose realflow only.** Flags (from `--help` and source lines 49/68/895; the script has NO `--dry-run`, and `--offline-gate` did not finish in a 150 s WSL budget when tried tonight, so it is not part of this plan): `--live --only realflow`. `realflow` is one of the BLOCKS; `preflight` and `session` always run with `--only`. Default is a FRESH map (`--no-fresh-map` to reuse F1's).
```
python.exe src/RimMandrake/FlowWorks/northstar/proof_hose.py --live --only realflow 2>&1 | tr -d '\r' | tee Transient/live_session/pass2_<stamp>/proof_hose_realflow.log
```
Output `northstar/proof_hose_<stamp>.json` (mode `partial`). M: the whole proof_hose was 127.6 s inside live_session; realflow alone E ~150 s (runbook). Rows: the six `NS_*` above; `NS_tank_does_not_bridge_pipe_runs` UNMEASURED SITE means the V tank was not built (a site, not a mod, finding).
**F3. suspension_bridge_proof whole, ALWAYS with `--fresh-map`** (runs a/b/c shared one map and leftover pawns produced the 816 kg reading). Sections: `posts,grate,underpass,waters,jetty,looks` (all by default). Flag check, run now: `python3 src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py --mock --only underpass,looks <out>` rc 0, prints `== section underpass` and rows `UND_floor_path_walks_under SKIP {"read": "UNDERPATH found=True ...", "mock": "PASS"}` (mock proves paths only). `--river/--lake/--sea x1,z1,x2,z2` are optional drags; the previous run's JSON records the ones used: read them from `Transient/suspension_live/suspension_bridge_proof_20261019c.json` `args` before launching so the `WAT_*` rows (UNMEASURED last time) get their waters.
```
python.exe src/RimMandrake/FlowWorks/northstar/suspension_bridge_proof.py --fresh-map Transient/suspension_live/suspension_bridge_proof_20261019d.json 2>&1 | tr -d '\r' | tee Transient/suspension_live/pass2_run.log
```
M: previous runs 215 s and 211 s (00:00:11-00:03:46, 00:04:22-00:07:53). Rows that were red: `LOOK_*_resolves` (Styleable defs), `UND_*` and `SB_path_crosses_on_deck` (underpass reach), `SB_rails_off_some_fall`, `SB_load_over_rating_whole_span_falls`, `SB_vanilla_bridge_refused_over_dug`.
Emit output at least every few minutes (600 s silence kill); `tee` does this.

**F4. climb_proof whole, with `--fresh-map`** (scenes A-G on one 46 x 12 site at the default origin `120,120`; flags from `--help`:
`[out] [--origin ORIGIN] [--fresh-map]`; the script has no `--dry-run`; its pure verdicts are `selftest_climb_proof.py`, PASS 2026-10-19):
```
python.exe src/RimMandrake/FlowWorks/northstar/climb_proof.py Transient/live_session/pass2_<stamp>/climb_proof.json --fresh-map 2>&1 | tr -d '\r' | tee Transient/live_session/pass2_<stamp>/climb_proof.log
```
E ~5.5 min (3 x 900-tick orders + up to 3,600 haul ticks). Rows to read: `CLIMB_raider_never_crosses_ramped_moat` (UNMEASURED with
"control" in `why` = the moat raider could not reach the edge up the ramp: read the `CLIMB_ramp_*` rows first),
`CLIMB_hauler_fetches_ramped_floor` (`detail.trail` = the hauler's cells; a sealed-phase FAIL means a hauler got onto a sheer D 4
floor with no ramp), and the pass-1 rows again. (`CLIMB_RAMP_ROWS_BUILD_STAIRS_ARRIVED_EARLY` is closed by the script fix.) Record the
rows on `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` A1.
**F5. live_session B2 + B5 + B6, same map as F4** (climb's site `120..165,120..131` is disjoint from the readout/ice/flood zones).
Flag check, run 2026-10-19: `python3 src/RimMandrake/FlowWorks/northstar/live_session.py --dry-run --only B0,B2,B5,B6` rc 0, zones
`readout (228, 15, 22, 16)`, `ice (15, 37, 16, 8)`, `flood (37, 37, 18, 10)`, `ESTIMATED wall for the selected blocks: 868 s`,
`DRY RUN: no bridge touched.`; `--mock --only B0,B2,B5,B6` rc 0 (14 rows, mock reads UNMEASURED as designed).
```
python3 src/RimMandrake/Utils/save_guard.py run --current-slot none -- python.exe src/RimMandrake/FlowWorks/northstar/live_session.py --only B0,B2,B5,B6 --no-owner-save --out-dir Transient/live_session/pass2b_<stamp>
```
Rows to read: `B2_readout_sea_never_dry` (`detail.edgeCell` must name WaterDeep at x = map width - 1), `B5_ice_freeze_thaw`
(`detail.coldest`, `expectedFreezes`, `frozeAfter`, `thawAfter`), `B6_flood_canal_kept` (`floodReachedAfter`, `recededAfter`,
`changed`). B2's dialog rows ride along (cheap).

### 6b. Optional (only if the owner wants it; not counted in the estimate)
B3 is triaged (section 0 leftovers): a `flowworks`-tier re-run would repeat its SITE/OWED rows, so it is not offered here; one look at the FlowWorks Mod Settings dialog to clear the `B2_dialog_*` reds.

### G. Read, record, restore FULL, release
```
python3 src/RimMandrake/Utils/modlist_swap.py --restore                 # plan
python3 src/RimMandrake/Utils/modlist_swap.py --restore --apply
python3 src/RimMandrake/Utils/modlist_swap.py --status                  # LIVE md5 must equal FULL (a40bedf5..., 542 active, unless the repair re-captured it: then the printed FULL md5)
./game --why "pass 2 done, FULL restored" down
python3 src/RimMandrake/rimflow/cli.py bridge release
```
If the md5 differs, STOP and report; do not hand-edit (`modset_builder.py --restore` restores the pre-swap before-copy md5-verified). Do not relaunch the 542-mod list (about 15 min cold load) unless asked.
Then read the three outputs before any ledger line: verify lines are WRITTEN, not run. A partial run (`--only`) records `verify` only for rows it actually measured; the full-run items stay owed.

## 3. Time budget

| step | E / M |
|---|---|
| A take + B deploy + C swap | 3-4 min (E; deploy seconds) |
| D launch + gate | 1-2 min (M 44-70 s, 11 mods) |
| E preflight + map | 3-6 min (E) |
| F1 live_session B0,B1,B4,B7 | 8 min (M 286 + 188 + 8 s) |
| F1b liquid_checks L5 | ~0.5 min (E) |
| F2 proof_hose realflow | ~2.5 min (E from M 127.6 s whole script) + fresh map ~8 s |
| F3 suspension proof | ~3.6 min (M 211-215 s) + fresh map |
| F4 climb_proof | ~5.5 min (E) + fresh map ~8 s |
| F5 live_session B0,B2,B5,B6 | ~14.5 min (E 868 s; B5 is up to 36,000 ticks) |
| G restore + release | 2 min (E) |
| gates, copying logs, reading rows | ~8 min (E) |
| **Total** | **~54 min (range 48-65)**, plus waiting for the current driver and a game-down |

## 4. Blockers and traps

- The current driver must be finished, the game closed and the bridge released; nothing here is startable earlier.
- Any FlowWorks Source committed after the last DLL makes the stamp stale: 1.1 (rebuild from a clean export) is then required before step B.
- `B4_reservoir_catch` and `B4_reservoir_fish_rolled` need the companion `jawa/fishing`; `B4_access_jump_pack_in_no_fall` and `B4_dig_cost_notch16` were UNMEASURED for unrecorded reasons: read `detail` in the new `session.json` before filing.
- Covers are rated 40/120/220 kg and a colonist weighs ~60 kg: if `B4_cover_120` still reads "gave way" at one colonist it is a MOD finding on `PIT_COVER_DIAGNOSE_GIVES_WAY_TOO_SOON`, not a harness one.
- Never save the map after a thirst run (not in this pass). Never live-test flyers without the owner.
- F5's B5 holds the whole map near -19 C for up to ~24,000 ticks: colonists left outdoors may take hypothermia. B5's row is not
  about health; if a colonist is downed by cold the row still reads (it only reads temperature, terrain and readouts), but heal before
  any later block. B6 floods every unroofed freshwater body's banks map-wide, not only the canal.

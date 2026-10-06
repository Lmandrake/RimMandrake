# BELT FlowWorks final pass 2026-10-05

## Part A (offline)
- 18:42 start; bridge FREE at start.
- 0c78c54a5: site_spec SETTINGS +14 (list matched C# exactly; 12 bools -> 48 toggles); selftest_flowworks_northstar PASS.
  RM_NorthstarProofs.cs (static_call read surface: ProofRoom, ProofCaptureDown, ProofLip, ProofPump, ProofWallFaces);
  RM_PitRooms.ShouldServeFromLip split into ShouldServeFromLipFor(worker, job, dest) so the proof asks the patch's own gate.
- Coordinator updates received: (1) sheet generator/HTML/serving now owned by another agent -> NOT touched by me;
  results go to northstar/validation_v2_result_*.json + extension_proof result JSON (paths below).
  (2) RiverWorks merges into FlowWorks (merge agent) -> RiverWorks dropped from deploy/live; river rows = extensions_rivers.py (theirs).
  (3) machinery builder in Source/Defs/Patches; its NEW ROWS land in Transient/belt_fwmachinery_20261005.md.

### Helper-library review (owner requirement)
- Retro helpers named in NORTHSTAR_PROCESS_RETRO_1 (game_cycle, run_from_root, save_keeper, literal_log_wait, status-vocab
  check) do NOT exist yet (item gated on GSS GREEN; grep of Utils/ finds no defs). Nothing to adopt; nothing local deleted for them.
- modcheck/helpers.kill_hostiles: REJECTED for v2 phase_P. v2 uses `jawa/destroy_bulk filter=nonColonists`, which removes
  hostiles AND wildlife with no death/corpse/detonation (helpers.kill_wildlife's own docstring measures the boomalope fire
  cascade a kill causes); kill_hostiles kills per id and would reintroduce corpses/fires into fire-sensitive rows.
- helpers.storyteller_off / random_events_off: need a modcheck Transaction (`tx`) the v2 RealBridge does not carry; v2 already
  clears the incident queue at the two points it matters. Not adopted (would need a tx shim for no new guarantee).
- prep_site.save_golden already does the before/after Saves stat a save_keeper would (wrong-slot trap) -- kept; it is the
  candidate to lift into the shared library when the retro builds save_keeper.
- bland_world.*: built for a bland WORLD start (GSS); FlowWorks runs on a fresh quicktest map per runsheet. Not applicable.

## Part B (live)

## Results

### Part A results (offline)
- DEFECT found offline + fixed (RM_LiquidFire.Maintain): firefoam on a burning cell never put it out (IsSmothered was only
  consulted when queuing a NEW light) and RainDouses had NO caller at all — both "built" features were inert. e5f11cb82;
  DLL ad971cb04 (built from a git-archive export of HEAD because two other writers hold uncommitted Source/ edits in this
  clone; the push guard refused the source-only commit, correctly).
- Core promotion (judged per bar): X10_canal_fire PROMOTED (canal_burning_reads_as_burning_liquid, canal_fire_persists,
  canal_spent_after_burn) — fire is a headline Phase 6 mechanism and nothing that runs by default proved it; ~4,000 ticks
  using canalBurnDaysPerLevel 0.02 for the row only. Mock fire model + 3 MockBridge faults (never spreads / never burns /
  no ash) each turn X10 red. plot_E_fire's three duplicate components CUT (lesson 6).
  KEPT in extensions: canal_fire_reaches_reservoir (needs a tar BODY; core bodies are water), reservoir_recharge_progress_visible
  (slow 20-pulse refill; look bar), sluice_gate_state_legible (look bar; flow_doors proves the mechanism),
  spikes_read_distinct (look bar on placeholder Skullspike art — nothing to prove until the art lands).
- New extension chains (24 components): fire_put_out, pit_prison_room, liquid_pump, bottle_revert, wall_faces, dig_finds.
  Not wired, with reasons in extensions.py: Charity-gated Exposed Prisoner (needs two live ideos), DBH thirst (DBH not on any
  list), fill-job fix (existing toggle_bottle_loop route), too-wide capture (C# selftest).
- Harness bugs fixed: pit_fill_effects called ProofReport with args="" (static_call reads "" as ZERO args, so the census never
  answered); pitDepthDrawOffsetEnabled was missing from extensions FW_TOGGLES (its chain existed).
- Walk prose (DRAFT, owner released): stale preamble "this walk proves digging ... not filling" and two anti-guessing notes
  claiming the walk steps still call canal_dig / were never rebuilt — deleted; ## north star section untouched (bars are his).
- Selftests: v2 offline all PASS, O-LIVE-NEG 35 faults red, mock GREEN 59 rows; selftest_extensions PASS (48 toggles);
  run_selftests 183/184 — the 1 FAIL is walklint BAD_PACKAGEID on FlowWorksRivers.md (`mandrake.rm.riverworks`), the merge
  agent's in-flight rename, not mine.
- [live] 19:06 bridge taken; game was DOWN; merge commit not on origin yet -> deploy HEAD FlowWorks as it stands
- [live] 19:07 deployed FlowWorks from origin/main export (20 files, VERIFIED); ModsConfig backup Transient/ModsConfig_before_fwfinal.xml (50 mods, sha 376d991d780cc3c4); tier flowworks applied (10). launching via northstar_driver.live_session.launch_and_wait (adopted: the shared launch+token wait)
- [live] 19:08 game up (37 s). preflight offline: P-O1 DRAFT (owner release, expected), P-O3/P-O5 = other writers' uncommitted Source/Defs in the shared clone vs deployed origin/main (deploy itself VERIFIED from an export), P-O4 FULL.LATEST drift (owner list file, not touched; restore is my byte backup). Golden site not rebuilt: new chains prep their own plots. Starting v2 --live --fresh-map
- [live] 19:08 watchdog HEALTHY at v2 start; Monitor polls watchdog every 5 min
- [live] 19:13 watchdog HEALTHY
- [live] 19:18 watchdog HEALTHY
- [live] 19:20 core v2 #1: 56 PASS / 3 FAIL (result src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261005T191242.json). L2 = HARNESS env: the clone's DLL is another writer's uncommitted rebuild (deployed = origin/main build fc5c9a); X10 = harness: unlocked weather -> rain doused a cell (the new douse working) -> pinned Clear+locked; P3_walk_in_held = pawn arrived after the 1200-tick wait (descent logged later); isolated probe Transient/belt_fwfinal_probe_p3.py walks in at 400 ticks with rooms ON and OFF -> not reproduced, re-running core from an origin/main export
- [live] 19:26 core v2 #2 (origin/main harness, deployed ad971cb04 build): 58 PASS / 1 FAIL = L2 identity only (origin moved under the run: merge 409d1f57c + machinery 3e473f37c pushed new DLLs). P3 + X10 PASS. Result /home/mandrake/rm/fwx/src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261005T192324.json (copied to the repo northstar/). Next: kill, redeploy current origin/main FlowWorks (merged rivers+machinery), re-run core at that hash.
- [A2] 19:4x origin moved (merge 409d1f57c, machinery 3e473f37c): site_spec +Rivers(40) +Machinery(6) classes -> 75 toggles; rivers suite registered in validation.py; machinery_hoses + machinery_found_works chains; 11 rivers toggles uncovered named RIVER_TOGGLES_OWED (merge agent's extensions_rivers.py; preflight P-O2 honestly refuses until covered). LANDED 4f76420cb
- [live] 19:27 game stopped; deployed origin/main 4f76420cb FlowWorks (26 files, DLL 256f8de incl. merged rivers + machinery); relaunching
- [live] 19:32 core v2 #3 (deployed 4f76420cb, L2 PASS now): 58/59, X10 FAIL (2 of 6 cells burned out in 4,000 ticks; flames 6->5->4) -> harness: weather transition rain still refilling/dousing; X10 now turns rainFills+rainDouses OFF for the row only. Re-running.
- [live] 19:36 core v2 #4: GREEN 59/59 (src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261005T193627.json). Next: extension chains
- [live] 19:41 extension run #1 (src/RimMandrake/FlowWorks/northstar/extension_result_20261005T193813.json in /home/mandrake/rm/fwx3): 10 PASS / 6 FAIL / 17 UNMEASURED. All 6 FAILs were HARNESS: (a) static_call splits args on '|' -> ProofRoom/ProofLip/ProofPump never answered (C# now ';'); (b) liquid_pump arg string bug; (c) spawn_batch makes no Filth_FireFoam -> foam laid by a Stun blast scattering foam; (d) dig_finds trusted a designation query, no cut happened -> done = depth rose, colonist given Mining; (e) hose-off +1 unit = a colonist emptying a fresh bottle left by bottle_revert -> bottles destroyed after; (f) pit_fill_effects colonists walked out of the pit -> held hostiles. fire_put_out split into fire_explosion/fire_foam/fire_rain. 79fbcf4e4 (DLL rebuilt from export). Redeploying.
- [live] 19:47 watchdog HEALTHY
- [live] 19:49 core v2 #5 GREEN 59/59 (fwx4 validation_v2_result_20261005T194509.json); ext #2: 15 PASS / 5 FAIL / 13 UNM -> fixed: plot row 2 sat in the edge-sink band (anchor now centred), fill terrain takes no filth so foam is tested by the popper's Extinguish blast, MOD DEFECT: foamSmothers setting did not gate the Extinguish route (fixed 740672212), prison-cell role recompute after raw owner write, dig-find letters counted by label. Redeploying 740672212.
- [live] 19:59 core #6 58/59 (X10: flow relit a spent cell, 5/6 spent at 4,000 ticks -> wait 6,000); ext #3 23 PASS / 3 FAIL / 7 UNM (fwx4 extension_result_20261005T195815.json): all 3 harness (held occupants wandered to dry pit cells -> isolated 1x1 pits; warden fled undrafted -> drafted; a colonist hauled a bottle -> colonists drafted during the wait). foam (Extinguish route + setting gate) PASS, rain PASS, explosion PASS, pump PASS, hoses PASS, dig finds PASS, wall faces PASS, room split + prison PASS.

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

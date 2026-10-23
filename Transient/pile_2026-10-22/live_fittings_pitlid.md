# Live: fittings switch + pit-lid check (BENCH helper, 2026-10-22)
Bridge: taken by BENCH "fittings switch + pit-lid live check"
## 1. joinFittings ON (JOINT_FITTINGS_RESTORE_SWITCHED_OFF_AT_HOME)
- LIVE read (jawa/mod_settings_field get, RM_MachinerySettings static): joinFittings=True at tick 145425 — already ON.
- Saved config Config/Mod_FlowWorks_RimMandrakeFlowWorksMod.xml (game-written 2026-10-22 14:30:19 local) holds NO joinFittings key;
  Scribe_Values omits a value equal to its default, and the default is true (RM_MachinerySettings.cs:167) -> loads ON.
- The "saved false" premise is stale (predates default-ON DLL d19106464f). No write needed; confirm ON after restart (step 2).
## 2. Pit-lid deploy + X8b/X8c
- game closed (taskkill), FlowWorks DLL 36d4749eeb deployed (VERIFIED in sync, sha1 cddc3f6f65d2 both sides), relaunched via Steam
  on fw_gss_sitting (14 mods), save b loaded (tick 144387). joinFittings=True after restart.
- validation_v2 --live (calm site, 280 s): 62 PASS / 1 FAIL. X8b PASS (beneath/held/trapped True, hidden=True, drawPatch=True).
  X8c FAIL = HARNESS: the row stands a colonist on the WOVEN-SCRAP lid (gives way under 40 kg); the lid sprang (covered=False,
  held/trapped True) so the colonist fell in and is drawn sunk (sink 1.2) -- correct for a faller. Result JSON:
  src/RimMandrake/FlowWorks/northstar/validation_v2_result_20261022T1940_bench_pitlid.json, stdout live_fit/v2_stdout.txt.
- Same rows on C12 (save b, plank lattice lid, 120 kg): Vicky ordered 71,33 -> 73,35: ProofBeneath beneath=False hidden=False
  covered=True sink=0.000 drawDz=0.000 (X8c bar met). Colonist Dixon put in the pit at 74,36 then the lid relaid: beneath=True
  hidden=True drawPatch=True, lid inspect "Below, hidden: Dixon" (X8b bar met).
## 3. By-eye captures
- live_fit/pitlid_walker_C12_tight.jpg, live_fit/pitlid_walker_and_under_C12_crop.jpg: Vicky drawn on the planks at ground,
  no dark square (owner's shot had one), not sunk, looks like Spirit on open ground; Dixon under 74,36 not visible at all.
- Fittings: live_fit/fit_C3n_pump_pipe_tank_joints_ON_OFF_diff.jpg (ON | OFF | diff x4): two fittings drawn on map C C3 north
  (pipe 17,43): flange at the pipe->tank join, coupler at pump top; both vanish with joinFittings off (restored True after).
  C7 pipe and the two hose->tank ports: no difference ON/OFF (no hose port-coupled to a pipe on this save; by design).
## 4. Findings filed
- verify run-1 A2 L1 FAIL (X8c HARNESS), run-2 A3 L2 PASS -> PIT_LID_FIX_VICKY_PEEKS_THROUGH validated, still owes L1.
- finding X8C_WALKER_FALLS_THROUGH_SCRAP_LID (HARNESS) -> spawned X8C_WALKER_FIX_FELL_THROUGH_THE_FLOOR.
- filed TANK_FLANGE_FIX_HOVERS_MID_PIPE (MOD: south-entry tank flange drawn ~0.5 cell below the skid).
- JOINT_FITTINGS_RESTORE_SWITCHED_OFF_AT_HOME closed at c8f8307b34 (already ON).
## 5. Bridge released / game state
- save b reloaded (tick 144387, paused), joinFittings True; bridge released. Nothing saved.

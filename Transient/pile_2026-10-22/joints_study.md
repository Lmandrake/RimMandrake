# FlowWorks joints study — night live walk 2026-10-22 (BENCH live helper)

Owner order (2026-10-22 ~00:00 PDT): "Hoses need to be twice as thick, too thin to see now. Solid pipes appear unchanged in width, should be reduced as well. ... really study how the hoses and pipes connect up. Make it look great."

## Status
- [x] Phase 1 deploy (00:50)
- [x] Phase 2 proofs (01:25)
- [ ] Phase 3 joints study

## Phase 1 — deploy
- Game closed (stamped), deployed FlowWorks (238 files incl. a peer's uncommitted text-only Defs/Keyed edits, all parse), GimmeSomeSlack (DLL), SWBestiary (29), HugeThings, PyrelandsMechanics, SolarMirrors, StructureInjectionsRUT, UtinniPatches (41), Warcasket, WasteRun — all VERIFIED in sync. FlowWorks DLL md5 repo==game 6ad35094.
- ModsConfig already == tier fw_gss_sitting (14 mods, md5 2fca0dd9). Relaunched; bridge up after 60 s.
- Plan output: Transient/pile_2026-10-22/deploy_plan.txt

## Phase 2 — proofs
- hose: proof_hose --only realflow (--skip-offline; offline HO5 red = Strand_Plump tiling seam, see defects) — NS_hose_ends_on_ports PASS; 10 PASS / 1 UNMEASURED (no VE pipe on tier). proof_hose_20261022T005611.json
- concealed pit: validation_v2 --live GREEN 62/62 incl. X8b_cover_occupant_stays_below PASS. validation_v2_result_20261022T011057.json
- reach map: 4 PASS / 1 OWED / REACH_WINCH_SITE FAIL (regression vs 5/5 at b5e399067a) -> REACH_WINCH_FIX_GHOST_ROAD_RETURNS. reach_map_proof_result_20261022T011113.json
- drawbridge: 12/12 PASS (HOSTILE_LOCKS rerun after a HARNESS step refusal). drawbridge_result_20261022T011210.json + _011524.json
- drawbridge looks live look: folded into Phase 3 (scenario map)
- machine dig: probe rows 1/2/4 PASS; real dig UNMEASURED/SITE (see log)
- NB: proofs ran from a git-archive export of HEAD 2038122711 (D:\ClaudeWork\scratch\bench_export) because a peer's uncommitted FlowWorks DLL sits in the bench worktree; deployed DLL a237375d = committed b1bab78fe5.

## Ranked defect list (join | look | facing | screenshot | what's wrong | proposed fix | files)
(pending)

## UI/UX notes
(pending)

## Log
00:48 phase 1 done
00:56 proof_hose offline gate RED: HO5_hose_art_sane FAIL 'Hose/Strand_Plump: seam 10.4 vs adjacent 2.4' — Strand_Plump.png (installed 2e22f30e3c 10-17) does not tile seamlessly; a visible seam every tile along a plump hose. MOD/art. Running live with --skip-offline (red is tiling art, not attach logic).
00:58 proof_hose --only realflow: NS_hose_ends_on_ports PASS (nozzleTip 161.236,158.698 on Scrapper reel; portEnd 175,160.021); 10/11 PASS, NS_external_pipe_is_visual_only UNMEASURED (no VE pipe on tier). JSON src/RimMandrake/FlowWorks/northstar/proof_hose_20261022T005611.json
01:11 validation_v2 --live (from HEAD export 2038122711, DLL a237375d = b1bab78fe5): GREEN 62/62, X8b_cover_occupant_stays_below PASS (beneath/held/hidden/covered True; lid inspect 'Below, hidden: TongXue')
01:12 reach_map_proof: 4 PASS, 1 OWED, REACH_WINCH_SITE FAIL (regression vs 5/5 at b5e399067a) -> filed REACH_WINCH_FIX_GHOST_ROAD_RETURNS
01:15 drawbridge_proof: 11 PASS + HOSTILE_LOCKS UNMEASURED/HARNESS (step refused 'busy with a long event'); rerun --only HOSTILE_LOCKS PASS -> 12/12
01:25 machine dig (DEEP_DIG_BUILD_DROIDS_TAKE_THE_SHOVEL, design §8) — probe-level via jawa/flowworks_job_probe, drawbridge map, cell 110,60 staged D=4 (2 m) + RM_DigCanal; control 114,60 D=2:
  row1 colonist (fresh Jake) D=4 hasJobOnCell=False, same colonist on D=2 control =True, designation NOT deleted -> PASS (probe). Right-click "needs a machine" text NOT checked.
  row2 colony Mech_Tunneler D=4 hasJobOnCell=True RM_DigCanalJob -> PASS (probe).
  row4 machineDigEnabled=False -> Tunneler no job -> PASS (probe). NOTE: with machines off the WorkGiver DELETES the designation (designationDeletedByWorkGiver=True, both pawns); with machines on it keeps it. UX question: an order nobody can dig is silently erased.
  real dig: 4000 ticks stepped, nobody dug either cell (spawned colonist Mining priority 0; Tunneler with no mechanitor idles) -> UNMEASURED/SITE. Item stays open (rows 3/5 + real dig owed). Scripts: Transient/pile_2026-10-22/machine_dig_live.py, machine_dig_tick.py; output machine_dig_live_2.txt

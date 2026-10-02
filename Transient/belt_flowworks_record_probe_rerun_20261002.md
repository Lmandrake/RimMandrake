# BELT: FlowWorks record / probe / rerun — 2026-10-02

## Task 1 — make the run recordable
(pending)

## Task 2 — probe tool for uncovered checks
(pending)

## Task 3 — two live reruns + determinism + record
(pending)

### Task 1 progress (code done, selftests green)
- New verb `modcheck record <Mod> --result <json> [--tier T]` -> `src/RimMandrake/Utils/modcheck/record.py` -> status.record_run. No ModsConfig touch.
- Refuses: non-live / aborted / other mod / no or STALE mod_hash / env.running != resolved tier set (modset_builder.resolve_tier, set compare) / tier guard refusal.
- Verdict: FAIL|UNMEASURED -> RED; all ok but UNBUILT/UNCOVERED -> REFUSED naming each bar; else verdict_for.
- status.py: `northstar/` excluded from mod_hash (result JSONs written there moved the hash every run); record_run(extra=); check() prints stored refused reason.
- validation_v2.py result now carries mod, mod_hash, env{running, running_sha256, assembly_sha256} (jawa/running_mods at run start).
- Legacy result 075609 -> REFUSED (no mod/mod_hash/env) as designed. Selftest: modcheck/selftest_record.py 22 PASS.
- BEFORE: `FlowWorks  STALE  checklist VALIDATED (38 lines)  [stored: GREEN]` (old FluidCanals@1789295363 entry)

### Task 2 progress
- New tool `jawa/flowworks_job_probe(x, z, kind=dig|fillin, pawnId?, forced=false)` in `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchFlowWorksJobProbeTools.cs` (reflection-coupled; CanDesignateCell + WorkGiver ShouldSkip/PotentialWorkCellsGlobal/HasJobOnCell/JobOnCell; restores a designation HasJobOnCell deletes, reports it). Builds clean (plan-only).
- validation_v2: S6_digToDepth_gate now probes designator (D1 ON accept / D4 refuse / D1 OFF refuse / undug OFF accept); J_workgiver_selection probes 3 job pawns before ordering + negative control (undesignated dug cell -> no job).
- Mock tool + 3 new faults (deepen_gate_ignored, workgiver_blind, workgiver_greedy): O-LIVE-NEG all 19 faults red. Mock: 58 PASS, 0 UNCOVERED, 12 UNBUILT.
- NEXT: kill game, build --gm --apply, relaunch, prove live.
- DEPLOYED (game PID 25748 killed, build --gm --apply "deployed", relaunched via Steam, bridge up 14 s). Tool listed live; no-map call -> loud "No current map.".

## Task 3 progress
- Rerun 1 (result 20261002T092652): 57 PASS, 1 FAIL, 0 UNCOVERED, 12 UNBUILT, 1570 ticks. S6 PASS live. FAIL = J_workgiver_selection for E7a/E7b: WorkGiver said hasJobOnCell=True/RM_FillInCanalJob, but pawns' Mining priority 0 -> giver not in normal list. Classified HARNESS (fresh colonist work settings). Fix: J sets Mining priority 1 via jawa/set_work_priority; mock pawns start at priority 0 (red oracle: dropping the call turns J red). Lesson in script docstring.
- Rerun B (092952, after relaunch): ABORTED in J -- pawn with Mining WORK TYPE disabled (skill read enabled); set_work_priority refused. HARNESS: re-roll such pawns; mock fault worktype_disabled_once guards (O-LIVE-NEG 20/20).
- Rerun A (092839, TemperateForest): GREEN, 58 PASS / 0 FAIL / 0 UNCOVERED / 12 UNBUILT / 1 SKIP, 1,030 ticks.
- Rerun B2 (093135, relaunch first, AridShrubland): GREEN, identical tally, 1,030 ticks.
- --compare A B2: SAME, 31 zero-tick rows, 0 differ.
- Recorded via `modcheck record`: 092652 -> RED (true history), 092839 -> REFUSED, 093135 -> REFUSED (final).
- AFTER: `FlowWorks  REFUSED (58 live rows PASS but 12 bars UNBUILT, 0 UNCOVERED: U_...)  checklist VALIDATED (38 lines)  [run ...093135.json at current hash 9909f906217d; PASS 58 SKIP 1 UNBUILT 12]`; floor: VALIDATED 38/38 covered, bar met.
- MOD defects found: none. HARNESS defects: 2 (both fixed, lessons in validation_v2.py docstring).
- Game left UP on flowworks tier, in the B2 quicktest map. Nothing committed (forbidden for this helper).

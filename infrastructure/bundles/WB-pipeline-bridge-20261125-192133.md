# WB-pipeline-bridge-20261125-192133 state

Worker run 1 on SteveDesktop, 2026-11-25 11:22 AM to about 1:15 PM PST. Context: 150k after the class step, 320k
after the first Steve1 sitting, 420k at this save (window 1M, line 500k). Restart from here.

## What the next context must know
- Run live checks as SteveDesktop lane jobs, not by hand: Steve1 and Steve2 are the lane's busy games. Every member
  clause has a committed proof line in `infrastructure/state/live_proofs/<ITEM>.txt`, mostly
  `src/RimMandrake/Utils/modcheck/live_queue/bridge_bundle_proof.py <CLAUSE>` (offline verdicts:
  `selftest_bridge_bundle_proof.py`). Submit from Archmagi (zsh there; write each command out in full):
  `ssh mandrake@archmagi-wsl 'cd ~/rm/bench && git fetch -q origin; python3 src/RimMandrake/Utils/testq/testq.py ask <ITEM> --purpose fix --by BENCH --sha <origin sha> --clauses <A1,..>'`.
  `ask` reads proof files from the Archmagi clone (it may lag): when it says CANNOT, use the `testq.py submit ...
  --proofs <A1,..> --profile tier:<tier>` line that a `--dry` ask prints. Results:
  `/mnt/d/RimTest/testq*/attempts/<job>.a1/result.json` and `proof_<clause>.log`. RUNNER's own verify passes no
  criterion: record `rimflow verify <ID> --criterion <C> --level L2 ...` yourself, WITHOUT `--sha`.
- The lane stages a fresh companion from the job's sources by itself (the thing_explain fix is deployed this way).
- Level L4 = the owner level. FOUNDRY put it on agent checks. Passing at L2 leaves "owes A1 L4": such members carry a
  `REFUSED BY BUNDLE (the L4 level only)` note for the Conductor to rescope (AWARENESS, BRIDGE_TARGETS,
  COMPANION_PROFILE, TPS_HOOKS).
- Raid tests are paused (`src/RimMandrake/rimflow/raid_pause.py show`).
- Evidence of the hand sitting: `/mnt/d/ClaudeWork/rimmandrake/bundles/WB-pipeline-bridge-20261125-192133/`.

## Done
| member | outcome | commit / reading |
|---|---|---|
| (no ticket) SteveDesktop lane: a `python3` proof line could not reach the bridge (8 attempts lost) | fixed, live | aa1f34fac8; every lane job since reruns under python.exe |
| (no ticket) map_awareness_proof A1 read HAR's kept kind as FAIL | check repaired | 20e97d2bef |
| (no ticket) rimbridge_client refused the reserved expect* arguments on every call | fixed, live | e7bc9e242e, selftest_rimbridge_reserved_args.py red then green |
| (no ticket) live_queue proofs gave up on a game at the main menu | fixed | e0b6a7f331, e7bc9e242e (`common.ensure_map`) |
| (no ticket) VITALS tier makeup count 20..26 refused the true 19-mod tier | check repaired | 9cffc6f84a, red then green |
| BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN | done | EVIDENCE PASS |
| NORTHSTAR_COMPANION_GAPS_1 | done | NORTHSTAR PASS |
| TILE_TEMP_CACHE_RESET_TOOL_1 | done | TILECACHE PASS |
| STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF | done | 01bc9212f2 + STATICCALL PASS |
| BRIDGE_TPS_REGULAR_REPORT_1 | done | TPS PASS |
| RIMMANDRAKE_REPAIR_FRAME_HIST_READS_THREE_WAYS_WRONG | done | caf6eb8af5 + lane FRAME PASS |
| VISITOR_DETECTORS_MEND_NAME_THE_STRANGER | done | A2 lane MAP A1 PASS, A4 map_A4 |
| AWARENESS A1, BRIDGE_TARGETS A1+A2, COMPANION_PROFILE A1+A2, TPS_HOOKS A1+A2 | PASS at L2, L4 refused | lane jobs, see notes |
| THING_LOOKUP A3 | PASS (validated) | 04ff1e5aac + db9b97d9c4 (fresh reader: killed pawns still explain) |
| MAP_AWARENESS A1 | PASS | lane J20261125T204038Z-bbca93; A10 refused (raid pause) |
| PAWN_ORIGIN A4, PEN A1 | criteria passed | map_A12, b_PEN |
| FLYERFRAMES, EXPERIMENT_MANIFEST, HEALTH_METRICS_JUDGE | REFUSED BY BUNDLE | owner act 1; C0-C5 run does not exist; costs unmeasured |
| step 4 fresh reader | done | 4 significant findings, all fixed in db9b97d9c4 |

## Next, in order
1. VITALS A1: lane job J20261125T205643Z-e2d5a0 got past the tier and FAILED inside vitals_overhead.py: "monitor
   armed state was [False, True]" on the off reps, "busy map has 0 of 60 wild animals", "no health change landed".
   Class each (mod, check or scene) and repair; A2 (full list) refuse.
2. PAWN_ORIGIN A2 (needs a launch with install.generation-early true in awareness_settings.json).
3. KEEPER_SAVES A1 (save_guard.py check on the real Saves folder + a save through the guard).
4. LAUNCHER_READY A1 (launch_and_wait.sh; find whether it runs on SteveDesktop or needs ArchSmall).
5. PEN A2 (a Pyrelands review keeper save), THING_LOOKUP A2 (two texture packs) and A5 (raid: refuse), and A4.
6. RIMMANDRAKE_PROVE_COMPANION_REFUSALS: the five extra refusals in its parent's note (transporter dryRun, pawn_kit
   full inventory, set_area out-of-map, flowworks + gss playtest_start in campaign, settlement import clearExisting).
7. BRIDGE_TPS_CAPTURE C3 (sampler from load: tps_report reads startedBy bridge-registration; the overhead half names
   the full list) and BRIDGE_TPS_REVIEW2 C3 (the interruption matrix: hitches, 40/90 s blocks, hang + kill) and C4
   (full list: refuse).
8. Polish lines from the fresh reader (one line each, no ticket): the rerun tail mixes the first run's text; mixed
   python.exe/python3 lines rerun their python.exe parts; TPS/FRAME/HOOKS leave the game Paused.

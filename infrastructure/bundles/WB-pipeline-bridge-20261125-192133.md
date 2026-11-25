# WB-pipeline-bridge-20261125-192133 state

Worker run on SteveDesktop, started 2026-11-25 11:22 AM PST. Context: about 150k after the class step, 320k after
the first live sitting (window 1M, line 500k).

## What the next context must know
- 23 of 25 members were BUILT and owed only a live reading. Their old build shas (fd2375d54cc2, 87d8821c20c3 ...) are
  not on origin/main (old history). `rimflow verify <ID> --criterion <C>` WITHOUT `--sha` passes the criterion on the
  built sha and moves the item (built -> done); a verify with `--sha <new>` leaves it owed; `close` refuses while a
  criterion is owed.
- Level L4 is the owner's level (`model.py` LEVELS: L4 -> needs owner). FOUNDRY pinned many live checks at L4 and
  wrote "full list" into them. Full-list testing is retired until integration. Read them on the small list at L2 and
  refuse the L4 remainder for the Conductor to rescope (his act: a looser criterion).
- Drive Steve1 from this machine: `source infrastructure/stevedesktop/testcentre_env.sh; export RIMFLOW_SEAT=BENCH
  WSLENV=$WSLENV:RIMFLOW_SEAT`, then `python3 src/RimMandrake/rimflow/host_guard.py run --seat BENCH --for "<what>" --
  python.exe <script>`. The rimbridge_client CLI needs `--yes-i-know-this-is-live` for most jawa tools.
- Steve1 at 11:27 AM PST holds a 30-mod "targeted" load WITH HAR (erdelf.humanoidalienraces), no save loaded
  (quicktest map, tick ~40k now). ModsConfig.xml holds the full list for the next load: a restart without a tier swap
  loads the full list.
- HAR's `ChangeKindPrefix` on Pawn.ChangeKind keeps a recruited Tribal_Warrior's kind (measured), so MAP_AWARENESS A1
  and VISITOR A2 need a HAR-free load (tier mods__base).
- With no save loaded the companion reads `test` whatever the profile file says (JawaBenchSafetyCore.Effective, by
  design), so COMPANION_PROFILE A1/A2 need a loaded save.
- Evidence logs: `/mnt/d/ClaudeWork/rimmandrake/bundles/WB-pipeline-bridge-20261125-192133/` (map_*.log, b_*.log).
- Raid tests are paused (`src/RimMandrake/rimflow/raid_pause.py show`).

## Done
| member | outcome | commit / reading |
|---|---|---|
| (no ticket) SteveDesktop lane: python3 proof lines could not reach the bridge (8 attempts lost) | fixed | aa1f34fac8, selftest_steve_worker_wsl_proof.py red then green; live: 9 of 11 map clauses PASS through python.exe |
| (no ticket) map_awareness_proof A1 read HAR's kept kind as a FAIL | check repaired | 20e97d2bef, red/green in selftest_map_awareness_proof.py; live reads UNMEASURED with the cause |
| THING_LOOKUP A3: thing_explain resolved a destroyed pawn's id | fixed in C#, NOT deployed | 04ff1e5aac; red live (b_EXPLAIN.log); needs deploy + rerun EXPLAIN |
| BRIDGE_CALL_EVIDENCE_WIRE_LOST_REPLY_UNKNOWN | done | EVIDENCE PASS |
| NORTHSTAR_COMPANION_GAPS_1 | done | NORTHSTAR PASS |
| TILE_TEMP_CACHE_RESET_TOOL_1 | done | TILECACHE PASS |
| STATIC_CALL_THINGID_FIX_DIGIT_EATS_ITSELF | done | 01bc9212f2 + STATICCALL PASS |
| BRIDGE_TPS_REGULAR_REPORT_1 | done | TPS PASS (12 windows, median 0.970) |
| VISITOR A4, PAWN_ORIGIN A4, PEN A1, TPS_HOOKS A1 (L2) | criteria passed | map_A4, map_A12, b_PEN, b_HOOKS |
| AWARENESS A1 test half | PASS | b_AWARE.log: GeneratePawn installed lazily by an arm, not at startup |

## Next, in order
1. Save + reload sitting on Steve1: clauses EPOCH (BRIDGE_TARGETS A1/A2), PROFILE on the loaded save
   (COMPANION_PROFILE A1/A2), FRAME (RIMMANDRAKE_REPAIR_FRAME_HIST), KEEPER (save_guard.py check + a save through it).
2. Deploy the companion (04ff1e5aac) with Steve1 down, swap to tier mods__base, restart: rerun EXPLAIN, MAP A1
   (VISITOR A2), AWARENESS campaign half, PAWN_ORIGIN A2 + MAP A11 (needs install.generation-early: true at launch).
3. Refusals with reasons: FLYERFRAMES (owner act 1), MAP A10 + THING_LOOKUP A5 (raid pause), L4/full-list criteria
   (TPS_HOOKS, BRIDGE_TPS_CAPTURE C3 overhead, BRIDGE_TPS_REVIEW2 C4, VITALS A2), HEALTH_METRICS_JUDGE, EXPERIMENT_MANIFEST.
4. Fresh reader (step 4) over aa1f34fac8, 20e97d2bef, 04ff1e5aac.

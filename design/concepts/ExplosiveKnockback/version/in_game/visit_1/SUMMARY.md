# ExplosiveKnockback 0.1.0 — in-game acceptance, visit 1

Started 2026-11-15 05:21 PST (detached helper, seat BENCH, item RIMMANDRAKE_DRIVE_EXPLOSIVEKNOCKBACK_IN_GAME_ACCEPTANCE_FIRST).

## Progress

- 05:22 skeleton written; precondition `in_game 0.1.0` [measured].
- 05:36 proof build (source 545e930429, DLL md5 76e4e00b) deployed; minimal+EK list 34 mods up (env_minimal.json); quicktest map AridShrubland 250x250; batch driver Transient/ek_visit1/batch.py; first 3 checks PASS.
- 05:50 batch 2: 14 checks; spared_states FAIL (diagnosed HARNESS: skipped pawns walk in the 240 ticks before the read; carrier's carry dropped before the blast), pawn_arc INVALID (walker 3 cells away cannot reach the landing cell inside a ~25-tick flight), closed_containers INVALID (no closed LWM container can reach 76-249 kg: WeaponsLocker 8 kg + maxTotalMass 50), storeroom_bomb_pit unknown scene.
- 06:15 four HARNESS faults fixed in proof scenes (bdd1326769; guard selftest_explosiveknockback_stage6_visit1.py watched red 5/6 on the base, green after); release DLL 191cb5eea1; proof build redeployed (md5 c7a28327); full minimal rerun on it.
- (times above were written from a wrong clock; true times from `date`:) 06:08 ledger note corrected the first tally to 25 PASS / 2 FAIL / 5 UNMEASURED of 32.
- 06:40 pawn_arc diagnosed live by job log (`set_colonist_job_logging`): a MOD defect (thrown mid-haul colonist re-hauls 1 of 3) plus two scene faults (walker re-ordered at launch arrives on the landing tick; teleport control respawned undrafted and stole the dropped stack). spared_states: the carry never happened (single-arg TryStartCarry refuses a spawned pawn) and skipped pawns walked before the read.
- 06:44 fixes landed ef266bbdf9 (release DLL with it); proof build of ef266bbdf9 deployed (md5 8b2b8252); full minimal rerun starts (env_minimal3.json).

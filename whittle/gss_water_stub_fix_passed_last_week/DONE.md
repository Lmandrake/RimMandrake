# Done claim

- true: **A1 (GREEN-MIN):** on the fw_gss list (`modset_builder.py --tier fw_gss_sitting`: FlowWorks + GimmeSomeSlack + | evidence: `whittle/gss_water_stub_fix_passed_last_week/evidence/A1_summary_run6_vs_20261023.json` `whittle/gss_water_stub_fix_passed_last_week/evidence/proof_all_fw_gss_sitting_run6.json` `whittle/gss_water_stub_fix_passed_last_week/evidence/proof_all_fw_gss_sitting_run6.log` `whittle/gss_water_stub_fix_passed_last_week/evidence/gss_dll_matches_source_run6.json` `whittle/gss_water_stub_fix_passed_last_week/evidence/MX_F60_T15_S0_board_run6.png`
  Full bullet: the A1 GREEN-MIN live proof. Run 6 (2026-11-11 21:51 PST, Archmagi, `proof_all.py --live --only matrix`,
  no `--allow-red`, offline gate 0 red): row `MX_F60_T15_S0` = PASS, got stubs 2, cord_edges 2, strands 2 (cords_min 2 /
  cords_max 2 is the "[2,2]"), node_types {battery 1, consumer 1, stub_water 2}, nets 1. The result's `tier` is
  `fw_gss_sitting`, measured from ModsConfig.xml activeMods parsed at run time and equal to the running packageIds
  (`env.tier`). GSS DLL: sha256 c16983bc… is the same in the `.srchash`, the repo, the Steam Mods folder and the assembly
  the running game loaded; all 70 `.srchash` source hashes match the source (`gss_dll_matches_source_run6.json`).
  FlowWorks deep swim: `deepSwimEnabled` = True, read from the running game (`env.flowworks_swim`). Runs 1–5 earlier in
  the sitting read the same F60 row. Ledger: `rimflow verify … --level GREEN-MIN --criterion A1 --result pass`. It names
  `--sha c29007b6b66e`, which holds an OLDER GSS DLL. The DLL tested was committed at 732415605f. Both contain the fix;
  a `rimflow note` on the item corrects the record (`done` is terminal, so no re-verify was possible).
- true: **Cause named:** candidate 1, FlowWorks co-loaded (R12 deep swim makes WaterDeep walkable; the cord adapter read | evidence: `whittle/gss_water_stub_fix_passed_last_week/evidence/cause_experiment_old_vs_new_rule_x_swim.json` `whittle/gss_water_stub_fix_passed_last_week/evidence/cause_experiment_old_rule.patch` `whittle/gss_water_stub_fix_passed_last_week/evidence/cause_oldrule_swimON_F60.png` `whittle/gss_water_stub_fix_passed_last_week/evidence/cause_oldrule_swimOFF_F60.png` `whittle/gss_water_stub_fix_passed_last_week/evidence/MX_F60_T15_S0_board_run6.png` `whittle/gss_water_stub_fix_passed_last_week/evidence/A1_summary_run6_vs_20261023.json`
  Two things. (1) Same 14-mod list as the 2026-10-23 FAIL (`same_list: true`): then 0 stubs, 1 cord across the canal;
  now 2 stubs. (2) Because a lot else changed since 10-23 (the judge's point), I isolated it: today's GSS
  (origin/main 487769d00c) built twice, differing ONLY in the one fix line (`cause_experiment_old_rule.patch`), each run
  on the same calm site and list, with deep swim switched through FlowWorks' own `RM_SwimWater.Reapply` and the canal's
  path-grid walkability read per cell:
  | GSS build | deep swim | canal walkable | F60 |
  |---|---|---|---|
  | old rule (db019519…) | on | True | **FAIL: stubs 0, cord_edges 1, one cord across the water** |
  | old rule | off | False | PASS: stubs 2 |
  | fix (c16983bc…) | on | True | PASS: stubs 2 |
  | fix | off | False | PASS: stubs 2 |
  The bug appears only when deep swim makes WaterDeep walkable AND the cord adapter uses the old "walkable first" rule,
  and the fix line alone removes it: candidate 1, confirmed. All four arms re-ran 21:55–21:58 after run 6 (the game restarted onto the
  old-rule DLL and back), with the same results as a first pass at 21:16–21:38. The pictures: `cause_oldrule_swimON_F60.png` (cord over the water) against
  `MX_F60_T15_S0_board_run6.png` (cords stop at both banks).
- true: **No regression in the run:** the other matrix scenes on the same run PASS (or any non-PASS is classified MOD, SITE | evidence: `whittle/gss_water_stub_fix_passed_last_week/evidence/A1_summary_run6_vs_20261023.json` `whittle/gss_water_stub_fix_passed_last_week/evidence/proof_all_fw_gss_sitting_run6.log`
  Run 6: every row PASS. That is all 30 reduced matrix scenes, D1 and D2 determinism (18 boards), Z log budget
  (0 errors, 0 new warnings) and preflight P1–P3. The offline gate ran first with 0 red. **Disclosed:** run 4 (21:23,
  same build) had one non-PASS: `D2_fresh_builder_same` FAIL on board B00 (F00 + D00, not the water scene). A fresh
  CordBuilder disagreed with the incremental one on one edge's key (missing 1, extra 1; offscreenRebuilds 12 vs the usual
  14). Classified MOD per the proof, unconfirmed against HARNESS (the probe may compare by a non-canonical key). It did
  not reproduce in 8 targeted tries or in runs 5 and 6. Filed as `RIMMANDRAKE_EXPLAIN_GSS_D2_SPLIT_ONCE_IN_TWELVE` with both
  explanations and the next probe. Every other row in run 4 passed, including F60 (`evidence/proof_all_fw_gss_sitting_run4_D2_fail.log`, saved when it happened).

## What I'm least sure about
- **The D2 flake** (above): 1 failure in 12 B00 builds today, none in any stored run before. If it is MOD, a cord could
  change shape after a reload on some layouts. It is filed, not fixed.
- **"Ordinary use."** A player can't place waterproof conduit on vanilla WaterDeep (live `jawa/build_check` refuses it),
  so F60 is a staged layout. The statement asks for that scene. What a player can build is waterproof conduit across
  FlowWorks' 2 m+ pit water (`RM_Fill_Water_Superdeep`, def-Standable, walkable even with swim off), and there GSS lays
  a cord on the water. That is a sibling with a different cause, not this item's: filed as
  `RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER`. Wadeable brim and chest-deep river water get a cord by GSS's
  long-standing rule. Details in BROADEN.md.
- **The item is already `done` on the ledger.** Recording the A1 pass with `rimflow verify` cleared the last owed
  criterion, and rimflow moved it built -> done by itself. I did not run `close`.
- **The game's FlowWorks copy:** the Steam Mods folder held another round's uncommitted LiquidDrill edits. I overwrote
  those four files with their committed (HEAD) versions so the proof ran on committed FlowWorks. Their working-tree
  edits are untouched.

## What I did not test
- Save/load of the crossing (`--only matrix` skips proof_all's save_load / d4_save blocks).
- Terrain changing under an existing powered crossing (bridge built or removed, freeze, flood, a FlowWorks dig under laid
  conduit). Pawns swimming over the buried run. Incremental rewiring.
- The full matrix (`--full-matrix`), and proof_all's core, aerial and style blocks. Any list other than fw_gss_sitting.
  The game was left up on that list, with deep swim on.

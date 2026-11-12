# JUDGE — GSS_WATER_STUB_FIX_PASSED_LAST_WEEK

Blind judge, 2026-11-11. I read STATEMENT.md, NOTES.md and the evidence/ files only. I did not read DONE.md, BROADEN.md
or the earlier JUDGE.md. No live game, no rimflow. I used read-only python over the JSON, git log/show, sha256sum
of the repo and deployed DLLs, and I opened the board images. I also checked the independent re-run
(`D:\ClaudeWork\rimmandrake\whittle_claude\CLAUDE_ARCHMAGI_FWLIVE\gss_ws\judge_run2.json`) and the 2026-10-23 FAIL
(`D:\ClaudeWork\rimmandrake\scratch\br1_gss\gss_A.json`).

## A1 (GREEN-MIN): TRUE
- Raw `proof_all_fw_gss_sitting_run6.json` (I read the raw file, not the A1_summary): row `MX_F60_T15_S0` = PASS, class MOD,
  "graph ok: 2 edges, 2 strands, 1 nets". In matrix.scenes.F60_T15_S0 the got values are stubs 2, cord_edges 2, strands 2,
  node_types {battery 1, consumer 1, stub_water 2}, nets 1, ends_without_net 0, and mismatches []. The expected values
  are the same, with cords_min 2 and cords_max 2. Decals: Plug 2. Edge hashes are battery 20,20 to stub_water 29,20 and
  consumer 35,20 to stub_water 32,20.
- Tier: `env.tier` = fw_gss_sitting. Its source is "ModsConfig.xml activeMods": 14 active, and active_equals_running is true.
  The running list has FlowWorks, GSS, Biomes, VEF core and all five DLC.
- DLL: the deployed DLL equals the running assembly (`assembly_matches` 1, sha c16983bc...). run_identity says deploy in-sync at start
  and end, and src_dirty false. My own sha256sum gives c16983bc... for both the repo DLL and the deployed
  `C:\...\RimWorld\Mods\GimmeSomeSlack\Assemblies\RimMandrakeGimmeSomeSlack.dll`, so the old-rule experiment DLL was taken
  back out. The fix line from 4b01d06994 is present in the current `Source/Core/SnapshotBlock.cs`.
- Swim: `env.flowworks_swim` deepSwimEnabled "True". proof_all.py:406 reads it live through `jawa/mod_settings_field`.
- Not a one-off: runs 2, 3, 4, 5 and 6, plus the other reviewer's judge_run2, all have F60 = PASS with the same counts,
  the same assembly and the same running-list hash.
- Small mismatch, not a defect: the statement says "built c29007b6b66e". The run ran at HEAD 7585d64 with a DLL that matches
  the current srchash. That is later than c29007b, and the fix is in it.

## Cause named (candidate 1, FlowWorks deep swim): TRUE
- The cause is recorded on the `implemented` events (the BENCH 2026-10-24 event has "root cause: candidate 1 (FlowWorks co-loaded)").
- The 2026-10-23 FAIL ran on the same list: its running_sha256 is 3da93efc..., the same as tonight's. Its F60 values were
  stubs 0, cord_edges 1, and no stub_water. That file does not record the swim setting, so comparing that date with tonight
  could not isolate the cause by itself: many commits landed in between.
- The 2x2 experiment settles it (`cause_experiment_old_vs_new_rule_x_swim.json`). Both arms used the same site and list,
  and only the one-line patch differs. On the canal (WaterDeep):
  - Old rule, swim ON: path grid walkable, FAIL with exactly the 10-23 signature (stubs 0, 1 edge).
  - Old rule, swim OFF: unwalkable, PASS.
  - New rule: PASS with swim on and with swim off.
  Each arm's DLL sha was read back. The images agree. `cause_oldrule_swimON_F60.png` shows one cord lying straight across
  the canal. `cause_oldrule_swimOFF_F60.png` and `MX_F60_T15_S0_board_run6.png` show the cord ending at both banks.

## No regression in the run: TRUE
- In run 6, 36 of 36 rows PASS: 30 of 30 matrix scenes, D1, D2, Z_log_budget, P1–P3, and offline red [].
- Run 4 had one non-PASS, D2_fresh_builder_same on B00, a board without water. It is classified MOD and filed as
  RIMMANDRAKE_EXPLAIN_GSS_D2_SPLIT_ONCE_IN_TWELVE (committed in 8d9f9db9c3). It did not come back in runs 5 and 6 or in judge_run2.
- Caveat on scope, not on truth: `--only matrix` runs 30 of the 109 designed scenes ("reduced from 109 to 30"). The
  statement only claims the other scenes in the run.

## Where the evidence is tidy or flattering
- MX_F60 is a best case: one straight 3-cell canal, flat calm site, dead power, one cord. Stills are enough here because
  the claim is about static graph geometry, not motion.
- In run 6 itself, the canal's path-grid walkability was not read. Only the swim setting was read. The newrule_swimON arm a
  few minutes later read it as walkable after Reapply. The 2026-10-23 run never recorded swim at all.
- Sibling evidence the builder supplied (`sibling_water_variants_swim{ON,OFF}_reapplied.json`, `sibling_XW1_fw_superdeep_cord_on_water.png`)
  shows the same defect on three other water terrains, with or without swim:
  - RM_Fill_Water_Superdeep: 0 of 2 stubs, the cord lies across the water, as the image shows. This one is filed:
    RIMMANDRAKE_BURY_GSS_CORDS_IN_FW_SUPERDEEP_PIT_WATER.
  - RM_Fill_Water_Brim and WaterMovingChestDeep: also 0 of 2 against an expected 2. I found no filing for these two.
    Someone should rule whether 2 stubs is the right expectation on walkable-by-def water, and if it is, file them. I could not file
    them this pass because rimflow was barred.
  These are outside this item's statement: they also fail with swim off, so the deep-swim cause did not create them.

would show: yes

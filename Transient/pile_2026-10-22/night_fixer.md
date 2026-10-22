# Night fixer — BENCH, 2026-10-22 (started 01:34 PDT)

| # | defect | status | sha |
|---|---|---|---|
| 1 | REACH_WINCH_FIX_GHOST_ROAD_RETURNS — no commit regressed it: the run was on a REUSED map; the wall-aware labels learnt new walls only at GatherData (1.6 runs it only when some pawn paths). Fixed: RegionDirtyer walkability + door/fence hooks; SelfTest case; item -> built (live rerun without --fresh-map owed) | done | 3810af4e5f |
| 2 | Hose strand seams: Strand_Plump (half-alpha col 0) + Styles/Modern/Strand_Plump (8-col gap) made periodic via art ledger; HO5 now also judges per-look strands; HO5 PASS | done | 27586425d9 |
| 3 | Machine-dig off: work giver deleted deep orders. Now stale only past OrderCap (machine cap, switch ignored); alert + right-click + placement text name the switch; item note (live row4 recheck owed) | done | 9aef556eff |
| 4a | D1 plump strand 9-13/64 rows (thinner than flat; Modern off-centre): all 4 re-cut to fill rows 1-62 centred; HO5 band check | done | 5ebfd259b2 |
| 4b | D5 pipe pole: span = look's own pipe (PipeSpan.png derived from atlas), ground pipe arm links to pole | done | d5481252ae |
| 4c | stale girth text in scenarios GIRTH_NOTE/c01/c03 + composite design doc | done | cda3b0f940 |
| 4d | UI: hose aimed at a tank/pump/machine lands on its nearest free side (was "target blocked") | done | ba1c8d16ab |
| 4e | D2 reel exit side, D3/D4/D8 fittings, D6 tap name, D7 Scrapper contrast, D9-D11 art polish | morning_questions.md Q1-Q5 | - |

## Log
- 01:34 start; 02:2x fixes 1 and 2 published
- 01:52 fix 3 published; polling joints_study.md
- 02:06 D1, D5, stale text published; next: hose lay onto tank cell, morning questions
- 02:12 morning_questions.md written (Q1-Q5); polling joints_study.md for new defects
- 02:13 helper FINAL at 02:10 deployed 5ebfd259b2 (has fixes 1-3 + D1). NOT in the walkthrough deploy: d5481252ae (pipe pole span + pole link, DLL + XML + PipePole textures), ba1c8d16ab (hose aimed at a tank). A redeploy from origin/main is needed before those can be seen; the game is UP on RM_fw_walkthrough_20261022 with the bridge held, so the fixer did not deploy.
- Live checks owed: reach_map_proof WITHOUT --fresh-map (REACH_WINCH_SITE), machine_dig row4 (designation kept with machines off), flowing-hose girth look per style.
- Not fixed (helper's scenario/site): C4 st4 lay 'no route' up the benches (a hose on dug ground needs a ramp or ladder by the crossing rule), C10 lead-out (D2, Q1).
- 02:14 defect list exhausted (remaining items need the owner: morning_questions.md Q1-Q5). Stopping.

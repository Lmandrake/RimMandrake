## spec
found-by: BENCH bridge run 1, driver 6 (§4 looks map, 2026-10-23), building `src/RimMandrake/FlowWorks/review_map.py` on a
fresh RM_TheRot 250 quicktest. Evidence: `Transient/bridge_run_1_20261023/captures/br1f/fw_review_map_verify.json` (`notes`).
Class: HARNESS (1), unknown (2).

1. Station 63's four hose lays (`lay:59,76,63,76` .. `lay:59,67,63,67`) and stations 66 (`lay:120,71,129,68`) and 67
   (`lay:142,71,151,68`) are refused with "no room for the straight lead-out from the nozzle" (layOk false), so those
   stations show no hose. The straight lead-out is an owner rule (question card 2026-10-06, HoseReviewChecks B5), so the
   station layout has to leave room for it. Done when: every station hose lays with layOk true.
2. Stations 35/36: 'Ladder' never read 'Ladder up'. Find out whether the builder reads the wrong label (HARNESS) or the ladder
   never reaches the up state (MOD).

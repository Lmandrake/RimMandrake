## spec
Seen once, 2026-11-11 21:23 PST, Archmagi, fw_gss_sitting list, GSS DLL c16983bc (= .srchash), by CLAUDE_ARCHMAGI_FWLIVE
during `GSS_WATER_STUB_FIX_PASSED_LAST_WEEK` (run 4 of `proof_all.py --live --only matrix`):

    D2_fresh_builder_same FAIL MOD  B00_ground ['F00_T0_S0', 'D00_n1_S0']
    {'edges': 2, 'same': 1, 'different': 0, 'missing': 1, 'extra': 1, 'offscreenRebuilds': 12, 'pending': 0}

Every other row passed, including D1 (zero-tick re-reads) and both scenes' counts. The incremental graph's edge hashes for
B00 were identical to runs 2 and 3 (`consumer:32,19|battery:20,19` 3f37058389c52dca, `terminal:53,16|battery:53,16`
f809522519b8b025). `offscreenRebuilds` was 12, against 14 on every passing build.

**Not reproduced:** 8 further B00 builds (`run_live.py --only F00_T0_S0 D00_n1_S0`), 5 back-to-back and 3 straight after
`test_site_saves.py load calm`. All gave same 2, offscreenRebuilds 14. D2 had never failed in any stored
`northstar/proof_all_*.json` (2026-10-05 → 2026-11-07). So far: 1 failure in 12 builds today.

**What the counts mean:** `GimmeSomeSlackProbe.Fresh` matches fresh vs incremental pieces by `LaidPiece.Key`. "missing 1
+ extra 1" means one edge exists in both but under different keys (or one edge really differs). Two candidates:
- **MOD:** CordBuilder's key or endpoint order (or the route itself) depends on the order in which sections rebuilt
  (12 vs 14 offscreen rebuilds), so the incremental and fresh builders disagree now and then. A shipped cord could
  then change shape after a reload.
- **HARNESS:** the probe compares by a non-canonical key (end order), so an identical cord counts as missing + extra.

**Next:** log both key sets in the `fresh` probe reply (one line of C#) so the next occurrence names the edge, and
check whether `LaidPiece.Key` is order-canonical. Evidence:
`whittle/gss_water_stub_fix_passed_last_week/evidence/proof_all_fw_gss_sitting_run4_D2_fail.json` and `.log`.

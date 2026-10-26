# FW_PROOF_TOOLS_HARDEN_READ_GAPS

GPT review findings FF_validation_suite_*, verified CONFIRMED by GPT_FW_REVIEW_VERIFY_REMAINING_FINDINGS (2026-10-26).
Raw findings: D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\F_validation_suite_<part>.md. Line numbers are at e101a7383a.
Each fix needs a selftest that fails before and passes after (see FlowWorks/northstar/selftest_gptfw_review_fixes.py for the pattern).

| finding | verdict | evidence | action |
|---|---|---|---|
| 4.5 | CONFIRMED | scenarios_map.py:679 snapshot keeps (d,f) only; excavation_rect rows have no liquid/dl (JawaBenchFlowWorksPulseTools.cs:318) | item (needs bridge read) |
| 7.12 | CONFIRMED | review_map.py:1296-1304 no fluid in verdict; no per-cell fluid read on bridge | item (with 4.5) |
| 6.2 | CONFIRMED | validation_v2.py:2077-2080 compares fill only; jawa/flowworks_pulse (JawaBenchFlowWorksPulseTools.cs:121-160) returns fill/depth only, no dL | item (bridge field) |
| 6.4 | CONFIRMED | underpass_raid_live.py:118-121 x,z only; band exists in C# (RM_SuspensionUnderpass.InFloorBand) but no Proof read | item (needs proof read) |
| 7.1 | CONFIRMED | validation.py:357-367 latest_hose_result no assembly_sha256 check (driver_rows_at 1095 has); proof_hose.py stamps none | item (hose-owned proof_hose) |
| 7.11 | CONFIRMED | selftest_hose_port.py:127-129 6-line window text match | item (hose file) |
| 8.3 | CONFIRMED | validation_hose.py run_carry 857-877 CR5 accepts forced fallback | item (hose file) |

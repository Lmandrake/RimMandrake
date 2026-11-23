## spec
Filed by the Producer, Producer weekly plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0045Z_weekly), goal 2. Broken: RM_Liquid_FreshWater <- `fw_live_checks.py:L5_switched_off_hose_spills`
(2026-10-11) and `TANK_DEBUG_BUILD_FILL_AT_WILL:A1` (2026-10-23; that item is built; BRIDGE_FLOATMENU_FIX_DEBUG_PICKER_UNREADABLE
is named on the A1 failure). Cause: UNMEASURED.

## verify
- L2: `fw_live_checks.py` L5_switched_off_hose_spills PASS on the current build.
- L2: TANK_DEBUG_BUILD_FILL_AT_WILL A1 re-verified PASS (or, if A1's failure is the debug picker, that bug fixed first).
- `mod_completion.py FlowWorks` no longer lists RM_Liquid_FreshWater as broken.
- Stopping point: finish.

## criteria
<!-- Written by the Producer, event re-plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0701Z_event), from this item's `## verify`; level-tagged for `rimflow implemented`. -->
- A1 L2: `fw_live_checks.py` L5_switched_off_hose_spills PASS on the current build
- A2 L2: TANK_DEBUG_BUILD_FILL_AT_WILL A1 re-verified PASS (or, if its failure is the debug picker, that bug fixed first)
- A3 L0: `mod_completion.py FlowWorks` no longer lists RM_Liquid_FreshWater as broken

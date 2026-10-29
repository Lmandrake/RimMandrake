## spec
Filed by the Producer, Producer weekly plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0045Z_weekly), goal 2. `mod_completion.py FlowWorks` (2026-10-28) counts four parts broken by these rows:
RM_Fluid_BoilingWater, RM_Liquid_BoilingWater, RM_WaterBoiling, RM_LiquidTank <- `glow_tank_live.py:GLOWTANK_SALT_DRAWN_ONE_UNIT`
(2026-10-22) and `GLOW_TANK_LIQUID_FEED_1:A2` (2026-10-09). Cause: UNMEASURED; first step is the failing rows' result files.
Related: GLOW_TANK_PROOF_FIX_BLIND_READ_PASSES (the same script's absence check passes on an unread inspect).

## verify
- L2: `glow_tank_live.py` on the current build: GLOWTANK_SALT_DRAWN_ONE_UNIT PASS, every row MOD-class PASS or named.
- L2: GLOW_TANK_LIQUID_FEED_1 criterion A2 re-verified PASS on the current build.
- `mod_completion.py FlowWorks` no longer lists any of the four parts as broken.
- Stopping point: finish (the four parts read works; no new mechanics).

## criteria
<!-- Written by the Producer, event re-plan 2026-10-29 (run folder D:\ClaudeWork\rimmandrake\producer\2026-10-29T0701Z_event), from this item's `## verify`; level-tagged for `rimflow implemented`. -->
- A1 L2: `glow_tank_live.py` GLOWTANK_SALT_DRAWN_ONE_UNIT PASS on the current build, every row MOD-class PASS or named
- A2 L2: GLOW_TANK_LIQUID_FEED_1 criterion A2 re-verified PASS on the current build
- A3 L0: `mod_completion.py FlowWorks` no longer lists any of the four parts as broken

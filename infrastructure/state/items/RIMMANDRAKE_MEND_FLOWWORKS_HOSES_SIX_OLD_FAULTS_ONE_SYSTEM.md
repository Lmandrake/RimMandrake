## spec

Design Version: FlowWorks 0.1.0 (current, a Problem against the locked bars). Filed by the FlowWorks ticket sweep of 2026-11-22
(RIMMANDRAKE_SWEEP_FLOWWORKS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE), which merged these older tickets into this one, one
cause or one file group. Each old ticket's prose is in `infrastructure/state/items/closed/<ID>.md` and its history in
`rimflow show <ID>`; read the one you work on to its end before you build.

FlowWorks hoses: six old faults in one system (small pump lays unconnected, no replan when walled, stale overdraw, style drift and lost links after reload, levelling budget starves the back row).

## merged tickets

- `SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED` (proposed): [MAJOR] Clicking a small pump lays the hose on the pump without connecting it
  - sweep reading: verified MAJOR (GPT review FB_hose_gss_1.1, confirmed by BENCH 2026-10-23); at HEAD CompHoseReel.ApproachIfOnPort still returns null when the target is Walkable (line ~456) and RM_LiquidPump is 1x1 PassThroughOnly, so a hose laid on a small pump never couples; no commit names the item
  - its check: new FlowWorks SelfTest: Deploy/Move a reel onto an isolated RM_LiquidPump couples to a pump port (red before the fix)
  - files: `src/RimMandrake/FlowWorks/Source/Hose/CompHoseReel.cs`, `src/RimMandrake/FlowWorks/Source/Hose/HosePorts.cs`
- `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS` (validated): FlowWorks: laid hose drawn under a battery and through a wall on the walkthrough save
  - sweep reading: A1 L0 + A2 L2 pass (HW1 run-1, wall-seam fix 849b1674ea); open A3 'a wall built across a laid hose re-plans it' is red live (M2, HOSE_REROUTE_FIX_WALL_IGNORED_ENTIRELY merged here)
  - its check: validation_hose.py M2_gap_walled_reroutes; proof_hose.py --live --no-fresh-map --only walls
  - files: `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs`
- `HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT` (proposed): RM_MapComponent_Hoses.DrawOverBuildings (~line 1724) re-derives a hose's over-building draw only when mapVersion changes; since buildings/trees are patched (HoseWorldPatch) instead of bumping the version, a building placed or removed under a hose that does not reroute leaves that draw stale (pre-existing since HOSE_TICK_REBUILD_ZERO_ALLOC; the old 16k overflow bump refreshed it by accident, gone with HOSE_DIRTY_LIST_WIDEN_NO_OVERFLOW_REBUILD)
  - sweep reading: still keyed on mapVersion at HEAD (RM_MapComponent_Hoses.cs ~1828 c.overVer != mapVersion); a building placed/removed under a hose that does not reroute leaves its over-draw stale
  - files: `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs`
- `HOSE_STYLES_FIX_RELOAD_DRIFT_SEEN` (proposed): FlowWorks SL3_hoses_and_reel_styles_survive FAILs live: hosesEqual False, reelStylesEqual False after save/load (21 hoses)
  - sweep reading: live row SL3_hoses_and_reel_styles_survive FAIL: hosesEqual False, reelStylesEqual False after save/load (21 hoses), testq J20261105T211041Z-b4fe4d.a2; no later pass recorded; save/load drift is ordinary play
  - its check: python3 src/RimMandrake/FlowWorks/validation_hose.py (row SL3_hoses_and_reel_styles_survive PASS)
  - files: `src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs`, `src/RimMandrake/FlowWorks/Defs/Hose/RM_HoseReelStyles.xml`, `src/RimMandrake/FlowWorks/validation_hose.py`
- `HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD` (proposed): BENCH_r17_midrain holds 100 hose rigs but RM_Levelling reads at most links=50 after a load (13-15 on the first cycle, 7 on the FlowWorks list), while the fresh scene of round5 read links=100. Cause unknown: lazy re-lay, working pumps or the mid-rain state could each explain it, and a real save/load loss of levelling links is not ruled out. Evidence D:\ClaudeWork\rimmandrake\levelling_spike\run\*_pt.txt.
  - sweep reading: open diagnosis, no later note: 100-rig save reads links<=50 after load vs 100 fresh; a real save/load loss of levelling links is not ruled out
  - files: `src/RimMandrake/FlowWorks/Source/Machinery/RM_Levelling.cs`
- `LEVELPORTS_FIX_BUDGET_STARVES_BACK_ROW` (proposed): RM_Levelling: when one network component's open ends (up to 16, by reel id) walk more than WalkBudget (120000 squares) in a cycle, hoseCursor restarts at that same hose and OpenEnds returns the same order, so the component's later ports never resolve and never level. Resume or rotate ports within the component (e.g. a per-component port cursor) when the budget turns one away. Found by GPT full-file review (D:\ClaudeWork\rimmandrake\levelling_spike\review_g1c.txt), not seen live.
  - sweep reading: at HEAD RM_Levelling.DugBody still tests walked >= WalkBudget before the keyIndex cache lookup (~line 542), so a component's later ports starve when the cursor restarts on the same hose; no SelfTest covers 3 early + 1 late components
  - its check: FlowWorks SelfTest: 3 early components + 1 late, the late one resolves within N cycles
  - files: `src/RimMandrake/FlowWorks/Source/Machinery/RM_Levelling.cs`

## his words (as recorded on the merged tickets)

- on `HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS`: And the hose is going under the battery and wall... we used to be better than this. (owner, 2026-10-23)

## verify

Acceptance test: none as one command, six causes in one hose system; each fix writes its own red-first SelfTest case (listed per ticket below), and the live rows run on one hose scene.

## criteria

- Each merged ticket above is fixed with its check passing (red first where it is a fix), or dropped with its evidence.
- No locked 0.1.0 bar is loosened or edited by this work.

## refs

item: SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED
item: HOSE_ROUTE_FIX_TUNNELS_UNDER_WALLS
item: HOSE_OVERDRAW_FIX_PATCH_FORGOT_REPAINT
item: HOSE_STYLES_FIX_RELOAD_DRIFT_SEEN
item: HOSE_LINKS_DIAGNOSE_HALF_GONE_AFTER_RELOAD
item: LEVELPORTS_FIX_BUDGET_STARVES_BACK_ROW

# WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES

## proof (corrected 2026-11-17, drain of the retired judge)
The offline half:

    python3 src/RimMandrake/Utils/run_selftests.py --only src/RimMandrake/FlowWorks/selftest_wrecked_links_draw_in.py

Measured 2026-11-17: rc=0, RESULT: GREEN. The code landed at b69a9aa0f1 (`RM_LiquidJoins.cs`,
`RM_IndustrialLiquidWorks.xml`, the FlowWorks DLL rebuilt: wrecked tiers draw in pipes and conduit like
repaired ones).
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/proofs/WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES.txt

## why this is ready, not done — the item's own acceptance is live
`infrastructure/state/live_proofs/WRECKED_LINKS_FIX_RUINS_SNUB_THEIR_PIPES.criteria`, both clauses L2:
  A1 L2 — a pipe beside EACH pipe-tagged ruin links as beside its repaired tier; the ruin has no net role or
          power comp
  A2 L2 — a conduit end beside EACH conduit-tagged ruin hooks in as at its repaired tier; the power net gains
          nothing
"Links" and "hooks in" are readings of the live net graph, per ruin def, on a map. The offline selftest reads
the def and source shape; it cannot build a net.

Next worker: with the game up and the rebuilt DLL deployed, place a pipe and a conduit end beside each tagged
ruin and read the net.

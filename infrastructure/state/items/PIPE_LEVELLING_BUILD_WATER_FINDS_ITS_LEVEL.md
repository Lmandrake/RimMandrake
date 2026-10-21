## spec
Passive gravity levelling between world bodies: `design/RimMandrake/flowworks_pipes_across_pits_design_2026-10-20.md`
§Ruled design P6. Feasibility first (owner: *"Let's see if we can do this"*).
- Scope: a pipe or open hose with its two ends in two liquid bodies moves liquid, no pump, higher surface to lower,
  slowly, until level. **Storage fill stays pump-only** (GSS ruling 3); Dump tanks' gravity drain unchanged
  (`Source/RM_PumpMath.cs:17-24`).
- Surface height and conserved decilitres from the built level-surface solver (`WATER_LEVEL_BUILD_DECILITRES_NOT_NOTCHES`).
  No overshoot, no negative body, no clamping gain; parallel links sum; a same-body link moves nothing; limitless
  sources exchange explicitly.
- **Siphon always** (review answer 10). Flow stops when the intake is exposed; a switched-off hose drains only its own
  contents.
- **No-mix** (review answer 11 points at the canal ruling: owner 2026-10-02, OWNER.jsonl tsn `1790950262957442637`;
  shipped as `RM_MapComponent_Excavation.cs:3326-3327`, `RM_FlowKernel.cs:1992`): different fluids never transfer; a dry
  receiver takes the source's fluid. Bodies stay spatially distinct across a link.
- One map-owned budgeted solver: cached volume/level, batched withdrawals, fixed cadence with elapsed-tick integration,
  convergence tolerance, thresholded repaint, invalidation on topology change.
ESTIMATE 3 to 5 agent-days after a 0.5-day feasibility read of the solver's per-body API.

## verify
- L0: feasibility note — which solver call gives a body's surface and accepts a bounded transfer.
- L1: selftests — 1-cell vs 100-cell basin at different floors converge to one surface, volume conserved; ten parallel
  links; same-body loop moves nothing; crest siphon flows; exposed intake stops; water↔oil link moves nothing; dry
  receiver takes the source fluid.
- L1 benchmark: 325×325 map, two 40,000-cell basins, 200 links: tick time and allocations recorded.
- L2 (live): two ponds of unequal height joined by a hose level out; a pond and an oil pit joined do not.

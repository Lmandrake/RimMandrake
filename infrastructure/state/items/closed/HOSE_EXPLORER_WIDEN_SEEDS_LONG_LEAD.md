# HOSE_EXPLORER_WIDEN_SEEDS_LONG_LEAD

## spec

Found 2026-10-24 by HOSE_SHORT_SPAN_DECIDE_NO_CURVE.
The offline explorer `src/RimMandrake/FlowWorks/Tools/hose_geometry_explore.py` seeds from Dubins paths (24 seeds, 7 radii).
On tankW it reports "no seed" at leads >= 1.4, but C# fits tankW at lead 1.85.
So for that row the explorer's largest lead (0.90) is a LOWER bound, not the true largest lead.

Fix: add seeds (clothoid-blended or C#-style shaped seeds), then re-run `sweep` and refresh `summary.json`.
Until then, read an explorer "shrunk to X" as "fits at least at X".

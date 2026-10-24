# HOSE_MATE_REWIRE_CONTINUOUS_COUPLING

## spec

Found 2026-10-24 by HOSE_SHORT_SPAN_DECIDE_NO_CURVE (the lead-out shrink, owner by card 2026-10-24 "Shorten the lead-out").
Design: `design/RimMandrake/flowworks_hose_geometry_g2_2026-10-23.md` §6 step 6 and §7.

The 12 `--hose-curves` rows mateA/mateB/splice (hose_hard_fittings) still fail with "no mate fits", even with the lead shrunk to 0.6.
MEASURED with the offline explorer `src/RimMandrake/FlowWorks/Tools/hose_geometry_explore.py`:
- a G2 mate exists at lead 1.05, with coupling C=(6.30,10.12) and axis -42.8 deg (explorer `rows`; picture `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\explore\rows.png`);
- with the coupling fixed at any of the C# `MateSlide` discrete candidates, NO fit exists at lead 1.0 or 0.6 (`D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\explore\t4.py`).
So the mate fails because C# picks the coupling from a discrete slide set, not because the geometry is impossible.

Fix: solve the coupling point and axis continuously (jointly with both halves, or a 1-D refine around the best candidate).
Then lower `HoseCurveChecks.Owed` and raise `Floor` (47 of 59 today).

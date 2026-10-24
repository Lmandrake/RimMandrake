# HOSE_FIT_HARDEN_FREE_LENGTH_SHORT_LEAD

## spec

Found 2026-10-24 by HOSE_SHORT_SPAN_DECIDE_NO_CURVE.
The C# G2 fit (`HoseClothoid.SolveCore`) solves at a FIXED length and pads the straight leads up to node multiples (0.5).
On short spans this leaves 3-5 free nodes and violates the bend bounds, so a lay the free-length explorer fits is refused.
Today's workaround (HoseMath.G2Fit/FitAt):
- a short lead uses step 0.25;
- the length is scanned by x{1.0,0.97,1.03,0.94,1.07}.

MEASURED effect: C# shrinks short to lead 0.8, where the explorer needs only 1.15.
Fix: make length a free variable, or make the lead an exact (unpadded) straight, so C# keeps the largest lead the geometry allows.
Evidence: `D:\ClaudeWork\rimmandrake\scratch\hose_geometry_20261023\explore\rows.json` vs `c_run9.txt` (LEADDBG lines).

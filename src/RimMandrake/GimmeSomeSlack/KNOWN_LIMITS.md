# Gimme Some Slack -- known limits

## C1: a cord's geometry may differ from a fresh rebuild after an edit just outside its corridor

The per-edge cache re-plans a cord only when a cell inside its corridor (its strands' bounding box + 3 cells) changed
walkability, but the sprawl looks up to 2.6 cells either side of the planned path. A change 3..7 cells beyond the
corridor can leave a cached cord that a fresh build would draw slightly differently (`Source/Core/CordBuilder.cs`;
`Source/SelfTest/GssFuzz.cs` counts it as a known gap, not a failure).

**Accepted non-goal** (owner, 2026-10-22, on the former walk bar M4 "same polylines after load"): *"I don't value that
the polylines are identical after load. Strike that."* The bar is gone from the walk and from proof_all.py. Widening the
margin to 7 would close the gap but fail the shipped "unrelated edit re-plans only the touched edge" check (M5).

# Gimme Some Slack -- known limits

## C1: a cord's geometry may differ from a fresh rebuild after an edit just outside its corridor

The per-edge cache re-plans a cord only when a cell inside its corridor (its strands' bounding box + 3 cells) changed
walkability, but the sprawl looks up to 2.6 cells either side of the planned path. A change 3..7 cells beyond the
corridor can leave a cached cord that a fresh build would draw slightly differently (`Source/Core/CordBuilder.cs`;
`Source/SelfTest/GssFuzz.cs` counts it as a known gap, not a failure).

**Accepted non-goal** (owner, 2026-10-22, on the former walk bar M4 "same polylines after load"): *"I don't value that
the polylines are identical after load. Strike that."* The bar is gone from the walk and from proof_all.py. Widening the
margin to 7 would close the gap but fail the shipped "unrelated edit re-plans only the touched edge" check (M5).

## C2: while the conduit graph changes on every frame, the cords show the last settled graph

A changed graph is reduced on a worker and adopted only when its inputs equal the current Build's
(`Source/Core/CordBuilder.cs`, Build/StartGraph), so a map whose conduits or machines change on every frame adopts no graph
until the change stops: the cords stay stale (whole, never torn) for the change span, then are fresh within two Builds,
adopting the job the last change started. `Source/SelfTest/SliceGateChecks.cs` SustainedChange pins it: 120 changing
frames, 120 jobs, 0 adopted, 120 stale frames; quiet, 0 new jobs, fresh after 2 Builds. Adopting a near-current graph
would end the starvation but break the equal-inputs guarantee that keeps the frame bit-identical to an unbudgeted Build.

## A wrecked machine's conduit draw-in is drawn by this mod alone

A wrecked machine has no power comp (`RM_RuinDrawsConduit`, `Source/Core/HookupPick.cs` PickRuin), so vanilla prints no wire to it.
With this mod off, or the conduit def unticked in its settings, a conduit ending at a ruin stops at the footprint.

# POND_BED_BUILD_HOLLOW_KEEPS_ITS_SHAPE

Spec: `design/RimMandrake/natural_bodies_as_canals_design_2026-10-11.md` §4 Option B, rulings 2-7; §9 for depth > 4
(that part is `POND_ELEVATION_BUILD_LAKES_RUN_DEEP`).

## state (BENCH night helper, 2026-10-13)

Prerequisites built: `POND_VOLUME_UNIFY_DEEP_NOTCH_YARDSTICK` (a9ecaad78dcb) and `POND_RETURN_LEG_BUILD_WATER_GOES_HOME`
(cd10284be668) — the return leg already takes water into a dry bed square and credits the pond, and a dug bed square
already leaves its pond and comes back on fill-in.

**Step 1 built (offline): the bed-ownership predicate (GPT #9, the design's named blocker for B).**
`RM_MapComponent_Excavation.IsNaturalBed(c)` / `NaturalBedDepthAt(c)`: an O(1) derived `bedGrid` (2 shallow, 4 deep,
from the recorded water), set by recession, cleared by a verified restore and by digging, set again on fill-in,
rebuilt from the bodies on load. Nothing reads it yet, so no behaviour changed. Selftest
`Pond_bed_predicate_is_kept_current`.

**Step 2 NOT built — the hollow itself.** The pit systems (trap, pawn sink, wall faces, lip occlusion, step cost,
spikes) read `ExcavatedDepthAt` (the raw dig grid), and `DepthAt` reads a dry bed as ground. Making a bed a hollow means
both read `NaturalBedDepthAt`, and the bed square's terrain shows the depth. Two things stop that tonight:

1. **Dependency: relative climbing first.** Under today's ABSOLUTE trap rule every dried deep square (D4) is a trap,
   so a drained deep pond becomes a field of traps. The owner's ruling 4 wants the opposite for natural beds (*"Natural
   ponds and lakes when pumped dry would leave just such gradual terrain so no chance to fall in and get stuck"*), and
   the fix is `PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP` (relative step vs creature height), BUILT OFFLINE in
   ae8d38f27c (live climb proof still owed). Step 2 plugs the bed depth into its one seam,
   `RM_MapComponent_Excavation.ClimbDepthAt`, and nowhere else.
2. **Owner decision: what a dry bed looks like.** The design leaves it open (§4 B costs: *"Bed terrain art is needed
   (or reuse `RM_Channel_*` at the bed depth)"*). Cosmetic changes need his permission.
   - (a) Reuse the dug-channel terrains at the bed's depth (`RM_Channel_Mid` for 2, `RM_Channel_Superdeep` for 4) with
     the existing wall faces. No new art; a drained pond looks like a dug pit of the same shape.
   - (b) New bed art (a cracked lakebed per depth band, through the art ledger). Reads as nature, not a dig; costs an
     art pass.
   - (c) Keep Mud on top and show depth only by wall faces and the pawn sink. Cheapest; the bed looks flat until
     someone walks in.

Also owed in step 2 (design §7 #8/#9): a canal brim-full beside a bed must run back into the pond (the kernel credits
the stock, never a dug cell), and rain on a bed square stays in Refill's rain term only (it already does: `ApplyRain`
walks dug cells).

## criteria
- O1 L0: `Pond_bed_predicate_is_kept_current` passes (selftest_flowworks_stock.py 292/292)
- O2 L0: step 2 — DepthAt and the pit systems read a dry bed's depth; selftests pin every reader
- A1 L2: a drained pond reads as a hollow of the pond's shape (shallow rim 2, deep middle 4); a colonist walks out of it
- A2 L2: pumping water back re-wets the bed last-in-first-out to the exact old shape
- H1 L4: the owner picks the bed look (a/b/c above)

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
rebuilt from the bodies on load. Selftest
`Pond_bed_predicate_is_kept_current`.

**Step 2: built offline 2026-10-14, see the next section.**

## state (BENCH, 2026-10-14) — step 2 BUILT OFFLINE, live proof owed

Nothing deployed, bridge untouched. Both blockers were cleared: the relative climb (`PIT_POCKET_GRID_BUILD_SLOPES_NEVER_TRAP`,
ae8d38f27c) and the owner's look, (b) by card: cracked lakebed per band (art installed b15b89ddc1).

**Built (FlowWorks, behind the new Mod Setting `pondBedHollowEnabled`, default ON; OFF = a dried square is flat mud, as before):**
- TerrainDefs `RM_Lakebed_Shallow` (bed 2: pathCost 45, Walkable/Light/Diggable, as `RM_Channel_Mid`) and `RM_Lakebed_Deep`
  (bed 4: pathCost 300, Standable, Light, as `RM_Channel_Superdeep`); Soil-tagged so a dry bed can still be dug (ruling 6).
  Deliberately NOT in `RM_ExcavationDepth.DepthOfDryTerrain`, so no legacy rehydrate reads a dried pond as a dug channel.
- `HollowDepthAt` (= `RM_Volume.HollowDepth`: dug depth, else the dry bed's depth when on). `ClimbDepthAt` returns it (the
  PIT_POCKET seam), `CopyClimbDepth` overlays the beds into the pocket grid, `ClimbCellCount`/`ClimbCells()` replace the dug-only
  early-outs (trap AnyHole/held/veto, fall detector, interim pathing). The absolute (relative OFF) branch still reads dug only,
  so a drained deep pond is never a field of traps.
- Visual readers read the hollow: pawn sink (`RM_PitDepthDraw`), lip occlusion, wall faces, step cost. Spikes, scorch, flow doors
  and the liquid surface stay on the dug depth (they belong to dug cells).
- `DepthAt` reads a dry bed's depth (FillAt stays 0, an empty bed). Every pour path already guards on `IsExcavated`, so a bed
  never takes canal water; `CanLiquidEnter` keeps its old meaning (dug or natural liquid) so the legacy flood never writes
  terrain onto a bed.
- `bedGrid` has one writer, `SetBed` (keeps `bedCellCount` and bumps the climb generation).
- Recession lays the lakebed at the bed depth; Restore puts the recorded water back LIFO (unchanged, exact); a filled-in
  detached bed comes back as lakebed; on load an old save's bare-mud bed squares are relaid as lakebed.
- §7 #8: `RunIntoBeds` after each kernel pulse — a dug square whose water stands above a neighbouring dry bed's floor
  (`RM_Volume.RunsIntoBed`; brim-full always) gives one level per pulse to the POND's stock via the return leg, checked before
  the take. Rain on a bed stays Refill's alone (`ApplyRain` still walks dug cells only).

Selftests (FlowWorks C#): `Pond_bed_hollow_math`, `Pond_bed_hollow_round_trip_is_lifo_exact`, `Pond_bed_hollow_readers_pinned`
(every reader pinned, O2); step-1 pins moved to `SetBed`; toggle registry 116.

**Gaps left (not in this step):** digging a dry bed still starts the cut at the surface (D 1), i.e. raises a 2/4-deep hollow
square to D 1, and filling it back in to D 0 re-hollows it (ruling 6's bookkeeping is unchanged); a bed-aware dig/fill-in is a
design question for the owner. Wall faces for a bed use the neighbour's terrain as material (water/lakebed), not soil.

## live proof owed
- A1: drain a pond with a shallow rim around a deep middle; it reads as a hollow of its shape (lakebed, shallow rim 2 / deep
  middle 4 by `jawa/flowworks_excavation_report` or the climb proof read), and a colonist standing in the middle walks out.
- A2: pump water back; the bed re-wets last-in-first-out to the exact old water terrain (compare a before/after terrain dump).
- Also worth one row: a brim-full canal beside a dry bed loses levels to the pond until its surface reaches the bed floor.

## criteria
- O1 L0: `Pond_bed_predicate_is_kept_current` passes (selftest_flowworks_stock.py 292/292)
- O2 L0: step 2 — DepthAt and the pit systems read a dry bed's depth; selftests pin every reader — done (offline)
- A1 L2: a drained pond reads as a hollow of the pond's shape (shallow rim 2, deep middle 4); a colonist walks out of it — OWED
- A2 L2: pumping water back re-wets the bed last-in-first-out to the exact old shape — OWED
- H1 L4: the owner picks the bed look (a/b/c above) — done: (b), by card 2026-10-13

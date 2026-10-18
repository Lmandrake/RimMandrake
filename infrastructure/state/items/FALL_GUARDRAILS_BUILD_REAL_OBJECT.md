## spec
Owner, 2026-10-18 (V3 card, note tsn 1792338532028995451 on `FLOWWORKS_DEPTH_REBUILD_ONE_BIG_DIG`): *"build guardrails as
a real object with real need (and support existing fences acting this way too)."*

The lethal half (deep falls can kill) is split off and built as `FALL_DAMAGE_BUILD_DEEP_DROPS_KILL` (0e4e253e2). What
remains here is the rail itself.

### design note (FOUNDRY, 2026-10-18; PROVISIONAL, for the build pass)
- **The need.** Since falls can kill, an unguarded lip is a hazard; a rail is the answer to it.
  Falls reach the pawn through three doors today (all in FlowWorks `Source/Superdeep/`):
  `RM_PitPathing.cs` ~565 (a landing that drops past the pawn's climb: knockback, skip, flyer landing),
  `RM_SuperdeepTrap.cs` ~645 (a walked arrival that falls: raiders and animals stepping off the lip, the
  `trapTriggerEnabled` trap), and `Pits/Building_PitCover.cs` ~217 (a cover giving way). A rail guards the
  first two; a cover giving way is a fall from ON the pit, which no rail can stop.
- **What a rail does.** A pawn crossing from a railed lip cell into a sheer drop (the step `ArrivalDropsTooFar` /
  `IsFallingArrival` would make a fall) does not fall: a walked step is refused (pathing cost: impassable over that
  edge, like a wall edge, never a whole-cell wall, so colonists still walk along the lip); a knockback or push stops at
  the rail. The jump-in order (`TryJumpInto`) still works: jumping is deliberate.
- **Which edge.** A rail is one cell on the lip and guards every edge from that cell to a lower neighbour by a sheer drop
  (`RM_RelativeRulesMath.StepIsAFall`) — the same edge set spikes and pit covers use (`RM_SpikeUtility.TallestWallOver`).
- **Existing fences count.** Any building whose def is a vanilla fence (`ThingDef.building.isFence`, Core
  `FenceBase` children, plus mods' fences that set it) acts as a rail on its cell. One predicate
  `RM_FallRails.IsRail(Map, IntVec3)`: our rail OR `isFence`. Vanilla fences block only animals' pathing; on a lip
  they additionally stop falls for everyone.
- **The object.** `RM_PitGuardrail`: a cheap, low, linking 1×1 building (steel or wood, stuff-made), buildable only on
  a cell beside a sheer drop (a PlaceWorker reading the same edge set), does not block sight or shots, does not hold
  pawns out of the pit (ladders are still the way in and out). Art: reuse vanilla fence art for the first pass
  (cosmetic changes need the owner's permission; a bespoke look is his call).
- **Raiders.** Raider AI (ruled the same day: go around, breach if no way, jump packs, ladders) is unaffected; a rail is
  not a breach target unless it stands on the only route.
- **Mod Settings.** `pitGuardrailsEnabled` (master), `fencesAreRails` (on), both labelled; defaults = shipped.
- **Kernel + tests.** Pure: `RM_FallRailMath.FallBlocked(bool railOnFrom, bool deliberateJump, bool stepIsFall)`;
  SelfTest cases for the edge set, the fence rule, the jump exception.

## criteria
- L1: the guardrail is in the build menu, places only beside a sheer drop; settings show and round-trip.
- L2: a raider walking toward a railed 7 m lip does not fall in; the same raider at an unrailed lip falls; a colonist
  pushed by knockback against a railed lip stops; a vanilla fence on the lip does the same; "jump into pit" still works.

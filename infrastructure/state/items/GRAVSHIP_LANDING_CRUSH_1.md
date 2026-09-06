# GRAVSHIP_LANDING_CRUSH_1 — crush-landing + unblockable-thrust patches built, patches verified attached

Owner, 2026-09-05, verbatim: *"We absolutely need mods that let the ship
just plop down on top of small barriers and blockages or a ship that size
will never find clear landing. Major mountains should be a no no as is deep
water or lava but otherwise it should just crush stuff and be done with it.
Also we should let it take off even if the thrusters are blocked. The grav
engine just goes straight up before the thrusters are even needed."*

## What was checked before writing any code

**An existing mod was checked first**, per the item's own instruction to
prefer one if well-maintained: Steam WS `3525655208`, "Just F*King Landing"
(`JustFKLanding.dll`). Decompiled it (not guessed) — its landing patch
(`Gravship_IsValidCell_Patch`) makes **every** cell valid except out-of-
bounds/no-build-edge, with no distinction for terrain at all — it would
also let a gravship land in lava, deep water, or on a mountain, which the
owner explicitly wants kept as hard refusals. Its takeoff patch
(`GravshipController_InitiateTakeoff_Patch`) is a no-op: the postfix body
is a single unused field read, no actual behaviour change. Not a fit for
either requirement — wrote our own instead.

**The real vanilla mechanism was decompiled directly** (live
`Assembly-CSharp.dll`), not guessed:
- `RimWorld.Designator_MoveGravship.IsValidCell(IntVec3, Map)` (private
  static) — the landing validation. Checks, in order: bounds, no-build-edge
  area, `map.landingBlockers` zones, **roofed** (this is what actually
  catches "major mountain" — natural rock roof), fogged, a blocking Thing on
  the cell (a Building without `canLandGravshipOn`, or anything flagged
  `preventGravshipLandingOn`), then `GenConstruct.CanBuildOnTerrain` against
  `TerrainDefOf.Substructure` — **this last check is what already refuses
  deep water and lava**, with zero code of ours needed to keep it. Plants/
  trees never hit the Thing-refusal branch at all (they aren't Buildings) —
  vanilla already auto-destroys them on landing
  (`InitiateLanding`'s `DestroyTreesAroundSubstructure` call), which is the
  existing precedent this patch extends to other small obstacles.
- `RimWorld.CompGravshipThruster.Blocked` (getter) — feeds `CanBeActive`,
  which every launch-readiness/link consumer keys off. Patching this one
  property, rather than each consumer, is the narrowest fix point.

## What was built

`src/RimMandrake/GravshipCrushLanding/` (`mandrake.rm.gravshipcrushlanding`),
three Harmony patches, each changing only the one branch named above and
leaving every other vanilla refusal untouched:

1. `Patch_GravshipIsValidCell` — full reimplementation of `IsValidCell`
   matching vanilla exactly, except a blocking Thing (per
   `CrushLandingUtility.IsCrushableBlocker`, shared with #2 so the two never
   drift apart) is treated as passable instead of refusing. Hostile/
   humanlike pawns still refuse, unchanged.
2. `Patch_GravshipInitiateLanding_CrushObstacles` — prefix on
   `WorldComponent_GravshipController.InitiateLanding`; reads the private
   `landingMarker` field via `AccessTools.Field` (same access pattern the
   checked-and-rejected reference mod used), computes the real footprint
   (`landingMarker.GravshipCells + landingPos`), and destroys every
   `IsCrushableBlocker` Thing sitting in it, with a dust puff to match
   vanilla's own tree-destroy flourish.
3. `Patch_GravshipThruster_NeverBlocked` — prefix on
   `CompGravshipThruster.Blocked`'s getter, always `false`.

Built clean, zero warnings: `RimMandrakeGravshipCrushLanding.dll`.

## Verification done — and what's still owed

**Deployed and loaded clean** on the minimal test list (`brrainz.harmony` +
core DLCs including Odyssey + this mod): `[RimMandrake.GravshipCrushLanding]
ready: crush-landing + unblockable-thrust patches active.` logged, no
config errors naming it.

**All three patches confirmed attached to the exact right methods**, live,
via `jawa/harmony_patches`:
```
Designator_MoveGravship.IsValidCell        -> Patch_GravshipIsValidCell.Prefix
WorldComponent_GravshipController.InitiateLanding -> Patch_GravshipInitiateLanding_CrushObstacles.Prefix
CompGravshipThruster.get_Blocked           -> Patch_GravshipThruster_NeverBlocked.Prefix
```
This proves the Harmony targeting resolved correctly (including the
private-static overload disambiguation and the property-getter target) —
real evidence the patches are wired to the right code, not just that the
DLL loaded.

**NOT yet done — a full behavioral live test**: actually designating a
landing over real obstacles and confirming they're crushed rather than
refused; actually blocking a thruster and confirming launch still succeeds.
This needs a live gravship, a prepared obstacle field, and driving the
actual landing/launch UI flow through the bridge — a bigger live-testing
setup than this pass reached. Cut short honestly: the bridge was reassigned
to BENCH by the owner mid-session before this could be attempted, and it
is not being retaken to finish this — that's the owner's call, not mine to
route around. **Left `doing`, not closed** — the code is real and grounded
in the decompiled mechanism, but "the patches attach" is not the same
proof as "a raider outpost gets flattened on landing," and this project's
own doctrine says not to claim the latter without having watched it happen.

## criteria
- [x] Existing-mod check done first, by decompile, and correctly rejected
      (too permissive on terrain; takeoff patch is a no-op).
- [x] Both patches written against the real decompiled vanilla mechanism,
      not guessed, with the terrain/mountain/water/lava refusals
      deliberately left untouched.
- [x] Builds clean; loads clean; all three patches confirmed attached to
      the correct methods live.
- [ ] Full behavioral proof: an actual crushed-obstacle landing and an
      actual blocked-thruster launch, watched happen on a live map.

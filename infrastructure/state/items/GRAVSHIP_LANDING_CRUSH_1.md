# GRAVSHIP_LANDING_CRUSH_1 — RETIRED our own mod (owner ruling); using Land On Anything instead

## RULING 2026-09-06 (owner, verbatim): "We should not have our own mod, that was a mistaken filing. Use the one I downloaded."

Our custom `mandrake.rm.gravshipcrushlanding` mod is RETIRED — source
(`src/RimMandrake/GravshipCrushLanding/`) and the deployed copy both
deleted (git history has it if ever needed). The requirement itself is
unchanged; the implementation is now **Land On Anything**
(`nep.landonanything`, Steam WS `3545384484`) per the research below,
with `allowedToSqishRoofs` and `allowedToLandOnAnyTerrain` forced OFF
from their (wrong, permissive) defaults to actually match the ruling.
`mf.jfklanding` comes off the active list — never a fit, already proven
so twice over.

---

_History below kept for the investigation trail — the custom-mod plan itself is dead, not the requirement it was answering._

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

## Second candidate mod found, owner-installed 2026-09-06

Owner subscribed Steam WS `3545384484`, **"Land On Anything"**
(`nep.landonanything`, author Nepenthe) — downloaded to disk, NOT yet in
`ModsConfig.xml`/active. Read its actual C# source (shipped in the
Workshop download, not decompiled) — a real, mature, settings-driven
implementation:

- Patches the **same private method we do** —
  `Designator_MoveGravship.IsValidCell` — via the identical
  `AccessTools.Method` reflection approach. **Direct collision risk if
  both mods are ever active together**; only one can safely own this
  patch point.
- Its terrain/roof/fog/thing/pawn refusals are each gated behind its own
  mod-settings toggle, defaulting (presumably) to preserving vanilla
  refusals — same `GenConstruct.CanBuildOnTerrain(TerrainDefOf.Substructure)`
  check we use for water/lava, same `cell.Roofed(map)` check we rely on
  vanilla for mountains. **With `allowedToLandOnAnyTerrain` and
  `allowedToSqishRoofs` left off, this mod satisfies the same ruling ours
  does** — not verified live, read from source only.
- Patches thrusters via `CompGravshipThruster.IsBlocked`/`.IsOutdoors`
  (two different members than the `CompGravshipThruster.Blocked` getter
  our mod patches) — **not yet confirmed whether these are the same
  vanilla check under two names or two genuinely different code paths**;
  worth a RimSage check before assuming equivalence.
- **Materially different behavior from ours on the crushed obstacle
  itself**: we DESTROY it outright
  (`Patch_GravshipInitiateLanding_CrushObstacles`); this mod DAMAGES it
  (fixed 25-30 or a configurable fraction of max HP via `DamageDefOf.Crush`)
  — a building can survive a landing on this mod, never on ours. It also
  does more than either the owner's spec or our build: a recursive
  radius-2 "clear ring" around the ship (damages/despawns non-plant,
  non-pawn things adjacent to the footprint, not just under it), automatic
  steam-geyser removal under the footprint, mote VFX, and a shuttle-landing
  variant of the same permissiveness. None of this was requested, but none
  of it violates the ruling either.
- Also patches `RoyalTitlePermitWorker_CallShuttle.GetReportFromCell`
  (shuttle landing), a surface our own mod never touched.

**Also newly confirmed, independent of the new mod**: on the CURRENT live
full-596 list, **only `mf.jfklanding` is active** — the mod this item
already decompiled and rejected as unfit (permits landing in lava, deep
water, and on mountains; its takeoff/thruster patch is a no-op). Our own
`mandrake.rm.gravshipcrushlanding` is built and proven-loading but is
**not currently active on the full list** (only ever run on the minimal
test list). So right now, tonight, the owner's own ruling
("only mountains, deep water and lava should block") is **not actually
enforced** on his live save — `mf.jfklanding` would wave a landing through
anywhere.

**Left for the owner's call, not decided here**: destroy-outright (ours)
vs. damage-with-possible-survival (Land On Anything) is a real gameplay-
flavor choice, not a criteria question — both satisfy the stated ruling.
Whichever is chosen, `mf.jfklanding` needs to come OFF the active list
first (it's currently the only one of the three actually running, and it's
the one everyone already agrees is wrong).

## Live-verified 2026-09-06, post-restart on the corrected full list

**Mod swap confirmed clean via `jawa/harmony_patches`**: `mf.jfklanding`'s
patches are gone entirely. `nep.NepLOA`'s prefixes are attached to the
right targets — `Designator_MoveGravship.IsValidCell` and
`CompGravshipThruster.IsBlocked` — matching the source read. Our own
retired mod's `CompGravshipThruster.get_Blocked` patch is confirmed gone
(no patches on that member at all now). `harvest_log.py` shows zero config
errors naming either mod, patch-failure count unchanged from baseline+2
(the pre-existing StarWarsPatches finding, unrelated).

**New collision found, not previously known**: `vanillaexpanded.gravship`
(Vanilla Gravship Expanded, already active) ALSO prefixes
`Designator_MoveGravship.IsValidCell`, same priority (400) as
LandOnAnything's prefix. Both will run; same-priority Harmony ordering is
load-order-dependent, and whichever runs second can overwrite the other's
`__result`. **Not investigated further this pass** — VGE's own patch
content wasn't decompiled (scope/time), so it's unknown whether it
conflicts with the crush-landing behavior or is compatible. This existed
before today's change too (VGE was always active alongside whichever of
the three landing mods was running) — not a regression introduced here,
but newly visible now that the right question is being asked.

**Settings forced off their wrong-permissive defaults, and PROVEN durable**:
`allowedToSqishRoofs` and `allowedToLandOnAnyTerrain` set to `false` via
`rimworld/update_mod_settings`, then verified two ways — read back
immediately, AND via `rimworld/reload_mod_settings` (discards in-memory
state, re-reads from `Config/Mod_3545384484_LandOnAnythingMod.xml`) — both
confirm `false`. The settings file itself omits both fields (RimWorld's
Scribe skips writing bool fields that equal `default(bool)` == `false`),
which looked like a possible silent-failure at first glance but is
confirmed CORRECT: the reload-from-disk round-trip proves the omission
still loads back as `false`, not the C# field's `true` initializer.
`allowedToLandOnThings=true` and `unblockableThrusters=true` (defaults,
unchanged) — matches the crush-and-launch-anyway requirement.

**Still not done**: the actual live-behavioral test (a real landing over a
small obstacle, a real refused mountain/lava/water tile, a real blocked-
thruster launch) — not attempted this pass. `gravship_scratch_d.rws`
exists and is the obvious vehicle for it next time the bridge is free for
it.

## criteria (updated)
- [x] Existing-mod check done first, by decompile, and correctly rejected
      (too permissive on terrain; takeoff patch is a no-op). — original,
      superseded approach; new approach used a REAL maintained mod instead
      of building our own.
- [x] `nep.landonanything` patches confirmed attached to the correct
      vanilla methods, live, via `jawa/harmony_patches`.
- [x] Settings forced to match the ruling and proven durable across a
      settings reload (not just an in-memory echo).
- [ ] Full behavioral proof: an actual crushed/damaged-obstacle landing,
      an actual terrain refusal, and an actual blocked-thruster launch,
      watched happen on a live map.
- [ ] VGE collision on `IsValidCell` — unresolved, not chased this pass.

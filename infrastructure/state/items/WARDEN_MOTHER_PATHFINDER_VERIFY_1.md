# WARDEN_MOTHER_PATHFINDER_VERIFY_1 — live-verify the warden mother's water-only movement and load cleanly

Caused by `WARDEN_MOTHER_BEFRIENDING_1`.

## what

`WARDEN_MOTHER_BEFRIENDING_1` shipped `RM_WardenMother` (ThingDef + PawnKindDef,
`src/RimMandrake/Miasma/Defs/ThingDefs_Races/RM_WardenMother.xml`) and the water-only
movement constraint that item's own text calls "the single new mechanism" —
`RM_CompWaterLocked` (tick-based backstop), `RM_JobGiver_AnchorWander`'s
`wanderDestValidator` (water-only wander destinations), and
`RM_JobGiver_AnchorDefense`'s `ExtraTargetValidator` (tolerance exclusion + water-
adjacency requirement on targets). `validate_patch.py --defs` passes clean (0
errors) and the assembly compiles clean, but **none of this has been observed
running**, and this item's own parent explicitly names three engine questions as
UNMEASURABLE without a Desktop pass:

1. Whether a pawn's pathing can be constrained to a terrain set at all.
2. Whether a `bodySize` this large (8, bigger than the evicted `AA_OvergrownColossus`
   at 6) paths through shallow water without breaking.
3. Whether the duty-consultation seam (`RM_ThinkTree_AnchorBehaviors`'s
   `insertTag="Animal_PreMain"`) actually fires for this PawnKindDef the way it
   already does for `RM_ThinkTree_StrandingBehaviors`/`RM_JobGiver_ReturnToWater`.

## why this is its own item, not folded into the parent

Per `rimworld-modding`'s own handoff rule: a live check is owed only to a mechanism
never once observed running. The water-only constraint is exactly that — genuinely
new C#, never exercised against the real engine. Per this project's standing rule
(said three times, 2026-09-25) against unattended live-bridge hunts for a subtle
visual/behavioural property: this is not a flight-animation hunt, but it IS a new
movement-constraint mechanism, so the same caution applies — verify with the owner
able to look, or via a deterministic state read, not a solo unattended bridge
session guessing at "did she stay in the water."

## spec (draft)

1. **Cold-load or minimal-list check first**: deploy, load (minimal list + Miasma
   tiled quicktest world per `rimworld-load-round`), confirm **zero new Config
   errors** in `Player.log` naming `RM_WardenMother`, `RM_CompWaterLocked`,
   `RM_ThinkTree_AnchorBehaviors`, `RM_AnchorGuard`, or `RUT_StrandedDeformation`.
2. **Scatter and observe**: trigger `RUT_GenStep_CrecheScatterer` on a Miasma
   quicktest map (or read the map after normal gen), confirm a warden mother spawns
   anchored to a `RUT_CrecheMarker` in brine-side shallow water.
3. **State-read, not a screenshot hunt**: over N game-hours, poll her
   `Pawn.Position` via the bridge and assert every sampled cell is water
   (`TerrainDef.IsWater`) — a deterministic, scriptable check, not a visual
   sighting. This is the "verify via state read" pattern
   `no-unattended-flyer-live-testing` already establishes for a different
   mechanism; it applies here too.
4. **Duty-seam check**: confirm via bridge/log that she actually fights or wanders
   (i.e. `RM_JobGiver_AnchorDefense`/`RM_JobGiver_AnchorWander` are winning jobs)
   rather than falling through to a default Animal AI with no anchor behaviour.
5. **The known gap**: confirm whether a melee chase (`JobDriver_AttackMelee`,
   unconstrained by the wander/target validators) can compute a path crossing one
   land cell to reach a shoreline target before `RM_CompWaterLocked`'s next tick
   check fires. If it can and it matters, that is the case for building the real
   pathfinder-level `PathRequest.IPathGridCustomizer` this item's own code
   comments flag as deliberately NOT attempted blind.
6. Only once (1)-(4) pass would this project's own idiom call any of this
   MEASURED; until then treat it as "built, offline-verified, not yet observed."

## Watch out

- Do this WITH the owner present if it becomes a live-bridge visual session, per
  the flyer-testing precedent — an unattended solo bridge hunt for "did she leave
  the water" is the same shape of unproductive session that rule already
  forbids for flight.
- `RM_CompWaterLocked`'s own header names exactly what it does and does not
  guarantee — read it before writing the verify script so the test asserts the
  right thing.

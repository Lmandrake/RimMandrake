# GREENTIDE_PLANT_SIGHT_BLOCK_ENGINE_1 — make a Plant actually block line of sight

## why this exists

`GREENTIDE_UNDERSTORY_PLANT_ROSTER_1` shipped all seven invented Greentide understory plants
(brakkel/tumbel/sarquin/phorrik/wollick/maddrick/illurin) per the owner's 2026-09-22 ruling that
they must be "tall and broad enough that a colonist cannot see over or past them." That item's own
spec required confirming the mechanism before authoring rather than guessing a field. It was
confirmed — **negative** — against the decompiled 1.6 source via RimSage, 2026-09-26. See that
item's own closing section for the full method; the summary:

🔴 **A `Plant` ThingDef cannot block line of sight in vanilla RimWorld, at any `fillPercent` value.**
`GenSight.LineOfSight` → `IntVec3.CanBeSeenOverFast` (`Source/Verse/GenGrid.cs:227`) reads only
`c.GetEdifice(map)` (`Source/Verse/GridsUtility.cs:443` → `map.edificeGrid[c]`), and the edifice
grid is populated exclusively by things whose `def.IsEdifice()` is true — which itself requires
`category == ThingCategory.Building` (`Source/Verse/EdificeUtility.cs`). A Plant's category is
always `Plant`, so it structurally cannot occupy the edifice grid and is invisible to the LOS check
regardless of `fillPercent`. `fillPercent` on a Plant still does something real (ranged-combat
cover via `CoverGrid`/`CoverUtility.BaseBlockChance`, and full-reveal-radius behaviour in
`FogGrid.Unfog` above 0.99) — but none of that is "cannot see over or past it."

⇒ The seven plants ship today with `fillPercent` set proportionate to their described bulk (real
cover, not decorative), but the ruling itself is unmet. This item is the engine work to actually
meet it.

## what it needs to do

Make a Plant (or a tagged subset of Plants, via a modExtension/comp so it is opt-in per-def rather
than global) actually block a colonist's line of sight, in the same functional sense
`GenSight.LineOfSight`/`CanBeSeenOverFast` currently reserve for full-fillage Buildings.

## spec

1. **Choose the mechanism** — most likely a Harmony patch on `GenGrid.CanBeSeenOver(IntVec3, Map)`
   / `CanBeSeenOverFast` (or the lower-level `Building`-only overload they call), postfixing in an
   additional check: is there a Thing at this cell carrying an opt-in marker (a modExtension or a
   comp) whose growth/fillPercent currently qualifies it as a sight-blocker? A comp-driven check
   keeps this generic (content-blind), matching the project's own established pattern
   (`RM_CompPlantAlarm` is the precedent cited by `GREENTIDE_WASP_SWARM_1` for the same "build the
   shared mechanism once" posture) — do not hardcode the seven Greentide defNames into the patch.
2. **Establish the side effects before shipping** — this item's parent already flagged all three,
   unresolved:
   - Does it interact correctly with ranged combat LOS (`Verb.CanHitCellFromCellIgnoringRange`,
     `ShootLeanUtility`, `AttackTargetFinder`) — should a sight-blocking plant also block a shot, or
     only a colonist's view? These are different call sites in vanilla and may want different
     answers.
   - Pathing: `CanBeSeenOverFast` is also consulted by pathing/avoidance code
     (`AvoidGrid`, `PawnPathUtility`) — confirm a sight-blocking Plant does not silently become
     impassable or unpathable as a side effect of whatever hook is chosen.
   - The player's own visibility of their colonists: does this affect the player's camera/rendering
     at all, or only AI/mechanical LOS? State which, explicitly — "the player can't see their own
     colonist" was the parent item's own named risk.
3. **Performance**: `CanBeSeenOverFast` is a hot path (called per-cell on every LOS check in the
   game, including every ranged attack evaluation). A postfix that does a full cell-contents scan
   per call needs to be cheap — consider a dedicated grid (a `bool[]`/bitarray keyed by cell,
   maintained incrementally on spawn/despawn/growth-stage-change) rather than a live scan, mirroring
   how `CoverGrid`/`FogGrid` themselves are maintained as grids rather than recomputed per query.
4. **Wire the seven Greentide understory plants to opt in** once the mechanism exists
   (`src/RimMandrake/Greentide/Defs/ThingDefs_Plants/RM_Greentide_UnderstoryRoster.xml`) — this is
   the payoff, not a separate pass.
5. Mod Settings toggle per the standing every-mod-ships-settings rule, since "how much of the map
   is unreadable" is exactly the kind of number-is-the-experience case that rule names.

## verify

A colonist standing on one side of a patch of (e.g.) `RM_Brakkel` genuinely cannot see a colonist or
hostile standing on the other side, confirmed live — not assumed from a def. Ranged combat, pathing
and the player's own camera behave as decided in spec step 2, and that decision is recorded here,
not left emergent. Performance is unaffected in a stress test (a Greentide map at `plantDensity
0.99`, per `GREENTIDE_BIOME_DENSITY_1`, is exactly the adversarial case).

## criteria

A colonist walks toward a wall of understory plants and the game genuinely stops them from seeing
what's on the other side — the owner's own bar, "tall and broad enough that a colonist cannot see
over or past them," met mechanically rather than only in the description text.

## Watch out

- ⛔ Do not hardcode the seven Greentide defNames into the patch — this is exactly the kind of
  mechanism the project keeps needing more than once (rooted ambushers, hive alarms, and now sight
  blockers are all "a plant/Thing does X to nearby colonists/pawns" content-blind comps). Build it
  generic.
- ⚠️ This is real engine risk, not a content-authoring task — a naive Harmony patch on a hot LOS
  path is exactly the shape of change that can silently tank performance or break shooting/AI in a
  way that is easy to miss in a quick test and expensive to find later. Budget a real test pass,
  not a five-minute check.
- 🔴 No unattended live-bridge hunt for "does this look blocked" — per the flyer live-testing rule's
  general lesson, verify via a deterministic state read (can pawn A's LOS-check function see pawn
  B?) rather than a visual screenshot hunt. A human-judged "does the jungle read as hidden" pass is
  separate and belongs with the owner or a `rimworld-live-review` session.

## built — mechanism and the step-2 decisions (FOUNDRY, 2026-09-26)

**Where:** `mandrake.rm.creaturebehaviors` (the shared kit Greentide already depends on, home of
`RM_CompPlantAlarm`), which now takes a Harmony dependency. `RM_CompProperties_SightBlocker`
(`minGrowth`, default 0.5; non-plants always count) + `RM_CompSightBlocker` register cells into
`RM_MapComponent_SightBlockGrid` (a `byte[]` per-cell count, updated on spawn / despawn /
`CompTickLong` growth crossing). `RM_SightBlockPatches` postfixes **both real
`GenSight.LineOfSight` overloads**, replaying vanilla's exact cell walk against that grid. All
seven understory rows opt in.

**Why not a postfix on `CanBeSeenOverFast` (spec step 1's guess):** it is a tiny static the JIT
may inline into `GenSight` (patch silently never runs); `GenExplosion`, `Verb_ShootBeam`, the
Burner ability and `ExitMapGrid` read it too (bushes would stop blasts and beams); and it cannot
tell the line's endpoints, so a pawn standing IN a thicket cell would go blind and invisible.

**Scope — the postfix only acts while a "pawn is looking" call site is on the stack** (a
`[ThreadStatic]` depth counter raised by prefix/finalizer pairs). Every other `LineOfSight`
caller — fire spread, the explosion cell set, short circuits, facility linking, foam turrets,
spawn-cell finders, GenSteps, social-chat range — stays byte-for-byte vanilla.

Decisions (step 2):
- **Ranged combat: BLOCKED by default.** In RimWorld, sight *is* the shooting LOS — blocking
  "view" alone would change almost nothing a player could notice, so the ruling only means
  something if you cannot target what the thicket hides. Hooked: `Verb.CanHitCellFromCellIgnoringRange`
  (every shot, AI or player-ordered), `AttackTargetFinder.CanSee`, `ShootLeanUtility.CellCanSeeCell`.
  Setting "Also blocks ranged fire" turns only this group off. Shooters never *lean* around a
  plant as if it were a wall corner (lean reads `CanBeSeenOver` directly, untouched).
  Perception group (always on with the mechanism): `PawnLocalAwareness.AnimalAwareOf`,
  `ThoughtUtility.Witnessed`, `PawnObserver.PossibleToObserve`, `FleeUtility.ShouldFleeFrom`.
- **Pathing: UNAFFECTED.** Nothing changes passability or pathCost; `AvoidGrid` reads the
  `Building` overload of `CanBeSeenOver`, never this grid. The plants stay walkable at their
  own pathCost 42.
- **Player camera: UNAFFECTED.** RimWorld has no LOS-driven rendering; `FogGrid` unfogs by
  region flood, not `LineOfSight`. The player always sees every pawn on unfogged ground.
- **Endpoints:** the viewer's own cell and the target's cell never count — a pawn standing in
  one thicket cell is seen, and sees out; what hides it is thicket *between*.

**Settings** (Creature Behaviors): master on/off, "also blocks ranged fire", and thicket depth
1–4 plants needed to hide something (the "how much of the map is unreadable" number).

**Verification instrument:** dev menu RimMandrake > "Sight-block probe" — a deterministic state
read: stages two colonists 6 cells apart, asks the real engine functions (CanSee, a revolver's
`CanHitTarget`, `Witnessed`, `CellCanSeeCell`) with and without a mature blocker between, asserts
plain `LineOfSight`, the explosion cell set and walkability are unchanged, exercises growth
threshold, endpoints and all three settings, cleans up, and logs `PASS n/n`. "Sight-block
stress" times 20,000 `LineOfSight` calls in and out of a sight scope on the current map.

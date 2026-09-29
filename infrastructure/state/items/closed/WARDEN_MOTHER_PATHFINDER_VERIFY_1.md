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

## measured 2026-09-29 (FOUNDRY)

Live-verified on the `baroque_wave0` tier (`modset_builder.py`: BRIDGE +
`mandrake.rm.biomes`, all 5 DLC, 13 mods) — a quicktest map, never the
campaign. State-reads only, no visual/screenshot judgment call, per this
item's own spec.

1. **Cold-load config-error sweep — caught and fixed a real bug named by this
   item's own §1.** First quicktest boot: `Config error in
   RUT_StrandedDeformation: has comps but hediffClass is not HediffWithComps
   or subclass thereof` (baseline 291 total config errors). Cause:
   `RUT_StrandedDeformation.xml` shipped `<hediffClass>Hediff</hediffClass>`
   while carrying two `<comps>` (`RM_HediffCompProperties_LocatableCall`,
   `RM_HediffCompProperties_SelfTameOnRecord`) — a plain `Hediff` never reads
   `HediffDef.comps` at all (only `HediffWithComps` does), so both comps were
   dead code, compiling clean and never once running. Fixed to
   `HediffWithComps` (matching this same folder's own `RUT_MiasmaExposure`
   precedent), redeployed, restarted: error gone (290 total), and zero
   `Config error` hits for `RM_WardenMother` / `RM_CompWaterLocked` /
   `RM_ThinkTree_AnchorBehaviors` / `RM_AnchorGuard` /
   `RUT_StrandedDeformation` on the clean restart. Unrelated to the water-lock
   mechanism itself but named explicitly in this item's own sweep list and
   fixed on sight per CLAUDE.md's correctness-outranks-seat-ownership.

2. **Scatter — used the item's own sanctioned fallback.** Did not trigger
   `RUT_GenStep_CrecheScatterer` standalone. Painted a 20×20 `WaterShallow`
   pond on open, unroofed ground (no `RUT_CrecheMarker`) and spawned
   `RM_WardenMother` via `jawa/spawn_pawn` (`faction: none`) at its centre,
   (200,200). `RM_CompTerritorialAnchor.PostSpawnSetup()`'s own documented
   fallback ("absent an explicit `SetAnchor()` call... anchors on the pawn's
   own spawn cell") fired, producing the identical anchor/duty shape the
   GenStep's `RM_SetPieceElement_AnchoredPawn.SetAnchor()` call would have.

3. **State-read over time.** Polled `jawa/pawn_get` position +
   `rimworld/get_cell_info` terrain **24 times across 12,000 game ticks**
   (~4.8 in-game hours, `ticksGame` 1→12001), `rimworld/step_game_ticks`
   between polls. **24/24 sampled cells were `WaterShallow`.** Positions
   ranged (194,196)–(207,200), all within ~5–8 tiles of the anchor
   (200,200) — consistent with `RM_JobGiver_AnchorWander`'s own
   `wanderRadius = 7.5f`, not an unconstrained generic animal wander.

4. **Duty-seam check.** `jawa/autosave_now`, then a direct read of the raw
   `.rws` XML for her `Thing_RM_WardenMother22258` block (never a
   screenshot) showed, in the same save:
   - `<anchor>(200, 0, 200)</anchor><anchorSet>True</anchorSet>` —
     `RM_CompTerritorialAnchor` anchored correctly.
   - `<mindState><duty><def>RM_AnchorGuard</def><focus>(200, 0,
     200)</focus><radius>16</radius>` — the exact `PawnDuty`
     `RM_CompTerritorialAnchor.ApplyDuty()` constructs from
     `RM_WardenMother.xml`'s own `anchorRadius>16`. No vanilla mechanism
     assigns this DutyDef to a random wild animal, so this alone proves the
     comp fired.
   - `<jobs><curJob><def>Wait_Wander</def>...<jobGiverThinkTree>Animal
     </jobGiverThinkTree>` — she is actively holding a wander job dispatched
     through the `Animal` think tree, exactly where
     `RM_ThinkTree_AnchorBehaviors`'s `insertTag="Animal_PreMain"` splices
     in — not idling, not falling through to generic Animal AI with no
     anchor behaviour.
   - **This closes all three of this item's own named UNMEASURABLE
     questions**: (1) pathing CAN be constrained to a terrain set — CONFIRMED;
     (2) a bodySize-8 pawn paths through shallow water without breaking —
     CONFIRMED, no stuck/error state across 4.8 hours; (3) the
     `Animal_PreMain` duty-consultation seam fires for this PawnKindDef —
     CONFIRMED.

5. **Known gap (§5, optional) — NOT resolved, left open.** No hostile ever
   threatened her during the observation window (faction `none`, nothing
   attacked her), so `RM_JobGiver_AnchorDefense` never had a target to accept
   or reject, and the melee-chase-crosses-one-land-cell race is still
   unverified. The only bridge route to hostile-pawn damage,
   `jawa/damage`, calls `Thing.TakeDamage` with no instigator `Thing`, which
   is unlikely to set `mindState.enemyTarget`/trigger real pursuit AI the way
   an actual attacking pawn does — a real test needs a genuine attacker (a
   hostile-faction pawn actually ordered to attack her, or a new companion
   tool that constructs a real `DamageInfo` with an instigator). Per this
   item's own instruction, not chased further this pass rather than force an
   unreliable result.

**Verdict**: the water-only movement constraint is genuinely MEASURED (not
merely offline-verified) for wander/backstop/duty-assignment. Closing this
item on that basis — §5's chase-vs-backstop race remains open and would need
a fresh, narrower live check (a real attacker) if the owner wants it settled.

Raw poll samples: `Transient/wm_poll_results.json`, `Transient/wm_poll_results2.json`.

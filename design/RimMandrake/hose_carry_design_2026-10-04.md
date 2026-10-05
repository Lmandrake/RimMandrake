# Hose carry design — colonist-deployed flexible hose (FLOWWORKS_HOSE_DEPLOY_DRAG_1)

*Design pass, 2026-10-04, FOUNDRY. Docs only. For the build agents that follow: §15 is the plan, §3 the state machine.*

## 0. Owner rulings this design is bound by

Verbatim, typed, 2026-10-04:

> *"The point of the flexible hose (as opposed to just building permanent piping) is that you can drag it to a body of
> water, drain it/move it around, then move the hose again. It's supposed to be much faster than laying down heavy metal
> pipe. So it's important to dynamically have a colonist 'do it' as you are often going to be stealing someone's liquid
> (or pumping nastiness towards their base as well). So let's do a design pass about that now... then get going on it
> please. No mod switch to just thrust the pipe somewhere: that's just a debug action I'm afraid."*

> *"'deploy to this location' from the pump-side, and then a colonist needs to drag it out there and that be shown
> graphically as it's happening, especially if it gets interrupted and 'dropped' at some location along the way. Then you
> can pick up the end and bring it back or 'retract' from the pump location."*

Consequences, all binding on the build:

1. **The instant `Lay hose` / `Reel in hose` gizmos become DEV-MODE ONLY** (labelled `DEV: lay hose instantly`,
   `DEV: reel in instantly`). There is **no** Mod Settings switch that restores them for normal play — he ruled that
   out by name. The player path is colonist jobs only.
2. **Fast** is the point. A 40-cell deploy must take roughly the walk time plus a few seconds, never a construction-
   length job. A hose is the thing you grab instead of building pipe.
3. **Mobile and re-usable**: deploy, drain, pick up the end, move it, deploy again. "Move the end" is a first-class
   job, not "retract everything and redo".
4. **Shown as it happens**: the hose is drawn live from the reel to the carrier along the path actually walked, and a
   dropped end lies where it fell.
5. Already decided earlier (kept): blocked/over-long hose re-routes within length else retracts with the alert
   (`HOSE_BLOCKED_REROUTE_RETRACT_1`); default length 40; relay reels chain hoses; hoses draw beneath overhead lines.
6. "Stealing someone's liquid / pumping nastiness towards their base" is the motivating play pattern. It shapes the
   design (the destination may be another faction's tank; a hostile can be the reason a carry is dropped) but the
   liquid economics belong to FlowWorks (§10).

## 1. What exists today (measured from source, 2026-10-04)

Files: `src/RimMandrake/GimmeSomeSlack/Source/Hose/` (`CompHoseReel.cs` 278 lines, `RM_MapComponent_Hoses.cs` 710,
`HoseMath.cs` 980, `HoseRelay.cs`, `HosePorts.cs`, `HoseFlow.cs`, `HoseProbe.cs`, `HoseSettings.cs`, `HoseStyles.cs`).

- **Laid state is DATA on the reel, two fields**: `CompHoseReel.laid` (bool) and `far` (IntVec3, the free-end cell),
  plus `end` (Open/Nozzle/EndCap). The geometry (`HoseLay`) is RECOMPUTED from (reel rect, far, seed, shape settings)
  by `RM_MapComponent_Hoses.EnsureLay` → `HoseMath.Lay` (CordPlanner A* + string-pull + round corners + rope settle +
  stiffen), cached by `layKey`. Nothing per-cell is spawned; the map component is kept out of the save
  (`Patch_Map_ExposeComponents_SkipHoses`). **The laid shape is therefore a PLANNED shape, not a walked one.**
- `TryLay(target)`: relay redirection (`ReelCovering` → `HoseRelay.TryIntake`), loop refusal, `CheckInstall` (length
  via `HoseMath.RouteLength` = taut A* × `RouteMargin` 1.05 against `MaxLength`), then sets `laid/far` instantly.
  `ReelIn()` clears instantly. `Retract(why)` = ReelIn + reason/tick/need + message; `Alert_HoseRetracted` lists them.
- **Tick** (`MapComponentTick`): per laid reel, flow signal → flat/plump `HoseStateMachine`; every 250 ticks a
  corridor hash check → `HoseMath.CheckReplan` → re-route or `Retract`.
- **Draw** (`MapComponentUpdate` → `DrawAll`): `Graphics.DrawMesh` ribbons (flat/plump/shadow) at
  `AltitudeLayer.Conduits + DrawOrder.HoseBaseLift + CrossLift(rank)`, one shared render queue
  (`DrawOrder.HoseQueue`), below the overhead queue (round 6). Settled hoses cache meshes; transitioning ones rebuild
  per frame (`frameMeshes`, destroyed next frame). Ends: reel end hidden under the drum (`HoseReelRect.Mouth`),
  joiners at bends, free end Open/Nozzle/EndCap or a brass coupling on a relay's edge.
- **Relays**: connection is DERIVED (a reel whose `far` is another reel's intake cell feeds it), never saved.
- **Ports**: `HosePorts.Find` — a reel beside a pipe/tank couples to it (feed hose drawn). The REEL end is the pump
  side; the FREE end today connects to nothing except a relay reel.
- **Flow**: `HoseFlow.Providers` = FlowWorks pump (reflection, finds nothing — no pump exists), relay, debug.
- **`SetLaidFraction` does NOT exist in code.** It is an API in `messy_conduit_phase2_design_2026-10-02.md` §3.2/§3.7
  (a planned-path hose drawn up to fraction f). This design **replaces** that idea: a fraction of a planned polyline
  cannot show a hose following the pawn's real walk or lying where it was dropped (owner sketch point 2).
- Probe verbs (`HoseProbe`): `set:`, `lay`, `check`, `reelin`, `flow`, `end`, `clearhist`. Validation:
  `validation_hose.py` (`--live`, `--save-load`, `--removal-check`, `--maze`, `--relay`). Review map:
  `human_review.py` stations 12-18, 22-23, 42 lay hoses through the probe (`hoses=[dict(reel, far, state)]`).
### 1a. Engine facts this design rests on (RimSage, decompiled 1.6, read 2026-10-04)

- **Vanilla already has a dragged line: `Pawn_RopeTracker`** (`RimWorld/Pawn_RopeTracker.cs`). `RopingDraw()` is
  called from `PawnRenderer` (line 271) and draws `GenDraw.DrawLineBetween(pawn.DrawPos.Yto0(), target,
  AltitudeLayer.PawnRope.AltitudeFor(), RopeLineMat)` every frame — a straight line from the pawn's INTERPOLATED draw
  position. `RopingTick()` **breaks every rope when the pawn is Dead, Downed, Drafted, asleep while roped, in any mental
  state but Roaming, or burning, or when its current driver is no longer `JobDriver_RopeToDestination`**. That list is
  our interrupt list, taken from the engine rather than invented (§5). We copy the pattern (a per-tick validity check on
  the holder, independent of job finish actions), not the class.
- `JobDriver_RopeToDestination` is the job-shape precedent: `AddFinishAction(... DropRopes())` + `Toils_Goto.Goto(B,
  OnCell)` with `AddPreTickIntervalAction`, and `pawnDestinationReservationManager.Reserve` on the destination cell.
- `Pawn_PathFollower`: `nextCell`, `curPath`, `Moving`, `MovePercentage`, `Destination` are public; `lastCell` is
  private. ⇒ the walked trail is recorded from `pawn.Position` changes in the job's tick action (no reflection).
- `Pawn_JobTracker.ExposeData` deep-saves `curJob` and `curDriver`; on load a driver resumes its toil index, and a job
  with no driver is ended `Errored` at PostLoadInit. `Pawn.ClearMind_NewTemp` (downed/mental paths) calls
  `jobs.StopAll`; `Pawn.DeSpawn` calls `jobs.StopAll()` when a job is running (so leaving the map, a caravan or
  a gravship launch ends our job through its finish action). `SetFaction` calls `roping.BreakAllRopes()`.
- `Pawn_DraftController.Drafted` setter: on ANY draft change (on or off) it clears queued jobs and, if the current job
  is player-interruptible, `EndCurrentJob(InterruptForced)`. ⇒ drafting a carrier drops the end, and so does
  undrafting a pawn that was carrying on a drafted forced order.
- `FloatMenuOptionProvider` (1.6): `Drafted`/`Undrafted`/`Multiselect` switches, and `GetOptions(context)` sees
  `context.ClickedCell` — so a right-click on a bare cell (a dropped hose end, which is not a Thing) can offer options.
- UNMEASURED (not read this pass): `WorkGiver_Scanner` member list (the standard `PotentialWorkThingsGlobal` /
  `HasJobOnThing` / `JobOnThing` / `ShouldSkip` shape is assumed); whether a door closes over a cell that holds no Thing
  (assumed yes: doors check things/pawns in the doorway, and a hose is no Thing); Multiplayer sync conventions.

## 2. Player UX

**Decided:**

| on the reel (selected, player-owned) | when | what it does |
|---|---|---|
| **Deploy hose** (target a cell) | Stored | places a DEPLOY ORDER on the reel: pending target cell. Targeting shows the reach circle (existing overlay) and, under the mouse, the taut route + "needs N of 40 cells" (existing `NeedFor`); an over-long or unreachable cell is refused at click time with the existing `Explain` text. |
| **Move hose end** (target a cell) | Laid or Dropped | MOVE ORDER: a colonist walks to the free end, picks it up and carries it to the new cell. Same targeting feedback. Choosing a cell on/next to the reel = "bring it back". |
| **Retract hose** | Laid or Dropped | RETRACT ORDER: a colonist goes to the reel and winds it in; the hose visibly runs back along its route. |
| **Cancel hose order** | an order pending | clears it; a carrier mid-walk drops the end where he stands. |
| **Free end: open/nozzle/cap** | always | unchanged. |
| `DEV: lay hose instantly` / `DEV: reel in instantly` / `DEV: flow` | `Prefs.DevMode` only | today's `TryLay`/`ReelIn`, kept for tests and the review map. **No setting exposes them.** |

- **Who does it: any free colonist, through a WorkGiver**, not a designated pawn. `WorkGiver_HoseOrders` under the
  vanilla **Hauling** work type (dragging a hose is labour every colonist can do; Construction would gate a 10-second
  errand behind builders), `priorityInType` high in Hauling so a pending order is taken before ordinary hauling.
  Rejected: a designated pawn per reel (more UI, and the pawn is often busy/away; nothing in the ruling asks for it).
- **Forced / drafted orders**: a `FloatMenuOptionProvider_Hose` (Drafted = true, Undrafted = true, Multiselect = false)
  offers, for the selected pawn: right-click a reel → "Carry hose out from <reel>" (then a cell targeter),
  "Retract hose at <reel>"; right-click a free-end cell → "Pick up hose end" (then targeter: new cell, or the reel to
  bring it back). These are `TryTakeOrderedJob` forced jobs: they ignore allowed areas like vanilla prioritized jobs,
  and a DRAFTED pawn may run them (the raid / theft use case: carry the hose under fire with a drafted pawn).
- **Forbidden / areas**: a forbidden reel gets no automatic work. The WorkGiver skips an order whose free end or target
  is outside the pawn's allowed area (`ForbidUtility.InAllowedArea`) or unreachable (`CanReach`, Danger.Some). Forced
  orders ignore the area (vanilla behaviour).
- **The dropped end is DATA, not a Thing** (consistent with "the laid hose is data on the reel", save rule M9). It is
  found by the right-click provider through the cell, drawn highlighted when its reel is selected, and the reel's
  inspect line says "Hose end dropped at (x,z), 23 of 40 cells out". Trade-off accepted: the player cannot click-select
  the end itself in v1. (A selectable `RM_HoseEnd` Thing is the upgrade path if the owner wants it; it costs a second def
  in every save and a guard against vanilla hauling it.)
- **Repeated orders**: an order with a dropped end and a still-pending target is picked up again automatically by the
  WorkGiver (the pending target survives the drop) — so a colonist interrupted by a raid finishes the job afterwards
  without the player re-ordering. Setting `autoResumeDroppedHose` (default on) controls this.

## 3. State machine

**Chosen: `Stored → Carrying → (Laid | Dropped) → Carrying | Retracting → Stored`, with Relay/Port/Water as DERIVED
end kinds of Laid, never states.**

Saved on the reel (`HoseCarryState` enum, appended order): `Stored, Carrying, Dropped, Laid, Retracting`.
Orthogonal saved field `pending` (`None, Deploy, Move, Retract` + target cell). Derived each 60 ticks, never saved:
`endKind` = `Relay | Port | Water | Free` (§7).

| from | event | to | notes |
|---|---|---|---|
| Stored | colonist starts Deploy job (grabs the end at the reel mouth) | Carrying(carrier, trail=[mouth cell]) | |
| Carrying | carrier enters a new cell | Carrying (trail append / backtrack-truncate, §8) | |
| Carrying | carrier arrives, end set down / coupled | Laid(trail, far=target) | pending cleared |
| Carrying | any interrupt (§5) | Dropped(trail, far=last trail cell) | pending KEPT (resume) unless cancelled |
| Carrying | hose at full stretch (pulled-taut trail > MaxLength) | Dropped | message "hose at full stretch at (x,z)"; pending cleared |
| Carrying | trail truncates to the reel (walked it back) | Stored | the end is stowed |
| Laid / Dropped | colonist picks up the end (Move job) | Carrying(carrier, trail kept) | |
| Laid / Dropped | colonist starts winding at the reel (Retract job) | Retracting(winder, trail) | |
| Laid / Dropped | 250-tick corridor check: route cut, a re-route fits | same state, trail replaced by the re-planned route | HOSE_BLOCKED_REROUTE_RETRACT_1, unchanged |
| Laid / Dropped | corridor check: no route fits | Retracting(winder=null, auto) | the ruled auto-retract, now ANIMATED, + `Alert_HoseRetracted` |
| Retracting | wound length reaches trail length | Stored | |
| Retracting | winder interrupted (§5) | Dropped(trail shortened, far = new end) | |
| any | reel despawned (destroyed, minified, map removed) | Stored (existing `PostDeSpawn`) | carrier's job fails on `FailOnDespawnedOrNull(A)` |
| Stored/Laid/Dropped | DEV instant lay / reel in | Laid (planned trail) / Stored | dev mode only |

Invariants (selftest asserts all): `Carrying ⇔ carrier != null`; `Retracting(non-auto) ⇔ winder != null`;
`trail.Count ≥ 1` in every state but Stored; `far == trail.Last` in Laid/Dropped; pulled length(trail) ≤ MaxLength in
every state; no state is ever "laid but not drawable" (a failed lay → Retracting, never a ghost).

## 4. Jobs and toils

Defs (`Defs/Hose/RM_HoseJobs.xml`): `JobDef RM_CarryHoseEnd` (driverClass `JobDriver_CarryHoseEnd`, reportString
"carrying a hose to TargetB.", `casualInterruptible false`, `suspendable false` — a suspend would resume without the
end), `JobDef RM_RetractHose` (`JobDriver_RetractHose`, "winding in a hose."), `WorkGiverDef RM_HoseOrders` (workType
Hauling, giverClass `WorkGiver_HoseOrders`, verb "deploy hose").

`JobDriver_CarryHoseEnd` — targetA = reel (Thing), targetB = destination cell, `job.count` unused.
1. `TryMakePreToilReservations`: reserve the reel (1 claimant: one hand on a hose at a time) and
   `pawnDestinationReservationManager.Reserve(B)` (the rope precedent).
2. `FailOnDespawnedOrNull(A)`, `FailOn(() => reel state is not Stored/Laid/Dropped/Carrying-by-me)`.
3. **Goto the end**: Stored → `Toils_Goto.GotoThing(A, InteractionCell)` (the reel's mouth side); Laid/Dropped → goto
   `far` (`PathEndMode.Touch`: the end may lie in water).
4. **Grab** (`Toils_General.Wait(grabTicks=45)`, faces the end) → `comp.BeginCarry(pawn)` (state → Carrying).
5. **Walk** `Toils_Goto.Goto(B, endMode)` where endMode = OnCell for a standable target, Touch for water/tank/pipe/reel
   targets. `AddPreTickIntervalAction`: `comp.CarrierStep(pawn.Position)` (trail update + stretch check; a stretch
   failure calls `EndJobWith(Incompletable)`). `locomotionUrgency = Jog` (fast is the point).
6. **Set down / couple** (`Wait(coupleTicks)`: 30 to set down, 90 to couple to a port or relay) → `comp.FinishCarry(B)`
   (state → Laid, endKind derived).
7. `AddFinishAction(cond => if (cond != Succeeded) comp.DropCarry(pawn))` — idempotent: only acts if this pawn is the
   carrier.

`JobDriver_RetractHose` — targetA = reel. Reserve reel; goto reel interaction cell; `comp.BeginWind(pawn)`; a
repeating toil (`defaultCompleteMode = Never`, tick action winds `windCellsPerTick × manipulation` cells, `WithProgressBar`
on wound/total, ends when Stored); finish action `comp.StopWind(pawn)` → Dropped with the shortened trail.

`WorkGiver_HoseOrders` (`WorkGiver_Scanner`): `PotentialWorkThingsGlobal` = the map component's reels with
`pending != None` (a short list — no map scan); `ShouldSkip` when that list is empty; `HasJobOnThing` checks faction,
not forbidden, `CanReserve`, reachability of the end and of the target, allowed area; `JobOnThing` makes CarryHoseEnd
(Deploy/Move) or RetractHose (Retract).

Speed budget (a 40-cell deploy): walk to reel (~0) + 45 grab + ~40 cells × ~13 ticks jogging + 30 set-down ≈ 600 ticks
≈ 10 s at 1×. Retract of 40 cells at 3 cells/s ≈ 13 s. Both ≪ building 40 pipe segments.

## 5. Interrupts

Two independent mechanisms, both required: (a) the job's finish action drops the end the instant the job ends any way
but success; (b) **the reel's own validity check every 30 ticks** (the `RopingTick` pattern) drops it if the carrier is
null, dead, despawned, on another map, downed, drafted-without-a-forced-hose-job, in a mental state other than Roaming,
burning, or its `curDriver` is not a `JobDriver_CarryHoseEnd` on this reel. (b) catches everything (a) misses: a
loaded save where the job was cleaned up, a pawn removed by another mod, an exception in a finish action.

| interrupt | result | where the end lies |
|---|---|---|
| player drafts the carrier | job ends (vanilla clears jobs on draft) → Dropped, pending kept | last trail cell (the pawn's cell) |
| carrier given any other order / job replaced | Dropped, pending kept | last trail cell |
| downed / killed | Dropped; pending kept | the cell he fell in |
| mental break (not Roaming) | Dropped | ditto |
| asleep from exhaustion, burning | Dropped | ditto |
| carrier leaves the map (exit, caravan, gravship, despawn) | Dropped, pending kept | last trail cell on THIS map (the edge cell); the end never leaves the map |
| reel destroyed / minified / map gone | reel → Stored (existing `PostDeSpawn`); job fails on A | — |
| target blocked (a wall built on it) or path blocked mid-walk | pather fails → job Incompletable → Dropped; pending CLEARED with message "could not reach (x,z)" (resuming would loop) | where he stopped |
| length exceeded (pulled trail > MaxLength) | Dropped, pending cleared, message with numbers (existing `Explain` format) | the last cell that fitted |
| enemy / danger | nothing special: vanilla flee, draft or downing produces one of the rows above | — |
| a second pawn ordered onto the same reel | refused by the reel reservation | — |
| a winder interrupted | Retracting → Dropped with the shortened trail | the current wound-back end |

A drafted pawn that was explicitly ordered (forced job) keeps carrying while drafted: the drop on draft is triggered by
the draft setter ending the job (measured, §1a), not by the Drafted flag itself (check (b) accepts Drafted when the
current driver is ours). Undrafting him mid-carry also ends the job — the end is dropped; with `pending` kept, an idle
colonist resumes it.

## 6. Live drawing

- **While Carrying**: the hose is drawn from the reel mouth through the TRAIL (cell centres, corners rounded with the
  existing `CordPlanner.RoundCorners` at radius `minBendRadius`) to the carrier's `pawn.DrawPos` (interpolated every frame,
  as vanilla's rope line). Flat pose, no rope settle (settle is the expensive part of `HoseMath.Lay`). The end piece is
  drawn at the pawn's hand: `DrawPos + facing × 0.25`, in the hose band (under the pawn sprite: reads as dragged along the
  ground). Two meshes: the **trail prefix** (rebuilt only when the trail changes, ~every 13 ticks while walking) and a
  **tail** segment from the last trail point to the pawn (2-4 samples, rebuilt per frame through the existing
  `frameMeshes` one-frame list).
- **Dropped / Laid**: the trail becomes the route for `HoseMath.Lay` (new overload `LayAlong(world, route, shape, seed)`
  that skips `CordPlanner.Plan` and runs round → settle → stiffen on the given cells), cached exactly as today
  (`layKey` now includes a trail hash). A dropped end draws the open end lying on the ground (the existing Open mouth
  piece; plain open end per round-1 review — no new art needed).
- **Retracting**: the drawn hose is the cached lay CLIPPED at arc length `total − wound` (sample-index cut + one
  interpolated point); the end piece rides the cut. Rebuilt per frame only while winding.
- **Draw order**: unchanged band — `AltitudeLayer.Conduits + HoseBaseLift + CrossLift(rank)`, one shared
  `DrawOrder.HoseQueue` below `OverheadQueue` (round 6). A carried hose is never drawn above overhead lines or pawns.
- **Perf**: a 40-cell trail ≈ 160 samples ≈ 320 vertices; one moving hose costs one prefix rebuild per ~13 ticks + one
  4-sample tail per frame. Even 10 hoses moving at once is trivial next to the cord layers. **LOD**: at
  `Find.CameraDriver.CurrentZoom ≥ Far` skip the end piece and the shadow ribbon for moving hoses.
- Pawn carry graphics: the carry tracker is NOT used (no Thing is carried; using it would block hauling and make a
  "drop" spawn an item). Rejected: an animated hand pose — RimWorld has none to drive.

## 7. Destination / connection rule

The free end's kind is DERIVED from where it lies (like relays and ports today), re-read every 60 ticks, never saved:

| end lies… | endKind | drawn | today's behaviour |
|---|---|---|---|
| on an intake cell of another reel | **Relay** | brass coupling on the relay's edge (existing) | relay flow provider (existing) |
| on a cell beside a pipe/tank of ANY faction (`HosePorts.Classify` on the end's neighbours, same rule as the reel side) | **Port** | brass coupling facing the port | coupling recorded; inspect names the port and its faction. Liquid: FlowWorks (stub) |
| in or touching water terrain (`TerrainDef.IsWater`, or a FlowWorks liquid terrain by tag) | **Water** | the chosen end piece lying in the water cell (intake) | "intake in <terrain>". Flow needs a pump at the reel: none exists, so it stays flat unless the DEV flow toggle is on |
| anywhere else | **Free** | open end / nozzle / cap on the ground | nothing |

**What "drag it to a body of water" connects to today**: the end is placed IN the water (the carrier stands on the shore
and the end goes into the target cell, `PathEndMode.Touch`), and the reel reports an intake. The pumping is FlowWorks'
`RM_PumpPortable` (not built): the existing `FlowWorksPumpFlow` reflection adapter already reads any pump beside the
reel, so the day a pump exists the water-intake hose plumps without a change here. **Stubbed, documented**: a public
read-only `CompHoseReel.FreeEnd` (cell, endKind, port Thing or null, terrain) for FlowWorks to read — no compile-time
reference either way.

## 8. Pathing authority

- **The pawn's own pather is authoritative for where the carrier walks** (doors, danger, allowed areas, other pawns —
  everything vanilla handles). **The hose follows what was WALKED.** CordPlanner is used only for (a) the order-time
  check (`CheckInstall`: taut route ≤ MaxLength, existing) and (b) re-routing a cut hose (existing).
- **Trail rule** (`HoseTrail`, Verse-free): on entering cell c — if c is already in the trail at index i, truncate to i
  (the carrier is dragging slack back; walking all the way back to the reel stows the hose); else append c. Then
  **pull taut**: the trail's any-angle string-pull (the same pulled-route geometry `HoseMath.RouteLength` uses, but over
  the given cells, never through a wall or pinched diagonal) is the hose's length. If pulled length > MaxLength the
  carrier is at full stretch (§5).
- **Legal for a pawn ⊂ legal for a hose** except doors and water: every walkable cell is hose-walkable in
  `RM_MapComponent_Hoses.World()`, doors are marked passable (`SetDoor`), and the hose floats on water the pawn cannot
  enter only via the final Touch placement (one cell). A hose cannot be carried across deep water in v1. A door closes
  over a hose (assumed, §1a): no temperature leak modelled.
- After Laid/Dropped the trail is the saved route; the 250-tick corridor check compares against the trail's corridor,
  and a cut re-plans with CordPlanner from the reel (the walked shape is then lost — correct: the obstacle moved it).
## 9. Speed, skill, fatigue

- **No skill gate, no XP, no slowdown** (decided). The ruling's point is speed and that anyone grabs it; Hauling has no
  skill in vanilla. The carrier jogs (`LocomotionUrgency.Jog`).
- Winding speed = `windCellsPerSecond` (setting, default 3) × the winder's Manipulation capacity (clamped 0.3-1.5).
  The auto-retract (no winder) runs at the base speed.
- Fatigue: none added; vanilla rest/needs interrupt the job normally (→ Dropped, resumed later).
- Rejected: Construction skill scaling (makes the fast tool slow for non-builders); a carry-weight speed penalty (needs a
  hediff or StatPart for no gameplay gain the owner asked for).

## 10. Hostile use / stealing

- **Allowed, by design**: the target may be another faction's tank or pipe (endKind Port), or water inside their base.
  Nothing in MessyConduit checks ownership. The drafted forced order (§2) is the raid tool: carry the hose in under
  cover, drop it if shot, pick it up again.
- **Out of scope here, hooks provided**: what flows and what it costs (goodwill, theft letter, poisoning their tank with
  "nastiness") is FlowWorks' and the owner's. Hook: `HoseEvents.EndPlaced(reel, endKind, port, faction)` and
  `HoseEvents.EndLifted(reel)` static C# events (no FlowWorks reference), raised on Laid/Dropped/pick-up.
- AI use: the job driver is faction-agnostic — a LordJob may give an enemy pawn `RM_CarryHoseEnd` on its own reel (the
  ruled tanker raid, `liquids_framework_design.md` §4). Not built now; nothing in the design prevents it. The WorkGiver
  is player-faction only.
- Enemies interacting with a player's laid hose (stepping on it, cutting it): nothing in v1. A hose has no HP (it is no
  Thing); a cut is FlowWorks' `Cut` in the phase-2 kit design.

## 11. Saving

New fields on `CompHoseReel.PostExposeData` (old keys untouched):

| key | type | notes |
|---|---|---|
| `rmHoseCarry` | `HoseCarryState` (Scribe_Values, default Stored) | appended enum order only |
| `rmHoseTrail` | `List<IntVec3>` (Scribe_Collections, LookMode.Value) | ≤ ~60 cells; turning points only would be smaller but the cell list is what the trail rule needs |
| `rmHoseCarrier` | `Pawn` (Scribe_References) | carrier or winder |
| `rmHoseWound` | float | cells wound in during Retracting |
| `rmHosePending`, `rmHosePendingAt` | enum, IntVec3 | the order |

- **Legacy load**: no `rmHoseCarry` key and `laid == true` → Laid with an EMPTY trail = "planned route" (today's
  `HoseMath.Lay` from reel to `far`). `laid` stays written (= state ∈ {Laid, Dropped}) so every existing reader (flow
  tick, relays, probe, alert) keeps working unchanged in stage 2.
- **Pawn reference**: resolved by vanilla in ResolvingCrossRefs; a carrier that became a world pawn or was discarded
  resolves to a non-spawned pawn or null. Either way the 30-tick validity check (§5 b) drops the end at the trail's last
  cell on the first tick after load. **The reel is authoritative, never the job**: the pawn's job is deep-saved by
  vanilla and resumes at its toil index; if it resumes, `CarrierStep` continues the trail; if vanilla discarded it
  (`Errored` at PostLoadInit), the reel drops the end.
- The map component stays out of the save (unchanged). Meshes are rebuilt from (reel, trail, seed).
- **Mod removal (M9)**: reel def missing → the reel is dropped (as today); a pawn mid-job holds a JobDef that no longer
  resolves → vanilla's missing-def handling ends the job with an error line. Accepted, same class as M9; the H11 removal
  check gains one row for a save made mid-carry.

## 12. Compat and settings

- **Multiplayer (rwmt) safety**: every player action goes through FIVE comp methods — `OrderDeploy(cell)`,
  `OrderMove(cell)`, `OrderRetract()`, `CancelOrder()`, `DevLayInstant(cell)` — so an MP compat patch can mark them
  `[SyncMethod]`. Sim code uses no `Rand` and no wall-clock; `pawn.DrawPos` is read only by drawing. Whether MP is in any
  tier's list: UNMEASURED; no compat patch is built now.
- Other mods: pure additions (2 JobDefs, 1 WorkGiverDef, 1 FloatMenuOptionProvider); no Harmony patch added.
- **Settings** (`HoseSettings`, the existing hose page; all defaults = shipped behaviour):

| setting | default | note |
|---|---|---|
| Hose length (existing) | 40 | |
| Winding speed (cells/s) | 3 | |
| Grab / set-down / couple time (ticks) | 45 / 30 / 90 | one "handling time" slider scaling all three, 0.25-3× |
| Interrupted hoses are picked up again automatically | on | §2 |
| Show the route and length while choosing where to deploy | on | |
| Colonists drag hoses | — | **not a setting**: there is no alternative path (owner) |

  `DEV:` instant gizmos appear only under `Prefs.DevMode`, with no setting at all.

## 13. Tests

**Offline (selftest, Verse-free, `Source/Hose/HoseCarry.cs` + `Source/SelfTest/HoseCarryChecks.cs`)** — economical,
each row load-bearing, each with a can-fail:
1. Transition table: every (state, event) pair in §3 gives the listed state; every other pair is refused (exhaustive
   enumeration, ~5×12). Can-fail: a table with the Carrying→Dropped row removed must fail row "interrupt drops".
2. Trail rule: walk out 10, back 4 → trail 6; walk back to the reel → Stored; a U-walk round a wall stub pulls taut
   to the measured length (reuse round-4 maze fixtures: station 23 must pull to 36.0 ± 0.5). Can-fail: a no-truncate rule
   leaves 14.
3. Stretch: a 50-cell walk with MaxLength 40 stops at the first cell whose pulled length > 40 and drops there.
4. Invariants of §3 after every step of 200 seeded random event sequences (deterministic seeds).
5. Retract clip: winding w cells from a lay of length L leaves a drawn length L − w ± one sample.
6. Legacy: a saved {laid=true, no carry key} reads as Laid + empty trail and lays the planned route (byte-identical
   geometry hash to today's).

**Live (`validation_hose.py --carry`, one scene, one colonist, state reads through HoseProbe, never screenshots)**:
CR1 order Deploy 24 cells → within 600 ticks the probe reads `Carrying`, carrier = the colonist; CR2 two samples 60
ticks apart: trail grew and its last cell is within 1 of the pawn's Position; CR3 draft him → `Dropped`, far within 1 of
his cell, pending kept; CR4 save + reload while Dropped AND (second save) while Carrying → state, trail, far identical;
the Carrying save comes back Carrying-resumed or Dropped, never Laid-without-trail; CR5 undraft → he (or another
colonist) resumes and the probe reads `Laid`, far = target, endKind as staged (put the target in water: `Water`); CR6
order Retract → `Retracting`, then `Stored` within (length/3 s × 60 + 300) ticks; CR7 DevMode off → the reel's gizmo
labels contain no "Lay hose"/"Reel in" (probe `gizmos` verb). Seven rows; no flight, no screenshots. Probe additions:
verbs `order:deploy:x,z|move:x,z|retract|cancel`, census fields `carry, carrier, trail (count + pulled length), pending,
endKind, wound`.

## 14. Review-map stations (`human_review.py`, row G, region 2, after station 42)

| # | title | staged through the probe | he checks |
|---|---|---|---|
| 43 | DEPLOY BY HAND | a reel with a pending Deploy order 24 cells out, one idle colonist beside it | a colonist walks it out, the hose unrolls behind him along his walk |
| 44 | DROPPED HALFWAY | a reel with a Dropped end 14 cells out (probe `settrail:`) | the open end lies on the ground; select the reel → "Move hose end" / "Retract hose" |
| 45 | INTO THE POND | a reel 10 cells from water, hose laid into it | the end lies in the water; inspect reads "intake in …" |
| 46 | ON THEIR TANK | a neighbour-faction `RM_LiquidTank` with a hose coupled to it | brass coupling on their tank; inspect names their faction |
| 47 | WIND IT IN | a laid 30-cell hose | press Retract: the hose runs back along its route to the reel |

Stations 43 and 47 need a colonist free to work: the review map must spawn one per station (or he drafts one).
The probe's `lay`/`settrail` verbs keep working with DevMode off (they are the review map's staging tools, not player
actions).

## 15. Staged build plan

Each stage ends testable; file ownership per stage so two agents never write the same file at once. Stages 1→2→3 are
sequential; 4 and 5 can run in parallel after 3.

| stage | owns (writes) | ends with | model / size |
|---|---|---|---|
| **S1 core** | NEW `Source/Hose/HoseCarry.cs` (state enum, transition table, `HoseTrail` append/truncate/pull/stretch — Verse-free), NEW `Source/SelfTest/HoseCarryChecks.cs`, `Source/SelfTest/Program.cs` (one Run line), SelfTest csproj | `selftest_gimmesomeslack.py` green incl. rows 1-5 | Sonnet, 0.5 d |
| **S2 reel state** | `CompHoseReel.cs` (fields, Scribe, legacy read, the five order methods, gizmos: player orders + `DEV:` gating), `HoseMath.cs` (ADD `LayAlong` only), `RM_MapComponent_Hoses.cs` (EnsureLay keyed on trail; validity tick hook), `HoseProbe.cs` (verbs + census), main csproj Compile lines | builds; selftest row 6; DEV instant lay still lays; the player gizmos place orders (nothing executes them yet); `validation_hose.py --live/--maze/--relay` unchanged-green | Opus, 1 d |
| **S3 jobs** | NEW `Defs/Hose/RM_HoseJobs.xml`, NEW `Source/Hose/Jobs/{JobDriver_CarryHoseEnd,JobDriver_RetractHose,WorkGiver_HoseOrders,FloatMenuOptionProvider_Hose}.cs`, main csproj | live CR1-CR6 pass with the hose drawn as an instant re-lay on each trail change (ugly but correct) | Opus, 1 d |
| **S4 live drawing** | `RM_MapComponent_Hoses.cs` (DrawCarrying prefix+tail, retract clip, LOD), NEW `Source/Hose/HoseEnds.cs` (endKind derivation, water/port free end, `FreeEnd` accessor, `HoseEvents`), `HosePorts.cs` (free-end port find) | the carry reads live on screen; endKind in the probe; CR5 `Water` row | Sonnet, 0.75 d |
| **S5 checks + review** | `validation_hose.py` (`--carry`, CR1-CR7), `human_review.py` (stations 43-47), `selftest_human_review.py`, `HoseSettings.cs` (§12 rows) | `validation_hose.py --carry` written; selftests green; review map stages 43-47 | Sonnet, 0.5 d |

Rules for every stage: commit explicit paths with `./publish`; a committed DLL carries its `.srchash`; the
`EnableDefaultCompileItems false` csproj needs a `<Compile Include>` per new `.cs`; never deploy while the game holds
the DLL. Existing `ReviewRound*` selftests must stay green — `TryLay`/`ReelIn` keep their signatures (they become the
DEV path and the probe's staging path).

Total ≈ 3.75 agent-days. Live proof needs one game session after S3 and one after S5.

## 16. Open decisions

None blocks the build. Two the owner may want to overrule after seeing it, both defaulted here:

1. **The dropped end is data, not a clickable thing** (§2). Default: right-click its cell / use the reel's gizmos. If he
   wants to click-select the end on the ground, S4 adds an `RM_HoseEnd` Thing (one more def in saves).
2. **Drafting a carrier drops the end** (vanilla draft behaviour, measured) unless he was ordered while already drafted.
   Default kept because it matches vanilla ropes and his own "interrupted and dropped".

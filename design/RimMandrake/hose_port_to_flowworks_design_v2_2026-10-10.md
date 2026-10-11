# Hose port: GimmeSomeSlack → FlowWorks — design v2 (2026-10-10)

status: DRAFT v2 (v1 + independent review applied). Next: GPT review with all of FlowWorks → merged design → port.
v1: `design/RimMandrake/hose_port_to_flowworks_design_2026-10-10.md` (kept unchanged). Review:
`design/RimMandrake/hose_port_to_flowworks_review_2026-10-10.md` (M = must-fix, S = should-fix ids below).

## Changelog v1 → v2

- **M1/M2/M7 — §4.1 rewritten.** Links join two *port things* read through the existing cached `Port()` / free-end reads;
  the reel footprint no longer conducts (it broke FlowWorks' no-accidental-merge invariant and disagreed with the drawn
  coupling); the far end seeds the BFS; stale ports are dropped by a `Spawned` check.
- **M3** — `HoseProbe` loses its aerial-material read; RL9 compares the two mods' probes in Python.
- **M4** — the reel's look rides a shared, def-agnostic style picker (`_Shared/StylePicker/`, five patches), not "~40 lines".
- **M5** — `_Shared/SlackGeometry` files become `internal`, like every `_Shared` precedent.
- **M6** — the strand render queue is derived in shared code from the shader, not read from GSS's `CordMaterials`.
- **M8** — type alias moves into step 2 (same commit as the move); "red error" corrected to warning + Scribe error.
- **M9** — settings import globs `Mod_*_FireHosesMod.xml` (Workshop folders, the MessyConduit-era file); 17 keys, 15 survive.
- **S1** — `RM_LiquidHose` is named as the framework's `RM_HoseSpool`; the reel takes that role; Q1/Q3 text updated; pipe stats retuned.
- **S2** — moved Harmony patches wired through `PatchApplier` with `[PatchFeature]`; save-skip and alias never switch off.
- **S3** — old-GSS detection with one red line; "config error" corrected (cross-mod defName replacement is silent).
- **S4** — spawn/despawn version counter dropped; per-tick topology-only cache.
- **S5–S9** — `RM_Liquid_FreshWater`; `levelsPerCycle × 5`; caller cadence (bath = `releaseTicks`); tint dwell; one route per tank stated.
- **S10** — proof manifest (`DECLARED_ROWS`, walk `checkout:`), `matrix` census, SL2 prefix added to the move list.
- **S11/S12** — hand counts dropped in favour of step 0; `HosePortKind.Machine` placement pinned.
- Q5 and Q6 become stated defaults in the card rather than questions.
Item: `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST` (owner-filed, `infrastructure/state/ledger/events/OWNER.jsonl:269`).
Design only: no mod code is written by this pass. Every `file:line` below was read on 2026-10-10 at bench HEAD `fe70301c3`.
Paths are repo-relative to `src/RimMandrake/` unless they start with `design/` or `infrastructure/`.

## 1. Owner order and scope

- Typed 2026-10-10 (filing the item): *"We need to move the GimmeSomeSlack hose code/functionality over to FlowWorks.
  That's the right home, and it allows GimmeSomeSlack to be entirely about cables and conduits and electricity."*
- Typed 2026-10-10 (this pass): *"do the full design pass on porting the existing flexible hose solutions and reels from
  GimmeSomeSlack into FlowWorks."*
- Earlier, still binding: 2026-10-04 round-2 notes (`design/RimMandrake/messyconduit_review_round2_owner_notes_2026-10-04.md:5-11`):
  the reel must connect to *"standard static piping and other pipe-friendly buildings (like tanks)"*, and those are
  *"universal pipes that can carry any liquid of any kind"*. Card decisions the same day (same file, §"Decisions taken by
  question card", items 1-2): a blocked hose reroutes within its length or retracts with an alert, never a ghost hose;
  "universal pipe: wait for FlowWorks", the reel's connection stays generic (any pipe-like building sharing an edge).
- Card 2026-10-06, straight lead-out: the hose leaves the reel's nozzle on a straight run and is refused, never laid,
  without it (`GimmeSomeSlack/Source/Hose/HoseMath.cs:134-136, 226-227, 239`). This ruling and tonight's fixes
  (`df359078c` live sites redrawn for it, `4afb43d46` install check runs a trial lay, `19ba7aff3` lead-out tries farther
  joins) move with the code unchanged; the port must not regress any of them.
- Out of scope: any new hose behaviour except what is needed to make flow real (§4); the GSS cable/aerial work another
  agent is doing in parallel.

## 2. What exists today (sources read)

### 2.1 The GSS reel hose (the one players see)

| piece | where | notes |
|---|---|---|
| Reel ThingDef `RM_HoseReel` (2x2, minifiable, Misc tab, cloth+steel) | `GimmeSomeSlack/Defs/Hose/RM_Hoses.xml:6-47` | thingClass vanilla `Building`; comps `CompProperties_HoseReel` + `CompProperties_Styleable` |
| 4 ThingStyleDefs `RM_HoseReel_{Scrapper,Industrial,Modern,Futuristic}` | `GimmeSomeSlack/Defs/Hose/RM_HoseReelStyles.xml:12,24,36,48` | per-build look |
| JobDefs `RM_CarryHoseEnd`, `RM_RetractHose`; WorkGiverDef `RM_HoseOrders` | `GimmeSomeSlack/Defs/Hose/RM_HoseJobs.xml:8,17,25` | colonist carry |
| C# (5,088 lines in `Source/Hose/*.cs` + 4 job files) | `GimmeSomeSlack/Source/Hose/` | namespace `RimMandrake.GimmeSomeSlack.Hose` |
| `CompHoseReel` (720 lines): lay state, carry state, state machine, gizmos | `Hose/CompHoseReel.cs:34`; Scribe keys `rmHose*` `:131-155` | the comp class is never written to a save (comps come from the def) |
| `RM_MapComponent_Hoses` (1,110): tick, lay cache, draw, reroute/retract, alert | `Hose/RM_MapComponent_Hoses.cs:17,261-290` | kept OUT of saves by `Patch_Map_ExposeComponents_SkipHoses` `:1036-1065` |
| `HoseMath` (1,517, Verse-free): planner, lead-out, state machine, tint table | `Hose/HoseMath.cs`; tint table `:1365-1380` | compiled straight into the SelfTest |
| `HoseFlow`: the flow-signal providers | `Hose/HoseFlow.cs:116-130` | FlowWorks adapter → relay → debug, first non-null wins |
| `HosePorts`: what a reel / free end couples to | `Hose/HosePorts.cs:29-150` | classifies by extension, then by type NAME (FW tank, VE PipeSystem, DBH) |
| `HoseRelay`, `HoseCarry`, `HoseLive`, `HoseEnds`, `ReelIntakeGeometry`, `Graphic_HoseReel`, `HoseStyles`, `HoseProbe` | `Hose/*.cs` | relay chains, carry jobs, live trail, end kinds, intake art geometry, reel art swap, look paths, bridge probe |
| Settings `HoseSettings` + `FireHosesMod` (a third Mod class, drawn as a tab of GSS's one window) | `Hose/HoseSettings.cs:13-76, 241-256`; tab `GimmeSomeSlackMod.cs:368-399` | 17 Scribe keys (`:54-75`), all scope [now] |
| Art: 40 PNGs, ~1.0 MB | `GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Hose/**` (root = Scrapper, `Styles/<Look>/`) | `HoseStyles.cs:22,36-40` |
| SelfTest: hose checks in 15 files (`HoseSelfTest.cs` 717 lines, `HoseCarryChecks`, `HoseLiveChecks`, `ReviewRound6/7Checks`, `StyleStage3Checks`, `GptReadFixChecks`, `GssFuzz`, `PileLookChecks`, …) | `GimmeSomeSlack/Source/SelfTest/`; csproj links `../Hose/HoseMath.cs`, `HoseRelay.cs`, `ReelIntakeGeometry.cs` (`RimMandrakeGimmeSomeSlack.SelfTest.csproj:45-50`) | offline hose 129/129 PASS (`Transient/unworked_items_2026-10-10.md:7`) |
| Live harness: `validation_hose.py` (856), `validation_style_hose.py` (343), `northstar/proof_all.py` blocks hose/maze/relay/carry/style_hose (`proof_all.py:61,84-101`) | `GimmeSomeSlack/` | probe class name hard-coded `validation_hose.py:51`; save-hygiene row H10b `:443-444` |
| North-star walk: 39 hose/reel lines | `design/validation_walks/RimMandrake/GimmeSomeSlack.md` | `state: DRAFT` (`:38`), so moving bars reverts no hash |

### 2.2 How the hose depends on the rest of GSS

The hose is built on GSS's Verse-free cord geometry, not beside it. Used members (grep of `Hose/*.cs`):
`CordPlanner.Plan/RoundCorners`, `CordLayer.Turn/ProjectOut/Settle/PinMask` (and `CordLayer`'s own `CordKind { Wire, Hose }`,
`Core/CordLayer.cs`), `CordBuilder.CellSig` (`Core/CordBuilder.cs:272`), `CordRng`/`Cell`/`V2`/`Geo` (`Core/CordMath.cs`),
`CordWorld` (`Core/CordWorld.cs`), `DrawOrder.LayerHose/HoseBaseLift/HoseQueue/Alt` (`Core/DrawOrder.cs:27-46`),
`CordMaterials.StrandQueue` (`CordMaterials.cs:60-72`), `StylePicker.{StyleFor,LookOfThing,RawStyle,IsStyled,DefaultLook}`
(`Aerial/StylePicker.cs:58-76`; `DefaultLook` reads `GimmeSomeSlackSettings.style`), `AerialStyles.{IsLook,Looks,StyleDefName}`,
`LegacyMigration.SettingsFiles`, `SettingsKitCore/Drawer` (already `_Shared`). The other direction: GSS's `StylePicker`
registers the reel (`Aerial/StylePicker.cs:36-37`), GSS's settings window has a Flexible-hoses tab (`GimmeSomeSlackMod.cs:376-399`),
and overhead spans are queued above hoses (`DrawOrder.cs:49` `OverheadQueue` uses `HoseQueue`; `AerialMaterials.cs:255-256`).

### 2.3 What FlowWorks has

| piece | where | notes |
|---|---|---|
| `RM_LiquidHose` — per-cell conduit-style tubing, vanilla `PowerConduit_Atlas` tinted blue, 1 steel, 30 HP | `FlowWorks/Defs/Machinery/RM_LiquidLogistics.xml:4-65` | marked by `RM_LiquidHoseExtension` |
| `RM_LiquidNet` — BFS over hose cells (cardinal), collecting `Building_LiquidTank`s 8-adjacent to the origin and cardinal to every hose cell; cap 1,500 cells; no cache | `FlowWorks/Source/Machinery/RM_LiquidNet.cs:21-134` | setting `liquidHosesEnabled` (`RM_MachinerySettings.cs:27,61,97`) |
| `Building_LiquidPump` — draw (channel/pond → net tank) or pour (net tank → channel), one level = 5 units per 250-tick cycle, powered + flickable | `FlowWorks/Source/LiquidTypes/Building_LiquidPump.cs:32-234`; `RM_PumpMath.cs:7,11` | records only `int Moved` (`:35,52`), **no `lastMovedUnits`/`lastMovedTick`** |
| `Building_LiquidTank` — one LiquidDef + units, `CanAccept/TryAddLiquid/TryRemoveLiquid` | `FlowWorks/Source/LiquidTypes/Building_LiquidTank.cs:29-128` | `RM_UniversalCargoTank` uses it (`RM_LiquidLogistics.xml:69-71`) |
| Net users: pump, `CompLiquidConverter`, `CompLiquidPipeAdapter` (VE PipeSystem), `RM_LiquidReaction`, `RM_LiquidBath` | `CompLiquidConverter.cs:179,201`; `CompLiquidPipeAdapter.cs:124,149`; `Kits/RM_LiquidReaction.cs:160,174`; `Kits/RM_LiquidBath.cs:94` | all go through `TanksFor`/`TankToFill` |
| `LiquidDef.color` | `FlowWorks/Source/LiquidTypes/LiquidDef.cs:71` | the real per-liquid tint the GSS hand table (`HoseMath.cs:1365-1380`) imitates |
| Settings: one `RimMandrakeFlowWorksSettings` with static sub-sections (`RM_MachinerySettings.ExposeData` etc.) | `FlowWorks/Source/RimMandrakeFlowWorksMod.cs:24,348,466-473,1235` | `PulseIntervalTicks` `:343` |
| Live chain `machinery_hoses` (pump → 5 hose cells → tank) | `FlowWorks/northstar/extensions.py:1960-1971` | north-star walk `FlowWorks.md` `state: DRAFT` (`:33`) |

### 2.4 The defect this port must close

`Transient/unworked_items_2026-10-10.md:17`: **hose reels never show real flow.** `FlowWorksPumpFlow` reflects for
`lastMovedUnits`/`lastMovedTick` on anything beside the reel (`HoseFlow.cs:26-89`) and FlowWorks has no such fields
(`Building_LiquidPump.cs:34-35`); no def carries `HosePortExtension` (`HosePorts.cs:14-17`). A reel plumps only from the
dev gizmo or a relay. Its comments are also false today: "No pump exists in FlowWorks yet" (`HoseFlow.cs:21-22`,
`HoseSettings.cs:46-49`) — the pump shipped in Phase 8. And the reel's hose carries no liquid at all: `RM_LiquidNet` never
sees it, so even a perfect flow signal would be a picture of a flow that is not happening. North-star bar
`NS_hose_plumps_only_from_powered_pump` is declared UNBUILT (`GimmeSomeSlack/validation.py`, per the unworked list).

## 3. One hose concept — which survives, what merges, what is deleted

**Decision: the GSS reel hose survives as FlowWorks' one and only "hose". `RM_LiquidHose` stops being a hose: it becomes
the static universal pipe the owner asked the reel to couple to.**

Why this split and not "delete one":

- They are two different objects, and the owner has asked for both. The reel hose is portable, carried out by a colonist,
  wound back, drawn as a stiff flat/plump sack-cloth strand with a straight lead-out (§1). `RM_LiquidHose` is a per-cell
  building laid like a conduit, permanent, conducting cardinally (`RM_LiquidNet.cs:97-110`). On 2026-10-04 he named the
  second exactly: *"standard static piping … universal pipes that can carry any liquid of any kind"*, and ruled the reel
  must connect to it. Today the only built object with that behaviour is `RM_LiquidHose`, mislabelled.
- Deleting `RM_LiquidHose` would delete FlowWorks' only working liquid line (the `machinery_hoses` chain,
  `FlowWorks/northstar/extensions.py:1960`). Deleting the reel would delete the owner-reviewed object.
- **Lineage (S1).** `RM_LiquidHose` was built as the liquids framework's `RM_HoseSpool` (`RM_LiquidLogistics.xml:4-6`;
  `design/RimMandrake/liquids_framework_design.md:177-181`: "fast-build, cheap, fragile … with a length cap", deployed
  "from shore to ship tank" in the tanker raid). That portable, length-capped, deploy-and-wind-back role is the reel's.
  So after the port the reel is the pillar's spool, and `RM_LiquidHose` becomes the permanent pipe the owner asked for
  on 10-04; its provisional fragile numbers (30 HP, 1 steel) are retuned as a permanent pipe at step 5 (still PROVISIONAL).
- Two things both called "hose" is the confusion the unworked list flags (`Transient/unworked_items_2026-10-10.md:17`). One
  name per object ends it.

So, after the port:

| object | defName | label | role |
|---|---|---|---|
| hose reel + flexible hose | `RM_HoseReel` (unchanged) | hose reel | portable line: one reel, one hose, reaches up to `maxLength` cells (default 40, `HoseSettings.cs:28-30`) |
| static pipe | `RM_UniversalPipe` (renamed from `RM_LiquidHose`, alias in §6) | universal pipe | permanent per-cell line; carries any liquid |

**What merges** — the reel's hose becomes a real edge of `RM_LiquidNet` (§4). The net already defines "which tanks a
machine reaches"; the reel adds one long link between two port things to it. The GSS `HosePorts` coupling rule merges with the net's adjacency rule
so that "what the drawn hose screws onto" and "what the liquid actually reaches" are one decision, not two that can disagree.

**What is deleted**
- `FlowWorksPumpFlow` (`HoseFlow.cs:26-90`): the reflection adapter. Replaced by a direct read of the link record (§4.3).
- `HoseTint`'s hand table (`HoseMath.cs:1365-1380`) and the `defaultFluid` setting (`HoseSettings.cs:48-49,75`): tint comes from
  the moved `LiquidDef.color` (`LiquidDef.cs:71`).
- The `useFlowWorksPumps` setting (`HoseSettings.cs:46-47,74`): flow is always the real net; nothing to opt into.
- The type-NAME classification of FlowWorks' own tank (`HosePorts.cs:43-44`): inside FlowWorks it is a compile-time type test.
  The VE PipeSystem / DBH name tests (`HosePorts.cs:55-65`) stay — they are the only way to see those mods without a reference.
- The "(none is built yet)" / "No pump exists" prose (`HoseFlow.cs:21-24`, `HoseSettings.cs:46-49`, `validation_hose.py:31`): false since Phase 8.
- `RM_LiquidHoseExtension` is kept as the marker class of the pipe (renamed `RM_UniversalPipeExtension`, old name kept as an
  empty subclass so an XML patch from another mod naming it still loads — see §6.4).

**What stays exactly as built** — the planner, lead-out, reroute/retract, carry jobs, relay chains, styles, art, alert,
state machine and every selftest assertion. The port is a move plus one new coupling, not a rewrite.

## 4. Coupling to FlowWorks pumps, tanks and the LiquidDef registry (real flow)

### 4.1 The reel and its hose as net members

`RM_LiquidNet.TanksFor` (`RM_LiquidNet.cs:46-113`) is a BFS over conducting cells. Three additions:

A **link** joins two *port things*, exactly the two the drawing already couples to (M1):
- the **reel-side port** = `CompHoseReel.Port()` (`HosePorts.Find` → `HosePortRule.Pick`, one neighbour; cached ≤60 ticks
  and re-read at once when the cached port is no longer `Spawned`, `CompHoseReel.cs:82-89`);
- the **far port** = the free end's relay reel (`RM_MapComponent_Hoses.RelayOf`) or `HosePorts.FindAt(end)`
  (`HoseEnds.Read`, `HoseEnds.cs:36-49`, cached 60 ticks). `FindAt` never returns a reel (a `CompHoseReel` thing is
  `HosePortKind.None`, `HosePorts.cs:44`); relays come only from `RelayOf`.

A reel's hose forms a link only while it is `Laid` (`HoseCarry.cs:12`) and both ports are non-null and `Spawned`. An open
end, a carried/wound hose, or a reel with no reel-side port forms none. **The reel footprint itself does not conduct**:
FlowWorks' net forbids accidental merges through endpoints (`RM_LiquidNet.cs:14-17`), and a stored reel touching two
pipe runs must not join them.

BFS rules (in `RM_LiquidNet`):
1. **Seeding.** As today (pipe cells around/under the origin), plus every link whose either port **is the origin** —
   so a pump or converter at the FAR end of a hose reaches the tanks at the reel end (M2).
2. **Traversal by port kind.** Reaching a port thing through a link: Tank → added to the result (an endpoint, as now);
   Pipe → its cells enqueued as pipe cells; Machine → not traversed (a machine is an origin, never a conductor); a relay
   reel → that reel's own link is followed (its reel-side port is the coupling the feeder screws into). Every tank or pipe
   cell reached also asks the index for links whose port is that thing, so a hose screwed onto a tank in the middle of a
   pipe run joins the run.
3. **Relays and rings.** Chains of any length conduct through rule 2; the lay-time ring refusal (`Loops`,
   `RM_MapComponent_Hoses.cs:149`) and the BFS `visited` set (keyed by cell and by thing) both guard loops.

`RM_HoseLinks` (per map) maps `port thing → reels` and is rebuilt lazily: an entry stores reel refs only, and every lookup
resolves `Port()` / the free end through their existing caches and drops a port that is not `Spawned` (M7 — the lay key
`RM_MapComponent_Hoses.cs:193` carries no port identity, so it cannot be the invalidation signal). The BFS never walks hose
geometry; each link costs one dictionary lookup.

**One coupling rule.** `HosePorts.Classify` gains `HosePortKind.Machine` (a `Building_LiquidPump`, or any thing with
`CompLiquidConverter` / `CompLiquidPipeAdapter` / `RM_LiquidReaction` / `RM_LiquidBath`), inserted before `None` in the enum
`{ Pipe, Tank, Other, None }` (`HoseMath.cs:1389`; `ClassifyComp` keeps the lowest, `HosePorts.cs:60`) with its rank pinned in
`HosePortRule` by a selftest (S12), and recognises `Building_LiquidTank` and the universal pipe by type/extension.
The net and the drawing then both read "the end is coupled to X" from `HosePorts`; a hose that LOOKS screwed on and a hose
that CARRIES are the same predicate. VE PipeSystem / DBH couplings remain visual only — liquid enters or leaves those nets
through `CompLiquidPipeAdapter` (`CompLiquidPipeAdapter.cs:11-20`), which a hose may couple to like any machine.

### 4.2 Crediting moved units to the hoses on the route

Flow is real only if the hose plumps because liquid moved *through it*. So the transfer, not a neighbour's counter, is
the signal:

- `TanksFor` records, for each tank found, the links crossed to reach it (BFS parent chain; a route crosses few reels,
  so this is a short list). Exposed as `RM_LiquidNet.Route(origin, tank)` from a per-tick cache (§9). **One route per
  tank**: where two paths reach the same tank, only the first-found is credited and a parallel hose stays flat — intended,
  and pinned by a selftest (S9).
- Every successful transfer calls one helper, `RM_LiquidNet.Credit(origin, tank, liquid, units, cadenceTicks)`, which stamps
  each reel on that route: `lastMovedUnits = units`, `lastMovedTick = now`, `lastLiquid = liquid`, `lastCadence = cadenceTicks`.
  The caller passes its own cadence: pump 250 (`IsHashIntervalTick(RM_PumpMath.CycleTicks)`), converter / adapter /
  reaction 250 (`CompTickRare`), bath (draws per craft, `Kits/RM_LiquidBath.cs:94`) passes `releaseTicks`, so one craft is
  one plump pulse, not a flicker (S7).
- Call sites (each already holds `origin`, `tank`, `liquid`, `units` at the moment of transfer):
  pump draw `Building_LiquidPump.cs:152,169`, pump pour `:231`; converter `CompLiquidConverter.cs:179-210`;
  pipe adapter `CompLiquidPipeAdapter.cs:124-160`; reaction `Kits/RM_LiquidReaction.cs:160-180`; bath `Kits/RM_LiquidBath.cs:94`.
- `Building_LiquidPump` also gets its own `lastMovedUnits`/`lastMovedTick` (inspect string, and the north-star reads), but
  the hose does not read the pump; it reads its own stamp.

Consequences, all wanted:
- **Unpowered, switched off, `liquidPumpEnabled` off, tank full, tank empty, foreign liquid in the channel** → nothing moves →
  nothing stamped → the hose drains flat after `releaseTicks`. That *is* `NS_hose_plumps_only_from_powered_pump`, built by
  construction rather than by a rule.
- A hose beside a busy pump but not on that transfer's route stays flat (the reflection adapter would have plumped it).
- Pour mode plumps the same hoses as draw mode (the route is undirected); direction is not drawn in v1 (open question 6).

### 4.3 The hose's flow signal

`HoseFlow.Providers` becomes `{ NetFlow, DebugHoseFlow }`:
- `NetFlow` reads the reel's stamp: flowing = `HoseMath.PumpFlowing(lastMovedUnits, lastMovedTick, now, lastCadence)`
  (`HoseMath.cs:1226-1227`, unchanged). Using the **crediting machine's cadence** fixes a latent bug: the adapter used the
  flow PULSE interval (`HoseFlow.cs:42-52`), but the pump cycles on its own fixed 250 ticks (`RM_PumpMath.cs:7`,
  `Building_LiquidPump.cs:90`); with the pulse set below ~170 ticks the window (1.5 × pulse) is shorter than the pump's
  cycle and a steadily pumping hose would flicker.
- `RelayHoseFlow` (`HoseFlow.cs:103-114`) is deleted: real flow through a relay is credited directly (4.1 rule 3). The debug
  flag still propagates down a relay chain for bridge tests: `DebugHoseFlow` answers true for a reel whose own flag is set or
  any of whose feeders' is (one `FeedersOf` walk, dev-only path).
- Order: `NetFlow` first; `DebugHoseFlow` only answers when `debugFlowing` is set (it returns null otherwise, so the
  default is "not flowing" rather than the debug flag's false masking nothing).

### 4.4 Tint from the LiquidDef registry

`Tint(r)` (`RM_MapComponent_Hoses.cs:483-490`) uses `r.tintLiquid.color` while the hose is plump/draining, keeping the
current wet-darkening blend (`Lerp(white, fluid, 0.25) * 0.85`). A hose last charged by a liquid keeps that liquid's tint
until it is flat. `tintLiquid` follows `lastLiquid` only once a different liquid has been credited continuously for
`minPlumpDwell` ticks, so two pumps of different liquids sharing a hose do not thrash its colour (S8). Debug flow with no
liquid ever moved tints with `RM_Liquid_FreshWater`'s registry colour (`RM_LiquidDefRegistry.xml:27`; via DefOf, null-safe;
there is no `RM_Liquid_Water`, and GSS's old stub `RM_Fluid_Water` is gone) (S5). `lastLiquid` is saved
(`Scribe_Defs`, key `rmHoseLastLiquid`) so a reloaded plump hose keeps its colour; the units/tick stamp is not saved (a
reload re-stamps within one cycle, and the saved state machine `rmHoseState` already holds the look across the reload).

### 4.5 What the hose does NOT do in v1

- It holds no liquid of its own (no in-hose volume, no spill when cut). Liquid is a tank-ledger transfer, as everywhere
  else in FlowWorks.
- An open nozzle lying in a pond or channel is not a pump intake/outlet. That is the tanker-raid shape
  (`design/RimMandrake/liquids_framework_design.md:177-181`, "hose from shore to ship tank") and is offered as an optional
  later increment (§10 step 9, open question 3).

## 5. File-by-file move

Target namespace **`RimMandrake.FlowWorks.Hose`** (tier grammar `RimMandrake.<Mod>.<Area>`, `design/NAMING_SCHEME_PLAN.md`;
matches FlowWorks' existing `.Machinery` / `.LiquidTypes`). Folders: `FlowWorks/Source/Hose/`, `FlowWorks/Source/Hose/Jobs/`,
`FlowWorks/Defs/Hose/`, `FlowWorks/Textures/RimMandrake/FlowWorks/Hose/`. Every move is a `git mv` so history follows.

### 5.1 Shared Verse-free geometry → `_Shared/SlackGeometry/`

The hose cannot leave GSS without the cord geometry it is built on (§2.2). Three ways, one recommended:

| option | cost | verdict |
|---|---|---|
| A. FlowWorks csproj links GSS's `Source/Core/*.cs` by relative path | zero GSS edits; FlowWorks' build then reads another mod's folder; types keep a `GimmeSomeSlack` namespace inside the FlowWorks DLL | rejected: a hidden build dependency on GSS's tree |
| **B. Move the shared files to `src/RimMandrake/_Shared/SlackGeometry/` (namespace `RimMandrake.Shared.Slack`), linked by both csprojs and both SelfTests** | one mechanical GSS edit (usings) | **recommended**: the precedent is `_Shared/SettingsKit` and `_Shared/HarmonyResilience` (`FlowWorks/Source/RimMandrake_FlowWorks.csproj:69-71`) |
| C. Copy the files into FlowWorks | none now; two copies drift | rejected |

Moved to `_Shared/SlackGeometry/`: `CordMath.cs` (Cell, V2, CordRng, Geo, DrawStack), `CordWorld.cs`, `CordPlanner.cs`,
`CordLayer.cs`, `DrawOrder.cs`, and `CellSig` lifted out of `CordBuilder.cs:272` into `CordWorld.cs` (so the 957-line
builder stays GSS-only). These files are Verse-free and carry no `[HarmonyPatch]`, so linking them into two assemblies
duplicates no patch.

**Every type in them becomes `internal`** (M5), as every existing `_Shared` file is (`_Shared/SettingsKit/SettingsKitCore.cs:13-32`,
`_Shared/HarmonyResilience/PatchApplier.cs` header: "every type here is INTERNAL, so each assembly carries its own copy").
Today they are `public` (`Core/CordMath.cs:16-123`, `CordWorld.cs:8-59`, `CordPlanner.cs:8-32`, `CordLayer.cs:13-77`,
`DrawOrder.cs:19,59`); left public, GSS and FlowWorks would each export a different `RimMandrake.Shared.Slack.Cell`, and any
by-name lookup would silently pick one. Any GSS public member that exposes one of these types becomes internal too (step 0
counts them; the SelfTests link source, so nothing there changes). File header rule: never name these types by string.

**Strand render queue (M6).** `DrawOrder.HoseQueue(strandQueue)` (`DrawOrder.cs:48-52`) takes GSS's runtime
`CordMaterials.StrandQueue`, computed from GSS's own `Strand_Jawa` material (`CordMaterials.cs:58-71`). The derivation moves
into shared code as `DrawOrder.BaseStrandQueue(int transparentShaderQueue)` (fallback 3000); GSS's `CordMaterials` and
FlowWorks' `HoseMaterials` both call it with `ShaderDatabase.Transparent`'s queue, so neither mod needs the other's texture
and the two cannot drift. `CordLayer`'s `CordKind.Hose` and `DrawOrder`'s hose constants stay: they are the shared contract that
keeps GSS's overhead wires drawn above FlowWorks' hoses (`DrawOrder.cs:46-49`) with neither mod referencing the other.
**This is the one step that edits GSS outside `Hose/`; it is sequenced first and alone, coordinated with the agent
building GSS features (§10 step 1).**

### 5.2 C# (GSS → FlowWorks)

| from `GimmeSomeSlack/Source/` | to `FlowWorks/Source/` | change beyond namespace |
|---|---|---|
| `Hose/CompHoseReel.cs` | `Hose/CompHoseReel.cs` | + stamp fields (§4.2), `rmHoseLastLiquid` Scribe; `HoseDefOf` stays in-file |
| `Hose/RM_MapComponent_Hoses.cs` (incl. save-skip patch, `Alert_HoseRetracted`, `HoseMaterials`) | `Hose/RM_MapComponent_Hoses.cs` | maintains `RM_HoseLinks` (§4.1); `Tint` reads `lastLiquid` (§4.4); `StylePicker` calls → `HoseLook` (below) |
| `Hose/HoseFlow.cs` | `Hose/HoseFlow.cs` | `FlowWorksPumpFlow`, `RelayHoseFlow` deleted; `NetFlow` added (§4.3) |
| `Hose/HosePorts.cs` | `Hose/HosePorts.cs` | + `Machine` kind; FW tank/pipe by type, not name (§4.1) |
| `Hose/HoseMath.cs` | `Hose/HoseMath.cs` | `HoseTint` table deleted; `HosePortKind` + `Machine`; `HosePortRule` ranks it |
| `Hose/HoseSettings.cs` | `Hose/RM_HoseSettings.cs` | becomes a static settings section of `RimMandrakeFlowWorksSettings` (§8); `FireHosesMod` deleted |
| `Hose/HoseCarry.cs`, `HoseEnds.cs`, `HoseLive.cs`, `HoseRelay.cs`, `ReelIntakeGeometry.cs`, `Graphic_HoseReel.cs` | same names under `Hose/` | namespace only |
| `Hose/HoseProbe.cs` | `Hose/HoseProbe.cs` | drops `GimmeSomeSlackProbe` **and** its `Aerial.AerialMaterials.OverheadQueue` / `Span.renderQueue` read (`HoseProbe.cs:174-175`, M3): it emits only the hose queue; GSS's `AerialProbe` emits the overhead queue; RL9 compares them in Python |
| `Hose/HoseStyles.cs` | `Hose/HoseStyles.cs` | `Root` → `RimMandrake/FlowWorks/Hose/`; the look list (`AerialStyles.Looks`/`IsLook`, 4 strings) is copied into `HoseStyles` |
| `Hose/Jobs/*.cs` (4 files) | `Hose/Jobs/*.cs` | namespace only |
| `Aerial/StylePicker.cs` def-agnostic core (GSS) | `_Shared/StylePicker/StylePickerCore.cs` (internal, linked into both) | M4: the reel's look depends on five patches, not a few helpers — `Designator_Build.ProcessInput`, the `ThingStyleDefNonPreceptSource` getter, `BuildCopyCommandUtility.BuildCopyCommand`, the `Thing.StyleDef` getter, `Frame.CompleteConstruction` (`StylePicker.cs:162-240`), all gated by `StyleIndex.Is` (`:150-160`). The shared core holds the index, the menu and the five patch bodies; each mod declares its own thin `[HarmonyPatch]` classes calling it with its own registered defs (GSS: anchors; FlowWorks: `RM_HoseReel`) and its own default look. Each gate's first test is a single def-set membership check (the `Thing.StyleDef` getter is hot). |
| — (new) | `Hose/HoseLook.cs` | FlowWorks' registration of `RM_HoseReel` with the shared picker, reading FlowWorks' own default-look setting (§8) |
| — (new) | `Hose/RM_HoseLegacy.cs` | type-name alias + settings import (§6) |
| — (new) | `Machinery/RM_HoseLinks.cs` | the link index: port thing → reels, resolved lazily (§4.1) |
| `Machinery/RM_LiquidNet.cs` (FW) | same | far-end seeding, links by port kind, route recording, `Credit` (§4.1-4.2) |

GSS keeps, and edits: `GimmeSomeSlackMod.cs:368-399` (Flexible-hoses tab removed; window becomes Cables | Overhead lines),
`Aerial/StylePicker.cs` (becomes GSS's thin patch classes over `_Shared/StylePicker`; stops registering `HoseStyles.StyledDefs`),
`CordMaterials.cs` (strand queue via the shared `DrawOrder.BaseStrandQueue`), csproj and SelfTest csproj (hose items removed),
`Core/LegacyName.cs:38-41` (the `FireHosesMod` settings handle stays so the *old* MessyConduit file still migrates into the
GSS-named file FlowWorks then imports — §6.3).

### 5.3 Defs

| from | to | change |
|---|---|---|
| `GimmeSomeSlack/Defs/Hose/RM_Hoses.xml` | `FlowWorks/Defs/Hose/RM_HoseReel.xml` | class paths → `RimMandrake.FlowWorks.Hose.*`; texPath → FW; `designationCategory` Misc → the tab FlowWorks' pump and tanks use (open question 5) |
| `GimmeSomeSlack/Defs/Hose/RM_HoseReelStyles.xml` | `FlowWorks/Defs/Hose/RM_HoseReelStyles.xml` | texPaths only |
| `GimmeSomeSlack/Defs/Hose/RM_HoseJobs.xml` | `FlowWorks/Defs/Hose/RM_HoseJobs.xml` | driver/giver class paths |
| `FlowWorks/Defs/Machinery/RM_LiquidLogistics.xml:16-65` (`RM_LiquidHose`) | same file | defName `RM_UniversalPipe`, label "universal pipe", description rewritten (no "hose"), extension class renamed |

**All defNames of the reel, its styles, jobs and work giver are unchanged.** They must vanish from GSS and appear in
FlowWorks in the same landed commit. A duplicate defName across two active mods is **not** an error: the later load
replaces the earlier silently (RimSage, `Verse/DefDatabase.cs:22-60`; only an intra-mod duplicate logs), which is why the
step-2 gate runs a script check for defNames present in both mods.

### 5.4 Textures (40 PNGs, ~1.0 MB)

`GimmeSomeSlack/Textures/RimMandrake/GimmeSomeSlack/Hose/**` → `FlowWorks/Textures/RimMandrake/FlowWorks/Hose/**`, byte-identical,
same relative layout (root = Scrapper, `Styles/<Look>/`). Paths change in defs, `HoseStyles.Root`, `validation_style_hose.py:42`
and the GSS art-sanity list `GimmeSomeSlack/validation.py:233-251` (which moves to the FlowWorks harness). Art-ledger records for
these files are re-pointed in the same commit. No pixel changes (see open question 4 on the art-review pause).

### 5.5 Settings — §8.

### 5.6 SelfTests

FlowWorks' SelfTest (`FlowWorks/Source/SelfTest/`, today `Program.cs`, `FlowKernelFuzz.cs`, `SequenceFuzz.cs`) gains:
- linked `_Shared/SlackGeometry/*.cs` and the Verse-free hose files (`HoseMath.cs`, `HoseRelay.cs`, `ReelIntakeGeometry.cs`,
  `HoseCarry.cs` pure parts, `HoseLive.cs` pure parts, `HoseStyles.cs`) exactly as GSS's SelfTest links them today
  (`RimMandrakeGimmeSomeSlack.SelfTest.csproj:45-50`);
- `HoseSelfTest.cs`, `HoseCarryChecks.cs`, `HoseLiveChecks.cs`, `StyleStage3Checks.cs` moved whole;
- the hose cases of mixed files split out: `ReviewRound6Checks.cs` (relay, 55 hose mentions), `ReviewRound7Checks.cs` (38),
  `GptReadFixChecks.cs` (35), `GssFuzz.cs` (hose fuzz section, 100), `PileLookChecks.cs` (36), `LaneAChecks.cs` (17),
  `LegacyNameChecks.cs` (6, the FireHosesMod handle) → new `FlowWorks/Source/SelfTest/HoseReviewChecks.cs` and
  `HoseFuzz.cs`; the cable cases stay in GSS.
- NEW: `HoseNetChecks.cs` — a Verse-free model of the net rules (reel footprint inert, link only when laid AND both ports spawned, far-end seeding, port removal,
  relay chain, route recording, credit stamps exactly the reels on the route, cadence window) — the offline proof of §4.

**Gate: the port is not landed until the hose assertion count in FlowWorks equals GSS's pre-port count (129 hose checks plus
the hose cases in the mixed files, counted at step 2 and written into the step's commit) and GSS's remaining count equals its
pre-port total minus exactly that number.** Nothing is allowed to fall between the two suites.

### 5.7 Validation, north-star and proof rows

| from | to |
|---|---|
| `GimmeSomeSlack/validation_hose.py` | `FlowWorks/validation_hose.py` (`HPROBE` → `RimMandrake.FlowWorks.Hose.HoseProbe`; H10b save-hygiene row checks both old and new class prefixes) |
| `GimmeSomeSlack/validation_style_hose.py` | `FlowWorks/validation_style_hose.py` |
| `proof_all.py` blocks `hose, maze, relay, carry, style_hose` + the hose half of `save_load` (`SL4_carry_states_survive`) (`GimmeSomeSlack/northstar/proof_all.py:61,84-101`) | a FlowWorks proof driver (`FlowWorks/northstar/proof_hose.py`) reusing the same block functions; GSS's `BLOCKS` loses those five |
| GSS walk hose bars (39 lines, `design/validation_walks/RimMandrake/GimmeSomeSlack.md`, DRAFT) | `design/validation_walks/RimMandrake/FlowWorks.md` `## north star` (DRAFT): moved verbatim, plus the new real-flow bars below |
| GSS `validation.py` hose rows / `suite.toggles` | FlowWorks `validation.py` |
| `human_review.py` hose stations (`save_review_map.py` has none; step 0 counts them) | FlowWorks `human_review.py` / `review_map.py` |
| `proof_all.py` `DECLARED_ROWS` (read by `modcheck/required_checks.py declared_rows()` via the walk's `checkout:` header) | split: hose rows into `proof_hose.py`'s own `DECLARED_ROWS`; the FlowWorks walk's `checkout:` names `proof_hose.py` (S10) |
| `matrix` block hose scenes (the 10-09 H0 hose matrix) | census at step 0; hose scenes move to `proof_hose.py` |
| `SL2_save_names_no_class_of_ours` | allows `RimMandrake.FlowWorks.Hose.JobDriver_*` in a save with a colonist mid-carry (6.1); forbids every other FlowWorks/GSS hose class name |

New bars (FlowWorks walk, DRAFT, seeded per the north-star practice):
- `NS_hose_plumps_only_from_powered_pump` — reel beside a powered pump, hose end on a tank: plumps within one cycle + transition;
  power cut: flat within `releaseTicks`; tank full: flat.
- `NS_hose_carries_real_units` — the far tank's units rise by exactly `levelsPerCycle × 5` per pump cycle through the hose (plain pump: 5; stations run 2 and 4, `RM_PumpingStation.xml:91,132`), and by 0 with the hose wound in.
- `NS_hose_far_end_pump` — pump at the hose's far end, tank beside the reel: the tank fills (M2).
- `NS_hose_port_removed` — far tank deconstructed mid-flow: no transfer, hose drains; rebuilt: flow resumes within 60 ticks (M7).
- `NS_hose_tint_is_carried_liquid` — a tar pump tints the hose with `RM_Liquid_Tar`'s registry colour, water with water's.
- `NS_relay_chain_carries` — pump → reel A → reel B → tank: B's tank fills; both hoses plump.
- `NS_pipe_and_hose_one_net` — pump → universal pipe run → reel → hose → tank fills.

## 6. Save compatibility

What an existing save holds that names hose things, MEASURED from the code and the 1.6 engine:

| saved thing | how it is named in the save | after the port |
|---|---|---|
| reel buildings, styles | defName `RM_HoseReel`, `RM_HoseReel_<Look>` | unchanged defNames, now FlowWorks' → loads |
| reel comp state | Scribe keys `rmHose*` under the thing (`CompHoseReel.cs:131-155`); comp class NOT written | unchanged keys → loads |
| enum values | by name (`HoseEnd`, `HoseVis`, `HoseCarryState`, `HosePendingOrder`) | names unchanged → loads |
| `RM_MapComponent_Hoses` | never written (`RM_MapComponent_Hoses.cs:1036-1065`; validation row H10b `validation_hose.py:443-444`) | nothing to alias |
| a colonist mid-carry or mid-wind | `curJob` def `RM_CarryHoseEnd`/`RM_RetractHose` + **`curDriver` written with `Class="RimMandrake.GimmeSomeSlack.Hose.JobDriver_…"`** — `Pawn_JobTracker.ExposeData` does `Scribe_Deep.Look(ref curDriver, "curDriver")` (RimSage, decompiled 1.6, `Verse/AI/Pawn_JobTracker.cs:90-93`); `Class=` resolves via `BackCompatibility.GetBackCompatibleType` → `GenTypes.GetTypeInAnyAssembly` (RimSage, `Verse/BackCompatibility.cs:166-192`) | **needs the type alias (6.1), landed in the same commit as the move (M8)** — without it Scribe logs a red could-not-find-class error, then the engine logs the **warning** "Cleaning up invalid job state" and ends the job (`Pawn_JobTracker.cs:105-108`) |
| `RM_LiquidHose` pipe cells | defName `RM_LiquidHose` | **needs the def alias (6.2)** |
| GSS hose settings | `Config/Mod_GimmeSomeSlack_FireHosesMod.xml` | **imported once (6.3)** |

### 6.1 Type-name alias

Lands in step 2, with the move (M8). A Harmony prefix on `GenTypes.GetTypeInAnyAssembly` in FlowWorks (`Hose/RM_HoseLegacy.cs`), the exact pattern GSS already uses
for its own rename (`GimmeSomeSlack/Source/GimmeSomeSlackMod.cs:456-465`, `Core/LegacyName.cs:58-68`): a name starting
`RimMandrake.GimmeSomeSlack.Hose.` **or** `RimMandrake.MessyConduit.Hose.` maps to `RimMandrake.FlowWorks.Hose.` + the rest.
It handles both prefixes itself, so it works with GSS absent, and with GSS present the two prefixes commute (GSS's maps
`MessyConduit.Hose.X` → `GimmeSomeSlack.Hose.X`, which FlowWorks' then maps; whichever runs first, the result is the
FlowWorks type). Selftest: a Verse-free `MapTypeName` table test, as `LegacyNameChecks.cs` does.

### 6.2 `RM_LiquidHose` → `RM_UniversalPipe`

A postfix on `BackCompatibility.BackCompatibleDefName`, the pattern `EnvironmentalHazards/Source/RM_DefAliases.cs` uses and
documents (a `BackCompatibilityConverter` is never asked when the mod list is unchanged — that file's header, measured from the
decompiled engine). One row: `ThingDef RM_LiquidHose → RM_UniversalPipe`. Also covers blueprints/frames (their defNames are
derived; the alias table lists `Blueprint_RM_LiquidHose`, `Frame_RM_LiquidHose` too). If the owner prefers to keep the defName
(open question 1), this sub-step is dropped and only the label changes.

### 6.3 Settings import

Verse names a settings file `Mod_<deployed folder>_<ModClass>.xml` (`Core/LegacyName.cs:9-11`). The folder is `GimmeSomeSlack`
on our machines, the Workshop id on a Steam install, and `MessyConduit` for a player who never ran GSS after its rename (GSS's
own migration runs in GSS's Mod constructor, so with GSS absent nothing renames that file) (M9). On FlowWorks' first load with
a new flag `hoseSettingsImported == false`: take the `Mod_*_FireHosesMod.xml` in `GenFilePaths.ConfigFolderPath` whose folder
is GSS's `content.FolderName` when GSS is loaded, else the newest by mtime; read it as XML by key name, ignoring its `Class=`
value; copy the 15 surviving keys (§8: 14 user-facing + `maxLengthDefaults`; the file holds 17, `HoseSettings.cs:54-75`) into
FlowWorks' hose section, set the flag, write settings. Never delete the old file. If absent, set the flag and use defaults.
`maxLength` goes through `HoseMath.MigrateMaxLength` as today (`HoseSettings.cs:60-66`).

### 6.4 Third-party XML

`RM_LiquidHoseExtension` was public for one week (built 2026-10-05). It is kept as an empty `[Obsolete]` subclass of
`RM_UniversalPipeExtension` so any patch naming it still resolves; delete it at the world-remake.

### 6.5 Mixed versions

The reel defs move between mods in one commit, so a deploy of one mod without the other can leave a player with no reel def
(GSS new, FlowWorks old) or two (GSS old, FlowWorks new). `deploy_custom_mods.py` deploys both from the same repo state, so
on our machines this cannot happen; for public builds the two mods ship together. FlowWorks' About.xml gains
`<loadAfter>mandrake.rm.gimmesomeslack</loadAfter>` (ordering only, not a dependency) so FlowWorks' def copy replaces an old
GSS's — but that replacement is silent (§5.3) and an old GSS still carries its own `CompHoseReel` type, map component,
style registration and save-skip patch, so `loadAfter` alone is not a fix (S3). FlowWorks therefore checks at startup for
the type `RimMandrake.GimmeSomeSlack.Hose.CompHoseReel` (`AccessTools.TypeByName`) and, if present, logs one red line:
"Gimme Some Slack is older than this FlowWorks; update both." Mixed versions are unsupported, and now visible.

### 6.6 Removal

Removing FlowWorks from a save with reels drops the reels with missing-def errors — the same contract every FlowWorks building
already has. Removing GSS no longer touches hoses at all (today it does). The GSS `M9_remove_mod_clean` row
(`GimmeSomeSlack/validation.py:1501`) gets simpler; FlowWorks gains no new class names in saves beyond `curDriver` (6.1).

## 7. Dependency direction after the move

- **GSS → FlowWorks: none.** GSS loses every hose file, def, texture and setting; `StylePicker` no longer names `HoseStyles`; the
  settings window loses its tab. GSS's only knowledge of FlowWorks today is inside `Hose/` (`HoseFlow.cs:47`, `HosePorts.cs:43-44`),
  so after the move a grep of `GimmeSomeSlack/Source` for `FlowWorks` must return 0 — a selftest/lint row (step 6).
- **FlowWorks → GSS: none.** FlowWorks references `_Shared/SlackGeometry` source, not GSS's assembly, folder or settings. It does
  not read GSS's global look (§8) and does not draw cords. About.xml adds only a `loadAfter` (6.5).
- **Shared contract:** `_Shared/SlackGeometry/DrawOrder.cs` — overhead spans (GSS) above hoses (FlowWorks) above cords (GSS).
  Both mods compile the same constants, so the stacking holds with either, both or neither present. The live row
  `RL9_overhead_drawn_over_hose` (`proof_all.py:90`) becomes a cross-mod row run only with both active.
- **Soft cross-mod niceties stay soft.** GS-2 / X-7 (a live fallen wire igniting spilled fuel, `design/RimMandrake/gpt_reviews/DESIGN_PASS_2026-10-08.md:83,147`)
  already plan a by-name lookup of `RM_LiquidFire.IgniteNow`; nothing here changes that.

## 8. Mod Settings in FlowWorks

**Harmony (S2).** FlowWorks applies patches one class at a time through `PatchApplier` (`RM_Patch_SuperdeepShooting.cs:27-36`),
which switches a broken patch's feature setting off and requires every patch to gate on it (`_Shared/HarmonyResilience/PatchApplier.cs:16-18`).
The moved style patches carry `[PatchFeature]` on `hose_enabled`. The save-skip patch (`Patch_Map_ExposeComponents_SkipHoses`)
and the type-alias prefix must never switch off — a failed save-skip writes the map component into saves — so they are
named in the step-2 gate's "patched N, missing X" census and a failure of either logs red.

The hose settings become one static section class, `RM_HoseSettings`, exposed from `RimMandrakeFlowWorksSettings.ExposeData`
and drawn from FlowWorks' window, the same way `RM_MachinerySettings` is wired (`RimMandrakeFlowWorksMod.cs:466-473, 1235`).
No separate `Mod` class (GSS's `FireHosesMod`, `HoseSettings.cs:241-256`, existed only so its own file was untouched). Keys are
stored with a `hose_` prefix so they cannot collide with FlowWorks' existing keys; the import (6.3) maps old → new.
Each group keeps its scope tag and per-section reset (the SettingsKit pattern GSS already uses, `HoseSettings.cs:212-238`).

| GSS key (`HoseSettings.cs:54-75`) | FlowWorks | note |
|---|---|---|
| `enabled` | `hose_enabled` "Flexible hoses" | **meaning widens:** off = hoses neither draw nor carry liquid; reels stay as fittings and keep their saved ends (open question 2) |
| `plumpAmount`, `transitionTicks`, `releaseTicks`, `minPlumpDwell` | same, `hose_` prefix | unchanged |
| `minBendRadius`, `maxLength`, `maxLengthDefaults`, `couplingSpacing`, `slack` | same | unchanged; `ShapeFingerprint` (`HoseSettings.cs:114-116`) unchanged |
| `handlingTime`, `windCellsPerSecond`, `autoResumeDroppedHose` | same | unchanged |
| `tintByContents`, `fillWobble` | same | tint now from the carried LiquidDef (§4.4) |
| `useFlowWorksPumps` | **deleted** | flow is always the real net (§3) |
| `defaultFluid` | **deleted** | replaced by the carried LiquidDef (§4.4) |
| — | `hose_defaultLook` (Scrapper / Industrial / Modern / Futuristic) | NEW: the look of a reel built without a picked style; replaces `StylePicker.DefaultLook`'s read of GSS's global setting (`Aerial/StylePicker.cs:70`) (open question 4) |
| — | `hoseSettingsImported` | internal migration flag, no control |
| FlowWorks `liquidHosesEnabled` (`RM_MachinerySettings.cs:27`) | `universalPipesEnabled` ("Universal pipes join tanks into a net") | renamed with the pipe; import reads the old key once |

Screen layout: a "Hoses and pipes" heading in FlowWorks' window holding four collapsible groups — *Flexible hoses* (master,
plump/transition/release), *Hose length and shape*, *Colonists carrying hoses*, *Look* (tint, wobble, default look) — and
the universal-pipe switch beside it. All scope [now], as audited for GSS (`HoseSettings.cs:213`). Every key gets a flip row
in FlowWorks' `validation.py` `suite.toggles` at the move — closing, for the hose half, the "20 switches never flipped" row
(`Transient/unworked_items_2026-10-10.md:21`, item `GSS_SWITCHES_PROVE_TWENTY_UNFLIPPED`).

## 9. Performance

Today, measured from the code:
- Every laid reel, **every tick**, runs `HoseFlow.Signal` (`RM_MapComponent_Hoses.cs:273-275`), whose first provider walks the
  reel's 8-way ring and, for every thing and every comp there, does a reflection field lookup and boxed reads
  (`HoseFlow.cs:54-89`). Cached per Type, but still ~12 cells × things × comps of dictionary + `GetValue` per reel per tick.
- `RM_LiquidNet.TanksFor` rebuilds its BFS on every call, with no cache (`RM_LiquidNet.cs:17-18`), and the pump calls it
  through `TankToFill` once per candidate reach cell per level (`Building_LiquidPump.cs:129-172`) — a station with reach and
  several levels per cycle runs it dozens of times in one tick.

After the port:
- **Hose signal: O(1) per reel per tick** — read four fields on the comp. The reflection walk is gone.
- **Net BFS: one per origin per tick**, cached as `(origin.thingIDNumber, TicksGame) → (tanks, routes)` in `RM_LiquidNet`;
  every `TanksFor`/`TankToFill`/`Route`/`Credit` in the same tick reuses it. The cache holds **topology only** — which tanks,
  by which route — never `CanAccept`, because the pump's draw loop fills tanks between its own `TankToFill` calls in that
  tick. No spawn/despawn version counter (S4): pipe and reel are vanilla `Building` (`RM_LiquidLogistics.xml:20`), so a
  counter would need a patch on every building spawn, and a cache keyed on the tick cannot outlive it anyway. This makes
  the net cheaper than today even with hoses added.
- **Links cost O(1)** per visited port thing (index lookup, then the reels' existing 60-tick port caches); the BFS never walks a hose's drawn geometry. `MaxHoseCells`
  (1,500) still caps a run; a link counts as one cell.
- **Credit cost** = route length in reels (typically 1-3) per transfer, ≤ a few transfers per machine per 250 ticks.
- Hose drawing, laying, rerouting and the 250-tick corridor checks are moved unchanged; their measured costs stay what GSS's
  harness reports (lay stopwatch already logged, `RM_MapComponent_Hoses.cs:195`).
- Budget check at step 7: a 20-reel, 4-pump, 10-tank map; `MapComponentTick` + all net work under 0.05 ms/tick mean,
  measured by the selftest's Verse-free net model plus one live dev-mode profile reading.

## 10. Port plan — landable increments

Each step lands on its own, leaves both mods loading clean on the full list, and carries an offline test that must pass
before it is pushed (`python3 src/RimMandrake/Utils/run_selftests.py` + the named suite). Live proof is batched at the end
(step 8) so the bridge is spent once.

| # | step | edits | offline test that gates it |
|---|---|---|---|
| 0 | **Census** — count every hose assertion in GSS's SelfTest (by file), every hose live row (incl. `matrix` scenes and `DECLARED_ROWS`), every hose setting key, every GSS public member exposing a §5.1 type, `human_review.py` hose stations; write the numbers into the step-2 commit body | none (read-only) | the counts themselves; sanity probe: `HoseSelfTest` reports 129 |
| 1 | **Shared geometry + style core** — `git mv` §5.1 files to `_Shared/SlackGeometry/` (all `internal`), namespace `RimMandrake.Shared.Slack`; `DrawOrder.BaseStrandQueue`; `StylePicker` core to `_Shared/StylePicker/`; GSS usings + csproj links | GSS (coordinate with the parallel GSS agent: land when its tree is clean of `Core/`) | GSS SelfTest count and result byte-identical to before (836/836 core, aerial 96, hose 129); `grep -n "public " _Shared/SlackGeometry` = 0; GSS DLL rebuilt with `.srchash` |
| 2 | **Move hose C#, defs, textures, selftests to FlowWorks; delete from GSS; type alias (6.1)** — namespaces, class paths, texPaths, `HoseStyles.Root`, `HoseLook`, `HoseProbe` aerial read removed, `PatchFeature` wiring, old-GSS detection (6.5), GSS tab + reel registration removed, art-ledger records re-pointed through the ledger tool. **Behaviour unchanged**: flow still debug/relay (the adapter is carried over verbatim for one step so nothing changes at once) | both mods, one commit, both DLLs + `.srchash` | FlowWorks SelfTest hose count == step-0 count, all pass; GSS count == old total − that; `MapTypeName` table test (both prefixes, unknown names untouched); `lint_mod_defs`/`validate_patch` on both; no defName in both mods (script check); `grep -r FlowWorks GimmeSomeSlack/Source` == 0; save-skip + alias patches present in the FlowWorks Harmony census |
| 3 | **Settings import + load order** — settings import (6.3), `loadAfter` (6.5) | FlowWorks | settings-import tests over fixtures `Mod_GimmeSomeSlack_FireHosesMod.xml`, `Mod_MessyConduit_FireHosesMod.xml` and `Mod_<workshopid>_FireHosesMod.xml` (15 keys copied, `maxLength` migrated, old file untouched, second load is a no-op) |
| 4 | **Settings section** — `RM_HoseSettings` in FlowWorks' window, `useFlowWorksPumps`/`defaultFluid` deleted, `hose_defaultLook` added, toggles rows | FlowWorks | shipped-defaults snapshot test (as `HoseSettings.cs:189-198`); every key has a `suite.toggles` row |
| 5 | **Universal pipe** — `RM_LiquidHose` → `RM_UniversalPipe` (label, description, extension class, def alias 6.2, PROVISIONAL permanent-pipe stats), `liquidHosesEnabled` → `universalPipesEnabled` | FlowWorks | def-alias table test; `machinery_hoses` chain renamed `machinery_pipes`, offline def check that the alias resolves |
| 6 | **Real flow** — links between port things (§4.1), far-end seeding, `RM_HoseLinks`, route recording, `Credit` at the six call sites with caller cadence, `NetFlow`, delete `FlowWorksPumpFlow`/`RelayHoseFlow`/`HoseTint`, tint from `LiquidDef.color` with dwell, `HosePortKind.Machine`, pump `lastMovedUnits/Tick` | FlowWorks | NEW `HoseNetChecks.cs` (§5.6): link only when laid + both ports spawned; open end/carried/wound = no link; stored reel touching two pipe runs does NOT merge them; pump at far end reaches tank at reel; far tank removed → no link, rebuilt → link; relay chain of 3 conducts; credit stamps exactly the reels on the route and none beside it; one route per tank; pour = draw route; cadence window = caller's cadence (no flicker at pulse 60; bath = one pulse); two-liquid tint holds for `minPlumpDwell`; hysteresis unchanged |
| 7 | **Net cache + perf** — per-tick topology cache | FlowWorks | cache test: two `TanksFor` in one tick = one BFS; next tick rebuilds; `TankToFill` re-checks `CanAccept` after a fill in the same tick; perf model under budget (§9) |
| 8 | **Live proof (one bridge session)** — moved blocks hose/maze/relay/carry/style_hose/save_load (+ hose `matrix` scenes) on the FlowWorks driver; the new real-flow bars (§5.7); RL9 cross-mod (both probes); load a pre-port save holding reels, a mid-carry colonist and `RM_LiquidHose` cells: no red error, reels laid as before, colonist resumes, pipes present | harness only | the offline harness's own selftests (`selftest_proof_all.py` moved/extended) before the bridge is taken |
| 9 | *(owner Q3; recommended in scope)* **Nozzle in liquid** — the end kind already exists (`HoseEndKind.Water`, "intake in <water>", `HoseEnds.cs:30-46`), it only moves nothing; — a pump coupled to a reel whose open nozzle lies in a dug channel or natural body draws from / pours into that cell as if it were in the pump's reach | FlowWorks | Verse-free reach test; one live row |

Item bookkeeping: steps 0-8 under `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST`; it also closes `HOSE_REEL_WIRE_TWO_HOSES_NO_WATER`
(`Transient/unworked_items_2026-10-10.md:51`) and builds `NS_hose_plumps_only_from_powered_pump`. Step 9 is filed separately if ruled in.

## 11. Open questions for the owner

1. **Should the static FlowWorks "liquid hose" become the "universal pipe"?** Today FlowWorks has a second, conduit-style
   thing also called a hose. It was built as the tanker raid's quick "hose spool" (cheap, fragile, laid from the shore to the
   ship's tank). The hose reel does that job better: it is portable, has a length limit and winds back in. *Recommend:* yes.
   The reel becomes the raid's hose. The conduit-style line is renamed universal pipe and made sturdier, as the permanent
   any-liquid pipe you asked the reel to plug into on 10-04. Old saves keep their pipes. Alternatives: delete it and make
   the reel the only liquid line (you lose permanent piping), or keep both names (two different "hoses" stays confusing).
2. **When flexible hoses are switched off in Mod Settings, should hoses still carry liquid invisibly?** *Recommend:* no. Off
   means hoses are hidden and carry nothing, so any tank fed only through a hose stops filling while it is off. Reels keep
   their hose ends, so turning it back on restores everything. Alternative: hidden but still carrying (a pure visual switch, as GSS had when hoses carried nothing).
3. **Should an open hose nozzle lying in a pond or canal act as the pump's intake or outlet?** That is the tanker-raid shape
   ("hose from the shore to the ship's tank"). The hose already *says* "intake in water" when its end lies in water, but no
   liquid moves. *Recommend:* yes, as the last step of this same job once the port is proven, on by default with a switch. Alternative: never — liquid only moves between tanks, and pumps must sit at the water's edge.
4. **Art and look.** (a) The 40 hose PNGs move to FlowWorks' folder byte-for-byte, no pixel changes — is that allowed during
   the art-review pause? *Recommend:* yes, it is a relocation, not art work. (b) Reels currently take GSS's one global
   look when built without a picked style. *Recommend:* FlowWorks gets its own default-look setting (Scrapper), so FlowWorks
   needs nothing from GSS; per-build look picking on the reel stays exactly as now.
Stated defaults in the same card, not questions (change them only if he writes otherwise):
- **Build tab:** the reel moves from Misc to Production, where every FlowWorks machine already sits
  (`RM_LiquidStills.xml:23`, `RM_LiquidLogistics.xml:47`, `RM_PumpingStation.xml:47`).
- **Flow direction:** not drawn in this job; plump and tint first.

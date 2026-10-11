# Hose port: GimmeSomeSlack → FlowWorks — design (2026-10-10)

status: DRAFT (BENCH design pass). Next: independent agent review → GPT review with all of FlowWorks → merged design → port.
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
| Settings `HoseSettings` + `FireHosesMod` (a third Mod class, drawn as a tab of GSS's one window) | `Hose/HoseSettings.cs:13-76, 241-256`; tab `GimmeSomeSlackMod.cs:368-399` | 16 fields, all scope [now] |
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
  `FlowWorks/northstar/extensions.py:1960`) and the static half of the tanker pillar's "pump at the shore fills a tank
  across the base" (`RM_LiquidLogistics.xml:19`). Deleting the reel would delete the owner-reviewed object.
- Two things both called "hose" is the confusion the unworked list flags (`Transient/unworked_items_2026-10-10.md:17`). One
  name per object ends it.

So, after the port:

| object | defName | label | role |
|---|---|---|---|
| hose reel + flexible hose | `RM_HoseReel` (unchanged) | hose reel | portable line: one reel, one hose, reaches up to `maxLength` cells (default 40, `HoseSettings.cs:28-30`) |
| static pipe | `RM_UniversalPipe` (renamed from `RM_LiquidHose`, alias in §6) | universal pipe | permanent per-cell line; carries any liquid |

**What merges** — the reel's hose becomes a real edge of `RM_LiquidNet` (§4). The net already defines "which tanks a
machine reaches"; the reel adds one long jump to it. The GSS `HosePorts` coupling rule merges with the net's adjacency rule
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

1. **A reel's footprint conducts.** Every cell of a spawned `RM_HoseReel` is a conducting cell, whatever the hose is doing.
   A reel is a fitting with a drum on it: a pump touching a reel reaches a tank touching the same reel, and a universal pipe
   ending at a reel joins it. (Stored reel = a short fat pipe; that is harmless and matches what the art shows.)
2. **A laid, coupled hose is a jump edge.** When the reel's hose is `Laid` (`HoseCarry.cs:12`) and its free end is coupled
   (`HosePorts.FindAt` returns a pipe/tank/machine/reel, `HosePorts.cs:116-149`), the BFS, on reaching any footprint cell
   of that reel, also enqueues the end cell as a conducting cell — and vice versa, so a pump at the FAR end reaches tanks
   at the reel end. An end lying open (`HoseEnd.Open`, `CompHoseReel.cs:19`) or a hose being carried/wound conducts nothing.
3. **Relays fall out for free.** A relay is a hose end coupled to another reel's intake (`HoseRelay.cs`, `FeedersOf`
   `RM_MapComponent_Hoses.cs:140`). That end cell is beside the second reel's footprint, which conducts (rule 1), whose hose
   is a jump (rule 2). Chains of any length conduct; the lay-time ring refusal stays the only loop guard needed, and the BFS
   `visited` set guards it anyway.

The set of jump edges lives in a per-map `RM_HoseLinks` index (reel thing → end cell, end cell → reel) maintained by the hose
map component when a lay/retract/couple changes (the same moments that already bump `layKey`, `RM_MapComponent_Hoses.cs:193`).
The BFS asks the index, O(1) per visited reel cell; it never walks hose geometry.

**One coupling rule.** `HosePorts.Classify` gains `HosePortKind.Machine` (a `Building_LiquidPump`, or any thing with
`CompLiquidConverter` / `CompLiquidPipeAdapter`) and recognises `Building_LiquidTank` and the universal pipe by type/extension.
The net and the drawing then both read "the end is coupled to X" from `HosePorts`; a hose that LOOKS screwed on and a hose
that CARRIES are the same predicate. VE PipeSystem / DBH couplings remain visual only — liquid enters or leaves those nets
through `CompLiquidPipeAdapter` (`CompLiquidPipeAdapter.cs:11-20`), which a hose may couple to like any machine.

### 4.2 Crediting moved units to the hoses on the route

Flow is real only if the hose plumps because liquid moved *through it*. So the transfer, not a neighbour's counter, is
the signal:

- `TanksFor` records, for each tank found, the jump edges crossed to reach it (BFS parent chain; a route crosses few reels,
  so this is a short list). Exposed as `RM_LiquidNet.Route(origin, tank)` from a per-tick cache (§9).
- Every successful transfer calls one helper, `RM_LiquidNet.Credit(origin, tank, liquid, units, cadenceTicks)`, which stamps
  each reel on that route: `lastMovedUnits = units`, `lastMovedTick = now`, `lastLiquid = liquid`, `lastCadence = cadenceTicks`.
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

`Tint(r)` (`RM_MapComponent_Hoses.cs:483-490`) uses `r.lastLiquid.color` while the hose is plump/draining, keeping the
current wet-darkening blend (`Lerp(white, fluid, 0.25) * 0.85`). A hose last charged by a liquid keeps that liquid's tint
until it is flat. Debug flow with no liquid ever moved tints with `RM_Liquid_Water`'s registry colour. `lastLiquid` is saved
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
duplicates no patch. `CordLayer`'s `CordKind.Hose` and `DrawOrder`'s hose constants stay: they are the shared contract that
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
| `Hose/HoseCarry.cs`, `HoseEnds.cs`, `HoseLive.cs`, `HoseRelay.cs`, `ReelIntakeGeometry.cs`, `Graphic_HoseReel.cs`, `HoseProbe.cs` | same names under `Hose/` | namespace only (`HoseProbe` drops its `GimmeSomeSlackProbe` dependency; its own verbs are self-contained) |
| `Hose/HoseStyles.cs` | `Hose/HoseStyles.cs` | `Root` → `RimMandrake/FlowWorks/Hose/`; the look list (`AerialStyles.Looks`/`IsLook`, 4 strings) is copied into `HoseStyles` |
| `Hose/Jobs/*.cs` (4 files) | `Hose/Jobs/*.cs` | namespace only |
| — (new) | `Hose/HoseLook.cs` | the reel's per-build look: the ~40 lines of `StylePicker` the reel uses (`StyleFor`, `RawStyle`, `LookOfThing`, menu on the build designator, `IsStyled`), reading FlowWorks' own default-look setting (§8) |
| — (new) | `Hose/RM_HoseLegacy.cs` | type-name alias + settings import (§6) |
| — (new) | `Machinery/RM_HoseLinks.cs` | the jump-edge index (§4.1) |
| `Machinery/RM_LiquidNet.cs` (FW) | same | reel footprint conducts, jump edges, route recording, `Credit` (§4.1-4.2) |

GSS keeps, and edits: `GimmeSomeSlackMod.cs:368-399` (Flexible-hoses tab removed; window becomes Cables | Overhead lines),
`Aerial/StylePicker.cs:36-37` (stops registering `HoseStyles.StyledDefs`), csproj and SelfTest csproj (hose items removed),
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
FlowWorks in the same landed commit (a duplicate defName across two active mods is a config error and the later load wins).

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
- NEW: `HoseNetChecks.cs` — a Verse-free model of the net rules (footprint conducts, jump only when laid AND coupled,
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
| `human_review.py` / `save_review_map.py` hose stations (162 mentions) | FlowWorks `human_review.py` / `review_map.py` |

New bars (FlowWorks walk, DRAFT, seeded per the north-star practice):
- `NS_hose_plumps_only_from_powered_pump` — reel beside a powered pump, hose end on a tank: plumps within one cycle + transition;
  power cut: flat within `releaseTicks`; tank full: flat.
- `NS_hose_carries_real_units` — the far tank's units rise by exactly 5 per pump cycle through the hose, and by 0 with the hose wound in.
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
| a colonist mid-carry or mid-wind | `curJob` def `RM_CarryHoseEnd`/`RM_RetractHose` + **`curDriver` written with `Class="RimMandrake.GimmeSomeSlack.Hose.JobDriver_…"`** — `Pawn_JobTracker.ExposeData` does `Scribe_Deep.Look(ref curDriver, "curDriver")` (RimSage, decompiled 1.6, `Verse/AI/Pawn_JobTracker.cs:90-93`) | **needs the type alias (6.1)** — without it the driver fails to load and the engine logs "Cleaning up invalid job state" and ends the job (same method, `:105-108`): recoverable, but a red error |
| `RM_LiquidHose` pipe cells | defName `RM_LiquidHose` | **needs the def alias (6.2)** |
| GSS hose settings | `Config/Mod_GimmeSomeSlack_FireHosesMod.xml` | **imported once (6.3)** |

### 6.1 Type-name alias

A Harmony prefix on `GenTypes.GetTypeInAnyAssembly` in FlowWorks (`Hose/RM_HoseLegacy.cs`), the exact pattern GSS already uses
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

Verse names a settings file `Mod_<folder>_<ModClass>.xml`; the hose's lives at `Mod_GimmeSomeSlack_FireHosesMod.xml`
(`Core/LegacyName.cs:9-11`). On FlowWorks' first load with a new flag `hoseSettingsImported == false`: if that file exists, read
it as XML (no type needed — the same text read `LegacyName.MigrateSettingsText` does), copy the 14 surviving keys (§8) into
FlowWorks' hose section, set the flag, write settings. Never delete the old file. If absent, set the flag and use defaults.
`maxLength` goes through `HoseMath.MigrateMaxLength` as today (`HoseSettings.cs:60-66`).

### 6.4 Third-party XML

`RM_LiquidHoseExtension` was public for one week (built 2026-10-05). It is kept as an empty `[Obsolete]` subclass of
`RM_UniversalPipeExtension` so any patch naming it still resolves; delete it at the world-remake.

### 6.5 Mixed versions

The reel defs move between mods in one commit, so a deploy of one mod without the other can leave a player with no reel def
(GSS new, FlowWorks old) or two (GSS old, FlowWorks new). `deploy_custom_mods.py` deploys both from the same repo state, so
on our machines this cannot happen; for public builds the two mods ship together and FlowWorks' About.xml gains
`<loadAfter>mandrake.rm.gimmesomeslack</loadAfter>` (ordering only, not a dependency) so that if an old GSS is ever present,
FlowWorks' copy of each def is the one that wins.

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
- **Net BFS: one per origin per tick**, cached as `(origin.thingIDNumber, tick) → (tanks, routes)` in `RM_LiquidNet`; every
  `TanksFor`/`TankToFill`/`Route`/`Credit` in the same tick reuses it. Invalidated also by a `RM_HoseLinks` change and by any
  spawn/despawn of a pipe, tank or reel on that map (a per-map version counter bumped by those things' `SpawnSetup`/`DeSpawn`).
  This makes the net cheaper than today even with hoses added.
- **Jump edges cost O(1)** per visited reel cell (index lookup); the BFS never walks a hose's drawn geometry. `MaxHoseCells`
  (1,500) still caps a run; a jump counts as one cell.
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
| 0 | **Census** — count every hose assertion in GSS's SelfTest (by file), every hose live row, every hose setting key; write the numbers into the step-2 commit body | none (read-only) | the counts themselves; sanity probe: `HoseSelfTest` reports 129 |
| 1 | **Shared geometry** — `git mv` §5.1 files to `_Shared/SlackGeometry/`, namespace `RimMandrake.Shared.Slack`, GSS usings + csproj links | GSS (coordinate with the parallel GSS agent: land when its tree is clean of `Core/`) | GSS SelfTest count and result byte-identical to before (836/836 core, aerial 96, hose 129); GSS DLL rebuilt with `.srchash` |
| 2 | **Move hose C#, defs, textures, selftests to FlowWorks; delete from GSS** — namespaces, class paths, texPaths, `HoseStyles.Root`, `HoseLook`, GSS tab + `StylePicker` registration removed. **Behaviour unchanged**: flow still debug/relay (the adapter is carried over verbatim for one step so nothing changes at once) | both mods, one commit | FlowWorks SelfTest hose count == step-0 count, all pass; GSS count == old total − that; `lint_mod_defs`/`validate_patch` on both; no defName in both mods (script check); `grep -r FlowWorks GimmeSomeSlack/Source` == 0 |
| 3 | **Save compat** — type alias (6.1), settings import (6.3), `loadAfter` (6.5) | FlowWorks | `MapTypeName` table test (both prefixes, unknown names untouched); settings-import test over a fixture `Mod_GimmeSomeSlack_FireHosesMod.xml` (14 keys copied, `maxLength` migrated, old file untouched, second load is a no-op) |
| 4 | **Settings section** — `RM_HoseSettings` in FlowWorks' window, `useFlowWorksPumps`/`defaultFluid` deleted, `hose_defaultLook` added, toggles rows | FlowWorks | shipped-defaults snapshot test (as `HoseSettings.cs:189-198`); every key has a `suite.toggles` row |
| 5 | **Universal pipe** — `RM_LiquidHose` → `RM_UniversalPipe` (label, description, extension class, def alias 6.2), `liquidHosesEnabled` → `universalPipesEnabled` | FlowWorks | def-alias table test; `machinery_hoses` chain renamed `machinery_pipes`, offline def check that the alias resolves |
| 6 | **Real flow** — reel footprint conducts, `RM_HoseLinks`, route recording, `Credit` at the six call sites, `NetFlow`, delete `FlowWorksPumpFlow`/`RelayHoseFlow`/`HoseTint`, tint from `LiquidDef.color`, `HosePortKind.Machine`, pump `lastMovedUnits/Tick` | FlowWorks | NEW `HoseNetChecks.cs` (§5.6): jump only when laid+coupled; open end/carried/wound = no jump; relay chain of 3 conducts; credit stamps exactly the reels on the route and none beside it; pour = draw route; cadence window = machine cycle (no flicker at pulse 60); hysteresis unchanged |
| 7 | **Net cache + perf** — per-tick route cache, map version counter | FlowWorks | cache test: two `TanksFor` in one tick = one BFS; a spawn bumps the version; perf model under budget (§9) |
| 8 | **Live proof (one bridge session)** — moved blocks hose/maze/relay/carry/style_hose/save_load on the FlowWorks driver; the five new real-flow bars (§5.7); load a pre-port save holding reels, a mid-carry colonist and `RM_LiquidHose` cells: no red error, reels laid as before, colonist resumes, pipes present | harness only | the offline harness's own selftests (`selftest_proof_all.py` moved/extended) before the bridge is taken |
| 9 | *(optional, owner Q3)* **Nozzle in liquid** — a pump coupled to a reel whose open nozzle lies in a dug channel or natural body draws from / pours into that cell as if it were in the pump's reach | FlowWorks | Verse-free reach test; one live row |

Item bookkeeping: steps 0-8 under `HOSE_REEL_MIGRATE_TO_FLOWWORKS_AT_LAST`; it also closes `HOSE_REEL_WIRE_TWO_HOSES_NO_WATER`
(`Transient/unworked_items_2026-10-10.md:51`) and builds `NS_hose_plumps_only_from_powered_pump`. Step 9 is filed separately if ruled in.

## 11. Open questions for the owner

1. **Should the static FlowWorks "liquid hose" become the "universal pipe"?** Today FlowWorks has a second, conduit-style
   thing also called a hose. *Recommend:* yes — rename it to universal pipe (it already is the static any-liquid pipe you asked
   the reel to plug into on 10-04), keep its behaviour, alias the old name so saves load. Alternative: delete it and make the
   reel the only liquid line (loses permanent piping), or keep both names (two "hoses" stays confusing).
2. **When flexible hoses are switched off in Mod Settings, should hoses still carry liquid invisibly?** *Recommend:* no — off
   means hoses are hidden and carry nothing; reels still work as fittings and keep their hose ends, so turning it back on restores
   everything. Alternative: hidden but still carrying (a pure visual switch, as GSS had when hoses carried nothing).
3. **Should an open hose nozzle lying in a pond or canal act as the pump's intake or outlet?** That is the tanker-raid shape
   ("hose from the shore to the ship's tank"). *Recommend:* yes, but as a later step after the port is proven, default on with a
   switch. Alternative: never — liquid only moves between tanks, and pumps must sit at the water's edge.
4. **Art and look.** (a) The 40 hose PNGs move to FlowWorks' folder byte-for-byte, no pixel changes — is that allowed during
   the art-review pause? *Recommend:* yes, it is a relocation, not art work. (b) Reels currently take GSS's one global
   look when built without a picked style. *Recommend:* FlowWorks gets its own default-look setting (Scrapper), so FlowWorks
   needs nothing from GSS; per-build look picking on the reel stays exactly as now.
5. **Which build tab should the hose reel live in?** Today it is under Misc (GSS). *Recommend:* Production, beside FlowWorks'
   stills, pump and universal pipe (`FlowWorks/Defs/Machinery/RM_LiquidStills.xml:23`, `RM_LiquidLogistics.xml:47`).
6. **Should a carrying hose show which way liquid runs?** *Recommend:* not now — plump and tint first; direction is a later
   look pass if you want it.

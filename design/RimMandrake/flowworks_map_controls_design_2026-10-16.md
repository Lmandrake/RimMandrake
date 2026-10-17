<!-- status: live -->
# FlowWorks map controls: what else beside Source and Sink (design pass, 2026-10-16)

Item: `FLOW_SOURCE_SINK_BUILD_TAPS_FOR_MAPMAKERS`. Owner, 2026-10-16, verbatim:

> *"We should have some debug-style objects in the game in FlowWorks that allow players making
> their own maps to simply have a Source and a Sink. [...] These would not be buildable, just dev
> mode placed [...] They should not have any fancy graphics, just a minimal appearance that can be
> overlooked should they be needed. I think this could enhance our Inhabited options actually...
> commission this please, after you do a small design pass asking: what other things like this do
> we likely want to create to allow us to control flows on our custom maps?"*

Source and Sink are being built separately. This memo answers his question only.

## 1. What a map maker can already use

**Headline: most of the machinery exists, but almost all of it is either a cursor-click debug
action or a whole-map/biome behaviour. Nothing is a placed object that saves with the map and
keeps doing its job.** That gap is what Source and Sink fill, and what the list below extends.

| exists | what it gives a map maker | why it is not enough |
|---|---|---|
| FlowWorks natural bodies (`RM_LiquidBody`, `limitless` flag) and `RM_LiquidStock` (floor-depth stock, recession, refill from seepage/rain/season) | a body read from terrain at map load; an edge-touching body is classified limitless, sticky | classified, not authored; you cannot say "this lake is finite" or "this edge drains" |
| Pumps, tanks, hoses, pipe nets, `CompLiquidConverter`, stills (`Machinery/`) | move and convert liquid between buildings | buildable player kit, needs power/upkeep, not a map fixture |
| Flow doors / sluices (`Superdeep/RM_FlowDoors.cs`), weirs (`Rivers/RM_Weir.cs`, arrest marker) | gate or stop flow and current on cells | gates only; nothing sets a level or a schedule |
| River current (`Rivers/RM_MapComponent_RiverCurrent.cs`) | 8-way surface current from vanilla `riverFlowMap` | "Nothing is authored here": a map with no vanilla river has no current |
| FlowWorks debug actions (`Debug/FlowWorksDebugActions.cs`): instant-dig canal, fill excavated cell with fluid, ledger/depth/cell reports | hand-staging one cell at a time | one-shot, nothing persists, nothing re-runs |
| Bridge tools `jawa/flowworks_*` (`spawn_flood`, `set_active_fluid`, `pulse`, `body_report`, `excavation_*`, `pit_report`) | scripted staging for proofs | external, agent-only, not in a save |
| Review map "frozen staging" through proof surfaces | stations held still for review | frozen for looking, not running |
| FloodedCanyon flood (`RM_MapComponent_CanyonFlood.cs`) + debug actions (arm, start now, recede, report) | the whole-map canyon flood cycle | map-wide and biome-gated (`map.Biome == RM_FloodedCanyon` or a settings switch); nothing aims it at a canal, which is why review-map station 11 failed |
| ExplosiveGrowth soak (`RM_SoakSources.cs`, `ExplosiveGrowthAPI.Soak`) + debug "Soak 5x5 here" | soak from flood and irrigated dug cells | one-click; no standing soak zone |
| WeatherSuite (`RM_WeatherKernel`, game conditions, `RM_WS_WeatherInstrument`) | map-wide weather/conditions, an instrument readout | weather is map-wide in vanilla; no local zone |
| RiverWorks folder | empty shell (only `__pycache__`); river work lives in FlowWorks `Rivers/` | nothing to reuse there |
| **Inhabited** (`src/RimMandrake/Inhabited`, design `design/Jawa/bridge/INHABITED_DESIGN.md`) | PLACE / CAST / ROUTE / FATE: hand-made places on world tiles (`Templates/*.txt`, e.g. `deepwater_cistern_hall`, `deepwater_hydroponics_bay`; PlaceDef `RM_InhabitedPlace_WaterHold`) with a persistent cast living a daily route | its water places are static terrain: a "water hold" holds water only as paint; nothing keeps a cistern full, runs a fountain, or drains a bath on a schedule |

## 2. Proposed companions (same spirit: minimal grey marker, dev-mode placed, not buildable, set in a gizmo/inspect pane, saved with the map)

Size: S = a comp over an existing hook, about a day; M = a new small mechanism; L = needs an
engine seam we do not have yet. **Inh** = Inhabited would use it in its templates.

1. **Level Holder** — holds a body or basin at a set fill fraction by adding or removing whichever
   liquid it holds (a Source+Sink pair with a setpoint read from `RM_LiquidStock`). Map makers get
   a pond that never dries or floods; test maps get a fixed water table. **S. Inh** (the water hold's
   cistern stays full without a cast doing pump work).
2. **Flood Seed** — a marker that a FloodedCanyon flood enters from, aimed at an adjacent canal or
   rect, firing on the flood clock or on a gizmo, with the biome gate lifted for that marker only.
   Fixes review-map station 11 directly; lets any map stage a flash flood. **M.**
3. **Schedule Switch** — links to nearby Sources/Sinks/flow doors and turns them on/off by hour of
   day or by a period (tide, spring burst, irrigation hour). Reuses the flow-door open/shut state.
   **S. Inh** (a ROUTE-shaped water day: fountain at dawn, bath drained at night).
4. **Current Painter** — paints direction and strength into the surface-current grid for cells with
   no vanilla river, so swept-away, silt drift and ferries work on hand-made channels. **M.**
5. **Edge Painter (Sealed / Drain)** — a dev designator marking map-edge cells as sealed (no off-map
   reservoir, so the body is finite) or drain (a limitless sink); overrides the sticky limitless
   classification. Lets a map maker decide which lakes are oceans. **M.**
6. **Soak Zone** — a rect that calls `ExplosiveGrowthAPI.Soak` at a set rate, so bloom/charge tests
   and garden maps do not need a real flood or irrigation. **S. Inh** (a planted court that blooms).
7. **Liquid Thermostat** — holds liquid within a radius at a set temperature through `RM_LiquidHeat`,
   for freeze, boil, steam and liquid-fire tests and for hot springs on authored maps. **M. Inh**
   (a heated bath or a frozen cistern).
8. **Flow Meter** — a readout tile: body id, fluid, fill, net in/out per day, limitless or not
   (the `flowworks_body_report` data, shown as an overlay label). Makes every other control
   checkable by eye and by bridge. **S.**

Considered and left off: a liquid-type converter tile (`CompLiquidConverter` already converts, and
a Source of liquid B next to a Sink is the same thing); a local rain zone (vanilla weather is
map-wide, so it is **L**; the Level Holder covers the refill a map maker actually wants).

## 3. Notes for whoever builds these

- One base class with Source/Sink: a hidden-from-architect ThingDef (`designationCategory` unset,
  dev spawn only), one flat grey texture, a gizmo per setting, all state scribed so it rides in a
  savegame (owner: *"Save user review options as save games."*).
- Every one ships behind a Mod Settings toggle and with its functional-script entry.
- Order suggestion: Flow Meter and Level Holder first (they make the others verifiable), then
  Flood Seed (it unblocks station 11), then the rest.

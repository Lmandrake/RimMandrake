---
name: rimworld-layout-layers
description: Assess a RimWorld structure on its INDEPENDENT LAYERS - power circuits, mod pipe networks (Helixien gas, chemfuel, deepchem, turret ammo, Rimefeller oil), roof and its support, floor bare-vs-covered, Odyssey substructure, and room access - checking that each is sensibly CONNECTED from sources to sinks rather than merely present. Use whenever authoring, generating, linting or reviewing a base layout, a rimplace/Lua structure template, a settlement, a gravship or any built thing headed for a live game; whenever a building is placed and does not work; whenever a cooler, turret, light, refinery or pipe-fed machine reports success and does nothing; before any deterministic write of a layout through the bridge; and any time you are about to conclude a layout is fine because every thing in it is present.
---

# Layers, not things

A RimWorld cell is not one slot. A cell is a stack of **independent layers**. A thing can be *present* on one layer and
still not *work*.

This skill prevents one failure: a building that is placed, read back exactly as planned, and dead. The building is dead
because nobody modelled the layer that makes the building work. This skill is not about a missing building.

**Presence is trivially checkable. Function is a graph problem.** Each layer below has sources and sinks. A source gives
something (power, gas, a way in). A sink needs that thing. The question is whether the sources and the sinks are connected.

Older evidence, dates and corrected lines: `references/history.md`.

## The measured case that motivates this

We placed a generated Jawa dwelling live. Each presence check passed: all 81 planned things were placed, with **0 missing,
0 wrong material**. Each room was sealed. But the nursery variant, with its `Cooler` and its `EggBox`, sat at **41.5 °C** in a
heat wave. Jawa eggs ruin above 32 °C. There were three separate causes, and each cause reported success:

1. **The template emitted no power layer at all**: no conduit, no generator, no battery. The plan, the lint and the 11
   bridge calls all said nothing about it.
2. **Hand-wiring it still silently failed.** Each call returned `success: true`. But the solar generator and the conduit
   run were on **separate power nets that never merged**. The generator read `Grid excess: 690 W`. The conduit run, four cells
   away, read `0 W`. Conduit laid directly under the generator fixed it.
3. **Correctly powered and running, it still failed.** One cooler held the 48-cell room at **35.2 °C against 39.6 °C outdoor**.
   The drop of 4.4 °C is real, and the room is still above its 32 °C limit.

Cause 1 is a gap in the model. Cause 2 is a silent fault of connection. Cause 3 is a question of size. **All three are
invisible to "is the thing there".**

## The layers

| layer | what stacks | the connectivity question |
|---|---|---|
| **things** | one **edifice** per cell; non-edifices stack freely | does the thing have what it needs beside it? |
| **terrain — top** | the visible floor | bare ground or a constructed floor? |
| **terrain — under** | natural terrain beneath a floor | what shows when the floor is removed? |
| **terrain — foundation** | Odyssey `Substructure` | do things with `terrainAffordanceNeeded=Substructure` have it? |
| **roof** | one RoofDef | is each roofed cell within support distance of a `holdsRoof` edifice? |
| **power** | conduits are non-edifice, so they sit *under* walls | is there a path from a generator to this machine? |
| **pipe nets** | the same non-edifice method, one net per resource | is there a path from a producer to this consumer? |
| **room access** | region graph | is this room enclosed, and can a pawn reach it? |

An edifice is a building def whose `isEdifice` is true (the default).

The engine rules, with real class names and constants, are in `references/layer-mechanics.md`. Read that file before you
reason about a layer. This project has repeatedly invented plausible mechanisms that were wrong.

Remember these five things:

- 🔴 **Power has TWO joining rules and mixing them up is the single most expensive mistake here.**
  - A **transmitter** is a def with `transmitsPower=true`. A transmitter joins a net **only by cardinal cell adjacency**. A
    transmitter has no radius.
  - A **connector** is a `CompPowerTrader` or `CompPowerBattery` that does not transmit, for example a Cooler. A connector
    links to the nearest transmitter within `PowerConnectionMaker.ConnectMaxDist = 6`.
  - The connector search is a plain `CellRect.ExpandedBy(6)` with **no line-of-sight test**. So the search reaches through a wall.
  - ⚠️ **`SolarGenerator` ships `transmitsPower: true`.** The generator is a *transmitter*, so do not give it the 6-cell
    reach. The wrong 6-cell reach was measured twice. A generator three cells from a conduit run sat alone at 1700 W, and the coolers read 0 W.
  - 🪤 **`Battery` is `transmitsPower: true`** too, so it is a transmitter. Only machines such as the Cooler get the 6-cell
    reach. Do not guess this from what a thing *does*. Read the def.
- 🔴 **A cooler cools the cell BEHIND it.** `Building_Cooler.TickRare` cools `Position + IntVec3.South.RotatedBy(Rotation)`. The
  cooler exhausts to `Position + IntVec3.North.RotatedBy(Rotation)`.
  - So **rot 0 in a north wall puts cold inside**. Rot 2 there points the cold side at the open air.
  - A backwards cooler still reports `Current power use: Low`, so it looks alive. Its `operatingAtHighPower` is false,
    because it tries to cool the outdoors.
- **`RoofCollapseUtility.RoofMaxSupportDistance = 6.9f`** is radial. The engine looks for support by a flood-fill through
  roofed cells. Support is *any edifice with `holdsRoof`*, not only a wall.
- **`Room.UsesOutdoorTemperature`** is true if the room `TouchesMapEdge`, or if
  `OpenRoofCount >= ceil(CellCount * 0.25)`. This property decides whether a shell can hold temperature *at all*. Check it
  before you blame a cooler.
- **A door is its own 1-cell Room**, with `properRoom: false` and role `None`. Its region type is `Portal`, and `Portal` never
  merges. So 1-cell `None` rooms in a read-back are correct, not a bug.

## This is a CHECK, not a gate

🔴 **Owner's ruling, 2026-08-26: none of this may become a hook or a block.** To paint an incomplete building is a legitimate
goal. Examples are a ruin, a half-built settlement, and a shell that someone will finish by hand. A linter that refuses to place an unpowered
cooler makes those impossible.

So the deliverable is **a report you can read and ignore**. The report answers the questions that a person asks:

```
Is this device powered?
Is this generator powering anything?
Are there breaks in the power lines?
Which rooms are sealed, and which are open to the sky?
Is this room reachable, or walled off?
Is the floor bare or covered?
Is any roof cell unsupported?
```

Each question is a **query with an answer**, not a verdict. Report the disconnected device, the generator that feeds nothing
and the gap in the run. Then build it anyway, if that is what was asked for.

## How to assess a layout

Work outward from the sinks. A **consumer** is anything that needs power, a resource, a roof, a floor or a way in. For each
consumer, ask the four questions in order. Stop at the first no, because the later questions then have no meaning.

1. **Is the layer modelled at all?** If the plan has no power net, no look at the plan finds the fault.
   Check the IR (the plan's data model, `BuildPlan` in `core.py`), not the picture.
2. **Is there a source?** A cooler needs a generator somewhere, not only a conduit. A pipe consumer needs a producer on *its
   own* `PipeNetDef`.
3. **Is there a path?** The path question is the graph question, and a path is what fails in practice. Trace the path:
   - cardinal adjacency for transmitters and pipes;
   - a 6-cell radius for power connectors;
   - region links through doors for access.
4. **Is it sized?** A path can exist and still be too weak. Examples: one cooler, too little wattage, a roof span that is too wide.
   Sizing is a *measurement*, never an inference.

**A layout that passes 1–3 and fails 4 is a design note. A layout that fails 2 or 3 is a defect that will look completely
fine on screen.** When the request is for an incomplete
building, a fail of 2 or 3 is only a line in the report.

### Assessing before a deterministic write

Assess the **plan**, offline, *before* you write a layout to a live game. A write that half-works is worse than one that
refuses. The half-working write uses a game load, looks correct, and gives numbers that people then cite.

- When a path is missing, report it before the write. Do not write and hope. Write only if the missing path is what was
  asked for (§This is a CHECK, not a gate).
- After the write, read the layers back **out of the engine**. Do not use the writer's own `success`.

⚠️ **The roof lint of rimplace is an approximation that can be wrong in both directions.** Its `roof-unsupported` rule asks
for a support within Manhattan ≤ 6. The engine uses radial 6.9, through roofed cells only.

- The lint over-warns where a support is inside 6.9 but outside Manhattan 6.
- The lint under-warns where unroofed cells separate the roof from its support. Measured: a lone roof cell 5 cells from a
  wall gives no finding. The engine does not count that cell as supported.

When you approximate an engine rule, say which way the error falls.

## What rimplace models today

rimplace is the structure template engine in `src/RimMandrake/Utils/rimplace/`. Its IR (`core.py`) holds:

- `things`, `terrain` (one layer), `foundation`, `roof` (one layer) and `floor_color`;
- `rooms` (a rect and a role string), `notes` and `refusals`;
- `clears`, `runs` and `pawns`.

**The IR has no power net, no pipe net, no circuit, no source/sink and no under-terrain layer.** `compile_calls` knows
which defs transmit, but only for the build order (§Emit transmitters BEFORE connectors).

The lint checks part of the access question, and more than people expect:

- `room-unreachable`: a room with no door on its perimeter;
- `aisle-blocked`: furniture that blocks the way in from the door;
- `room-not-sealed`, `room-unroofed`, `roof-unsupported` and `vent-defeats-cooling`.

The lint does *not* build a **graph** of rooms. `Room.doors` is declared, and it is always empty (`doors: []`). So nothing can
ask "which room connects to which" or "is this room reachable from outside".

The full API, each lint rule, the palette, and where a connectivity model would attach: `references/rimplace-gaps.md`.

🪤 **How to author a conduit over a wall.**

- `place()` refuses a second, different def in an occupied cell (`footprint-collision`).
- `wall_mount()` *deletes* what is in the cell. So `wall_mount()` with a conduit erases the wall.
- `place_overlay("CONDUIT", x, z)` is the verb for this job. The verb shares the cell and skips each collision check. A plan with
  conduit overlays on a wall row lints clean. No live paint of such a plan was measured.
- The engine allows the stack, because it rejects only a second **edifice**. But a new transmitter wipes a
  conduit in its cells. A live cell with `Cooler` + `PowerConduit` reads
  back as `solidThingDefs: ["Cooler", "PowerConduit"]`.
- Use `place_overlay` only for a def that ships `isEdifice=false`. The game wipes one of two edifices in a cell, while the
  plan reports both as placed. Conduits and pipes ship `isEdifice=false` and `altitudeLayer=Conduits`.

⚠️ **Do not simply delete that rule** of `place()`. The rule exists because three of 81 things were silently wiped while the
lint reported clean. The overlay is an exemption that the author declares. rimplace does not read `isEdifice` from the def.

## Pipe networks

Four active resource nets share **one framework**, `PipeSystem`, inside Vanilla Expanded Framework. So one assessment model
covers all four. A def joins a net through `PipeSystem.CompProperties_Resource`. Its `pipeNet` field names a `PipeNetDef`. The
oil net of Rimefeller is a separate, older implementation, and it needs its own handling.

The net defNames, the pipe defNames, the producer and consumer classes and the rule for walls are in
`references/pipe-networks.md`.

🔑 **The assessment is identical in shape to power**: producers, receivers, storages, and a pipe path between them. So build
one connectivity checker with the net as a parameter, rather than four checkers.

## Instruments, and what they cannot tell you

🔴 **Read every layer back through a DIFFERENT tool than the one that wrote it.** A bridge call's own `success` is not
evidence. Roughly 40 calls on this bridge report success and change nothing.

| layer | read it with | gap |
|---|---|---|
| things | `rimworld/get_cells_info`, `jawa/list_things` | — |
| terrain | `jawa/get_terrain_layers` (all layers at once) | — |
| roof | `jawa/get_roof_batch` | **no support or collapse-risk query exists** |
| rooms | `jawa/room_get` (holds `usesOutdoorTemperature`) | skips an outdoor room, so a breached room can return no row; pass `includeOutdoors` |
| power | `jawa/get_power_nets_batch`, `jawa/power_net`, `jawa/inspect_string` | the rate is in watt-days per tick (see the text after this table) |
| pipes | `jawa/pipe_net_info` | current map only; totals and counts per net, no members or cells; Rimefeller and Dubs Bad Hygiene rows are `verified: false`; nothing writes |
| reachability | `jawa/order_pawn` (`canReach`, then the cell where the pawn ended) | **no `CanReach` query between two cells without a pawn** |

`jawa/fix_floating_roofs` is not a query. That tool removes unsupported roof over the whole map.

`jawa/get_power_nets_batch` takes many thing ids. Things on one net share a `netIndex`, so one call shows which things are
wired together. `jawa/power_net` and the batch give the rate in watt-days per tick, so a tiny number is normal. 1 W reads as 1/60000.
Multiply the rate by 60000 to get watts.

`jawa/inspect_string` returns the text of the inspect pane. For one device, that text is decisive:

```
Power needed: 200 W
Grid excess: 0 W (0 Wd stored)      <- on a net, but nothing feeding it
Current power use: Off
```

And after the two nets were joined:

```
Grid excess: 1680 W (0 Wd stored)
Current power use: Low               <- powered, but not moving heat now
```

For a cooler or a heater, `Off` means no power. `Low` means powered, but not moving heat at that moment. `High` means that
the device moves heat. So `Low` alone does not prove that a room is cooled.

🪤 `jawa/inspect_string` takes `rect`, **not** `x`/`z`. The tool declares `defName, limit, rect, thingIds`. Our client
(`rimbridge_client.py`) refuses `x`/`z`. In a raw call the bridge drops an unknown key. A tool that has defaults then answers
on them.

## 🔴 Emit transmitters BEFORE connectors

**A connector that already has a net keeps that net. A better net that appears later does not claim it.** So a power layer
must spawn its transmitters first. Do the same for a pipe layer; for pipes this is not measured.

What the engine does (`PowerNetManager`, `PowerConnectionMaker`):

- On the next frame after its spawn, a connector takes the nearest transmitter within 6 cells.
- If no transmitter is there, the connector waits. Each new net then claims the unconnected connectors within 6 cells of its
  transmitters.
- If the connector took a transmitter on a net with no source, the connector stays on that dead net. Join that
  net to a source, or place the connector again.

Measured: coolers painted before their conduit bus read `Grid excess: 0 W`. The bus then had power and the game ticked, and
the coolers still read that. The same two coolers, destroyed and placed again, read `1700 W` immediately. The reading
`Grid excess: 0 W` means that a thing is on a net. A thing with no net prints the "not connected" text instead.

**`compile_calls` already does this.** `rimplace/netinfo.py` reads `transmitsPower` and the PipeSystem and Rimefeller pipe
comps from the def dump. The build groups then put transmitters ahead of connectors.

- 🔑 The answer is **read, never guessed**. If the dump is unreadable, `netinfo.py` returns `None`. The compiler then keeps the
  order by `(defName, stuff)` and writes a warning onto the plan. Act on that warning: place the connectors again after the
  bus, or run again with the dump.
- 🪤 **The dump nests every ThingDef field under `fields`.** `comps` is not a top-level key. A read from the root returns `None`
  silently, which reads as "nothing transmits": a clean wrong answer.

## Traps that cost real time here

- 🪤 **`jawa/destroy_batch` defaults to `categories: "Plant"`.** Use `categories`, plural. A raw call can pass a key that the tool
  does not declare, for example `defs`. The bridge drops that key. The tool then reports `Destroyed 0 thing(s)` with
  `success: true`.
- 🪤 **`jawa/build_batch` takes rotation per-op, `Def:x,z,rot`.** A top-level `rot` parameter is not declared and does nothing.
  A cooler with no rotation in its op faces north (rot 0).
- 🪤 **`rimplace calls` truncates its output at 150 characters with `…`.** The output is a *display*, not a payload for replay. The
  output cuts a 64-wall batch. Call `compile_calls()` directly. Never parse the printed list.
- 🪤 **Solar generators produce exactly 0 W at night** (`CompPowerPlantSolar`, scaled on `CurSkyGlow`). A power test at 21:30
  measures nothing. Check the clock first: `ticksAbs % 60000 / 2500` is the hour.
- 🪤 **Destroying a building marks its roof for collapse, and rebuilding under it does not cancel that.**
  - The collapse fires on the next *tick*. So a `set_roof_batch` run while paused changes 0 cells, because the doomed old roof
    still reads as correct. The room is open as soon as time runs.
  - Measured: 64 of 64 cells unroofed and `usesOutdoorTemperature: true`. The "sealed" nursery then tracked the outdoor
    temperature to the decimal.
  - 🔑 **Always read `room_get.openRoofCount` after the first tick.** Never trust the roof writer's own count.
- 🪤 **`jawa/set_substructure_batch` returns `success: true` even when it refuses cells.** The tool refuses each cell that has
  under-terrain. Such a cell is a floor over natural ground.
  - Read `changed` and `refusedCount`. Then read the foundation back: count `isSubstructure` via `jawa/get_terrain_layers`
    against the rect.
  - Measured: AncientConcrete ruins left 75/400 gravship pad cells bare, each with "Not connected to grav engine".
  - Recovery: `jawa/set_terrain_layer` with `layer=removeTop`, then `set`. Then lay the floor again, or repaint the holes to
    `Soil`.
- 🪤 **A heat wave is the cheap way to make a hot tile.** Read temperature results at *equilibrium*.
  - **Two in-game hours (~5,000 ticks) is enough** (owner, 2026-08-26). A longer run gives nothing more. A longer run starts to throw
    quest dialogs at whoever watches the screen.
  - Start the run from steady state. A room that still sheds heat from an earlier fault gives a "worst" reading that is
    history, not design.

## The template that passes

Read `design/Jawa/templates/nursery.lua` before you author a powered structure. The template is the worked answer:

- an 8x8 shell, 6x6 inside, sealed;
- two coolers in the north wall at rot 0;
- a conduit bus outside, along the north wall;
- a solar generator and a battery, each cardinally on that bus, because both are transmitters.

The template passed live. The first run held 21.7 C against 56.3 C outdoor, with a 32 C threshold. The second run came
straight from the paint, with no manual step. That run held 25.1 C at worst against 38.8 C.

⭐ **The whole cycle — edit the Lua, lint, compile, paint, soak, read back — cost no game load at all.** To soak is to let
the game run until the temperature is steady. So find and fix a wrong design against a running game, in one sitting.

## Reference files

- `references/layer-mechanics.md` — RimWorld source truth for each layer: `PowerNet` formation, `ConnectMaxDist`, roof
  support, the terrain grids, the `Room` enclosure properties, reachability. Real symbols only.
- `references/pipe-networks.md` — the `PipeSystem` framework, the four active nets and their defNames, and Rimefeller's
  separate implementation.
- `references/rimplace-gaps.md` — the engine's Lua API, its IR, each lint rule, and where a connectivity model would attach.
- `references/history.md` — the full measurements, their dates, and the lines that were wrong.

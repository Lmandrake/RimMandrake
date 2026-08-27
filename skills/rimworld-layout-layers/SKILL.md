---
name: rimworld-layout-layers
description: Assess a RimWorld structure on its INDEPENDENT LAYERS - power circuits, mod pipe networks (Helixien gas, chemfuel, deepchem, turret ammo, Rimefeller oil), roof and its support, floor bare-vs-covered, Odyssey substructure, and room access - checking that each is sensibly CONNECTED from sources to sinks rather than merely present. Use whenever authoring, generating, linting or reviewing a base layout, a rimplace/Lua structure template, a settlement, a gravship or any built thing headed for a live game; whenever a building is placed and does not work; whenever a cooler, turret, light, refinery or pipe-fed machine reports success and does nothing; before any deterministic write of a layout through the bridge; and any time you are about to conclude a layout is fine because every thing in it is present.
---

# Layers, not things

A RimWorld cell is not one slot. It is a stack of **independent layers**, and a
thing being *present* on one of them says nothing about whether it *works*.

The failure this skill exists to prevent is not a missing building. It is a
building that is placed, verified present, read back byte-perfect — and dead,
because the layer that would have made it function was never modelled at all.

**Presence is trivially checkable. Function is a graph problem.** Every layer
below has sources and sinks, and the only real question is whether they are
connected.

## The measured case that motivates this

A generated Jawa dwelling, placed live 2026-08-26, passed everything a
presence check can ask:

- 81 planned things, **81 placed**, 0 failed, 0 refused
- terrain **112/112**, roof **180/180**
- read back cell by cell against the plan: **0 missing, 0 wrong material**
- every room sealed — `properRoom: true`, `openRoofCount: 0`, `usesOutdoorTemperature: false`

The nursery variant additionally placed a `Cooler` and an `EggBox`, and the
room it was built to cool sat at **41.5 °C** through a heat wave. Jawa eggs
ruin above 32 °C. Three separate causes, each of which reported success:

1. **The template emits no power layer at all** — no conduit, no generator, no
   battery. `palette.json` has no `CONDUIT` entry. The cooler was dead on
   arrival and nothing in the plan, the lint, or the 11 bridge calls said so.
2. **Hand-wiring it still silently failed.** A solar generator and a conduit
   run were added, every call returned `success: true`, and the two ended up on
   **separate power nets that never merged** — the generator reading
   `Grid excess: 690 W`, the conduit run reading `0 W`, four cells apart. Fixed
   only by laying conduit directly under the generator.
3. **Correctly powered and running, it still failed.** One cooler held the
   48-cell room at **35.2 °C against 39.6 °C outdoor** — a real 4.4 °C
   depression, and still above the 32 °C the room exists to guarantee.

Cause 1 is a modelling gap, cause 2 is a silent connectivity failure, cause 3
is a sizing question no presence check could ever raise. **All three are
invisible to "is the thing there".**

## The layers

| layer | what stacks | the connectivity question |
|---|---|---|
| **things** | one **edifice** per cell; non-edifices stack freely | does it have what it needs adjacent? |
| **terrain — top** | the visible floor | bare ground or a constructed floor? |
| **terrain — under** | natural terrain beneath a floor | what is revealed if the floor is removed? |
| **terrain — foundation** | Odyssey `Substructure` | do things needing `terrainAffordanceNeeded=Substructure` have it? |
| **roof** | one RoofDef | is every roofed cell within support distance of a `holdsRoof` edifice? |
| **power** | conduits are non-edifice, so they sit *under* walls | is there a path from a generator to this machine? |
| **pipe nets** | same non-edifice trick, one net per resource | is there a path from a producer to this consumer? |
| **room access** | region graph | is this room enclosed, and is it reachable? |

Full source-level mechanics — real class names, real constants — are in
`references/layer-mechanics.md`. Read it before reasoning about any of these;
this project has repeatedly invented plausible mechanisms and been wrong.

The four things worth carrying in your head:

- 🔴 **Power has TWO joining rules and mixing them up is the single most
  expensive mistake here.** A **connector** (`CompPowerTrader`/`CompPowerBattery`
  that does not transmit — Cooler, Battery) links to the nearest transmitter
  within `PowerConnectionMaker.ConnectMaxDist = 6`, via a plain
  `CellRect.ExpandedBy(6)` with **no line-of-sight test**, so it reaches through
  a wall. A **transmitter** (`transmitsPower=true`) chains **only by cardinal
  cell adjacency** — no radius at all.
  ⚠️ **`SolarGenerator` ships `transmitsPower: true`.** It is a *transmitter*.
  Giving it the 6-cell reach is wrong, and was measured wrong twice: a generator
  three cells from a conduit run sat alone at 1700 W while the coolers read 0 W.
- 🔴 **A cooler cools the cell BEHIND it.** `Building_Cooler.TickRare` cools
  `Position + IntVec3.South.RotatedBy(Rotation)` and exhausts to
  `Position + IntVec3.North.RotatedBy(Rotation)`. So **rot 0 in a north wall
  puts cold inside**; rot 2 there points the cold side at the open air. A
  backwards cooler still reports `Current power use: Low` and looks alive —
  `operatingAtHighPower` is false because it is cooling the outdoors.
- **`RoofCollapseUtility.RoofMaxSupportDistance = 6.9f`**, radial, flood-filled
  through roofed cells, and support is *any edifice with `holdsRoof`* — not
  specifically a wall.
- **`Room.UsesOutdoorTemperature`** is true if the room `TouchesMapEdge`, or if
  `OpenRoofCount >= ceil(CellCount * 0.25)`. That single property decides
  whether a shell can hold temperature *at all*, before any cooler matters.
- **A door is its own 1-cell Room**, `properRoom: false`, role `None`, because
  its region type is `Portal` and `Portal` never merges. Seeing 1-cell `None`
  rooms in a read-back is correct, not a bug.

## This is a CHECK, not a gate

🔴 **Owner's ruling, 2026-08-26: none of this may become a hook or a block.**
Painting an incomplete building is a legitimate goal — a ruin, a half-built
settlement, a shell someone will finish by hand. A linter that refuses to place
an unpowered cooler makes those impossible.

So the deliverable is **a report you can read and ignore**. The questions it
answers are the ones a person actually asks:

```
Is this device powered?
Is this generator powering anything?
Are there breaks in the power lines?
Which rooms are sealed, and which are open to the sky?
Is this room reachable, or walled off?
Is the floor bare or covered?
Is any roof cell unsupported?
```

Each is a **query with an answer**, not a verdict. Report the disconnected
device, the generator feeding nothing, the gap in the run — then build it
anyway if that is what was asked for.

## How to assess a layout

Work outward from the sinks. For each **consumer** — anything that needs
power, a resource, a roof over it, a floor under it, or a way in — ask the four
questions in order. Stop at the first no; the rest are moot.

1. **Is the layer modelled at all?** If the plan has no concept of a power net,
   no amount of inspection of the plan will find the fault. Check the IR, not
   the picture.
2. **Is there a source?** A cooler needs a generator somewhere, not just a
   conduit. A pipe consumer needs a producer on *its own* `PipeNetDef`.
3. **Is there a path?** This is the graph question and the one that actually
   fails. Trace it: cardinal adjacency for transmitters and pipes, 6-cell
   radius for power connectors, region links through doors for access.
4. **Is it sized?** A path that exists can still be inadequate — one cooler,
   too little wattage, a roof span too wide. Sizing is a *measurement*, never
   an inference.

**A layout that passes 1–3 and fails 4 is a design note. A layout that fails 2
or 3 is a defect that will look completely fine on screen.**

### Assessing before a deterministic write

The whole point of assessing is to do it **before** committing a layout to a
live game, because a write that half-works is worse than one that refuses:
it consumes a game load, looks correct, and produces numbers people then cite.

So: run the layer assessment against the **plan**, offline, and refuse on a
missing path rather than writing and hoping. Then, after writing, re-read the
layers **out of the engine** — never from the writer's own `success`.

⚠️ **Roof support is the one check that is safe to approximate.** rimplace's
`roof-unsupported` uses Manhattan ≤ 6 where the engine uses radial 6.9. Since
Manhattan distance is always ≥ Euclidean, Manhattan ≤ 6 implies Euclidean ≤ 6,
so the lint **over-warns and never under-warns**. That is the right direction
for an approximation to err, and it is worth stating explicitly whenever you
approximate a rule: say which way the error falls.

## What rimplace models today

`src/RimMandrake/Utils/rimplace/` — the engine's IR (`core.py`) holds `things`,
one `terrain` layer, one `roof` layer, `rooms` (a rect and a role string),
`notes` and `refusals`. **There is no power net, no pipe net, no circuit, no
source/sink, and no terrain layer beyond the single floor.**

Its lint already covers more of the access question than people expect —
`room-not-sealed`, `room-unreachable` (a room with no door on its perimeter),
`room-unroofed`, `roof-unsupported`, `vent-defeats-cooling`. What it does *not*
do is build a **graph**: `Room.doors` is declared and always left empty, so
"which room connects to which" and "is this room reachable from outside" cannot
be asked. Three doors were placed in the measured case and all three rooms
reported `doors: []`.

Detail — full API surface, every lint rule, the palette, and where a
connectivity model would have to attach — is in `references/rimplace-gaps.md`.

🪤 **The cell-collision rule is why conduits are inexpressible.** `place()`
refuses a second, different def in an occupied cell, and `wall_mount()` — the
only primitive that touches a wall cell — *deletes* what is there first. So a
conduit-over-wall cannot be authored: you would erase the wall. The engine
allows it happily (`Cooler` + `PowerConduit` in one cell reads back as
`solidThingDefs: ["Cooler", "PowerConduit"]`), because RimWorld only rejects a
second **edifice**.

⚠️ **Do not simply delete that rule to fix this.** It exists because of a real
incident where three of 81 things were silently wiped and lint reported clean.
What is missing is a **non-edifice layer exemption** — conduits and pipes all
ship `isEdifice=false` and `altitudeLayer=Conduits`, which is exactly the
testable property that should permit the stack.

## Pipe networks

Four active resource nets all share **one framework**, `PipeSystem`, shipped
inside Vanilla Expanded Framework — so one assessment model covers all of them.
A def joins a net through `PipeSystem.CompProperties_Resource`, whose
`pipeNet` field names a `PipeNetDef`. Rimefeller's oil net is a separate,
older, parallel implementation and needs its own handling.

Net defNames, pipe defNames, producer/consumer classes and the wall-coexistence
rule are in `references/pipe-networks.md`.

🔑 **The assessment is identical in shape to power** — producers, receivers,
storages, and a pipe path between them — which is why it is worth building one
connectivity checker parameterised by net, rather than four.

## Instruments, and what they cannot tell you

🔴 **Read every layer back through a DIFFERENT tool than the one that wrote
it.** A bridge call's own `success` is not evidence; roughly 40 calls on this
bridge report success and change nothing.

| layer | read it with | gap |
|---|---|---|
| things | `rimworld/get_cells_info`, `jawa/list_things` | — |
| terrain | `jawa/get_terrain_layers` (all layers at once) | — |
| roof | `jawa/get_roof_batch` | **no support or collapse-risk query exists** |
| rooms | `jawa/room_get` | no `usesOutdoorTemperature` field; derive from `openRoofCount / cellCount` |
| power | `jawa/inspect_string` | see below |
| pipes | — | **nothing, in either direction** |
| reachability | — | **no `CanReach` wrapper; only walking a pawn there** |

⚠️ **`jawa/power_net` exists in the companion source and is NOT deployed.** The
game's loaded DLL predates it. Until it is redeployed, the only live power
reading is `jawa/inspect_string`, which returns the inspect pane as free text —
and it is genuinely decisive:

```
Power needed: 200 W
Grid excess: 0 W (0 Wd stored)      <- on a net, but nothing feeding it
Current power use: Off
```

versus, after the nets were bridged:

```
Grid excess: 1680 W (0 Wd stored)
Current power use: Low               <- actually running
```

🪤 `jawa/inspect_string` takes `rect`, **not** `x`/`z`. It declares
`defName, limit, rect, thingIds`; passing `x`/`z` is refused by the client, but
a tool that did accept unknown keys would discard them and answer on defaults.

## 🔴 Emit transmitters BEFORE connectors

`compile_calls` groups build ops by `(defName, stuff)`, which orders them
**alphabetically**: `Battery, Cooler, Door, EggBox, PowerConduit, SolarGenerator, Wall`.
So every connector is spawned before the conduit bus exists.

**Measured 2026-08-26:** coolers painted in that order read `Grid excess: 0 W`
even after the bus was energised and the game ticked. Destroying and
re-placing the same two coolers — nothing else changed — made them read
`1700 W` immediately.

⇒ **A connector binds to a transmitter at spawn, and a transmitter appearing
later does not retroactively claim it.** Any compiler that emits a power or
pipe layer must order transmitters first.

✅ **Fixed in `compile_calls` 2026-08-26.** `rimplace/netinfo.py` reads
`transmitsPower` out of each ThingDef's json in the def dump — and the
PipeSystem/Rimefeller pipe comps too — and the build groups sort transmitters
ahead of connectors. 🔑 It is **read, never guessed**: if the dump is
unreadable it returns `None`, the compiler keeps its old order and writes a
warning onto the plan, rather than inventing an ordering nobody measured.

🪤 **`Battery` is `transmitsPower: true`** — a transmitter, not a connector.
So is `SolarGenerator`. Only the machines (Cooler and friends) get the 6-cell
reach. Guessing this from what a thing *does* gets it wrong; read the def.

🪤 **The dump nests every ThingDef field under `fields`** — `comps` is not a
top-level key. Reading it from the root returns `None` silently, which reads as
"nothing transmits": a clean wrong answer, and exactly the failure this
project's instrument register exists to catch.

## Traps that cost real time here

- 🪤 **`jawa/destroy_batch` defaults to `categories: "Plant"`.** Pass a `defs`
  key it does not declare and it reports `Destroyed 0 thing(s)` with
  `success: true`, having ignored you. Use `categories`, plural.
- 🪤 **`jawa/build_batch` takes rotation per-op, `Def:x,z,rot`** — a top-level
  `rot` parameter is not declared and does nothing. A cooler placed at the
  default rotation faces whatever the grammar gave it.
- 🪤 **`rimplace calls` truncates its output at 150 characters with `…`.** It
  is a *display*, not a replayable payload — a 64-wall batch is cut. Drive from
  `compile_calls()` directly, never by parsing the printed list.
- 🪤 **Solar generators produce exactly 0 W at night**
  (`CompPowerPlantSolar`, lerped on `CurSkyGlow`). A power test run at 21:30
  measures nothing. Check the clock: `ticksAbs % 60000 / 2500` is the hour.
- 🪤 **Destroying a building marks its roof for collapse, and rebuilding under
  it does not cancel that.** The collapse fires on the next *tick*. So a
  `set_roof_batch` run while paused reports `Roofed 0 cell(s) — already correct`
  against the doomed old roof, and the room is wide open the moment time runs.
  Measured: 64 of 64 cells unroofed, `usesOutdoorTemperature: true`, and a
  "sealed" nursery that tracked outdoor temperature to the decimal.
  🔑 **Always read `room_get.openRoofCount` after the first tick**, never the
  roof writer's own count.
- 🪤 **A heat wave is the cheap way to make a hot tile**, and temperature
  results must be read at *equilibrium*. **Two in-game hours (~5,000 ticks) is
  enough** — owner, 2026-08-26. Longer runs buy nothing and start throwing quest
  dialogs at whoever is watching the screen. Start the run from steady state:
  a room still shedding heat from an earlier fault reports a "worst" reading
  that is history, not design.

## The template that passes

`design/Jawa/templates/nursery.lua` is the worked answer, and it is worth
reading before authoring any powered structure. Measured live 2026-08-26 on a
6x6 sealed shell with two coolers, an exterior conduit bus, a solar generator
sitting cardinally on that bus, and a battery inside reaching out as a
connector:

```
outdoor 56.3 C   ->   room 21.7 C        worst 22.8 C vs a 32 C threshold
```

⭐ **The whole cycle — edit the Lua, lint, compile, paint, soak, read back —
cost no game load at all.** That is the actual promise of a template engine,
and it holds: four wrong designs were found and fixed against a running game in
one sitting.

⭐ **Re-run end to end after the compiler fix: it passes with no manual step.**
Painted onto a cleared site, every powered thing came up on one 1700 W net
straight from the paint, and the room held **25.1 C worst against 38.8 C
outdoor**. Five wrong designs were found and corrected against a running game
in one sitting, at a cost of zero game loads.

## Reference files

- `references/layer-mechanics.md` — RimWorld source truth for every layer:
  `PowerNet` formation, `ConnectMaxDist`, roof support, the three terrain
  grids, `Room` enclosure properties, reachability. Real symbols only.
- `references/pipe-networks.md` — the `PipeSystem` framework, the four active
  nets and their defNames, Rimefeller's separate implementation.
- `references/rimplace-gaps.md` — the engine's full Lua API, its IR, every
  lint rule, and where a connectivity model would attach.

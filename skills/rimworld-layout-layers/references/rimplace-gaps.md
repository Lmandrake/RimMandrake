# rimplace — what it models, and where a layer model would attach

Audited 2026-08-26, corrected 2026-11-23, against `src/RimMandrake/Utils/rimplace/{core,luaenv,plan,contract,cli,selftest}.py`,
`palette.json`, the spec `design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md`,
and `design/Jawa/templates/dwelling.lua`.

## The IR (`core.py`)

```
Thing   : defName, x, z, rot=0, stuff=None, role=None, paint, extra, overlay=False
          # role is provenance only; overlay = a non-edifice that shares its cell
Room    : id, role, rect, doors=[]
Refusal : what, reason, x, z, level="WARN", code="generator-refusal"

BuildPlan: meta, things[], terrain{(x,z)->defName}, foundation{(x,z)->defName},
           roof{(x,z)->defName}, floor_color{(x,z)->ColorDef},
           rooms[], notes[], refusals[], clears[], runs[], pawns[]
```

🔴 **There is no power net, pipe net, circuit, connectivity, or source/sink
anywhere in the IR.** One top terrain layer and a `foundation` layer — no `under`.
Exactly one roof layer. No `ctx` verb writes `foundation`.

`compile_calls` emits `jawa/map_commit` with `power: True`, but that only asks
the live game to *recompute* the grid from whatever was placed. The plan never
models a net, and nothing can predict whether the grid will connect. `netinfo.py`
reads which defs transmit, only to sort the build order.

**`Room.doors` is declared and never populated.** A dwelling that placed three
doors reported `doors: []` on all three rooms. So the door→room adjacency graph
— the thing needed to answer "is this room reachable from outside" — does not
exist, even though door *things* do.

## The complete Lua `ctx` API (`luaenv.py`)

| method | signature | does |
|---|---|---|
| `role` | `role(name)` | palette role → defName; nil if unmapped |
| `has_role` | `has_role(name)` | bool |
| `in_bounds` | `in_bounds(x,z)` | inside the template rect |
| `buildable` | `buildable(x,z)` | **always True — vacuous, no site model** (recorded as such) |
| `occupied` | `occupied(x,z)` | any thing at this cell |
| `sizes` | `sizes()` | ThingDef footprint index; `{}` = UNMEASURED |
| `footprint_of` | `footprint_of(def,x,z,rot)` | cells a placement occupies, nil if unmeasured |
| `place` | `place(def,x,z,rot,stuff,role)` | the emit primitive; all refusal checks |
| `width_of`/`height_of` | `(name)` | footprint dims, default 1 if unmeasured |
| `can_place` | `can_place(name,x,z,rot)` | whole footprint fits |
| `place_role_fit` | `place_role_fit(role,x,z,w,h,rot)` | first fitting cell in a rect |
| `place_role` | `place_role(role,x,z,rot)` | resolve role, place at exact cell |
| `floor` / `floor_rect` | | set terrain |
| `roof` / `roof_rect` | | set roof |
| `wall_rect` | `wall_rect(x,z,w,h,def,stuff)` | perimeter only; does not roof |
| `door` / `window` | `door(x,z,def,stuff,rot)` | **removes the thing at the cell first**, then places; a removed non-wall gives a WARN, `wallcell-replaced-non-wall` |
| `wall_mount` | `wall_mount(role,x,z,rot)` | same replace-not-stack, for coolers/vents |
| `place_overlay` | `place_overlay(name,x,z,rot)` | a non-edifice that shares its cell (conduit, decal, sign); skips each collision check |
| `wall_attach` | `wall_attach(role,x,z,rot)` | a wall lamp on the floor cell in front of a wall; an overlay |
| `role_at` / `role_covering` | `(x,z)` | which role is in the cell / covers the cell |
| `paint` / `floor_color` | `(x,z,colorDef)` | paint a thing / colour a floor |
| `clear` / `run` / `pawn` / `ruin` | | directives; `run` is mapgen-only, `pawn` is live only for `alive` |
| `room` | `room(role,x,z,w,h,roofed)` | declare a room; floors + roofs interior |
| `note` / `refuse` | | plan annotations |

Globals: `role`, `note`, `rect`, `params`, `rng{int,chance,pick}`, plus the helper
functions of `prelude.lua`.

🪤 **There is no `rng.value()`** — only `int`, `chance`, `pick`. For a weighted
pick, nest `rng.chance()` calls rather than reaching for a uniform-float API
that does not exist: `if rng.chance(0.3) then A elseif rng.chance(0.5) then B
else C end` gives roughly a 30/35/35 split.

⭐ **A template may declare its own canvas floor: `function min_rect(params) return
W, H end`**, a global the engine looks for the same way it looks for `build`. It is
checked BEFORE `build()` runs, so an undersized rect raises `TemplateTooSmall` with
nothing placed, and `rimplace minrect <template>|all` answers the question without
building anything. It takes `params` because some floors depend on them —
`dwelling.lua` needs `5 * rooms + 1` columns.

⚠️ **A declared floor is a minimum, not a guarantee, and its absence is not a
promise.** `build()` may still `ctx:refuse` a rect that clears the floor, for reasons
no pair of numbers can express; and a template with no `min_rect` is either genuinely
size-agnostic or simply has not had one written. Nothing forces a template to declare
one — four of them (`bantha_graveyard`, `mynock_roost`, `glass_sea`, `broken_ring`)
have no real minimum and must not grow a fake one.

🔴 **No verb creates a network of any kind.** There is no `conduit()`, no
`pipe()`, no `connect()`. A template places each conduit cell itself, with `place`
or, over a wall, with `place_overlay`.

## Every lint rule (`plan.py::lint`)

| # | code | level | catches |
|---|---|---|---|
| 1 | `cell-collision` | ERROR | ≥2 things share a cell — build_batch would silently wipe one |
| 1b | `footprint-collision` | ERROR | multi-cell footprints overlap (needs the size index; else `size-unmeasured` WARN) |
| 2 | `outside-footprint` | ERROR | a thing outside the plan rect |
| 3 | `room-not-sealed` | ERROR | perimeter gap not covered by WALL/DOOR/COOLER/HEATER/WINDOW |
| 4 | `room-unreachable` | ERROR | a room with no DOOR on its perimeter |
| 5 | `room-unroofed` | WARN | interior cells lack a roof entry |
| 5b | `vent-defeats-cooling` | ERROR | a VENT in the shell of a nursery/coldroom/freezer |
| 6 | `roof-unsupported` | WARN | roof cell >6 cells **Manhattan** from any wall/pillar/window |
| 7 | `def-unverified` | ERROR | defName absent from the live def dump (only if `verified_defs` passed) |
| 8 | — | varies | re-emits generator refusals with their own level/code |
| 9 | `empty-plan` | ERROR | the template placed nothing |
| 10 | `footprint-not-cleared` | ERROR | the first directive is not a CLEAR over the whole footprint |
| 11 | `interior-bare-ground` | ERROR | a room interior cell has no floor |
| 12 | `regular-grid` | WARN | furniture in a lattice |
| 13 | `no-secondary` | ERROR | a room with a primary and no clutter |
| 14 | `door-centred` | WARN | a door at the exact midpoint of a long wall |
| 15 | `aisle-blocked` | ERROR/WARN | the doors cannot reach a primary, or reach under 45% of the room |

Overlays are exempt from rules 1 and 1b.

⚠️ **Rule 6 approximates the engine, and it can be wrong in both directions.** The
engine uses radial `RoofMaxSupportDistance = 6.9f` flood-filled through roofed
cells; the lint uses Manhattan ≤ 6 and ignores the path. It over-warns for a support
that is inside 6.9 but outside Manhattan 6. It **under-warns** where unroofed cells
separate the roof cell from the support.

⚠️ **Rule 4 is not a reachability check.** "Has a door somewhere on its
perimeter" does not establish a path to the outside, nor which rooms connect. Rule
15 fills one room from its own doors, so it does not either.

## The refusal that stops a conduit in a wall cell

`luaenv.py::Ctx.place` (shortened). `overlay=True` (`place_overlay`, `wall_attach`)
returns before the clash test, so a conduit overlay over a wall is allowed:

```python
for ex in self.plan.thing_at(x, z):
    if ex.defName == str(defName):
        return True                      # idempotent: same def, fine
...
cells = self.footprint_of(defName, x, z, rot)
if overlay:
    ...                                  # must lie inside the rect; then added
    return True
if cells is None:
    self.plan.refuse(str(defName), "size UNMEASURED ...", x, z)   # WARN, still places
else:
    clash = self._footprint_owner(cells, defName, (x, z))
    if clash is not None:
        other, cell = clash
        self.plan.refuse(str(defName),
            f"footprint overlaps {other.defName} (...)",
            x, z, level="ERROR", code="footprint-collision")
        return False
```

🪤 **A different def in an occupied cell is refused only when the size index is
loaded.** With an empty index that branch is skipped entirely and the collision
is caught later, offline, by lint rule 1 — never refused at generation time.

`door()`, `window()` and `wall_mount()` strip the cell first
(`_replace_wall_cell`), so routing a conduit through a wall with `wall_mount` would
**delete the wall**, with no refusal (in a declared room the lint then gives
`room-not-sealed`). Use `place_overlay`.

## Where a layer model would attach

- **IR**: `BuildPlan` needs `nets: {netId -> {kind, members[(x,z)]}}` alongside
  `things`, and an `under` terrain layer.
- **Collision**: the overlay exemption is declared by the author. Conduits and
  PipeSystem pipes ship `isEdifice=false` + `altitudeLayer=Conduits`; a check that
  each overlay def has that property must come from the def index, not a hardcoded
  name list.
- **Lint**: a `net-unpowered` / `net-no-source` ERROR that walks the graph —
  cardinal adjacency for transmitters and pipes, radius-6 for power connectors.
- **Rooms**: populate `Room.doors` at `door()` time, then a `room-unreachable`
  that means it — flood-fill to the map edge through Portal cells.
- **Palette**: `palette.json` has `CONDUIT` (`PowerConduit`) and `OIL_PIPE`
  (`OilPipeline`), each in some blocks only. A role with no entry makes `ctx:role`
  return nil and `place_role` hit the "no palette entry" refusal. Any other pipe or
  wire role needs adding there first.

## compile_calls

Order: clears (`jawa/destroy_batch`) → pawns → foundation, then terrain
(`jawa/set_terrain_batch`) → things grouped by `(defName, stuff)`, transmitters first
(`jawa/build_batch`) → roof (`jawa/set_roof_batch`) → paint and floor colour → one
trailing `jawa/map_commit` with `regions/pathing/power/redraw = True`. Chunked at
`MAX_OPS=4096` / `MAX_CELLS=70000`, both read from the companion's own constants.

Rotation is emitted **per op and only for things**:
`f"{defName}:{t.x},{t.z}" + (f",{t.rot}" if t.rot else "")`. Terrain and roof
rects carry none.

🪤 `rimplace calls` **prints** a truncated view — `s[:150]` with an `…`. It is a
display, not a replayable payload. Drive from `compile_calls()` directly.

## Selftest

Count the cases with `grep -c "^@case" selftest.py`. Coverage includes sandbox escapes (io/os/require unreachable), determinism
by seed, the stuff-grouping and call-ordering contract, an invented-parameter
contract check, footprint overlap, and "a footprint too small for the rooms asked
is REFUSED, not silently shrunk".

🔴 **No case covers power, pipes or connectivity** — because the IR has none of
them.

# rimplace — what it models, and where a layer model would attach

Audited 2026-08-26 against `src/RimMandrake/Utils/rimplace/{core,luaenv,plan,contract,cli,selftest}.py`,
`palette.json`, the spec `design/Jawa/bridge/STRUCTURE_TEMPLATE_ENGINE_SPEC.md`,
and `design/Jawa/templates/dwelling.lua`.

## The IR (`core.py`)

```
Thing   : defName, x, z, rot=0, stuff=None, role=None      # role is provenance only
Room    : id, role, rect, doors=[]
Refusal : what, reason, x, z, level="WARN", code="generator-refusal"

BuildPlan: meta, things[], terrain{(x,z)->defName}, roof{(x,z)->defName},
           rooms[], notes[], refusals[]
```

🔴 **There is no power net, pipe net, circuit, connectivity, or source/sink
anywhere in the IR.** Exactly one terrain layer — no `under`, no `foundation`.
Exactly one roof layer.

`compile_calls` emits `jawa/map_commit` with `power: True`, but that only asks
the live game to *recompute* the grid from whatever was placed. The plan never
models a wire, and nothing can predict whether the grid will connect.

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
| `door` | `door(x,z,def,stuff,rot)` | **removes the thing at the cell first**, then places |
| `wall_mount` | `wall_mount(role,x,z,rot)` | same replace-not-stack, for coolers/vents/wall lamps |
| `room` | `room(role,x,z,w,h,roofed)` | declare a room; floors + roofs interior |
| `note` / `refuse` | | plan annotations |

Globals: `role`, `note`, `rect`, `params`, `rng{int,chance,pick}`. That is the
whole surface after the sandbox prelude.

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
`pipe()`, no `connect()`.

## Every lint rule (`plan.py::lint`)

| # | code | level | catches |
|---|---|---|---|
| 1 | `cell-collision` | ERROR | ≥2 things share a cell — build_batch would silently wipe one |
| 1b | `footprint-collision` | ERROR | multi-cell footprints overlap (needs the size index; else `size-unmeasured` WARN) |
| 2 | `outside-footprint` | ERROR | a thing outside the plan rect |
| 3 | `room-not-sealed` | ERROR | perimeter gap not covered by WALL/DOOR/COOLER/HEATER |
| 4 | `room-unreachable` | ERROR | a room with no DOOR on its perimeter |
| 5 | `room-unroofed` | WARN | interior cells lack a roof entry |
| 5b | `vent-defeats-cooling` | ERROR | a VENT in the shell of a nursery/coldroom/freezer |
| 6 | `roof-unsupported` | WARN | roof cell >6 cells **Manhattan** from any wall/pillar |
| 7 | `def-unverified` | ERROR | defName absent from the live def dump (only if `verified_defs` passed) |
| 8 | — | varies | re-emits generator refusals with their own level/code |
| 9 | `empty-plan` | ERROR | the template placed nothing |

⚠️ **Rule 6 approximates the engine wrongly but in the safe direction.** The
engine uses radial `RoofMaxSupportDistance = 6.9f` flood-filled through roofed
cells; the lint uses Manhattan ≤ 6. Manhattan ≥ Euclidean always, so Manhattan
≤ 6 ⇒ Euclidean ≤ 6 ≤ 6.9. It **over-warns, never under-warns**.

⚠️ **Rule 4 is not a reachability check.** "Has a door somewhere on its
perimeter" does not establish a path to the outside, nor which rooms connect.

## The refusal that makes conduits inexpressible

`luaenv.py::Ctx.place`, lines 140–167:

```python
for ex in self.plan.thing_at(x, z):
    if ex.defName == str(defName):
        return True                      # idempotent: same def, fine
...
cells = self.footprint_of(defName, x, z, rot)
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

`door()` and `wall_mount()` both strip the cell first
(`plan.things = [t for t in ... if not (t.x==x and t.z==z)]`), so routing a
conduit through a wall with `wall_mount` would **delete the wall**.

## Where a layer model would attach

- **IR**: `BuildPlan` needs `nets: {netId -> {kind, members[(x,z)]}}` alongside
  `things`, and `terrain` needs to become a dict of layers keyed
  `top|under|foundation`.
- **Collision**: rule 1 needs a **non-edifice exemption**. Conduits and every
  PipeSystem pipe ship `isEdifice=false` + `altitudeLayer=Conduits`; that is the
  testable property, and it must come from the def-size/def index, not a
  hardcoded name list.
- **Lint**: a `net-unpowered` / `net-no-source` ERROR that walks the graph —
  cardinal adjacency for transmitters and pipes, radius-6 for power connectors.
- **Rooms**: populate `Room.doors` at `door()` time, then a `room-unreachable`
  that means it — flood-fill to the map edge through Portal cells.
- **Palette**: `palette.json` has **no `CONDUIT` entry**; `ctx:role("CONDUIT")`
  returns nil and `place_role("CONDUIT", …)` hits the "no palette entry"
  refusal. Any pipe or wire role needs adding there first.

## compile_calls

Order: terrain (`jawa/set_terrain_batch`) → things grouped by `(defName, stuff)`
(`jawa/build_batch`) → roof (`jawa/set_roof_batch`) → one trailing
`jawa/map_commit` with `regions/pathing/power/redraw = True`. Chunked at
`MAX_OPS=4096` / `MAX_CELLS=70000`, both read from the companion's own constants.

Rotation is emitted **per op and only for things**:
`f"{defName}:{t.x},{t.z}" + (f",{t.rot}" if t.rot else "")`. Terrain and roof
rects carry none.

🪤 `rimplace calls` **prints** a truncated view — `s[:150]` with an `…`. It is a
display, not a replayable payload. Drive from `compile_calls()` directly.

## Selftest

**28 cases** (`grep -c "^@case"`), not the 23 the spec claims — the spec line is
stale. Coverage includes sandbox escapes (io/os/require unreachable), determinism
by seed, the stuff-grouping and call-ordering contract, an invented-parameter
contract check, footprint overlap, and "a footprint too small for the rooms asked
is REFUSED, not silently shrunk".

🔴 **No case covers power, pipes, connectivity, or terrain layers** — because the
IR has none of them.

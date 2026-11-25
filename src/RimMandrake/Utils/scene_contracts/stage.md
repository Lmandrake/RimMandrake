# `s.stage`: put the cast, things and terrain on a clean station

**For:** it makes what the scene needs and tells the script what the game really made, read back in the same call.

## Accepts

| argument | meaning | example |
|---|---|---|
| `cast` | pawns by alias: `kind`, `at` (a cell, or a list of cells for a group), `faction` (default `player`), `can`; or `take=` a thing id or a list of ids that the map already holds (a fixture save) | `{"digger": dict(kind="Colonist", at=(4, 4), can=["Mining"])}`, `{"raiders": dict(take=["Human21181", "Human21233"])}` |
| `things` | things by alias: `thing` (a def), `at` (a cell or a list), `stuff`, `rot` (0 north, 1 east, 2 south, 3 west) | `{"lamp": dict(thing="WallLamp", at=(3, 7), rot=0)}` |
| `terrain` | rectangles and their terrain: `rect` (x, z, w, h), `terrain` | `{"plot": dict(rect=(0, 0, 12, 6), terrain="Soil")}` |
| `station` | a request to the stage map's allocator, `dict(size=(w, h), margin=, edge=, incident=, home=, weather=)`: the allocator gives a station that keeps its margin from every other station, it is cleaned first, and every position is relative to its corner; at close it is cleaned and released, or retired when the clean leaves a thing. Or a rectangle (x, z, w, h) on any map, cleaned first. `None`: positions are map cells and nothing is cleaned | `dict(size=(12, 8), margin=3)` |

A group (`at=[...]` or `take=[...]`) is bound as `alias[0]`, `alias[1]`, and so on, in the order given.

The game must be paused.

## Returns

A `Cast`: for each alias, the object that the game made (its id, its kind as made, its cell), or a list of them for a group.
Each value is read from the `readBack` block that the staging tool builds in its own main-thread hop
(`design/specs/2026-11-23-bridge-v2/boundary.md` §THE STAGE READ-BACK), never from the request. A taken thing is read back with
`jawa/read_paths`. Each alias is then bound in the game's session (`jawa/session` action `bind`), so that a track or a condition
can name it.

Receipt: `did`: one line for each object made and each cell changed; `hands`: the batch tools that were called;
`could_not_look`: for example "the skills of `digger` were not read: the pawn was gone at the read-back".

## State changes

It cleans the station, changes its terrain, and spawns the cast and the things. It touches no cell outside the
station. At close the station is cleaned again, unless the script asks to keep it for reading.

## Refuses

| name | when | repair |
|---|---|---|
| `GAME_RUNNING` | the game is not paused | stage before the first run, or after a run has stopped |
| `UNKNOWN_DEF` | a kind, thing or terrain def is not in the frozen dump | read the name from the def |
| `ALIAS_TAKEN` | an alias is already bound in this session | choose another alias |
| `OUTSIDE_STATION` | a position is outside the station | move it inside, or ask for a larger station |
| `NO_STAGE` | a station request on a map that no stage save put on the game | load a stage save, or make one: `python3 src/RimMandrake/Utils/stage_map.py make <game> --kind settlement` |
| `STAGE_STALE` | the game's stage file is for a map of another size | load the stage save again |
| `NO_ROOM` | no station of that size, margin and edge distance is free | release a station, or make the stage again |
| `POCKET_CANNOT_SERVE` | a pocket stage, and the request fires an incident or needs an edge, a home or weather | stage on a settlement map |
| `BAD_ARGS` | a spec of a wrong shape, or nothing to stage | the message names the spec |

**Fault:** `NO_CLEAN_STATION`: the clean of the station left a thing that blocks; `detail` names it.
**Fault:** `COULD_NOT_LOOK`: a staging tool gave no `readBack` block (an older companion), so what it made is not known.
**Fault:** `STAGING_FAULT`. The game made something other than what was asked: a replaced pawn kind, a pawn that cannot
do what `can` asks, a build that the ground refused. `done` lists what was made and what was not. The scene's run is
then an APPARATUS FAULT; it never becomes a result about the mod.

## Example (FlowWorks visit 9: `sc_ice` staged a colonist with Mining disabled; in `sc_moat_raid` grass refused the build)

```python
cast = s.stage(
    cast={"digger": dict(kind="Colonist", at=(4, 4), can=["Mining"])},
    terrain={"plot": dict(rect=(0, 0, 12, 6), terrain="Soil")})
# visit 9, as it would read here:
# scene.Fault STAGING_FAULT: digger was made as Human21301 with Mining disabled; plot: 3 cells kept Grass
```

On visit 9 each of these two faults was found only after its scene failed, and each was repaired by hand.

## The red check

`test_stage_refuses_*` (one for each row), `test_stage_reply_is_built_from_read_back`,
`test_stage_replaced_pawn_kind_is_staging_fault`, `test_stage_half_done_lists_made_and_not_made`. Planted fault: a
`stage` that echoes the request.

## Limits

It stages a station, not a colony. A bar that needs a living colony needs a fixture save (`scene.open`). `can=` is not checked yet: the receipt says so in `could_not_look` (the cast
asserts are `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER`). A read-back block whose two frames differ is named in
`could_not_look`. A stage is not put back at close: the map is disposable (only a canonical save is precious).

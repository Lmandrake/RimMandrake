# `s.stage`: put the cast, things and terrain on a clean station

**For:** it makes what the scene needs and tells the script what the game really made, read back in the same call.

## Accepts

| argument | meaning | example |
|---|---|---|
| `cast` | pawns by alias: kind, faction, position, and what each must be able to do | `{"digger": dict(kind="Colonist", at=(4, 4), can=["Mining"])}` |
| `things` | things by alias: def, stuff, position, rotation | `{"lamp": dict(thing="WallLamp", at=(3, 7))}` |
| `terrain` | cells or rectangles and their terrain | `{"plot": dict(rect=(0, 0, 12, 6), terrain="Soil")}` |
| `station` | the station to use; default: the next clean one | `None` |

The game must be paused.

## Returns

A `Cast`: for each alias, the object that the game made (its id, its kind as made, its cell) or its state when it was
not made.

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
| `NO_CLEAN_STATION` | no station of the map could be cleaned | the message names what stayed on each station |

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

It stages a station, not a colony. A bar that needs a living colony needs a fixture save (`scene.open`). The read-back
is made in the same main-thread hop as the write only after the staging hands promise that
(`RIMMANDRAKE_BUILD_STAGE_OPS_READ_BACK_NEVER_ECHO`); until then the receipt says `could_not_look: a frame may have run
between the write and the read-back`.

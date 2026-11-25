# `s.read`: read a value now, a hidden one included

**For:** it reads one value of the game at this tick and says whether the value was really read. It changes nothing.

## Accepts

| argument | meaning | example |
|---|---|---|
| `target` | an alias of the cast; or `"def:<DefType>/<defName>"`; or `"static:<Type>"`; or `"map"` | `"raider_1"` |
| `path` | field steps from the target. A step may be a public or a **private** field, a property from the reviewed list, a comp by class (`comp<RM_CompX>`), a list index. No method call | `"Position"` |

`s.read_many(reads=[(target, path), ...])` reads many values in one call, on one tick. `s.read_many(rect=(x, z, w, h),
path=...)` reads one path for every thing in a rectangle; each `Value` there also has `.of`, the thing it was read from
(`thing:<id>`). An alias is read as the thing it is bound to (`thing:<id>`); an alias that holds nothing reads `unbound`.

For a value on **every tick**, do not loop over `s.read`: name the same path in `s.run(record=...)`.

## Returns

A `Value`: `state`, `v`, `tick`.

| state | meaning |
|---|---|
| `ok` | `v` is the value. `0`, `False`, `""` and `[]` are real values here |
| `gone` | the target was made and no longer exists (dead, destroyed, left the map) |
| `unbound` | the alias was never bound to an object |
| `error` | a step of the path failed; `detail` names the step and lists the fields that the type has |

When the state is not `ok`, `v` raises if the script uses it as a number. It is never 0.

Receipt: `did: []`; `hands`: `jawa/read_paths`, 1 call; `could_not_look`: each value whose state is not `ok`; and "the
game was running: the value belongs to tick T, and the game has moved on" when the game was not paused.

## State changes

None. A read calls no method of the game except the properties on the reviewed list, each of which was reviewed to
have no effect.

## Refuses

| name | when | repair |
|---|---|---|
| `UNKNOWN_ALIAS` | the alias is not in this session | stage it, or read a def or a static |
| `BAD_PATH` | the path is not in the grammar | `help read` |
| `PATH_CALLS_METHOD` | a step is a method, or a property that is not on the reviewed list | ask for the reader in code review; meanwhile use `s.raw` (the run is then EXPLORED) |
| `SESSION_CLOSED` | the session has ended | open a session |

A wrong field name is not a refusal. It is state `error`, with the fields that exist, because only the game knows the
type.

## Example (FlowWorks: whether the moat holds a raider is hidden state of the mod)

Today the mod carries a C# proof helper that prints a text line with `held=b` (`RM_NorthstarProofs.cs`). Python calls the
helper through `jawa/static_call` and searches the text for `held=True` (`concept_scenes.py`, `_moat_rows`). The conversion
found that no path reaches that flag: `RM_SuperdeepTrap.IsHeld` computes it in a method, and nothing stores it. So the
converted scene reads where the raider stands, and the held flag waits for a trace point in the mod (a hands ticket).

```python
at = s.read("raiders[0]", "positionInt")       # "x,y,z" of the cell, read from the thing's private field
if at.state != "ok":
    raise scene.Fault("COULD_NOT_LOOK", detail=repr(at))   # never treated as 0
```

## The red check

`test_read_refuses_*` (one for each row), `test_read_gone_thing_is_gone_never_zero`,
`test_read_private_field_and_static_are_read`, `test_read_changes_nothing` (the game's state digest is the same before
and after 1,000 reads). Planted fault: a read that returns 0 for a pawn that is gone.

## Limits

A value that exists only inside a method (a local variable, a computed result that is not stored) cannot be read. That
needs a trace point in the mod (`RMTrace`), which is a hands ticket. A hidden read shows the mod's state; a bar is about
what the player sees, so a hidden value is evidence for a cause, and rarely the success condition itself.

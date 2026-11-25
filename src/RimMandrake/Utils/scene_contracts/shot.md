# `s.shot`: take a picture that is known to be fresh

**For:** it makes one picture of a rectangle of the map, for a judge agent or for the owner, and says on which tick the
picture was taken.

## Accepts

| argument | meaning | example |
|---|---|---|
| `rect` | the rectangle of map cells to show (x, z, w, h), or an alias and a margin | `("lamps", 3)`, `(60, 60, 30, 12)` |
| `name` | a name for the picture, unique in the run | `"wall_lamps_all_looks"` |
| `zoom` | pixels for each cell; default 64 | `64` |

The game must be paused.

## Returns

A `Shot`: `path` (a file in the run's folder), `tick`, `size`, `fresh`.

`fresh` is `True` only when this call wrote the file: the file's size and time differ from before the call, and the capture
tool (`jawa/artboard_capture`, off screen, 4 frames armed) says it wrote a file of more than 0 bytes. A sidecar `<path>.json`
holds the name, rectangle, tick, stamps and session. A picture that is not fresh is a fault, never a returned path.

Receipt: `did`: "wrote <path>"; `hands`: the off-screen capture tool, 1 call; `could_not_look`: for example "12 cells of
the rectangle are fogged", "the rectangle is partly off the map: 4 columns cut"; `stamps`: as the session (a picture of
a tuned game says TUNED in its sidecar file).

## State changes

It writes one picture file and its sidecar. It does not move the player's camera, does not select anything, and never
puts the game in focus or in fullscreen. The game stays paused on the same tick.

## Refuses

| name | when | repair |
|---|---|---|
| `GAME_RUNNING` | the game is not paused | `s.run` to the tick first, so that the picture has a tick |
| `RECT_OFF_MAP` | the whole rectangle is outside the map | give cells of this map |
| `NAME_TAKEN` | the name was used in this run | choose another name |
| `BAD_ARGS` | a rect of a wrong shape, a name that is not letters, digits, `_` and `-`, a zoom outside 8 to 256 | the message names it |

A shot of a flyer in flight is never a proof of flight (verify flight with `s.read` of the flight tracker). 0.3.0 does not
refuse such a shot: no converted scene has a flyer.

**Fault:** `SHOT_NOT_FRESH`: the capture returned no new file, or an empty one.

## Example (Gimme Some Slack `sc_wall_lamp_looks`: four wall lamps, one for each look, and "a capture is kept for the judge")

```python
shot = s.shot(rect=("lamp_wall", 3), name="wall_lamps_all_looks")
print(shot.path, shot.tick, shot.receipt.could_not_look)
```

The scene's rows read which look each lamp draws (`s.read`); the picture goes to the art judge.

## The red check

`test_shot_refuses_*` (one for each row), `test_shot_stale_file_is_a_fault`, `test_shot_does_not_move_camera`. Planted
fault: a `shot` that returns the path of the picture from the run before.

## Limits

A picture decides no bar by itself: a check reads state, and a judge agent makes the taste call. It shows the map as
drawn off screen; a window (the trade window, a settings page) is not in it.

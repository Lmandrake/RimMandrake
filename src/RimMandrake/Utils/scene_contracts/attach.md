# `scene.attach`: take over a session whose driver died

**For:** when a script died or a reply was lost, it gives the open session of that game to a new script, so that the
session can be read and then ended cleanly.

## Accepts

| argument | meaning | example |
|---|---|---|
| `game` | the game's name | `"ArchSmall"` |

## Returns

The session `s` of that game, with `s.state`:

| field | meaning |
|---|---|
| `paused`, `tick` | whether the game is paused, and its tick |
| `last_run` | the last run: ended or not, why, on which tick; its `trace` is `whole`, or says what is not |
| `open_act` | an act with a start record and no end record, or `None` |
| `stamps` | the stamps of the session |

The script then calls one of two: `s.close()` (undo calm, write back tuned values, clean the station, write the closing
record, release the lock) or `s.abort()` (write the closing record with `aborted`, release the lock, change nothing
else). After `attach`, the script may also read (`s.read`, `s.shot`) before it ends the session. It may not stage, run
or act: a session that lost its driver makes no more evidence.

Receipt: `did`: "took the session <id> from driver <pid>, which is dead"; `hands`: the session tool, 1 call;
`could_not_look`: for example "the last run has no end record: the game may have played past its condition".

## State changes

The session's driver becomes this process. A live run is cancelled, so that its trace gets its closing record. The game is paused if it
was running. Nothing else changes until `close` or `abort`.

## Refuses

| name | when | repair |
|---|---|---|
| `NO_SESSION` | no session is open on that game | nothing to attach; `scene.open` |
| `DRIVER_ALIVE` | the session's driver process still lives | wait for it, or stop that process; the message names it |
| `OWNER_HOLD` | his hold is on that game | use another game |
| `GAME_HELD` | another process drives that game | wait, or read `game_lock.py query all` |
| `TAKEN_OVER` | a run, or a raw call that can change the game, on a session that was taken | read it, then `s.close()` or `s.abort()` |
| `UNKNOWN_GAME` | the name is not one of the four | the message lists the four names |

## Example (FlowWorks visit 9, `sc_pit_trap_raid`, class HARNESS: "an unfinished capture")

```python
s = scene.attach("ArchSmall")
print(s.state.last_run, s.state.open_act, s.state.trace)
s.shot(rect=("pit", 4), name="as_found")      # keep what the dead driver left
s.abort()                                     # `s.shot` is not built yet; the run is judged COULD NOT LOOK: the trace says aborted
```

A session that is ended this way gives COULD NOT LOOK or APPARATUS FAULT at `scene.judge`. It does not give a
result that someone must explain later.

## The red check

`test_attach_refuses_*` (one for each row), `test_attach_pauses_a_running_game`,
`test_attach_then_run_is_refused`, `test_abort_writes_closing_record`. Planted fault: an `attach` that lets the new
driver go on with the scene.

## Limits

It needs the game process to be alive. When the game itself died, there is no session: the trace on disk has no closing
record, and `scene.judge` answers COULD NOT LOOK from the file alone. An attach that fails half way leaves the session open for the
next attach. The `abort` leaves the calm on until the calm's own lease ends.

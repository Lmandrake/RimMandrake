# `s.run`: let the game play to an exact tick, and record values on every tick

**For:** the game plays in its own loop until a condition is true or a limit is reached, stops on that tick, and
records what the script named on every tick on the way. This is the per-tick capture and the exact stop.

## Accepts

| argument | meaning | example |
|---|---|---|
| `until` | a condition from `scene.cond`, or a number of ticks | `c.any("raiders", c.outside("moat"))` |
| `limit` | the most ticks to play; always needed | `2500` |
| `speed` | `"Normal"`, `"Fast"`, `"Superfast"`, `"Ultrafast"` (the game's own loop, PLAY), or `"Step"` (the game stays paused and the companion steps the tick in slices, once a frame: STEP) | `"Normal"` |
| `rand` | the random state to write back at arm, a decimal string: the `rand` of an earlier run's `open` record. The game writes it in the hop that arms the run; the receipt says when it did not | `"12345678901234567890"` |
| `record` | more values to capture on every tick: an alias (one thing or a group) and a field path. A path may name a private field or a static field of a mod (`help read` gives the path grammar) | `[c.track("raiders", "Position"), c.track("raiders", "CurJobDef")]` |

The game must be paused at the start. Every value that `until` or the contract's conditions read is recorded without
being named in `record`.

**A group is frozen.** A group alias holds the things that were bound to it (by `s.stage`, or by `bind=` of an act),
by their ids. A member that dies or leaves reads `gone` from that tick on and stays in the group. A thing that appears
later is not in the group.

## Which speed counts for a bar

PLAY at speed 1 (`"Normal"`) is the reference. **An arm that was not compared with the reference counts for no bar.** An
arm is a speed (`"Superfast"`, `"Ultrafast"`, `"Step"`, ...). A comparison is `scene.py compare`: one plan, one fixture save
loaded fresh for every run, the random state written back before every run, five runs of each arm, traces compared tick
by tick (`scene_compare.py`). The comparison holds for one key: the plan's hash, the loaded hashes of our mods, the
companion's hash, the mod list and the arm. When any part of the key changes, the comparison is owed again, and until it
is made again the arm counts for no bar. The latest result: `design/specs/2026-11-23-bridge-v2/experiments/play_vs_step_result.md`.

## Returns

A run result `r`: `r.why` (`hit`, `limit`, `unknown`, `cancelled`, `fault`), `r.hit` (`why` is `hit`), `r.tick` (the
tick on which the game stopped, whatever the reason), `r.values` (each recorded value at the end of that tick, with its
state), `r.trace` (the file).

- **The first evaluation is before any tick.** A condition that is already true gives `hit` on the start tick, and no
  tick is played.
- **A hit wins over the limit** when both fall on one tick.
- **An unreadable value stops the run.** When a value that `until` reads is not `ok` at the end of a tick, the
  condition is neither true nor false. The run stops on that tick with `why = "unknown"`, and names the value. The
  library never counts an unreadable value as false and never as true. A `gone` member that the condition expects
  (`c.gone_ok(...)`) is readable. `r.hit` raises when `why` is `unknown`, and so does the `.v` of a value that was not read. When
  the game's own answer is `hit` or `limit` over an unreadable value, the library still answers `unknown` and says so.
- **A lost reply is handled inside the call.** The library gives the run a request id before it sends it, and asks the
  game for that id's status until the run has ended. The script gets `r` or a fault that carries the id. When the
  script's own process died, `scene.attach` returns the same run.

Receipt: `did`: "played ticks T1 to T2 at speed S; paused on T2"; `hands`: `jawa/run_until`, 1 call; `could_not_look`:
each recorded value that was not readable on some tick (its state, the first tick, the count of ticks), and trace rows
that were dropped. A value is written to the trace on the first tick, on the last tick, and on each tick on which it
changed.

## State changes

The game's clock moves from T1 to T2 and the game does what it does. The library changes nothing else. The game is
paused on T2. The condition is evaluated inside the game at the end of each tick; it decides only when to stop, never a
verdict.

## Refuses

| name | when | repair |
|---|---|---|
| `NO_LIMIT` | no `limit` | give the most ticks the run may play |
| `GAME_RUNNING` | the game is not paused at the start | `s.run` ends paused; something else unpaused the game: read `s.state` |
| `RUN_ACTIVE` | this session already has a run that has not ended | read `s.state.last_run`, then `s.cancel_run()` |
| `UNRECORDED_VALUE` | `until` reads a value that no track or tap is able to record | use a recordable path (`help cond`), or file a hands ticket |
| `BAD_PATH` | a path in `record` is not in the path grammar | `help read` |
| `SESSION_CLOSED` | the session has ended | open a session |

**Faults:** `RAN_PAST_END` (the game played ticks after the condition was true), `PAUSE_REFUSED` (another mod kept the
game running), `TRACE_INCOMPLETE` (no closing record, or the closing record counts dropped rows). After each of them the
run cannot be evidence.

## Example (FlowWorks `sc_moat_raid`: three valid runs gave PASS, FAIL, PASS; the scene now reads each raider every 60 ticks from Python)

```python
raid = s.act.incident("RaidEnemy", points=400, bind="raiders")   # the group is what this act spawned
s.act.remove("sluice_gate", name="sluice_open")
r = s.run(until=c.any("raiders", c.outside("moat")), limit=2500,
          record=[c.track("raiders", "Position"), c.track("raiders", "CurJobDef")])
if r.hit:   # paused on the tick on which the first raider left the moat
    print(r.tick, r.values["raiders.Position"], r.values["raiders.CurJobDef"])
```

The trace then holds every raider's square and job on every tick of the drain, and the game stands on the tick of the
escape for a read or a picture.

## The red check

Python side, against a fake bridge: `test_run_refuses_*` (one for each row),
`test_run_unreadable_value_stops_as_unknown`, `test_run_true_at_start_plays_no_tick`,
`test_run_lost_reply_is_recovered_by_request_id`, `test_run_dead_member_stays_in_group_as_gone`. Planted faults: a run
that counts an unreadable value as false; a run that returns 0 for a pawn that is gone.

Game side, the live proof of the hand (`prove_run_until.py`, UNRUN until `jawa/run_until` is built): the stop tick is
read a second time, by `TicksGame` after the pause, and must equal the trace's tick; the count of trace rows must equal
the closing record's count.

## Limits

When the game has no `jawa/run_until`, the run is played by `jawa/scene_slice`, and the receipt says so: it has no request id, it
asks for a pawn (the receipt names it), it reads the fields of things only, and it stops on an unreadable value only when the whole
condition becomes unknown. A run whose clock stands still for 60 s of wall time is cancelled (`why` is `fault`). It observes at the end of a tick. An event inside a tick needs a tap (an event recorder), which `record` can also name.
It does not act: for an act on tick T, run until T, then `s.act`.

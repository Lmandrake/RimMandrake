# `s.act`: do one act on the paused game; `s.act.tune` writes a live value

**For:** it does one named act between two ticks, reads the effect back, and writes the act into the trace.

## Accepts

One verb for each call. `help verbs` gives each verb's arguments.

| verb | what it does | built in 0.3.0 |
|---|---|---|
| `damage` | hurts a thing (`jawa/damage`); `damage(target, amount, kind="Blunt")` | yes |
| `job` | forces a job on a pawn through the player-order path (`jawa/ordered_job`); `job(pawn, job, target=None, cell=None)` | yes |
| `place` | makes one thing after staging (`jawa/build_batch`); `place(thing, at, stuff=None, rot=None, bind=None)` | yes |
| `order` | gives a pawn an order through the game's own work giver or float menu code | no: `RIMMANDRAKE_BUILD_CAST_ASSERTS_AND_ORDER_THROUGH_GIVER` |
| `explode` | makes an explosion on a cell | no: no converted scene needed it (`jawa/explosion_at` through `s.raw`) |
| `incident` | fires an incident | no: no converted scene needed it |
| `weather` | sets the weather | no: no converted scene needed it |
| `remove` | removes one thing after staging | no: no converted scene needed it |
| `reload` | saves and loads in the middle of the scene, and binds each alias again | no: `RIMMANDRAKE_BUILD_LOAD_CROSSING_ACT_REBINDS_ALIASES` |
| `tune` | **the live write.** Writes one value into the running game: a def field, a static field of a mod, or a mod setting. `s.act.tune(target, value)` | no: `RIMMANDRAKE_BUILD_DEVIATION_RECORD_SETTINGS_FIELD_JOINS_FIRST` |

A verb that is not built refuses `NOT_BUILT` and names its ticket. Until then `s.raw` reaches the tool, and the run is EXPLORED.
Every verb may take `name=` (so that a condition can say "after this act") and, where it makes things, `bind=` (the
alias for what the act spawned). The other arguments of each verb, with their defaults, are the catalogue
`help verbs`; the catalogue is printed from the code, and the selftest compares it with the signatures.
Every act is sent through `jawa/act_batch` with a request id, also one act alone. `with s.act.batch() as b:` sends several acts in
one call, **with no frame between them**; after the block, `b.effects` holds one `Effect` for each act. `reload` cannot be in a
batch. The game must be paused.

## Returns

An `Effect`: `accepted` (the game took the act), `observed` (what the verb reads back, below), the tick, the frame
count. **Accepted is not completed.** An order that was given is not work that was done; the script waits for the
result with `s.run(until=...)`.

| verb | `observed` is |
|---|---|
| `order`, `job` | the pawn's current job after the act, and the giver's own answer (`given=False` with its reason is a fact about the mod, not an error) |
| `damage` | the victim's health before and after |
| `explode` | the cells of the explosion as the game made it |
| `incident`, `place` | the ids of what was spawned |
| `remove` | that the thing is gone |
| `weather` | the weather def now |
| `tune` | the value before and after, the follow-up that was done, and ACTING or UNVERIFIED |
| `reload` | each alias: bound again, or `gone` |

A repeat of a request (the same id, the same arguments), for example after a lost reply, returns the first `Effect`
again with `replayed = True`; the act is not done twice. The game keeps the ids for the whole session, also across
`scene.attach`.

Receipt: `did`: one line for each change, for `tune` also the value before, the value after and the follow-up that made
the game notice it; `hands`: the tool that did it; `could_not_look`: for example "tune: the value was written and read
back, but whether the game acts on it is UNVERIFIED for this field"; `stamps`: `TUNED` after any `tune`.

## State changes

The act itself. Each act writes a start record and an end record in the trace. **`tune` marks the game process as
tuned, from that act until the game restarts.** Every later receipt, run and picture of that process carries the stamp,
in every session, also after the value is put back. A save written in a tuned process carries the mark inside the
file, and a game that loads it is tuned. `scene.judge` gives such a run its outcome with `counts_for_bar = False`, and
the verdict ledger records it as TUNED, never as PASS. At close, each tuned value is written back and read back.

## Refuses

| name | when | repair |
|---|---|---|
| `GAME_RUNNING` | the game is not paused | `s.run` to the tick first |
| `REQUEST_CONFLICT` | a request id that the game has done comes again with other arguments | a bug in the caller: never reuse an id |
| `RELOAD_IN_BATCH` | `reload` inside a batch | do the reload as its own act |
| `UNKNOWN_ALIAS` | an alias is not bound | stage it or place it first |
| `TUNE_NOT_LIVE` | the target's write recipe says LOAD ONLY or NEVER LIVE, or the target is a `const` | use a build |
| `TUNE_NO_RECIPE` | the target has no write recipe, so nobody knows when the game reads it (a mod may have copied it at startup) | add the recipe (`design/specs/2026-11-23-bridge-v2/04_live_tuning.md` §1), or pass `unverified=True`: the write is made and the receipt says UNVERIFIED |
| `TUNE_CANONICAL_SAVE` | a canonical world save is loaded | use a fixture or a fresh map |
| `TUNE_UNKNOWN_TARGET` | the def, type or field does not exist | the message lists near names |

## Example 1 (FlowWorks `sc_fill_front`: water and tar start on one tick in two notches)

```python
with s.act.batch() as b:                       # one call, no frame between the two
    b.place("water_head", fluid="Water", metres=2.0, at=head_a, name="fill")
    b.place("tar_head", fluid="Tar", metres=2.0, at=head_b)          # name= is optional
r = s.run(until=c.ticks_after("fill", 12), limit=60, record=[c.track("notch_a", "depth"), c.track("notch_b", "depth")])
```

## Example 2 (FlowWorks test pilot sitting 2026-11-23: with the melee rule off, a held raider stabbed a warden)

```python
s.act.tune("setting:RimMandrakeFlowWorksSettings.<the melee rule's field>", False)   # the run is TUNED from here
```

That sitting changed the setting through `jawa/mod_settings_field` by hand, with no stamp on the result.

## The red check

Python side, against a fake bridge: `test_act_refuses_*` (one for each row), `test_act_repeat_returns_first_effect`,
`test_tuned_run_never_counts_for_a_bar`, `test_tune_put_back_at_close_and_stamp_stays`,
`test_marked_process_marks_a_new_session`, `test_marked_save_marks_the_game_that_loads_it`. Planted faults: a tuned run
that the ledger records as PASS; a second session in a tuned process with no stamp.

Game side, the live proof of the hand (`prove_act_batch.py`, UNRUN until `jawa/act_batch` is built): the frame count is
read before and after a batch of two acts by a per-frame counter that the batch does not write, and must be equal; a
repeated request leaves the victim's health as after one hit.

## Limits

It cannot act in the middle of a tick. In Design Version 0.1.0 two separate acts on one stop are allowed; the trace
holds the frame count of each. If experiment A scene 3 shows that the frame between them changes a result, a later
version of this page refuses that, and says so in its change line. `tune` proves nothing about the shipped build: only a run on a build that holds
the value, with no stamp, is evidence (`design/specs/2026-11-23-bridge-v2/04_live_tuning.md`).

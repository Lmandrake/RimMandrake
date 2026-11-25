# BOUNDARY: the generic hands of BRIDGE v2.0 (session, run until, read paths, act batch), Design Version 0.1.0

Code: `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchPathCore.cs` (all of it),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchHandsCore.cs` (all of it),
`src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchHands.cs` (all of it). The run that the hands start is on
`../2026-11-23-bridge-v2/boundary.md`. Item: `RIMMANDRAKE_WIDEN_SLICE_INTO_RUN_UNTIL_AND_ACT_BATCH`. Contracts served:
`run.md`, `read.md`, `act.md` (the batch and the request ids) and `attach.md` (the session's state), found by
`../2026-11-23-bridge-v2/contracts/README.md`. Each promise has a test of its name in
`src/RimMandrake/bridgetools/selftest_run_until.py`. Live proofs: `prove_run_until.py`, `prove_act_batch.py` beside it.

A hand names no mod, no scene and no check. The caller gives each condition, path, act and limit as data. A hand gives no
verdict. Each hand is a plain public static method of `JawaBenchHands` (main thread) with a thin tool wrapper.

## THE WIRE (what Python sends and gets)

A refusal is `{"success": false, "refused": "NAME", "message": "...", "repair": "..."}`. Nothing was changed.
The bridge host drops a null member from every reply, so an absent key is null. `state` is always there and says what the
null means: `ok` with no `v` is a null that was read; `gone`, `unbound` and `error` have no `v` at all.

### `jawa/session`

`action` is `open`, `state`, `bind`, `take`, `close` or `abort`. `driver` is any text that the caller chooses; the caller sends the
same text on each call.

| action | does |
|---|---|
| `open` (`driver`, `leaseS`) | opens the one session of this game process. Pauses the game. Reply: `session`, `state` |
| `state` | reads: `session`, `stage` (`none`, `open`, `closing`, `closed`, `aborted`), `driver`, `leaseEnded`, `leaseLeftS`, `paused`, `tick`, `lastRun`, `openAct`, `bound`, `rows`, `dropped`, `recordDir`, `writerSession`. No driver is needed |
| `bind` (`driver`, `bindings`) | `bindings` is JSON: `{"pawn_1": "Human12"}` binds one thing; `{"raiders": ["Human3", "Human4"]}` freezes a group; `null` in place of an id declares an alias that is not bound. The thing must exist, or the call is refused (`UNKNOWN_THING`) |
| `take` (`driver`, `from`) | gives the open session of a dead driver to `driver`: the live run is cancelled, the game paused, a `session_taken` row written. `from` is the dead driver's text (the caller looked: that process is gone); it is not needed after the lease has ended. A taken session is read and ended, never played (`TAKEN_OVER`) |
| `close`, `abort` (`driver`) | writes the closing record after the writer has drained. A live run is cancelled first. After the lease has ended, `abort` takes any driver |

Refusals: `SESSION_OPEN`, `NO_SESSION`, `NOT_THE_DRIVER`, `DRIVER_ALIVE`, `TAKEN_OVER`, `NO_GAME`, `BAD_ARGS`, `UNKNOWN_THING`.

### `jawa/run_until`

`action` is `start`, `status` or `cancel`. `start` takes `driver`, `request` (the id that the caller made before it sent the
call), `until` (a JSON condition tree), `limit`, `speed`, `record`, `acts`, `tickBudgetMs` (0 = no bound on what reading one tick may take).

- `until`: the nodes and probes of `jawa/cond_eval`, two more probes and two group nodes.
  `{"p": "value", "of": T, "path": P}` reads a value path. `{"p": "value.state", "of": T, "path": P}` gives its state as text
  (`ok`, `null`, `gone`, `unbound`, `error`) and can always be read, so "a dead member counts" is
  `{"any": [{"cmp": [{"p": "value.state", ...}, "==", "gone"]}, ...]}`.
  `{"any_of": {"group": "raiders", "node": N}}` and `all_of` repeat N for each member; in N, `"of": "$"` is the member.
- `record`: a JSON list of `{"of": T, "path": P}` (a group gives one track for each member, `raiders[0].P`) or
  `{"name": "...", "probe": {...}}`. Each value that `until` reads is a track without being named, `game.tick` apart.
- `acts`: a JSON list of `{"id": "...", "tool": "jawa/...", "args": {...}, "at": 0}`. `at` 0: done after the first sample, in
  the same main-thread hop that starts the clock. No paused frame sees it. `at` N: done on tick N after the start, after that tick's sample.
- Reply: `request`, `run`, `stage` (`running`, `settling`, `closed`), `why` (`hit`, `limit`, `unknown`, `cancelled`, `fault`;
  null while it runs), `state`, `tickFrom`, `tick`, `values` (name -> `state`, `v`, `detail`, `reads`: the samples taken), `couldNotLook`, `unknownValue`,
  `faults`, `acts`, `rows`, `dropped`, `drained`, `replayed`, `lockReads`, `breaches`, `costliest`.

Refusals: those of the session, and `NO_LIMIT`, `GAME_RUNNING`, `RUN_ACTIVE`, `REQUEST_CONFLICT`, `NO_REQUEST`, `BAD_PATH`,
`PATH_CALLS_METHOD`, `UNKNOWN_GROUP`, `EMPTY_GROUP`, `OPTIONAL_COUNTS_UNKNOWN_FALSE`, `BAD_CONDITION`, `CANNOT_RUN`, `UNKNOWN_REQUEST`.

### `jawa/read_paths`

`reads` is a JSON list of `{"of": T, "path": P}`. With `rect` ("x,z,w,h") and `path`: one value for each thing in the
rectangle, or for each cell when the path holds `[cell]` (`of` is then `map` or a map component path). Reply: `tick`, `paused`, `values` (each: `of`, `path`, `state`, `v`, `detail`).
It needs no session; an alias then reads `unbound`. Refusals: `BAD_PATH`, `PATH_CALLS_METHOD`, `BAD_ARGS`, `NO_GAME`.

### `jawa/act_batch`

`driver`, `acts` (JSON list of `{"id", "tool", "args"}`). Reply: `acts`, one for each act in order: `id`, `tool`, `state`
(`done`, `refused`: the tool answered success false, `failed`: the tool threw, `not_one_hop`: the tool did not end inside the
hop, `not_tried`: an act before it was not done), `reply`, `error`, `tick`, `frame`, `replayed`. Refusals (the whole batch, nothing done): those of
the session, and `GAME_RUNNING`, `RUN_ACTIVE`, `REQUEST_CONFLICT`, `NO_REQUEST`, `UNKNOWN_TOOL`, `NOT_ONE_HOP`, `NESTED_HAND`, `BAD_ARGS`.

## THE PATH GRAMMAR

Target `of`: an alias; a group member `raiders[2]`; `thing:<id>`; `def:<DefType>/<defName>`; `static:<full type name>`; `map`
(the map of the session, or the current map); `game`; `world`.
Path: steps joined by a point. A step is a field (public or private), a property, `comp<Class>` (a comp, map component or game component
whose class has that short or full name), or an index `[n]`, `[x,z]` (a map-sized array). A property is read only when its
getter returns a field and does nothing else (the field is read, no method is called), or when it is on the reviewed list
in `JawaBenchPathCore.Reviewed`. A step that calls is `PATH_CALLS_METHOD`.
A value is a number, a bool, a text, an enum name, a defName, a thing id, a cell `x,z`, null, or a list of those. A list is a
value of `jawa/read_paths` only; in a track or a condition it reads `error`.

## THE TRACE

The records of `scene_trace_v1`, with one more field `sess`, and with `n` counted over the whole session. More records:
`session_open`, `bind`, `act_start` and `act_end` (`id`, `tool`, `state`, `frame`), `lease_ended`, `session_close` (`end`,
`rows`, `dropped`, `drained`). A session with no `session_close` is incomplete.

## LIMITS

- **60 s for the writer to drain, then the closing record says `drained` false.** Danger: a full or dead disk keeps a session
  open for ever, and no later session can open.
- **The lease (600 s when the caller names none).** Danger: a driver that died leaves a game playing with nobody to stop it
  (FlowWorks visit 9, `sc_pit_trap_raid`: "an unfinished capture"). Its end pauses the game and closes nothing.

## DOES NOT SURVIVE (not promised)

- **a-load-inside-a-session.** Each bound thing reads `gone`. The load barrier is another item.
- **a-changing-tool-from-a-caller-outside-the-session, between runs.** The run lock holds while a run is live
  (`../2026-11-23-bridge-v2-life-cycle/boundary.md`). Between two runs of a session, another caller can change the game.
- **a-tool-of-the-bridge-host.** A batch calls companion tools only. `rimworld/` tools go through the host's own queue.
- **a-side-effect-inside-a-reviewed-property.** The list is read by a person; a Harmony patch on a listed getter runs.
- **a-type-that-was-never-used.** The first read of a static field runs the type's own initializer, as any first use does.
- **zero-allocation.** A value-typed leaf makes one box for each read.

## PROMISES (each one is owed a test of the same name)

- **the-slice-promises-hold-in-a-session.** The eleven promises of the slice hold for a run that is part of a session and has no act of its own.
- **one-session-one-trace-no-gap.** Two runs of one session write one trace: `n` rises by one over both.
- **true-at-start-plays-no-tick.** A condition that is true at the start ends as `hit`; the clock is not started.
- **hit-wins-over-limit.** A hit and the limit on one tick end as `hit`.
- **an-unreadable-value-ends-as-unknown-and-is-named.** The run stops on that tick; `unknownValue` names the value and its state.
- **a-group-is-frozen.** A dead member reads `gone` and stays; a later spawn is not in the group.
- **private-fields-and-statics-are-read.** A track on a private field and on a static field reads the value.
- **a-wrong-field-is-an-error-with-the-fields.** The state is `error` and `detail` lists the fields that the type has.
- **an-unreviewed-method-is-refused-by-name.** Nothing is called.
- **a-thousand-reads-change-nothing.** The state digest is equal before and after.
- **only-the-driver-drives-an-open-session.** Another caller is refused by the session hands. While the session is open
  or closing, `jawa/scene_slice` refuses `start` and `cancel` and allows `status`. The driver can cancel a session run
  through `jawa/run_until`. The offline check covers the slice guard and the driver's cancel.
- **a-taken-session-is-read-and-ended-never-played.** A live lease is taken only with the dead driver's own text.
- **a-session-past-its-lease-stays-open-and-paused.** It is not closed by itself, it can be read, and the game is paused.
- **no-session-no-run.** A run or a batch with no open session is refused by name.
- **the-slice-tool-still-passes.** `jawa/scene_slice` passes its own selftest.
- **no-frame-inside-a-batch.** A batch is one hop: the frame count of its first and last record is equal.
- **a-repeated-id-returns-the-first-reply.** The act is not done twice.
- **a-changed-repeat-is-refused.** The same id with other arguments does nothing.
- **a-thrown-act-keeps-the-acts-before-it.** The first act is `done`, the second `failed`, the third `not_tried`.
- **an-act-at-zero-shares-the-hop-that-starts-the-clock.** The first sample is before the act, and no frame is between the act and the start.
- **an-act-on-a-tick-is-any-tool-call.** It is done on its tick with its own records and its request id.

## LIVE READINGS (tier `flowworks`, SteveDesktop, quicktest map, 2026-11-23)

| proof | reading | testq job |
|---|---|---|
| `prove_run_until.py` | 13 of 13 rows PASS | `J20261124T062048Z-97f683` |
| `prove_act_batch.py` | 8 of 8 rows PASS; 436 companion tools, 8 cannot be one hop, 5 can with their wait at 0 | `J20261124T061237Z-8f43fd` |
| `exp_a_state_after_act.py --scene pocket --arms P,G,T --trials 3` | P held at +10 in 3 of 3; G and T in 0 of 3 and 0 of 3; all held at +100 | `J20261124T061237Z-8f43fd` |

Not run in a game: the full mod list; a game that is replaced under a session; a full disk; a run that a game window pauses by force.

Later lists beside this page: `polish.md`.

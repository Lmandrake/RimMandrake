# BOUNDARY: the scene library, Design Version 0.3.0

Code: `src/RimMandrake/Utils/scene.py`, `src/RimMandrake/Utils/scene_core.py`, `src/RimMandrake/Utils/scene_cond.py`,
`src/RimMandrake/Utils/scene_hands.py`, `src/RimMandrake/Utils/scene_world.py` (all of each). The contract of each name is
its page in `src/RimMandrake/Utils/scene_contracts/`; this page holds what the names share. Item:
`RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY`; design `../2026-11-23-bridge-v2/11_design.md`. Each promise
has a test of its name in `src/RimMandrake/Utils/selftest_scene_library.py`, against the fake game of
`src/RimMandrake/Utils/scene_fake.py`, which replays replies recorded on ArchSmall on 2026-11-23
(`src/RimMandrake/Utils/scene_recorded.json`). The plants are `src/RimMandrake/Utils/scene_library_mutants.py`.

## WHAT A NAME REACHES

- **The game**, by name (`game_names.py`) and never by the shell's environment: the port and the token of that game.
- **The game's disk health.** `scene.open` and `s.run` check the named process and its heartbeat before reaching the
  bridge. A broken or gone game is refused. A blind reading adds one `could_not_look` line to the receipt and the call
  continues through its normal checks. The [watcher boundary](../2026-11-23-bridge-v2-watcher/boundary.md) names its test.
- **The driver lock** of that game (`game_lock.py`). A take that this process inherited (`game_lock.py run`), or that the
  window of this clone holds, is kept. His switch can still refuse a new scene. A Windows python cannot claim, so a WSL
  child (`game_lock.py run <g> -- cat`) holds the lock. Its input closes when the script's process ends, and the lock is
  free within about a second. The take of another scene is never inherited.
- **The process mark and the session record.** One text in the environment block of the game's own process
  (`System.Environment`, through `jawa/static_call`), with the game's process id in it. It dies with the process. A
  process that the game starts inherits the text, and the id in it then names another process, so it is not read as a mark.
- **The deviation record.** When the companion exposes it, receipts carry its live entries and marks. An explicit
  `needs["overlay"]` declaration arms settings through the session hand. See the
  [deviation boundary and offline checks](../2026-11-23-deviation-record/boundary.md).
- **The run:** `jawa/run_until` in a `jawa/session` when the game has both tools, else `jawa/scene_slice`, and the
  receipt says which. `jawa/scene_slice` has no request id and needs a pawn: the library knows its run as the first run
  that began after the call, and names the pawn that it used.
- **The run folder** (`<agent storage>/scratch/scene_runs/`): `run.json`, `receipts.jsonl`, `trace_<request>.jsonl`.

## LIMITS

- **A run whose clock stands still for 60 s of wall time is cancelled** (`why` is `fault`). Danger: a window that pauses the
  game from outside leaves a script waiting for ever (measured 2026-10-09: "paused externally", `run()` hung).
- **The status of a run is asked for 60 s over lost replies.** Danger: a game that died never answers, and the script waits
  for ever.
- **The wait for a load to settle: 600 s.** Danger: a game stuck in MapInitializing (measured live 2026-10-26, load r8).
- **The wait for the run's closing record is 20 s.** A full disk can prevent the record from being written. The fault
  is then `TRACE_INCOMPLETE`.
- **Session close uses the companion's 60 s writer drain limit.** A blocked writer can keep the session in `closing`.
  If the stage is still `closing` at the end of the wait, close reports `CLOSE_INCOMPLETE`.
- **A bridge call: 600 s**, the hang guard of the older layers. Danger: a game on a stalled frame.

## DOES NOT SURVIVE (not promised)

- **a-save-that-carries-the-mark.** A save made in a marked process does not carry the mark until the tuning tickets build
  it. After a fixture is loaded, `could_not_look` says that its mark was not read.
- **a-raw-call-made-outside-the-library.** The bridge client and the older layers leave no mark.
- **a-hand-that-wants-to-cheat.** A raw `jawa/static_call` can write the text of the mark.
- **a-campaign-game.** `jawa/static_call` is refused there, so the mark cannot be read. The name that needs it says so.
- **a-driver-that-died.** Its session stays open. `scene.attach` takes it over, to read it and end it; `scene.py end-session <game>` ends it.

## PROMISES (each one is owed a test of the same name)

- **a-refusal-changes-nothing.** After each refusal of `scene.open` the lock, the calm, the session record and the loaded
  map are as before, and the phase report names the phase and what was put back.
- **owner-hold-refuses-a-new-scene.** `OWNER_HOLD` is checked before inheriting a take. The existing take stays in place
  and the library refuses before connecting (`test_open_refuses_owner_hold_under_an_inherited_take`).
- **build-lines-come-from-the-game.** The build lines of a receipt are the game's own reply; the repo's hash is not in them.
- **could-not-look-is-not-a-refusal-and-not-clean.** A lock, a tool list, a handshake or a mark that could not be read is a
  Fault or a `could_not_look` line, never "free", "no mods" or "no stamp".
- **unreadable-is-never-false.** An unreadable value of the condition ends the run as `unknown`, also when the hand says `hit`
  or `limit`. `r.hit` then raises. A bare thing id and an explicit `thing:` target both match the hand's track
  (`test_run_unreadable_thing_target_stops_as_unknown`).
- **a-lost-reply-is-found-by-its-id.** The recovered run is returned without another start. The exact `action=status`
  reads of both run tools pass the bridge client's pending guard. Finding the run reconciles its original start marker
  (`test_run_lost_reply_passes_the_pending_guard`, real client with stub transport).
- **true-at-start-plays-no-tick.** A condition already true at the paused start hits on that tick. Both hands send the
  specified condition on the wire (`test_run_true_at_start_plays_no_tick`).
- **a-trace-that-is-not-whole-is-a-fault.** No closing record, a gap, a dropped row, a writer that did not drain.
- **a-game-that-ran-on-is-a-fault.** Ticks after the stop, or a game that is not paused after it, read a second time.
- **the-game-holds-the-mark.** A changing raw call marks the process before the call; a new session in that process carries
  the stamp; another process does not.
- **raw-arguments-are-recorded-before-the-call.** A raw marker carries the tool name and full argument JSON. A marker
  failure appears in `could_not_look` (`test_raw_batch_arguments_are_in_the_trace`).
- **an-undeclared-tool-is-changing.** Only a description that begins with READ ONLY is read-only; `jawa/static_call` never.
- **accept-needs-one-identity.** It refuses a tree that is not clean, a script outside the repo and a script that imports an
  older layer, in the script or in a module of the repo that it imports. A tree that could not be read is its own answer.
- **accept-ignores-the-mod-ledger.** The clean-tree test of `accept` leaves out each mod's `design/concepts/<Mod>/ledger/`
  folder, which a holder's lease program rewrites while the run lasts; code, scenes and the test table stay counted
  (`test_accept_ignores_the_mod_ledger_a_lease_renews`).
- **accept-game-names-the-free-game.** `scene.py accept <script> --game <name>` runs the script on the named game, over the
  game its source names; an unknown name is refused before the script runs; without `--game` the script's own game stands, and
  the name never comes from the shell's environment (`test_accept_game_names_the_free_game_over_the_script_default`).
- **explore-is-stamped.** Each receipt of a run from `explore` carries EXPLORED.
- **close-puts-back.** Close puts back the session record, the calm and the lock after a normal end and after an error.
  It holds the take while it waits for the companion session to report `closed` or `aborted`. If the wait fails, close
  names the unfinished session and continues cleanup (`test_close_waits_for_the_session_writer`).
- **a-name-not-built-says-so.** The six names still owed refuse `NOT_BUILT` with the ticket that builds them.
- **help-equals-the-code.** Help prints the ten names; each built page takes the arguments that the function takes.

**LIVE PROOF** (2026-11-23, ArchSmall, companion `6ac9a7490885`, so every run was played by `jawa/scene_slice`):
- `scene.py accept src/RimMandrake/bridgetools/scene_smoke_run.py` at commit 67e5c46ec0f4: 11 of 11 rows PASS, exit 0.
- `src/RimMandrake/bridgetools/prove_scene_mark.py`: first run 12 PASS and 1 FAIL (the lock of a killed driver was read between two
  states); after the repair (9610cf8230f6) 13 PASS and 1 UNMEASURED (the process was already marked; that row passed in the first run).
- `prove_scene_mark.py --unmarked` after a restart: 1 of 1 PASS.
- UNRUN: a run played by `jawa/run_until` (the smoke run on a companion that has
  it); `WRONG_BUILD`, `OWNER_HOLD`, a lost reply, and a game that ran on, each from a real game (offline only).

Later lists beside this page: `polish.md`.

## THE FIVE NAMES OF 0.3.0 (`scene_names.py`)

Code: `src/RimMandrake/Utils/scene_names.py` (all of it): `scene.contract`, `s.stage`, `s.act` (the verbs `damage`, `job`,
`place`, and `s.act.batch()`), `s.read`, `s.read_many`, `s.shot`. Item: `RIMMANDRAKE_CONVERT_THREE_SCENES_SHOW_IF_TEN_NAMES_HELP`.
Each promise below has a check of its name in `src/RimMandrake/Utils/selftest_scene_conversion.py`, against the same fake game;
the replies of the new hands there are made from their wire pages, not recorded. `--mutants` plants four wrong codes.

It accepts what each page's Accepts table names. It does not survive (not promised): a staging reply with more than 50 rows
(each call is cut to 50 rows, `ROWS_LISTED`); a def name checked where the frozen dump is not readable (a helper clone: the
receipt says so); a condition tree counted at exactly 64 nodes (the count may be one higher than the judge's); an act that a
mod does only through its own UI path (it goes through `s.raw`, and the run is EXPLORED).

- **a-contract-touches-no-game.** `scene.contract` makes no bridge call; a bad contract in a script refuses before
  `scene.open` loads a map (`t_contract_makes_no_bridge_call_and_is_checked_before_the_load`).
- **no-success-without-exposure.** A success with no exposure is refused `NO_EXPOSURE`; the judge never gives SUCCESS to a
  run whose exposure was not seen (`t_contract_refuses_success_with_no_exposure`, `t_storeroom_plays_to_its_end`).
- **a-kind-b-writes-its-budget.** Kind B with no budget is refused; an (X, Y) budget allows a miss
  (`t_contract_refuses_kind_b_with_no_budget`).
- **a-condition-names-only-what-is-recorded.** A tap that is not armed is refused `UNRECORDED_VALUE`, a tree over 64 nodes
  `CONDITION_TOO_LARGE`, a missing end `NO_END` (`t_contract_refuses_a_tap_that_is_not_built`).
- **a-stage-reply-is-the-read-back.** What `s.stage` returns is read from the staging tool's `readBack` block; a replaced
  pawn kind is `STAGING_FAULT`; a reply with no block is `COULD_NOT_LOOK`, never made
  (`t_stage_reply_is_built_from_the_read_back_and_a_replaced_kind_is_a_staging_fault`).
- **a-gone-thing-reads-gone.** `s.read` of a thing that is gone has state `gone`, and its `.v` raises
  (`t_read_gives_gone_for_a_gone_thing_never_zero`).
- **every-act-has-a-request-id.** Each act is sent through `jawa/act_batch`; a batch is one call
  (`t_moat_plays_to_its_end`).
- **the-last-run-is-judged.** Each `s.run` of a session with a contract records the contract's values (of bound aliases) and
  writes `contract.json` for its own request (`t_moat_plays_to_its_end`).
- **a-marked-run-counts-for-no-bar.** A run after a changing `s.raw`, or a planted run, counts for no bar; a clean accepted
  run counts (`t_a_run_after_a_changing_raw_call_does_not_count_for_a_bar`).
- **a-trace-with-no-close-is-could-not-look.** (`t_a_trace_with_no_closing_record_is_could_not_look`)
- **load-answers-the-known-load-windows-only.** At the end of the settle after a load, each window that
  `quiet_site.MODAL_HANDLERS` names gets its one approved answer (VEF's `Dialog_NewFactionSpawning`, which opens a few frames
  after the load returns: "Do nothing", the save's world unchanged), and the settle phase says what it answered. Any other window stays open, for the calm to refuse by name
  (`test_load_answers_the_known_load_windows_only`).


## STATIONS (`s.stage(station=dict(...))`)

Code: the station functions of `src/RimMandrake/Utils/scene_names.py` (`_stage_of`, `_take_station`, `put_back_stations`), the
stage files of `scene_world.py` (`stage_state`, `stage_save`, `stage_loaded`, `stage_made`), and the allocator
`src/RimMandrake/Utils/scene_stations.py` (its own promises: `design/specs/2026-11-23-bridge-v2/boundary.md` §THE STATION
ALLOCATOR). Item: `RIMMANDRAKE_BUILD_STAGE_MAP_CAST_ONLY_NO_BYSTANDERS`. Each promise has a check of its name in
`src/RimMandrake/Utils/selftest_scene_stage_station.py`, on the fake game.

It accepts a request `dict(size=(w, h), margin=, edge=, incident=, home=, weather=)` on a map that a made stage save put on
the game (`stage_map.py make`), or a rect `(x, z, w, h)` on any map, as before. The stage files live under the agent storage
root, `scratch/scene_stages/`: `made/<save>.json` for each stage save, `live/<game key>.json` for the map that a game holds
now. It does not survive (not promised): a map loaded on the game by a tool that is not `scene.open` while the live file stays
(the size check catches a map of another size only); two sessions on one game at once (the driver lock refuses the second).

- **a-request-draws-a-clean-station.** The station comes from the allocator, is cleaned before anything is staged on it, and
  every position is relative to its corner. At close each station that the session took is cleaned and released
  (`a_station_request_draws_a_clean_station_and_positions_are_relative`).
- **a-cleaned-station-has-no-roof.** After the clean and before anything is staged, the roof over the station comes off
  (`jawa/set_roof_batch`, every cell read back). The clean destroys the rock under a mountain roof, and that roof would
  collapse on the first tick and crush the stage. A roof that stays is `NO_CLEAN_STATION`
  (`a_station_loses_its_roof_before_anything_is_staged`).
- **a-dirty-station-is-retired.** A station whose clean leaves a thing that blocks is retired with the thing named, and the
  allocator gives another (`a_station_whose_clean_leaves_a_thing_is_retired_and_another_is_given`).
- **a-refused-request-changes-nothing.** A request that the stage cannot serve (`POCKET_CANNOT_SERVE`, `NO_ROOM`), or a plan
  whose cells are outside the station, is refused before any station is taken or cleaned
  (`a_pocket_stage_refuses_a_raid_scene_before_any_change`).
- **a-colony-station-says-shared-map.** The receipt of a station on a `colony` stage has a `could_not_look` line that starts
  "shared map" (`a_colony_station_says_shared_map_on_its_receipt`).
- **no-allocator-on-a-map-that-is-not-a-stage.** A request on a map that no stage save put there is `NO_STAGE` with the make
  command; a live file for a map of another size is `STAGE_STALE` (`a_map_that_is_not_a_made_stage_is_refused_no_stage`).

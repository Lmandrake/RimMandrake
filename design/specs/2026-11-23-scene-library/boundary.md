# BOUNDARY: the scene library, its skeleton, Design Version 0.1.0

Code: `src/RimMandrake/Utils/scene.py`, `src/RimMandrake/Utils/scene_core.py`, `src/RimMandrake/Utils/scene_cond.py`,
`src/RimMandrake/Utils/scene_hands.py`, `src/RimMandrake/Utils/scene_world.py` (all of each). The contract of each name is
its page in `src/RimMandrake/Utils/scene_contracts/`; this page holds what the names share. Item:
`RIMMANDRAKE_BUILD_SCENE_LIBRARY_TEN_NAMES_FIVE_LAYERS_TODAY`; design `../2026-11-23-bridge-v2/11_design.md`. Each promise
has a test of its name in `src/RimMandrake/Utils/selftest_scene_library.py`, against the fake game of
`src/RimMandrake/Utils/scene_fake.py`, which replays replies recorded on ArchSmall on 2026-11-23
(`src/RimMandrake/Utils/scene_recorded.json`). The plants are `src/RimMandrake/Utils/scene_library_mutants.py`.

## WHAT A NAME REACHES

- **The game**, by name (`game_names.py`) and never by the shell's environment: the port and the token of that game.
- **The driver lock** of that game (`game_lock.py`). A take that this process inherited (`game_lock.py run`), or that the
  window of this clone holds, is kept. A Windows python cannot claim, so a WSL child (`game_lock.py run <g> -- cat`) holds the
  lock; its input closes when the script's process ends, and the lock is free within about a second. The take of another scene is
  never inherited.
- **The process mark and the session record.** One text in the environment block of the game's own process
  (`System.Environment`, through `jawa/static_call`), with the game's process id in it. It dies with the process. A
  process that the game starts inherits the text, and the id in it then names another process, so it is not read as a mark.
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
- **The wait for the closing record: 20 s.** Danger: a full disk; the fault is then `TRACE_INCOMPLETE`.
- **A bridge call: 600 s**, the hang guard of the older layers. Danger: a game on a stalled frame.

## DOES NOT SURVIVE (not promised)

- **a-save-that-carries-the-mark.** A save made in a marked process does not carry the mark until the tuning tickets build
  it. After a fixture is loaded, `could_not_look` says that its mark was not read.
- **a-raw-call-made-outside-the-library.** The bridge client and the older layers leave no mark.
- **a-hand-that-wants-to-cheat.** A raw `jawa/static_call` can write the text of the mark.
- **a-campaign-game.** `jawa/static_call` is refused there, so the mark cannot be read. The name that needs it says so.
- **a-driver-that-died.** Its session stays open. `scene.attach` is not built; `scene.py end-session <game>` ends it.

## PROMISES (each one is owed a test of the same name)

- **a-refusal-changes-nothing.** After each refusal of `scene.open` the lock, the calm, the session record and the loaded
  map are as before, and the phase report names the phase and what was put back.
- **build-lines-come-from-the-game.** The build lines of a receipt are the game's own reply; the repo's hash is not in them.
- **could-not-look-is-not-a-refusal-and-not-clean.** A lock, a tool list, a handshake or a mark that could not be read is a
  Fault or a `could_not_look` line, never "free", "no mods" or "no stamp".
- **unreadable-is-never-false.** An unreadable value of the condition ends the run as `unknown`, also when the hand says `hit`
  or `limit`; `r.hit` then raises.
- **a-lost-reply-is-found-by-its-id.** The run is found and returned; it is not started twice.
- **a-trace-that-is-not-whole-is-a-fault.** No closing record, a gap, a dropped row, a writer that did not drain.
- **a-game-that-ran-on-is-a-fault.** Ticks after the stop, or a game that is not paused after it, read a second time.
- **the-game-holds-the-mark.** A changing raw call marks the process before the call; a new session in that process carries
  the stamp; another process does not.
- **an-undeclared-tool-is-changing.** Only a description that begins with READ ONLY is read-only; `jawa/static_call` never.
- **accept-needs-one-identity.** It refuses a tree that is not clean, a script outside the repo and a script that imports an
  older layer, in the script or in a module of the repo that it imports. A tree that could not be read is its own answer.
- **explore-is-stamped.** Each receipt of a run from `explore` carries EXPLORED.
- **close-puts-back.** The session record, the calm and the lock are put back after a normal end and after an error; what
  could not be put back is named.
- **a-name-not-built-says-so.** The other seven names refuse `NOT_BUILT` with the ticket that builds them.
- **help-equals-the-code.** Help prints the ten names; each built page takes the arguments that the function takes.

**LIVE PROOF** (2026-11-23, ArchSmall, companion `6ac9a7490885`, so every run was played by `jawa/scene_slice`):
- `scene.py accept src/RimMandrake/bridgetools/scene_smoke_run.py` at commit 67e5c46ec0f4: 11 of 11 rows PASS, exit 0.
- `src/RimMandrake/bridgetools/prove_scene_mark.py`: first run 12 PASS and 1 FAIL (the lock of a killed driver was read between two
  states); after the repair (9610cf8230f6) 13 PASS and 1 UNMEASURED (the process was already marked; that row passed in the first run).
- `prove_scene_mark.py --unmarked` after a restart: 1 of 1 PASS.
- UNRUN: a run played by `jawa/run_until` (the smoke run on a companion that has
  it); `WRONG_BUILD`, `OWNER_HOLD`, a lost reply, and a game that ran on, each from a real game (offline only).

Later lists beside this page: `polish.md`.

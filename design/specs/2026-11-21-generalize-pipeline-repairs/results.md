# Results: the general repairs made for the review beside this file

Item `RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES`. Principle numbers are those of `review.md`.

State at 2026-11-21 2:20 AM PST.

### Principle 4, a test makes no live effect: fixed, commit `fa04fa200c`

- The change: `src/RimMandrake/rimflow/test_process.py` is the one definition of a test process. A descendant of a
  `selftest*.py` program is now a test process, with or without a mark in its environment. `control.launch_unit` and
  `model.append` ask it. Page: two promises on `design/specs/2026-11-18-pipeline-control-surface/boundary.md`.
- The test replays tonight's leak (a child of a selftest, clean environment, a pipeline-family launch). Red with the
  guards removed: 3 FAIL. Green with them: 0 FAIL. Must-stay-green cases pass both ways: a probe-family unit, a launch
  that passes `runner=`, a test that replaced `subprocess.run`, a ledger of the test's own `[measured]`.
- Behaviour kept: 338 related selftests were run with the guards. 336 ran; I stopped the last long one. 27 failed.
  All 27 give the same exit code on a copy of the base commit `[measured]`. `./publish` ran 108 pipeline checks green;
  one (`selftest_maturation_autonomy.py`) ran past 180 s under machine load and reads UNMEASURED at the door; alone it
  passes in 210 s `[measured]`.
- The ledger event files were byte-identical before and after the 336 tests `[measured: sha256 of each shard]`.
- Found by the guard: `selftest_bridge_lock_owner_holes.py` appended bridge-release events to the real ledger of its
  checkout on every run. It set `RIMFLOW_LEDGER` and never bound it. Repaired with one line `[measured]`.
- Counts: definitions of "a test process" 3 -> 1. Machinery lines +92, -14 (the new module is 63 of them). Test lines
  +130, -11. By the measure of this item (lines removed), this fix is weak: it closes a class, and it removes little.
- Not deleted, with the reason: the four older guards keyed on `RM_DISPATCHER_STATE` (`dispatcher.py`,
  `red_dispatch.py`, `incident.py`, `detached_helper.py`). A real process on another machine can hold that variable
  at a non-default folder, and the new guards must never stop real work. The isolation code inside each selftest also
  stays: removing it is safe one test at a time only.
- UNRUN: no live launch by the tick was watched after this change. The tick is not a test process by any of the three
  clauses `[guess ~95%]`: its command is `maturation_dispatch.py tick`, and my own detached run wrote ledger notes
  through the changed `model.append` `[measured]`.

### Principle 8, a named target: fixed for the game name, this commit

- The change: `.claude/settings.json` sets `WSLENV` for every agent shell to the list in `game_instance._WSLENV`. A
  bare `RM_GAME_INSTANCE=b` now reaches `python.exe`. The bridge client then takes game b's own port.
- Measured on `python.exe`, with no call to any game: with no `WSLENV` the name is `None` on the Windows side; with
  the list, `resolve_endpoint()` gives port 5175 and game b's token; with no game named, nothing changes.
- The copy of the list in `settings.json` is checked by a program (`selftest_game_instance.py`, `name_crosses`): red
  on the base, green now `[measured]`.
- Deleted: the two-line rule in the root `CLAUDE.md` and the same sentence in `skills/rimbridge/SKILL.md`.
- UNRUN: a new agent session was not started to read `WSLENV` from `settings.json`. The setting takes effect in
  sessions that start after this commit. A detached unit for game b already carries the same list (`08b3ba8881`).

### Principle 9, a rule that a tool can do: started

- Root `CLAUDE.md`: 736 -> 727 lines `[measured]`. Deleted or merged: the bare-game-name rule (2 lines), three lines
  under "Queue items are NAMED" that restate what `rimflow` prints, and the section "A limit from before the Maturation
  Pipeline is suspect" (now one bullet under "No limit without the danger it guards").
- During this run the two live runs added rule text: `standing_rulings.md` 1,734 -> 1,831 lines `[measured]`.
- Exact next step, after the two live runs end: replace the nine root sections of principles 1, 3 and 6 (about 109
  lines) with three short sections. Do it in one commit, and check each deleted line with the test of principle 9.

### Principle 2, one home for a fact: not fixed; exact next step

- Evidence gathered: exact repeats across the 21 role files, the root `CLAUDE.md` and `CHARTER.md` are few: 52 long
  lines stand in two or more files (125 copies) `[measured]`. The repeated rules are paraphrases, so a text compare
  does not find them.
- Next step 1 (identity): add `game` to the control store's run record. Then list every reader that takes a mod, item
  or stage from a unit name, an item title or a note (`git grep -n "rm-detached-\|title" -- src/RimMandrake/rimflow`
  is the start), and point each at the record. The files are `maturation_dispatch.py`, `maturation_now.py` and
  `maturation_hands.py`; the first is held by a live run tonight.
- Next step 2 (copies): one publish check that makes each `GENERATED from` copy again and compares. First users:
  `mod_owner_hold.json` (mirror of the control store) and the `WSLENV` list above.

### Principle 7, a limit names its danger: not fixed; the count is made

- Pipeline code (1,174 non-test files of `rimflow`, `Utils` and `.claude/hooks`) holds 766 inline `timeout=<number>`
  sites and 567 named numeric limits. 5 of them name a danger on the line or the line above. 10 boundary pages have a
  LIMITS section `[measured by pattern]`.
- Two rules pull against each other: the call-deadline lint asks for a timeout on every call, and the rule asks each
  limit to name its danger. So deleting unnamed limits one by one is wrong.
- Exact next step: one deadline helper (`Utils/load_policy.py` is "the ONE deadline policy" for the bridge client)
  that names the one danger of a call deadline (a hung child holds the run) once. Callers pass no number. Then a
  number in a call is either gone or carries its own danger. This removes most of the 766 numbers.

### Principle 5, could not look: no change needed

- Already in the machinery (`probe_result`, the lint at `./publish`).

### Before and after

| measure | 2026-11-20 | start of this run | end of this run |
|---|---|---|---|
| root `CLAUDE.md` lines | 638 | 736 | 727 |
| `standing_rulings.md` lines | 1,553 | 1,734 | 1,831 (the two live runs) |
| definitions of a test process | 3 | 3 | 1 |
| doors to a live effect that refuse a test | 2 (control store, Conductor log) | 2 | 4 (also launch, ledger) |

By the owner's measure (fewer and more general rules than on 2026-11-20), this run has not reached the goal: the root
`CLAUDE.md` is still 89 lines longer than on 2026-11-20. The large deletions depend on the two live runs ending.

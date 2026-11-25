# Results: the general repairs made for the review beside this file

Item `RIMMANDRAKE_GENERALIZE_PIPELINE_REPAIRS_INTO_FEW_PRINCIPLES`. Principle numbers are those of `review.md`.

State at 2026-11-21 2:20 AM PST, carried on 2026-11-22 3:15 AM PST (section "The second run" at the end).

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

### Polish (no ticket)

- `selftest_tick_names.py` makes its temp folder inside the repo root (`.rimflow_selftest_tick_names/`) and leaves it when the run is killed. Seen once in this run's sweep.
- Commit `fa04fa200c` carries its body paragraph as its subject (`./publish` took the last `-m`). The intended subject: a test makes no live effect.

## The second run, 2026-11-22

The two runs that held the files had ended. Each step below: page first, a test red on the base, the fix, the test
green, planted faults red.

### Principle 9, the merge of the root sections of principles 1, 3 and 6: already done by another item

- `RIMMANDRAKE_MERGE_TWELVE_REFUSAL_RULE_SECTIONS_THAT_WAITED` (`ac9cca02b4`, 2026-11-21) made the nine sections into
  three: "Stops that the work did not cause", "A fault of form is repaired where it is found", "After a change, only
  the checks that the change touches run again". It cut 15 root lines and found that the cases do not repeat one
  another (`design/specs/2026-11-21-crystallize-rule-files/results.md`, "The second run").
- This run cut what was left that no reader needs: two `Item:` lines (provenance; the root holds none) and a second
  pointer to the same section. 2 lines `[measured]`. No rule line went.
- The lose-nothing check (`selftest_rule_files_lose_nothing.py check`) reads FAIL with 6 losses. None is this run's: all
  six are the Scald exception, which the run on mechanics by their conditions deleted on purpose (`cba242eda8`). The
  check's base is fixed at `cea8d0bae6`, so it reads every later deliberate change as a loss.

### Principle 7, a limit names its danger: fixed for test deadlines, commit `4b996a6a74`

- The form: a deadline on a call or a test is a hang guard, never a speed bar. Its danger is named once for the class.
  Speed has its own signal (`selftest.slow_test_flag_s`).
- The change: `run_selftests.py` has one default of 600 s, and a `# selftest-timeout:` tag can only raise it. Page:
  `design/specs/2026-11-22-selftest-deadline/boundary.md`, with the danger, the evidence and the value under LIMITS.
- Retired: 136 per-test tags `[measured]`. They were 136 per-case repairs of one limit: 107 at exactly 600 s, 14
  between 241 and 599 s, and 15 at 240 s or less, which named no danger. 14 tags above 600 s stay. Each one marks a
  test that really is slower.
- Test: `selftest_selftest_deadline.py`. Red on the base: 3 of 4 FAIL, 136 dead tags found. Green after: 4 of 4. A
  planted dead tag in a temp repo reads red. With the `max()` removed, `t_a_tag_only_raises` reads red. `./publish`
  ran 117 pipeline checks green.
- Root `CLAUDE.md`: one clause names the class ("a call or test deadline is a hang guard"). This replaces the
  per-site duty for the 766 inline call timeouts. Each of them is the same class, and `call_deadline_lint.py` names
  its danger and evidence.
- Not built, with the reason: a `deadline.run` helper that takes the number out of 766 call sites. It would change
  about 400 files that other runs edit, and no behaviour would change. The class clause does the work of the helper.

### Principle 2, one home for a fact: fixed for "the mod an item names", commit `1f5dd16429`

- Found: three readers each had their own rule for which mod an item names (`maturation_now.item_mod`,
  `rimflow_metrics.item_mod` with its own alias table, `fleet_mods.mod_by_name`). On the ledger of 2026-11-22 they
  gave different mods for 1,288 and 2,736 of 9,649 items `[measured]`.
- The change: `rimflow/item_identity.py` is the one rule and the one alias table. The three readers import it. Page:
  `design/specs/2026-11-22-item-identity/boundary.md`. A title names a mod only by its whole name, its initials or an
  alias. Before, a title word such as "Mandrake" or "patches" placed 43 items on MandrakePatches.
- Retired: 2 parser functions and 1 alias table. The 3 readers' item-to-mod code went from 78 lines to 10 lines
  `[measured, git diff --stat]`. The new module has 51 lines.
- Test: `selftest_item_identity.py`. Red on the base: 4 of 4 FAIL. Green after. Planted faults, each red: a tie that
  guesses, a lost alias, the title before the id, the initials removed. The unchanged copy stays green. The three
  readers' own selftests pass.
- Run on the real ledger: in the metrics' mod heat, unmapped items went from 2,023 to 1,799 of 3,088. I read 12 of the
  858 changed answers. About 9 are right and 2 are wrong (a prose word that is also a mod's name: "wreckage", "atlas").
  The old rules also placed some items wrongly `[guess ~80% precision on changed answers]`.
- Not done (next step): write the mod as a field when the item is filed (`cli.py file` stamps `item_identity.item_mod`,
  or the filer names it), and write the stage on every launch record. Today 139 of 395 detached runs in the control
  store carry a mod and 80 carry a stage `[measured]`. Then the readers read the field, and the guess is only for
  items that are older than the field.

### A short look for forms the review missed

Candidates, not built. Each count is what it would retire.

1. **Identity is written once, when an item is filed and when a run is launched** (principle 2 carried through). It
   retires the other name parsers: `owed.py` (2 sites), `ops_health.py` (1), `modledger_backfill.py` (4 matching
   sites), `testing_census.py`'s `MOD_ALIASES`, and in `maturation_now.py` the guessing of a run's stage from journal
   headings and note text (`stages_named` and 3 placement branches). About 11 special cases `[guess ~60%]`.
2. **The selftest runner takes a test's lane from what it measured.** It records memory peaks already, and `winbuild`
   has a machine-wide build lock (`a8b7f15b91`). It would retire 25 per-test names in `run_selftests.py`:
   `DOTNET_LANE` 21, `MEMORY_HEAVY` 3, `SEQUENTIAL_ISOLATED` 1 `[measured count; feasibility guess ~50%]`.
3. Looked at and rejected: 54 item ids written into pipeline code. Most are ruling ids that mark authority
   (`--per-ruling`), not branches on one item's name.

### Before and after, second run

| measure | start of the second run | end |
|---|---|---|
| root `CLAUDE.md` lines | 726 | 725 (−2 pointer lines, +1 class clause) |
| per-test deadline tags | 150 | 14 |
| rules for the mod an item names | 3 | 1 |
| alias tables for mod names among those readers | 1 | 1 (now the only one) |

By the owner's measure: 136 per-case limits and 2 duplicate rules are retired. The root `CLAUDE.md` is still 87
lines longer than on 2026-11-20 (638). Most of that growth is new rulings from 2026-11-21 (mechanics by their
conditions; the guiding principles), not repairs.


## The third run, 2026-11-22: identity from the launch record, carried through

### Principle 2, the stage a run ran: fixed, this commit

- Found: every pipeline launch has recorded its stage since 2026-11-19 (`RM_CONTROL_STAGE`, in `maturation.py` and
  `maturation_autonomy.py`). But the status page (`maturation_now.runs_for_mods`) never read that field. It guessed the
  stage from journal headings in the run's time and from the run's own notes. On the 2026-11-22 records the guess
  matched the recorded stage for 17 of 91 runs. It was wrong for 13, added extra stages for 22, and found none for 39
  `[measured]`. After the field existed, the guess also put 6 hand launches into stages that they never ran (for
  example, a ColdStorage admission into Stages 1 and 8) `[measured]`. Each wrong placement changes a box's CYCLED count.
- The form: a run is on the stage that its launch recorded, and on no other. Prose places nothing.
- Page: promise `a-run-is-on-its-recorded-stage` on `design/specs/2026-11-22-item-identity/boundary.md`. Test:
  `t_a_run_is_on_its_recorded_stage` in `selftest_item_identity.py`. Red on the base: 3 FAIL. Green after. Planted
  faults, each red: the record is ignored (1 FAIL), and the notes guess is put back (2 FAIL).
- Retired: the two prose placement branches (journal headings, ledger notes) and the special case "a DESIGN item older
  than the journal is Stage 1". `runs_for_mods` went from 49 to 35 lines, and `maturation_now.py` changed by +16 and −32 lines (net −16) `[measured]`. `stages_named` stays, because
  `maturation.py` still uses it to date a stage's start from the journal.
- On real data after the fix, all 91 recorded runs sit on their recorded stage. 278 runs carry no stage, and 51 are
  before the pipeline. Those 278 were placed by prose before, at 19% agreement where it could be checked.

### Not built, with the reason

- **Stamp `item_identity.item_mod` on the item at `file`.** It would store a guess as a field: a second home for the
  same fact, which goes stale when the rule improves. That is the fault that principle 2 removes. The real facts at
  launch (mod, stage) are already recorded by every pipeline launch. A hand launch names a mod with
  `--env RM_CONTROL_MOD=<Mod>`.
- **`owed.py` (2 sites).** These sites make new item names from an id's words. They do not read which mod an item is on.
- **`ops_health.is_system` mod words.** Against the one rule it disagrees on 579 of 9,650 items, but only 4 of the 168
  open system items would move, and 1 of the 4 would be wrong ("STRANDED" is a prose word). It fails test 1 (polish).
- **`modledger_backfill.other_mod_words`.** A one-time SHADOW import for each mod. A new rule would change only past
  imports (polish).
- **`testing_census.MOD_ALIASES`.** A study tool from 2026-10-27 that no operation runs (polish).

### Polish (no ticket)

- `ops_health.words_of`/`mod_names`: its own "the id names a mod" rule (exact folder name, or two words joined). It
  misses initials and long words. It moves 4 open system items, 1 of them wrongly.
- `modledger_backfill.other_mod_words`: a fourth variant of the mod-word rule, in a one-time import.
- `Utils/sim/testing_census.py` `MOD_ALIASES`: a second alias table, in a study tool that nothing runs.

### Principle 2 (b), the game in the run record: still waits

- This waits for `RIMMANDRAKE_RENAME_GAMES_ARCHBIG_ARCHSMALL_STEVE1_STEVE2_LETTERS_UNREADABLE` to end. That run renames
  the games.

## Reconcile, 2026-11-24

- **Principle 2 (b), the game in the run record: done by `9f0336de6e`** (2026-11-21, item
  `RIMMANDRAKE_FIX_OFFLINE_STEWARD_REFUSED_BY_GAME_A_WALK_HOLD`). `detached_helper.py` writes `"game": run_game(item, cenv)`
  in every detached launch record, and `maturation_dispatch.run_game` reads the record's `game` first.
- **Principle 7, call deadlines:** settled by the root rule "No limit without the danger it guards": a call or test
  deadline is a hang guard, and the class names its danger once. No per-call number needs its own danger line.
- **Principle 9, the merge of principles 1, 3 and 6:** done (`ac9cca02b4`, second run).
- **Principle 2, next step 2 (a publish check that remakes each `GENERATED from` copy):** no failure from a stale copy is
  on record. It fails test 1 of "Touching code has a cost". Polish line below, no ticket.

### Polish (no ticket)

- A publish check that remakes each `GENERATED from` copy (`mod_owner_hold.json`, the `WSLENV` list) and compares.

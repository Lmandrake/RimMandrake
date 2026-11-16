# Codex experiment, scored — 2026-11-15

Item `RIMMANDRAKE_SCORE_CODEX_EXPERIMENT_FOUR_LANES_NO_CLAUDE`. The experiment: five Codex-only lanes the Conductor launched
~1:50 PM PST on the owner's order (*"conceive of several uses for CODEX and dispatch them"*). Outputs:
`D:\ClaudeWork\rimmandrake\codex_experiment_20261115\` (README.md first). Judged by a detached Opus run that made none
of it, against origin/main `fb2a08e966`. Every count below was measured in this run unless tagged otherwise.

Codex cost, from the lane logs' `tokens used` lines: lane C 240,226 tokens over 7 attempts; lane E 2,046,519 tokens over
4 drafts; lanes A, B and D went through `gpt_consult.py` and log no token count (UNMEASURED). Share of Codex's week:
UNMEASURED (no weekly-limit reading was taken before or after).

## Lane A — full-file code review of five pipeline files

**Asked:** correctness bugs in `maturation_autonomy`, `maturation_dispatch`, `coverage_judge`, `detached_helper`,
`maturation_convergence`, with trigger and smallest fix. **Produced:** 63 findings, 26 of them P1/High (autonomy 6,
dispatch 7, coverage_judge 6, detached_helper 7; convergence's 7 carry no severity, not scored). Reviewed revisions:
autonomy at `c5c259f906`, dispatch at `d13ff9728d`, detached_helper at `0c28b2596e` (all changed since); the
findings were checked against origin/main, not the reviewed text.

**Verdict: 22 of 26 confirmed, 4 false, 0 already fixed. High value.**

| finding | verdict | trigger (confirmed) or why false | item |
|---|---|---|---|
| autonomy: autolock overwrites a second writer's version | FALSE | land.sh replays with `merge-tree`; a conflicting VERSION.json refuses the landing, it never overwrites origin. The residue is the next row | — |
| autonomy: routing bypasses holds and disabled | CONFIRMED (held); disabled half FALSE | `held` is not in WAIT, so `_route` ran and `_road_back` launched a fixer past a Conductor hold. `disabled` is applied after resolve and empties launches | `RIMMANDRAKE_HONOUR_CONDUCTOR_HOLD_ROAD_BACK_FIXER_IGNORED_IT` |
| autonomy: failed autolock landing becomes a lock | CONFIRMED | land.sh fails on index.lock; the local VERSION.json stays locked; next tick routes to preflight on an unpublished lock | `RIMMANDRAKE_RESTORE_VERSION_FILE_WHEN_AUTOLOCK_LANDING_FAILS` |
| autonomy: cancelled launch keeps its slot | CONFIRMED | max_live 1, A planned; a road-back fixer replaces A's build but `live_total` still counts A: slots_full every tick | `RIMMANDRAKE_RETURN_SLOT_OF_REPLACED_LAUNCH_FIXER_NEVER_RAN` |
| autonomy: wrong-shaped JSON crashes the tick | CONFIRMED | VERSION.json `["0.1.0"]` raised AttributeError; a list stage.json escaped `designer_state` | `RIMMANDRAKE_READ_WRONG_SHAPED_JSON_LIST_CRASHED_TICK` |
| autonomy: seed landing failure refuses forever | CONFIRMED | `seed_mod` writes the record, land.sh fails, `widen` sees the file and never retries | `RIMMANDRAKE_RETRY_SEED_LANDING_LOCAL_RECORD_KEPT_REFUSAL` |
| dispatch: timer and `clear` overwrite each other | CONFIRMED | state.json is machine-wide (`doorbell.state_dir()`); a `clear` during a minutes-long tick is lost, or resurrected | `RIMMANDRAKE_LOCK_DISPATCH_STATE_CLEAR_LOST_TICK_WRITES` |
| dispatch: unreadable state resets safeguards | CONFIRMED | `_read` returned `{}` on a truncated file: every stop, retry count and spent release gone | `RIMMANDRAKE_REFUSE_UNREADABLE_DISPATCH_STATE_RESET_STOPS` |
| dispatch: spend-landing timeout loses launches | CONFIRMED | `land_spend`'s subprocess timeout escaped after `execute`, before state.json was written | `RIMMANDRAKE_CATCH_SPEND_LANDING_TIMEOUT_TICK_LOST_LAUNCHES` |
| dispatch: missing mod reading becomes zero occupancy | FALSE | the page lists only mods with VERSION.json; an absent entry is a Designer-stage concept with no placed runs. UNMEASURED there would read every tick as slots_unknown and stop all launches | — |
| dispatch: driver exclusion ignores non-advancing mods | CONFIRMED (narrow) | a hand-launched in-game run on a non-advancing mod, before it takes the bridge, did not hold a second driver back | `RIMMANDRAKE_COUNT_EVERY_MOD_INGAME_DRIVER_NOT_ADVANCING_ONLY` |
| dispatch: killed retry drops its spend | CONFIRMED | `stage_spent` ignored `killed_before` units not yet placed in a box, and a never-started retry dropped `killed_before` | `RIMMANDRAKE_CHARGE_KILLED_ATTEMPTS_RETRY_DROPPED_DOLLARS` |
| dispatch: ceiling release lifts unrelated stop | CONFIRMED (narrow) | `"ceiling" in why`: a progress stop naming a bar with "ceiling" in it lifted on a release | `RIMMANDRAKE_MATCH_CEILING_STOP_BY_FLAG_NOT_SUBSTRING` |
| coverage_judge: final freshness check can sign an unjudged tree | CONFIRMED (milliseconds) | `CT.sign` reloaded tree.json with no expected hash | `RIMMANDRAKE_SIGN_ONLY_THE_JUDGED_TREE_HASH` |
| coverage_judge: concurrent invocations duplicate judges | FALSE as deployed | `rm-dispatcher.service` is a oneshot (ticks never overlap) and a hand `run` happens in another clone | — |
| coverage_judge: stale refusal blocks a newer concept | CONFIRMED, NOT FIXED | rm/dispatch is shared by two timers and land.sh's seat_sync updates it mid-judge; freshness is checked only for `covered`, so a stale not_covered counts toward NOT_COVERED_LIMIT and `hold()` writes blocked over newer state. Left open: the fix decides what counts as a refusal (the refusal contract), for the neutral criteria fixer | `RIMMANDRAKE_REVALIDATE_INPUTS_BEFORE_REFUSAL_STALE_THIRD_STRIKE` |
| coverage_judge: shared-material gaps dropped | CONFIRMED | only floor.json changes; a gap tagged regression naming row B was dropped as off-scope | `RIMMANDRAKE_KEEP_GAPS_OPENED_BY_SHARED_MATERIAL_CHANGES` |
| coverage_judge: exam.json invisible to delta | CONFIRMED | `entries()` never read exam.json though the full judge does | `RIMMANDRAKE_HASH_EXAM_IN_DELTA_ENTRIES_CHANGE_UNSEEN` |
| coverage_judge: repeated sheet headings hide edits | CONFIRMED | two `## Controls` sections shared one key; the second overwrote the first | `RIMMANDRAKE_KEY_REPEATED_SHEET_HEADINGS_SECOND_HID_FIRST` |
| detached: clone acquisition not exclusive | CONFIRMED (narrow) | two launches of one item both passed the holder check during a minutes-long `./sync` | `RIMMANDRAKE_LOCK_DET_CLONE_TAKE_TWO_LAUNCHES_ONE_CLONE` |
| detached: launch overwrites a finished run | CONFIRMED (narrow) | a helper that exits at once is recorded finished before launch writes `running` | `RIMMANDRAKE_KEEP_FINISHED_RECORD_LAUNCH_WROTE_RUNNING` |
| detached: concurrent record writers | CONFIRMED, half fixed | the shared `<record>.tmp` is fixed (a name per write); the read-modify-write lost update between backfill and return stays | `RIMMANDRAKE_UNIQUE_TEMP_PER_RECORD_WRITE_SHARED_TMP` |
| detached: ownership follows the caller's environment | FALSE as deployed | no unit or tool sets `RM_DETACHED_POOL` (only forwarded); every caller reads the default pool | — |
| detached: failed scope termination completes the run | CONFIRMED | kill and stop both FAILED and the scope still active: finish recorded `finished` and never retried | `RIMMANDRAKE_RETRY_FINISH_WHEN_SCOPE_STOP_FAILED_BILLING` |
| detached: supervisor kills finish after 30 s | CONFIRMED, measured | `journalctl --user`: 10 detached units hit "State 'stop-post' timed out" 2026-11-08..15, the last at 15:41 today | `RIMMANDRAKE_COVER_FINISH_IN_TIMEOUTSTOPSEC_TEN_KILLED` |
| detached: failed clone sync still launches | CONFIRMED | `take_clone` returned a reused clone whatever `./sync` exited | `RIMMANDRAKE_REFUSE_STALE_DET_CLONE_WHEN_SYNC_FAILS` |

**Landed:** `79348d40e0` fixes the 21 confirmed-and-fixed rows, tests first:
`src/RimMandrake/rimflow/selftest_codex_review_fixes.py`, 26 checks, 25 FAIL on `fb2a08e966` and 26 PASS after; the
11 existing selftests of the touched modules green. All 21 items closed on that sha. Detached units now get
`TimeoutStopSec=600` (it bounds the main process's stop too; `finish` SIGKILLs the scope first).

## Lane B — second opinion on Pyrelands' round-6 coverage verdict

**Asked:** which of the 18 gaps are real and which are judge noise. **Produced:** 14 CANNOT TELL, 4 NOISE, 0 REAL: the
lane was not given `scenes.json`, `record.json` or the tests, which 14 of 18 calls needed. **Verdict: low value as
run;** the input set, not the model, decided it.

Its proposed rule, *freeze the acceptance contract before round seven* (judge against a fixed checklist; a gap must name
a concrete broken behaviour every named check would accept; new requirements become next-version proposals), is
**sound**: it matches the Design Version rule (Divergent work never moves the current bars) and the delta judge's
late-gap rule, and adds one testable clause the brief lacks. Handed to the neutral criteria fixer as a note on this
item; the calibrated brief was not edited.

## Lane C — patches for red nightly selftests

**Asked:** one attempt per red selftest. **Produced:** 7 attempts, 6 patches (stage3_owed honestly left RED with a
correct diagnosis: the reds are features not yet built). All 6 tests were still red on origin/main before review.

| test | verdict | why |
|---|---|---|
| `selftest_no_bare_cuts` (273 lines) | **LANDED** `bd608673e1` | 30 sites, each line only drops a slice: text stored whole, per his 2026-11-12 ruling. No assertion, allow-list or `cut-ok` touched. Applied by line over the lane A fixes; the touched modules' selftests green |
| `selftest_extra_art_commission` | **LANDED** `2c93be57f3` | files RSW_ColoClawFish's young row. The tool reproduces it: `extra_art_commission.py receipt` from the live registry writes the same receipt byte for byte; `plan` gives the same rows (another order). It also turns `selftest_extra_art_filed_rows_kept` green |
| `selftest_extra_art_filed_rows_kept` | REJECTED | rewrote the test's own fixture from the live plan (it no longer reads the filed commission) and added a `try/except TypeError` fallback; the data fix above made it green untouched |
| `selftest_extensions` | REJECTED | grows `TOGGLES_NOT_ON_FLOOR` by 17 switches, a list commented "listed so it cannot grow unseen": an allow-list widened to get green |
| `selftest_review_map` | not landed: sound but stale | 2 relabelled rows and 7 new ones (6 in the module's documented `matrix: <reason>` class), but origin/main gained 5 more uncovered items since (RM_TossFlame, RM_LiquidCoat and three settings), so it stays red |
| `selftest_swbestiary_pack_overlays` | REJECTED | a binary PNG diff with no data (cannot apply), and art lands only through the art ledger's `art install` and a judge |

## Lane D — Stage 7 (pre-human check) and pass-record design draft

Usable: it covers inputs, the programs run before the reader, the fresh reader's six questions, refusal routing, exit
test, the owner's brief, a pass-record format, acceptance tests and a first slice on Explosive Knockback, each tied to
a ruling. Weak where it should measure: "reuse an existing folder-hash routine if available" was left unchecked.
Feed it to the Designer as the starting text for Stage 7, not as a decided design.

## Lane E — first-touch Designer drafts

The drafts cite 71 `file:line` references, every one resolving; 12 of 12 sampled owner quotes are verbatim in the repo.

- **LeaningScrub** (286 lines): complete, all seven parts (root, first demonstration, sheet, tree and checks,
  contradictions, questions with obvious answers, 0.1.0/0.2.0). **Ready as Designer input.**
- **FeverWood** (474 lines): complete, all seven parts, the chorus question answered from his words. **Ready as Designer
  input.**
- **Cauldron** (185 lines): the sheet and some leaves only; it says itself "Remaining before this becomes a complete
  first-touch draft: finish the exhaustive read". Partial input only.
- **Stillsand** (216 lines): grounded core and scenes, but "does not yet provide the exhaustive" inventory, by its own
  words. Partial input only.

Certifying a first-touch Designer pass stays the owner's (delegation_policy §2); nothing was admitted.

## Overall

Lane A was worth its cost: 22 real defects in five files, one of them measured killing finishes in production. Lane C
gave 2 sound fixes out of 6 patches, and 2 of the rejections were the "get green" shortcuts the brief warned about.
Lane E gave 2 usable Designer inputs of 4. Lanes B and D are inputs for the next design work, not results. Re-run B
with scenes.json and record.json before reading anything into its zero REAL count.

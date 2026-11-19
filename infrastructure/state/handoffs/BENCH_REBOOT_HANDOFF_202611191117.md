# BENCH_REBOOT_HANDOFF_202611191117 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202611190625`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

## The one thing to carry forward

<!-- The single most important thing learned. Not a list — the thing that would cost the next seat hours if it had to rediscover it. If nothing qualifies, write 'nothing this wave' and mean it. -->
NIGHT ORDER, still in force until he next writes (owner, 2026-11-19 12:43 AM PST): "Take some risks and keep things going slowly and thoughtfully overnight. Maybe make some new hypotheses on how we could do this all better and run a few experiments to play around with possibilities. Tell me about it in the morning." Cap: two helpers. When he writes, give him the morning summary first: it is already written at `/mnt/d/ClaudeWork/rimmandrake/conductor/situation_2026-11-19_0315.md` (native `D:\ClaudeWork\rimmandrake\conductor\situation_2026-11-19_0315.md`); open it in Typora and add anything that happened after 3:15 AM PST. Three things bind every brief: (1) his 8:22 PM 2026-11-18 stop on Codex and GPT reviews of pipeline code stands (one calibration call was allowed by card and is spent); every brief appends `/mnt/d/ClaudeWork/rimmandrake/conductor/briefs_20261118/_addendum_no_review.md`. (2) Pipeline machinery is now built page first (his three card answers, `standing_rulings.md` §A boundary page before pipeline code): a new component owes a `boundary.md`, a fresh read of it, and a test per promise that FAILS under a deliberate break; "N of N covered" from `boundary_check.py` only proves a named test runs (it read 23 of 23 when 7 tests caught nothing). (3) Detailed code questions to him are written in Simplified Technical English (his words 2026-11-18 11:23 PM PST; `roles/conductor.md` Workshop rules): a card in design vocabulary came back "I can't make heads or tails of ANY of these options".

## What the owner should see

<!-- Findings that need HIS eye or HIS decision: a number nobody ruled on, a mod that vanished from his list, a change he can veto. Say what you shipped deliberately with a flag raised. Empty is a legitimate answer. -->
- **Read him the morning summary** (path above); its top section ranks what needs him, about ten minutes: the page is stricter than the labels the 18 complaints were sorted by (blind reader and Codex each call 21 of 35 real, the analyst 4: fix them, or move rare failures to the page's "does not handle" list; I recommend the second); a second Codex test of the reviewer instructions needs his word; the sea biomes' cleanse proposal changed shape after his approval (70/33/43 to 77/38/46) when the tenancy row was dropped; six hand-launched helpers worked FeverWood design tickets under his hold.
- **Delegated calls he can veto:** the tenancy row dropped without a card (his 2026-09-27 "Remove"); the control code cut to its page and its launch reader removed; seven promise tests rewritten; the shared-starting-context change NOT built (about 2% saving against real risks); the 299-place lint and the ten-file conversion left unstarted until he has seen the blind relabel.
- **Token figures from the Conductor log before 1:23 AM PST 2026-11-19 are too high** (resumed runs counted their whole session): 2026-11-18 is 290.2M weighted tokens, not 371.3M; the review design's 303.5M and 52.8M carry the fault.
- **Code written tonight had no outside review**, by his stop; its guard is the page, its tests and the deliberate breaks.
- **This window's goodbye restart was refused** at 11:27 PM PST ("no goodbye of his within 3600 s") though he wrote "Afk. Goodnight."; the window stayed open all night. Not traced.

## What is half-done, and where it stops

<!-- Anything left mid-flight, one bullet each: `- ITEM_ID -- state; NEXT: <one imperative action>`. A pointer without a ledger item id does not survive a seat change, and a pointer without a NEXT: measured ~0% pickup. An item in `doing` with no line here is a trap for the next seat. The Conductor's pointers each cite an open owed id too: file the act first (`rimflow file <ID> --for BENCH --kind owed --caused-by <item>`), then cite it on the line; --check runs `owed.py check-pointers`. -->
<!-- These are the items you started this window and did not
     close. Say what state each is in and ONE imperative NEXT:
     action, or close/block it. --check refuses while any is
     unaccounted for or lacks a NEXT:, so deleting a line here
     is not a way past it. -->
- `RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED` — fix published 2a5b1558b2; its acceptance test reads VERDICT EMPTY until a resumed run launched after the fix has ended; waits to 2026-11-21; NEXT: after the next resumed detached run ends, run `python3 design/experiments/2026-11-19-night-hypotheses/tools/check_resumed_run_tokens.py . /mnt/d/ClaudeWork/rimmandrake/dispatcher/detached --since 2026-11-19T09:19:00Z` and close on VERDICT PASS with --sha 2a5b1558b2 (owed `RIMMANDRAKE_CLOSE_TOKEN_COUNT_FIX_ON_FIRST_RESUMED_RUN`)
- `RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS` — instructions and calibration set built (62a7614d81); the one Codex test read 16 of 35 against labels that a blind reader also disputes (05-three-way-labels-20261119.md, 9f3712dc27); waits to 2026-11-21; NEXT: put to him, in Simplified Technical English, the draft wording change and the 12-claim pass mark, and ask his word for a second Codex test (owed `RIMMANDRAKE_ASK_HIM_SECOND_CODEX_TEST_FIRST_READ_SIXTEEN`)
- `RIMMANDRAKE_TELL_HIM_THE_NIGHT_IN_THE_MORNING` — summary written, not yet told; NEXT: when he writes, open situation_2026-11-19_0315.md in Typora, give him its top section, then close this debt with `told him at <time>`
- `RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE` — closed at 0bf215847a36 but unproven live; NEXT: read the first prompt of the next detached helper's transcript and confirm it holds no block starting "You are this session's seat." (owed `RIMMANDRAKE_READ_NEXT_HELPER_START_NO_SEAT_IDENTITY_BLOCK`)
- `RIMMANDRAKE_NAME_RECEIVER_FOR_SEAT_ALARMS_PENDING_WITH_NONE` — still owed; selftest_known_reds now passes by asserting the no-receiver state (3fac6d0d7da2); NEXT: name the receiver, then turn the two rewritten known_reds checks back to assert a filed chase item
- `RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED` — filed with its test, not started on purpose; NEXT: after he has ruled on how strict a page is, launch one Opus run per three files to read the flagged places, never one run for all 299 (owed `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS`)

## Traps learned

<!-- Instruments that lied, silent failures, commands that ate their own input. ONE line each, ending with where it now lives -- file it with `lessons.py add` the moment it is learned, then cite `(filed: lessons)` or `(see: <item/doc>)`. Never re-explain a trap that is already recorded somewhere durable. -->
- A `.git/index.lock: File exists` in the Conductor's clone is another short git process in the same clone; a failed `./sync` leaves a 0-byte lock and a stale ledger, so `rimflow show` reads a closed item as open (hit three times, 12:45 to 3:11 AM PST). (filed: infrastructure/state/lessons/20261119T084833Z-BENCH-git-index-lock-file-exists-refusal.md)
- A resumed run's recorded spend was its whole session, so every sum over run records double counted. (see: infrastructure/state/facts/instrument_traps.md)
- `what_fills_context.py` counted request-copy lines twice and reported large reads as half of tool text; the true share is 36%. (see: design/experiments/2026-11-19-night-hypotheses/06-large-reads.md)
- "promises covered 23 of 23" was reached by renaming existing tests; breaking each promise on purpose showed 7 tests caught nothing. (see: design/specs/2026-11-18-pipeline-control-surface/promise_tests_broken_on_purpose.md)
- A run that died of API error 529 leaves its uncommitted files only in the orphans bundle `real_untracked.tar`; `--resume <session>` gets the transcript back but not the files, so the resume brief must say to untar them first. (see: /mnt/d/ClaudeWork/rimmandrake/conductor/briefs_20261118/_resume_night_hypotheses.md)

## Closed since the last handoff (42)

- `RIMMANDRAKE_LABEL_CONDUCTOR_OPENED_SCOPE_NOT_HIS_WORDS` — 5570fc1a7119
- `RIMMANDRAKE_GUARD_CONTROL_COPY_RETAINED_RULES_ONE_WORD_REVERSES` — 5570fc1a7119
- `RIMMANDRAKE_HARDEN_PIN_ANCHOR_THREE_EDGES_CODEX_FOUND` — 5570fc1a7119
- `RIMMANDRAKE_CORRECT_FOUR_SEAS_GREY_CATCH_SAYS_THIRTEEN` — f0ca981b0ce7
- `RIMMANDRAKE_RETIRE_COMBINED_SEA_DESIGN_TWO_SEAS_FOUND_WRONG` — f0ca981b0ce7
- `RIMMANDRAKE_CHECK_RESUMED_READERS_PAGES_FOR_TRIMMED_READING` — 9fcac0b4d3dd
- `RIMMANDRAKE_UNPLACE_MACHINERY_HELPERS_FROM_MODS_SLOT_TAKEN` — c8e06b5d3197
- `RIMMANDRAKE_RECONCILE_TWO_EXAM_RETAKE_TESTS_LEAF_VERSUS_FILE` — addbc1f7cf39
- `RIMMANDRAKE_TEACH_HELPER_WAIT_OWNERS_TURN_RELAUNCHED_FABLE` — cfb9fb5f8c76
- `RIMMANDRAKE_CHECK_COMMITTED_TREE_NOT_DIRTY_WORKTREE_AT_DOOR` — d04ab1009366
- `RIMMANDRAKE_SAMPLE_PYRE_NEVER_ROWS_BETWEEN_FIVE_HUNDRED_TICKS` — d04ab1009366
- `RIMMANDRAKE_RETIRE_LEASE_GUARD_TWENTY_FIVE_GHOST_LEASES` — bb0f483b3a2a83b4763010c9dff9a507ea7a10ea
- `RIMMANDRAKE_UNCLOG_SCRATCH_ARCHIVE_BACKLOG_29_KB_CLONES_EACH` — 0e46d65aa1
- `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` — 7ab8a45321
- `RIMMANDRAKE_CARD_REPAIR_RULES_WHEN_ROUND_SPLIT_IS_MEASURED` — 1dbd8e0457
- `RIMMANDRAKE_READ_NIGHT_RUN_REPORTS_SEVEN_STARTED_AT_TEN` — 1dbd8e0457
- `RIMMANDRAKE_MEASURE_TWO_MORE_REVIEW_ROUNDS_BEFORE_ANY_FILTER` — 1dbd8e0457
- `RIMMANDRAKE_ENACT_PAGE_BEFORE_CODE_CONTROL_STORE_IS_PILOT` — daad400e3429
- `RIMMANDRAKE_READ_CONTROL_PAGE_FRESH_BEFORE_CODE_IS_CUT` — cf4f0a87a246
- `RIMMANDRAKE_ASK_CLEANSE_TENANCY_ROW_APPROVED_AFTER_HIS_CUT` — 84609890c017
- `RIMMANDRAKE_CUT_CONTROL_STORE_TO_PAGE_ARGV_READER_GOES` — 4f12b10443b4
- `RIMMANDRAKE_DRILL_KILL_ON_THROWAWAY_UNIT_ZERO_LIVE_KILLS` — 8481f1a76a94
- `RIMMANDRAKE_MEND_TWO_SELFTESTS_RED_BEFORE_THE_CODE_SPLIT` — 3fac6d0d7da2
- `RIMMANDRAKE_PROVE_TWO_COVERAGE_JUDGE_FAULTS_OVERTURN_DOUBLED` — 4a49d294f9c9
- `RIMMANDRAKE_END_GHOST_RUNS_STORE_SAYS_STARTED_SYSTEMD_GONE` — b058baa480
- `RIMMANDRAKE_RELABEL_OLD_CLAIMS_BLIND_CODEX_AGREED_ON_SIXTEEN` — 9f3712dc2714bdf75a97d72457911c20f4d70ddf
- `RIMMANDRAKE_TRY_NIGHT_HYPOTHESES_ON_RUNNING_FACTORY_BETTER` — 321f8272c2e2
- `RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED` — 046554a9334e27d35362a97b037f8db8352c155a
- `RIMMANDRAKE_CHECK_PAGE_ONLY_EDIT_AT_PUBLISH_SLIPS_PAST` — 60274d0df25d
- `RIMMANDRAKE_TEST_SHARED_STARTING_CONTEXT_TWO_TINY_LAUNCHES` — ed91191396ffaeba199b77c59ffa2a250f76787c
- `RIMMANDRAKE_STRIP_CONDUCTOR_IDENTITY_HELPERS_TOLD_DELEGATE` — 0bf215847a36 (owed `RIMMANDRAKE_READ_NEXT_HELPER_START_NO_SEAT_IDENTITY_BLOCK`)
- `RIMMANDRAKE_BREAK_EACH_PROMISE_DOES_ITS_NAMED_TEST_FAIL` — 9cb84a6dca35
- `RIMMANDRAKE_HARDEN_PROMISE_TESTS_SEVEN_BREAKS_SLIPPED_PAST` — 910aba337e886a03398c0230ebfa977435f4afbb
- `RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN` — be1b9a29452d
- `RIMMANDRAKE_READ_PROBE_RESULT_PAGE_FRESH_WRITER_COULD_NOT` — 255dfb096e98
- `RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE` — 0210176155e1
- `RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS` — 958c4a287c9b
- `RIMMANDRAKE_SETTLE_SPLIT_CONTROL_REVIEW_LEFT_OPEN` — e68d32a7a9
- `RIMMANDRAKE_SETTLE_HIDE_CAP_STOP_LEFT_OPEN` — e68d32a7a9
- `RIMMANDRAKE_REPIN_GRAFFITI_SOAK_FIX_AFTER_WEDNESDAY_RESETS` — e68d32a7a9
- `RIMMANDRAKE_SETTLE_STALE_CONDUCTOR_DEBTS_THIRTY_ONE_OWED` — 43895e317b
- `RIMMANDRAKE_SPLIT_CONTROL_REVIEW_ROUND_FOUR_FIFTEEN_UNTRIED` — done by verify, no close

## Filed and still open (8) — the next seat's queue

- `RIMMANDRAKE_WRITE_REVIEW_BRIEF_CALIBRATE_ON_THIRTY_FIVE_CLAIMS` — Write the code-review brief for pipeline machinery (two looks, against the boundary page only), add the code_review refusal family, and calibrate it o (owed `RIMMANDRAKE_ASK_HIM_SECOND_CODEX_TEST_FIRST_READ_SIXTEEN`)
- `RIMMANDRAKE_TELL_HIM_THE_NIGHT_IN_THE_MORNING` — When he next writes: give him the morning summary of the night (what landed with shas, what is half-done, what needs him, what broke, and the hypothes
- `RIMMANDRAKE_SHOW_PHONE_ALERT_DRAFT_BEFORE_ITS_CARD` — Show him the phone-alerts draft (RIMMASTER_DESIGN_PHONE_ALERTS_THAT_ACTUALLY_RING section 9) as a message before putting its card
- `RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED` — A resumed run's recorded weighted tokens are its whole session so far, so every sum over run records counts the earlier runs twice (26 of 26 resumed r (owed `RIMMANDRAKE_CLOSE_TOKEN_COUNT_FIX_ON_FIRST_RESUMED_RUN`)
- `RIMMANDRAKE_SHARE_HELPER_START_ONE_STATUS_LINE_REWRITES_IT` — Every helper writes its ~50,000-token start into the cache new: give helpers one fixed path (own clone bind-mounted), no git status block and a fixed 
- `RIMMANDRAKE_MOVE_OWN_UNREADABLE_CLASSES_ONTO_PROBE_TEN_LEFT` — The ten files under rimflow and Utils that define their own Unreadable or Unmeasured class answer through probe_result.py instead
- `RIMMANDRAKE_ARM_COULD_NOT_LOOK_LINT_299_PLACES_ALLOWED` — Switch could_not_look_lint.py at ./publish from shadow to refusing (owed `RIMMANDRAKE_LAUNCH_LINT_READS_AFTER_HE_RULES_PAGE_STRICTNESS`)
- `RIMMANDRAKE_USE_OR_DROP_ACT_BEFORE_VALUE_NOBODY_READS` — The control store writes a 'before' value on every act and no code reads it: pipe log does not print it and pipe undo does not use it, so the only rec

## Commits

```
21785b6536 conversations: catch-up 1 record(s)
59db08ef3c ledger: detached run on RIMMANDRAKE_SETTLE_STALE_CONDUCTOR_DEBTS_THIRTY_ONE_OWED ended
2de313e9f0 ledger: debt sweep item closed
43895e317b ledger: debt sweep, 3 closed, 11 NEXT notes
e68d32a7a9 ledger: debt-settling sweep filed
32cc2611ff ledger: RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS clone bundled
5abd439ced conversations: catch-up 1 record(s)
d25f50918f ledger: detached run on RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS ended
3d4bae7cad lesson: transcript api-request-blob lines repeat tool results; count by tool_use_id
bf327e12bd ledger: RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS closed
958c4a287c experiment: builder surprise and large reads replayed; earlier tool-text figure counted 9.6M twice
96bb2b3d6d ledger: DISPATCHER notes (1)
8d88de4d7c ledger: RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE clone bundled
e2cf54c696 conversations: catch-up 1 record(s)
79bf67f880 ledger: detached run on RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE ended
b8524ee4ef ledger: RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS note
d5357d3c7e ledger: RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE closed
5e11374cc3 ledger: RIMMANDRAKE_COUNT_JUDGE_AND_ART_REASK_TOKENS_ONCE closed
0210176155 coverage judge and calibration re-asks count the session once A --resume result is the whole session (modelUsage, total_cost_usd); both took it on top of the first ask's figure. Rounds re-asked 2026-11-17 07:00Z..now are inflated; v1-era rounds are not. art_calibration: unproven, unchanged.
bdffe5740d experiment: pre-register the builder-surprise and large-read replays
... 225 more: git log --oneline 8dcdd4c93b..HEAD
```

## Game / bridge / tree state at wrap

- running   : NOT RUNNING   (tasklist.exe lists no RimWorldWin64)
- recorded  : DOWN
- Bridge: FREE    since 2026-11-17T19:16:24Z

Working tree clean apart from untracked `Transient/`.


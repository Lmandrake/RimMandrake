# WB-cause-RIMMANDRAKE-ORDER-TEN-SLOW-ACTION-FIXES-PAGE-FILED-NONE-20261127-185008: state

Members (7). Restart 1 is owed (context 559 k of 1,000 k at 3:05 PM PST, past the 500 k line). Publishes waited 45 to 55 min
for a slot this afternoon; two were refused because a Codex build of the same member landed while they waited. Every member's code and
test is written and committed; what is left is landing, live readings, the slow-actions page lines and the closes.

## Done (code, tests red-then-green, boundary page; commit shas change on publish: find them by subject)

- `RIMMANDRAKE_RUN_LANE_CHECKS_ONCE_193_OF_218_SECONDS` (first member, claimed): LANDED at 30f91fb7d9f3.
  `check_once.py` + `check_reads_hook/`; page `design/specs/2026-11-27-check-once/boundary.md`. Live since about
  12:30 PM on the dispatch clone: rm-list-effect 129 to 192 s before, 53 to 74 s after; rm-list-dispatch 370 to 480 s
  before, 86 to 203 s after (one 379 s). Offline, real 81 checks: first beat 83 s, second 42 s (56 kept, 16 unnamed run
  every time: git children, shell loops), load 45. Follow-up commit (not yet landed): list_dispatch's reading carries
  `checks`. Close it with the landed sha of that follow-up, `--evidence` the timings above.
- `RIMMANDRAKE_CUT_TICK_PAGE_REPEAT_WORK_716_LAST_WORDS`: the Codex lane's build LANDED first (cdec189bc4); this
  bundle's build was dropped at 5:10 PM. Its numbers (tick 62.5 -> 41.5 s, page 94 -> 31 s) were of the dropped build:
  profile one tick and one page of the landed code before writing a line on the slow-actions page. Ideas from the
  dropped build that the landed one may lack: run records and out-file facts kept by stat (dir_fd); PNG at zlib default
  (4 to 6 times faster, same pixels). Read the landed code first; any of these is a new item, not this one.
- `RIMMANDRAKE_MEMO_SUBJECT_ALIASES_THREE_MILLION_CALLS_A_RUN`: the Codex lane's build LANDED first (db371e01aa). This
  bundle's own build was dropped before publish. Measured with this bundle's build: collect 82 -> 54 s wall. Check the
  ticket's state; close it on db371e01aa if still open.
- `RIMMANDRAKE_SPEED_DEPLOY_PLAN_RELATIVE_STAT_ENOMEM_SILENT`: the Codex lane's build LANDED first (6:20 PM); this
  bundle's build was dropped. Its numbers (Gimme Some Slack on ArchSmall, interleaved at load ~30: base 97.7 and 98.0 s,
  dropped build 60.3 and 54.5 s) were of the dropped build: time the landed code the same way before writing the line.
  What the dropped build found: 85 of 104 s of a plan is the def guard (parse_defs stats by absolute path, 6,411 at
  about 9 ms; xml_files lists by path, 3,288); xml_files also skipped a failed listing without a word.
- `RIMMANDRAKE_SPEED_SCRATCH_REAP_FOLDER_TIME_TWO_MILLION_LSTAT`: the Codex lane's build landed first (young or held
  folders kept by their own time; child_time names the child commands). This bundle's part is merged on top:
  find_clones reads each folder's `.git` from its listing, and publish_check_* folders are not searched and are swept as
  fixtures. NOT LANDED: origin's scratch_reap.py moved again (40475c6bcd, RIMMANDRAKE_SPEED_SCRATCH_REAP_SEAT_TMP_PUBLISH_
  CHECK_RESIDUE_2M: another run took the publish_check litter). The two commits are kept as a patch,
  `D:\ClaudeWork\scratch\checkonce\scratch_listing_two_commits.patch` (and the local branch scratch-listing-pending
  in this clone): test `selftest_scratch_reap_listing.py`, page `design/specs/2026-11-27-scratch-reap-listing/
  boundary.md`. Next: read 40475c6bcd; land only find_clones's `.git` from the listing if it is still not there.
  Cause measured: 870 k folders walked, 806 k in 100 publish_check_* folders left by killed publishes; candidates()
  288 s (load 26) -> 127 s (load 42). Dry run 723 s at load ~40: live 322 s (the borrower find 314 s), judge 254 s.
- `RIMMANDRAKE_RECORD_MODEL_AND_TOOL_SECONDS_833_HOURS_UNSPLIT`: the Codex lane's build LANDED first (ccc65c468d,
  fields model_seconds and tool_seconds); this bundle's build was dropped at 5:10 PM. Owed for the spec: the 7-day split
  on the slow-actions page, from the landed fields or the transcripts.
- `RIMMANDRAKE_MEASURE_PUBLISH_SLOT_DANGER_BEFORE_ANY_CHANGE`: DONE (closed by the list_effect tick on its page check).
  Restart 1 (7:25 to 8:05 PM PST) built recommendation 2: door_reads.py keeps one record per test and tree
  (`TREES = 16`), LANDED at 539495cd3d (test `t_a_tree_that_never_landed_hides_no_record` red on the parent); the page
  has the Conductor's 4 PM reading and the census of unseen reads. Recommendation 3 is its own item,
  `RIMMANDRAKE_NARROW_DOOR_UNSEEN_READS_SIXTY_EIGHT_RECORDS_TWENTY_KINDS`. That item's before-and-after measurement with
  `publish_line_measure.py` also reads the "another version" share under the per-tree store.

## Found on the way (no ticket before)

- The Codex lane sent four members of this live bundle to Codex (13:11 to 13:33 PM): fixed, commit
  "RIMMANDRAKE_KEEP_CODEX_LANE_OFF_LIVE_BUNDLE_MEMBERS" (codex_lane.plan skips a live bundle's member, a live run's item,
  and all while runs cannot be read; test t_a_member_of_a_live_bundle_or_run_is_never_sent red first). Codex builds of
  cut-tick, deploy, scratch and run-seconds are landing in their own clones (`/home/mandrake/rm/runs/clones/<ID>.det`).
  Whichever lands second must reconcile: keep one build per file. Read origin first.
- `selftest_stage6_checks.py` is red on origin (PRE-EXISTING at the door): not this bundle's.
- The landed Codex `selftest_deploy_listing.py` passes when run alone and FAILS under `run_selftests.py --only` (its
  t_relative_stat_gives_the_same_index_as_absolute: `assert scans == {True}` reads {False}; seen 6:25 PM). Class it
  (test or code) and fix it test first, or file it with that evidence.

## Polish

- Done: list-shape self-loop (`list_shape.own_check`); the maturation-record token_unit line deleted. The list-dispatch
  line was deleted on origin by another run.
- Kept: `design/specs/2026-11-23-one-failure-classifier/polish.md` CYCLED count (a change would change what
  selftest_maturation_now case 9 checks).

## Next, in order

1. Read `git log origin/main` for this bundle's subjects and for the Codex landers' subjects; land what is not landed
   (`./publish`; the line held 7 ahead at 3 PM). Reconcile with a Codex build that landed first on the same files.
2. Write each member's before/after line on `design/specs/2026-11-26-slow-actions/one_page.md` (rows 2 to 10; the
   numbers are above), and the 7-day split from `seconds_of`.
3. Close each member with its landed sha and its evidence; file the door-reads change; the bundle's end files the
   fresh reader (do not file it by hand).

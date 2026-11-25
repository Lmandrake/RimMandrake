# BOUNDARY: CODEBASE_NOW, the standing clean/dirty treemap page, Design Version 0.1.0

Code: `src/RimMandrake/Utils/codebase_now.py`, run by `rm-codebase-now.timer` (units in `src/RimMandrake/Utils/systemd/`).
Item: `RIMMANDRAKE_REVIVE_CLEAN_DIRTY_TREEMAP_ON_STANDING_TABS`. Why it exists: his card of 2026-11-19 5:54 PM PST,
*"the Python to visualize the clean/dirty codebase is ressurrected and included on the standard suite of Desktop
visualizations to track"*. The page is `D:\ClaudeWork\rimmandrake\conductor\CODEBASE_NOW.html`, beside
`MATURATION_NOW.html`. A program writes it with no model call. Written 2026-11-19.
Each promise has a test of its name in `src/RimMandrake/Utils/selftest_codebase_now.py`.

The older treemap (`src/RimMandrake/Utils/codebase_health.py`, `rm-codebase-health.timer`) stays. It paints red for
open bugs and blue for uncommitted edits in the bench clone, and it writes into that clone's `Transient/`. This page
answers one question only: which code files a cold read found clean, and which changed since or were never read.

## ACCEPTS (the only inputs the page is built for)

- **a-git-clone.** The root is a git clone (the timer runs in the dispatch clone, `/home/mandrake/rm/dispatch`, which
  fetches every few minutes). The file set is `git ls-files` at that root, one git call.
- **the-review-record.** `infrastructure/state/code_review/*.jsonl`, read only through `code_review_status.load()` and
  `code_review_status.clean_state()`. The page never parses the record by hand.
- **the-boundary-pages.** `design/specs/*/boundary.md` and their tests files, read only through
  `code_review_status.page_states()`.
- **a-cache-file.** The tests verdict cache, `codebase_now_tests_cache.json` in the output folder. Any unreadable or
  foreign cache is treated as empty.

## DOES NOT SURVIVE (not promised; where the page notices, it says so)

- **a-root-that-is-not-a-clone.** With no git answer, there is no file set. The page then says UNMEASURED with the
  cause (could-not-look-says-unmeasured).
- **a-review-record-in-a-new-shape.** A record field renamed under the page reads every file as never read. The page
  cannot tell a rename from no reviews. `selftest_code_review_status.py` guards the record's shape.
- **a-tests-file-that-reads-other-files.** The tests cache key holds the page, its tests file and the files the page
  names. A test result that depends on another file can be reused for up to 24 hours after that file changed.
- **two-runs-at-once.** The service is a oneshot, and systemd does not start a running oneshot again. A hand run
  during a timer run is outside: the last rename wins, and each page is whole.

## PROMISES (each one is owed a test of the same name)

- **every-file-has-one-state.** Each code file in the set (the extensions of `codebase_health.CODE_EXT`, minus the
  excluded trees) gets exactly one state: read-clean, dirty, never-read or unmeasured. The totals by files and by
  lines are the sums of those states. Tested by `t_every_file_has_one_state`.
- **read-clean-is-hash-equal.** A file reads read-clean only when `clean_state()` says CLEAN: its bytes equal the
  bytes of its last clean mark. A file edited since its mark, or reopened, reads dirty. A file with no record reads
  never-read. Tested by `t_read_clean_is_hash_equal`.
- **unreadable-file-is-unmeasured.** A file that is listed but cannot be read reads unmeasured, never dirty and never
  never-read. Tested by `t_unreadable_file_is_unmeasured`.
- **evidence-trees-excluded-and-said.** Files under an excluded tree (the retired `whittle/` and `infrastructure/whittle_claude/`,
  and the trees `codebase_health.EXCLUDE_PREFIXES` names) are not in the denominator. The page names each excluded
  tree and the count of listed files that it dropped. Tested by `t_evidence_trees_excluded_and_said`.
- **flagged-unmeasured-without-source.** While `code_review_status` has no list of flagged files, the FLAGGED
  legend reads UNMEASURED with its cause, and no file is painted flagged. Tested by
  `t_flagged_unmeasured_without_source`.
- **page-state-where-a-page-names-it.** A file that a boundary page names shows that page state (CLEAN, DIRTY or
  UNREADABLE, from `page_states()`) with a ring of that state's colour. A file that no page names shows no ring.
  Tested by `t_page_state_where_a_page_names_it`.
- **tests-cache-reused-only-when-unchanged.** A tests file runs again when the page, the tests file or a file the
  page names changed, or when its cached verdict is older than 24 hours. Otherwise the cached verdict is used, and
  the page says how old it is. Tested by `t_tests_cache_reused_only_when_unchanged`.
- **could-not-look-says-unmeasured.** When git or the review record cannot be read, the run still writes a page.
  That page reads UNMEASURED with the cause in place of every total, paints no file, and the run exits 3. It never
  shows 0 and never green. Tested by `t_could_not_look_says_unmeasured`.
- **stale-clone-says-unmeasured.** When the clone's last fetch (`.git/FETCH_HEAD`) is more than 1 hour old, or
  absent, every total reads UNMEASURED with the fetch age, because the record may be behind origin. Tested by
  `t_stale_clone_says_unmeasured`.
- **stale-page-says-so.** The page holds its build time. Opened more than 1 hour after that time, it shows a STALE
  banner and hides every total behind UNMEASURED. Tested by `t_stale_page_says_so`.
- **whole-page-or-none.** The page is written to a temporary file and renamed. A reader never sees half a page, and
  the page's modification time is the reading `rm-deadman` checks. Tested by `t_whole_page_or_none`.
- **no-network-no-model.** The page loads nothing from the network and the program calls no model. Tested by
  `t_no_network_no_model`.
- **click-a-cell-drills-in.** A click on a treemap cell opens the folder of that cell one level down (the tree is
  embedded in the page; no network), and a click on the breadcrumb comes back. Tested by `t_click_a_cell_drills_in`,
  which clicks in real headless Chrome (UNMEASURED where no Chrome is found).

## LIMITS

- **1 hour, the stale line for a page and for a clone fetch.** Danger: a timer that died leaves a page that looks
  current. The timer runs every 15 minutes, and the dispatch clone fetches every few minutes (measured 2026-11-19), so
  an age past 1 hour means a dead run. Evidence that runs die: `rm-deadman` exists because promises died.
- **24 hours, the tests cache age.** Danger: a tests verdict that a change to an unlisted file broke
  (a-tests-file-that-reads-other-files). Without the cache, each run would start every boundary tests file, about two
  minutes for 14 files (measured 2026-11-19, `code_review_status.TESTS_TIMEOUT_S` comment).

## LIFE CYCLES (a move not listed here is a defect)

- **a run:** list files (git fails: UNMEASURED page, exit 3) → read the record (fails: UNMEASURED page, exit 3) →
  read each file and its state → page states, with the tests cache → lay out the treemap → write the page atomically
  → exit 0.

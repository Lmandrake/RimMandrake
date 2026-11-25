# BOUNDARY: the owner's one view and the count of needs not filed anywhere, Design Version 0.1.0

Code: `src/RimMandrake/Utils/no_home.py` (all of it), `src/RimMandrake/Utils/probe_his_words.py` (`no_home_rows`,
`cards`; moved from `design/specs/2026-11-22-one-view-of-open-work/`), `owner_queue.one_view`, `owner_queue.ours`,
`owner_queue.write_view`/`read_view`/`fresh_view`, and their calls in `src/RimMandrake/Utils/maturation_now.py` (`live_facts`,
`needs_md`, `needs_html`).
Tests: `src/RimMandrake/Utils/selftest_owner_one_view.py` (each promise below has a test of its name). Acceptance:
`src/RimMandrake/rimflow/acceptance/step3_one_view_accept.py`.
Item: `RIMMANDRAKE_BUILD_ONE_OWNER_VIEW_NO_HOME_COUNT_BESIDE`, step 3 of
`design/specs/2026-11-22-coordination-every-agent-must-use/plan.md` (§Capture; "Your short needs you block on Fleet
Now stays, as a view of the same records by one rule (`owner_queue.is_his`), with not filed anywhere: N beside it").
Why: on 2026-11-23 Fleet Now listed 4 things for him and Maturation Now's "Needs Mandrake" listed 2, from two rules.

## ACCEPTS

- **sources-as-callables.** `no_home.count(sources)`: `{name: callable -> list of needs with no home}`.
- **his-ours-home.** `one_view(his, ours, home, fmt)`: `his` and `ours` are lists of `{item, q}` (`ours` also `age`);
  `home` is what `count` returns, or None when no reading exists.
- **the-conductor-window-transcripts.** `~/.claude/projects/-home-mandrake-rm-bench/*.jsonl` on Archmagi, only files
  written since the window began; and the ledger's events.

## DOES NOT SURVIVE

- **chat-counts-as-no-home.** The typed-words source counts every typed message of the Conductor window that no ledger
  event quotes or echoes (`probe_his_words.py`'s rule). Chat ("goodnight") counts too; 32 of 51 such messages in the
  probe of 2026-11-22 needed no home. The number is a count to read, not a list of owed work.
- **a-home-in-other-words.** A ruling written into the ledger in other words reads NO HOME (5 of 51 in that probe).
- **words-typed-elsewhere.** Words typed on SteveDesktop, the Desktop, the Laptop or another window are not read. The
  view names this source UNMEASURED, never 0.

## PROMISES

- **count-sums-the-readable-sources.** `count` returns `no_home` = the sum over sources that answered, `by_source` =
  each answering source's own number, `unmeasured` = the names of sources that raised, in the order given, and `names`
  (up to `NAMES_SHOWN` per source) of what each source found.
- **no-readable-source-is-none-never-zero.** With no source, or no source that answered, `no_home` is None. A source
  that answered with nothing is a measured 0.
- **an-unanswered-card-is-a-need.** `unanswered_cards(asked, answered)` returns the asked card ids with no answer, in
  the order asked. `probe_his_words.cards(since, until)` reads an `AskUserQuestion` call as asked, its tool result
  without an error as answered (a card a hook refused is not answered), and a card that is the session's last entry as
  still on screen (neither).
- **an-ended-run-with-no-later-act-is-a-need.** `ended_runs(records, items, last_event, now)` lists each run that ended
  in the window (`WINDOW_S`) on an item that is still open, carries no outcome check (the List Pipeline reads the end
  of a run on an item with a check), and has no act after the run ended (`list_pipeline.last_act`: a program's note
  about a run's end is not an act). A run whose item waits (a dated wait or a block) or that left a `LEFT OPEN:` note
  since it began gave its end a home, and is not counted; so did a Maturation Pipeline stage run (`RM_CONTROL_STAGE` on
  its record), whose end the Dispatch tick reads.
- **the-reading-is-shared-and-cached.** `no_home.reading(...)` answers from one file in the state directory while it is
  younger than `TTL_S`; else it counts, and writes the file. Each build within `TTL_S` reads the same file, so it shows the same count.
- **a-test-never-writes-the-shared-files.** A test process (`test_process.under_test`) never writes the real `view.json`
  or `no_home.json`: `write_view` returns the refusal and `reading` returns its count with `write_failed`. A test's own
  path or `RM_OWNER_VIEW_DIR` is written. Why: `selftest_maturation_now` builds the page live; on 2026-11-23 5:15 AM PST
  a publish's test run wrote the real view.
- **one-view-shows-his-ours-and-the-count.** `one_view` prints his rows (question and item), then our rows oldest first
  with their age, then `not filed anywhere: N` with each source's own number and the names of the sources not read.
  With `no_home` None it prints `not filed anywhere: UNMEASURED` and never `0`. `fmt="md"` returns Markdown lines;
  `fmt="html"` returns one line of HTML with no blank line in it (Typora).
- **not-his-before-its-turn.** `owner_queue.is_his` is False for an item with a dated wait ahead, or with a block on a
  ticket that is still open (`later`); `needs_you` names it under `later`. A date that cannot be read and a blocker that
  was never filed keep the row on his list. A Designer turn that waits on him is his whatever the wait. Tested in
  `src/RimMandrake/Utils/selftest_owner_queue.py`.
- **the-page-builds-from-one-view.** `maturation_now` (its "Needs Mandrake" block on MATURATION_DETAIL; the short block on
  MATURATION_NOW draws the same rows and counts) calls `owner_queue.one_view`. `maturation_now.live_facts` writes the
  view it built (`write_view`).
- **the-live-promise-follows-the-shared-view-file.** The item's `## live` line names the timer that builds Maturation
  Now and the `owner_view/view.json` it writes. The line holds when the timer is enabled and active and the file is
  within `VIEW_FRESH_S` (five minutes). A firing alone cannot prove that the view was written.
- **each-limit-names-its-danger.** `WINDOW_S`, `TTL_S`, `NAMES_SHOWN` and `VIEW_FRESH_S` are written beside their
  dangers.

## LIFE CYCLES

- **a Maturation Now build (every minute):** `live_facts` → `owner_queue.needs_you` → `owner_queue.ours` →
  `no_home.reading` (cached) → `write_view` → `needs_md`/`needs_html` call `one_view`.

Later lists beside this page: `polish.md` (none yet).

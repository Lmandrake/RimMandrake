# Temporary Work Bundle Monitor: the page of promises

Item: RIMMANDRAKE_BUILD_TEMPORARY_WORK_BUNDLE_MONITOR_DAILY. The owner decided it by card on 2026-11-25 about 11:10 AM
PST. The monitor is temporary: it lives only as long as the evaluation of Work Bundles needs
(`design/specs/2026-11-24-work-bundles/design.md`). If it stays useful, it is folded into Operations; it is not grown
here.

Code: `src/RimMandrake/rimflow/work_bundle_monitor.py` (one file, three parts). Judge brief:
`src/RimMandrake/rimflow/work_bundle_monitor_judge.md`. Report brief: `src/RimMandrake/rimflow/work_bundle_monitor_report.md`.
Tests: `src/RimMandrake/rimflow/selftest_work_bundle_monitor.py`; each promise below has a case of the same name.
Units: `src/RimMandrake/Utils/systemd/rm-work-bundle-monitor.{service,timer}`.

```
python3 src/RimMandrake/rimflow/work_bundle_monitor.py measure [--since ISO] [--until ISO] [--json]   part 1, no model
python3 src/RimMandrake/rimflow/work_bundle_monitor.py judge  [--since ISO] [--until ISO]            part 2, Sonnet per row
python3 src/RimMandrake/rimflow/work_bundle_monitor.py calibrate                                     part 2 on the 25 labelled rows
python3 src/RimMandrake/rimflow/work_bundle_monitor.py daily                                         parts 1, 2 and 3 (the timer)
```

## What it reads

| source | where | read for |
|---|---|---|
| detached run records | `<dispatcher>/detached/rm-detached-*.json` (one dot in the name) | the runs of the day: item, model, at, ended, tokens (`weighted_v2`, `role_launch.tokens_v2`), session |
| role run results | `<dispatcher>/roles/rm-role-*.json` | the session of a role run that set work down (transcript only; not in the share) |
| bundle records | `<dispatcher>/work_bundle/bundles/*.json` (`work_bundle.all_bundles`) | which units are bundle runs, the members, the pipeline, `live_runs` |
| bundle state files | `infrastructure/bundles/*.md` | named in the report as evidence; not parsed for numbers |
| the ledger | `infrastructure/state/ledger/events/*.jsonl` (`evidence_metrics.ledger_events`) | closes (with `role_unit`), filings and their `not_now`, notes, waits, reopen signals |
| stage records | `design/concepts/<Mod>/version/stage_record*.json`, field `moves` | forward and backward stage moves |
| live rows of a mod | `design/concepts/<Mod>/version/in_game/early_rows.jsonl`, `unrun.jsonl` | live checks run or recorded UNRUN for a bundle member |
| transcripts | `~/.claude/projects/*/<session>.jsonl` (`role_launch._transcript_files`) | tokens before the first edit; the judge's view of a run before a set-down |
| prices | `role_launch.MODEL_PRICES` through `role_launch.run_tokens` | every token figure, unit `weighted_v2` |

`<dispatcher>` is `doorbell.state_dir()` (`/mnt/d/ClaudeWork/rimmandrake/dispatcher`). The output folder is
`<agent storage>/rimmandrake/work_bundle_monitor/` (`agent_storage.py`): `reading_<date>.json`, `verdicts_<date>.jsonl`,
`report_<date>.md`, and `latest.json` (the page and the digest read this one file).

## Words

- A **bundle run** is a run whose unit is in a bundle record with two or more members. A **bundle of one** is a run
  whose unit is in a bundle record with one member. A **single-ticket run** is every other detached run. The share and
  the efficiency numbers compare bundle runs with single-ticket runs; a bundle of one is counted with the single-ticket
  runs and also shown on its own line.
- The **pipeline** of a run is the bundle record's `pipeline`. For a run that is not in a bundle: `maturation` when its
  item names a mod (`maturation_nonmod.classify`, the page's one rule), else `workshop`.
- A run's **closes** are the ledger closes whose `role_unit` is the run's unit, and, for a bundle run, every close of a
  member after the bundle's launch (a member can be closed by the outcome tick after the run ends).
- A close **stays closed** when, in the 3 days after it, no reopen signal names the item (`start`, `claim`,
  `implemented`, a `verify` fail after close, a `live` broken). A close younger than 3 days is **pending**, never
  counted as stayed or not stayed.
- A **set-down** is a `file` or `spawn` event whose `not_now` carries a `class` (an agent's words). A `not_now` that
  carries only `program` is a program filing, counted apart, never a set-down.
- A **backward move** is a stage move to an earlier stage, or to the same stage (a road back that opens a new cycle).
- The **role** of a run is `rm-role-<role>` for a role run; for a detached run, the first `roles/<name>.md` its brief
  names, else `detached helper`.

## The four answers

Every number is one of: a measured count (the instrument was shown able to see), `[]` none found, `could not look` with
its cause, or `failed` with its cause. A source that cannot be read prints `could not look: <cause>` and its numbers are
`UNMEASURED`; it never prints 0. A run with no token figure is counted as `unpriced`, never as 0 tokens.

## DOES NOT SURVIVE (not promised)

- **a-run-record-in-an-unknown-unit.** A run record whose `tokens` is in an unknown unit is unpriced, named in the
  reading.
- **a-model-without-prices.** A model that `MODEL_PRICES` does not hold raises `role_launch.UnknownModel`; it is caught
  per run, and the run is unpriced with the model named.
- **a-lost-transcript.** A transcript that was deleted, or that lives on another machine (a SteveDesktop helper): the
  tokens before the first edit read `could not look` for that run, and the judge is told the transcript could not be
  read.
- **a-corrupt-ledger-line.** It is skipped and counted (`delivery_metrics._jsonl`), not shown by name.
- **a-live-run-outside-the-bundle-tool.** A bundle's live check counts only when it went through `work_bundle.py live`
  or `maturation.py live-row`; a live run the worker made another way is not seen (the report of 2026-11-25 found one).
- **role-runs-in-the-share.** Role runs (`rm-role-*`) work no ticket list; they are not in the share or the efficiency
  numbers. Their set-downs are counted and judged.

## LIMITS

- `JUDGE_TIMEOUT_S` and `REPORT_TIMEOUT_S` are `time_budget.JUDGE_S` (class `judge`): a hang guard. Danger: a hung
  `claude -p` call stops the day's monitor. The 50 calibration calls took 14.3 s at most.
- `EXCERPT_CHARS`: the judge reads the last 60,000 characters of the run's acts before the set-down. Danger: a
  transcript of several MB would overflow the judge's context.
- `TimeoutStartSec` of the service: a hang guard; danger: a hung run stops the timer for good.

## The polish watch (item RIMMANDRAKE_WATCH_POLISH_FOR_NEW_BUGS_HE_FEARS_THE_OLD_NOISE)

The owner asked on 2026-11-25 (12:41 PM PST): "is the code becoming buggier due to the Polish inclusions?" Three
measures answer it, in part 1, with no model call. Each is in the reading (`born`, `regress`, `polish`, `lines`), the
report's day's numbers, the page section and the digest line.

| source | where | read for |
|---|---|---|
| commits | `git log --name-only` of the clone the unit runs from, back 5 days | subject, committer time, files |
| published shas | each bundle unit's transcript, the lines `PUBLISHED <sha>` (bundles of the last 5 days) | which commits a bundle made |
| nightly reds | `known_reds.log_path()` (`Transient/selftests_nightly.log` of the data clone), `known_reds.nights` | the red tests of each whole night |
| fresh reader records | `infrastructure/state/code_review/<SEAT>.jsonl` (clean marks), `code_review/flags/<SEAT>.jsonl` (flags) | the reader's verdict on a file after a change |

- **Tickets born per ticket closed** (measure 1). Born: the distinct ids of `file` and `spawn` events. Closed: the
  distinct ids of `close` events. The day reads the whole ledger in the window. Per kind (bundle, bundle of one,
  single) and per bundle, it reads the runs that ended in the window: born is the tickets their units filed
  (`role_unit`), closed is their closes (the same closes as the headline). Under 1 the list shrinks by closes; over 1
  the old ticket trap is back. A group with no close reads `no close`, never a ratio and never 0. Drops and supersedes
  are counted beside the day (`dropped`), not in the ratio: on 2026-11-22 and 2026-11-23 drops were 224 and 254 of the
  ids that left the list (measured 2026-11-25), so with drops in it the ratio would hide the trap behind a cleanup.
- **A bundle's commits.** A commit is the bundle's when one of its units printed it as `PUBLISHED <sha>`, or when it
  lies in the bundle's life (launch to 5 minutes after its last unit ended) and its subject names a member. A subject
  that starts `ledger:` or `chore(sync)` is never a change of the bundle.
- **A file a bundle changed** (measure 2) is any path of those commits except a tool's record: `infrastructure/state/`,
  `Transient/`, `*.jsonl`, `DEPLOYED_SHA`, `*.srchash`, `*.dll`. Its change time is the bundle's last commit on it.
- **The columns.** `polish`: one of the bundle's commits on the file has a subject that starts `polish:`. `no_polish`:
  none has. `before_rule`: a commit of that change predates the `polish:` rule (b39aa9f4e1, on origin/main 2026-11-25
  2:54 PM PST). A polish change then had no such subject, so the polish split of those days is NOT MEASURED: those
  files are never counted in `no_polish`, and never as 0 polish.
- **A regression of a file**: in the 3 days after the change, by a commit that is not the bundle's: a fix commit, a
  revert, a member ticket that reopened (`stayed`) and whose commit named the file, or a whole night that read red on
  the file or its `selftest_<stem>.py`. A fix commit has a fix word (fix, fixes, fixed, repair, repairs, repaired, mend,
  mends, mended, regression, broke, broken) among its lead words: the first three words of its item id, and the first
  six words of its description. A revert starts `Revert` or has a revert word among the same lead words. A polish
  commit is never a fix. The lead-word rule exists because "fix" and "reverting" anywhere in a long subject matched
  prose ("where it can fix", "undo by reverting this commit") in the first real reading (2026-11-25).
- **Ripe and pending.** A file younger than 3 days is `pending`: its events so far are shown, and it is never counted
  as clean. The comparison is the ripe day (the bundle changes of the 24 hours that ended 3 days ago); today is
  provisional. The first file changed after the rule ripens 2026-11-28 about 2:54 PM PST. The daily run's ripe day
  first holds such files on the run of 2026-11-29 6:30 AM PST (its ripe day is 2026-11-25 6:30 AM to 2026-11-26 6:30
  AM PST). Until then the `polish` and `no_polish` ripe counts read 0 of 0: no comparison yet, not a clean result.
- **Polish changes** (measure 3): the commits whose subject starts `polish:`, after the rule, in the window, split by
  in a bundle or not. Each is classed by the fresh reader's record on its files in the 3 days after it: `finding` (a
  code_review flag, or a later commit on the file whose subject names a fresh read), `read clean` (only a clean mark),
  `no recorded read`. A window that ends before the rule reads `not measured`; one that starts before it is `partial`
  and counted from the rule.
- **The probe.** Before a day after the rule may read 0 polish changes, `polish_probe` makes a throwaway repo with one
  `polish:` commit and one other commit and reads it with the same reader. If the reader does not see exactly that one
  polish commit, the polish count reads `could not look` with the cause.

**The lines.** Each line that makes the monitor speak, with the danger it guards and the evidence for its number
(`LINES` in the code; a crossed line owes the report's `## Lines crossed` section with its evidence, three repairs
and one recommended):

| line | number | danger | evidence |
|---|---|---|---|
| `bundle_born_per_closed` | bundle runs' born per closed over 1, on the day and the day before (born with no close counts as over) | the old ticket trap: bundle work, now with polish, files more tickets than it closes | 1 by arithmetic (over 1, more enter than leave by close). Two days: the Conductor's brief named "over 1 for two days"; one day of bundles is thin (2 bundle runs on 2026-11-25). The whole ledger read over 1 on 13 of the 25 days of 2026-11-01..25, so the day's ratio alone is no line. |
| `regress` | none | — | no evidence yet for a normal share of regressed files; the first ripe comparison is the run of 2026-11-29 |
| `polish` | none | — | no evidence yet; the `polish:` subject began 2026-11-25 2:54 PM PST |

**DOES NOT SURVIVE (not promised), the polish watch**
- **a-fix-that-names-no-fix-word.** A fix commit whose lead words hold no fix word is not seen; a commit whose lead
  words hold one but which fixes another fault is counted. Both columns share the error.
- **a-bundle-commit-on-another-machine.** A SteveDesktop bundle unit's transcript is not here: its commits are found
  only by a subject that names a member (`regress.transcripts_unread` counts the units).
- **a-red-of-a-test-with-another-name.** A nightly red counts on a file only when the red test is the file or its
  `selftest_<stem>.py`; the nightly checks FINISHED mods only.
- **an-unrecorded-fresh-read.** A fresh reader that recorded no mark, flag or "fresh read" commit reads `no recorded
  read`, not clean.

## PROMISES (each one is owed a test of the same name)

- **bundle-unit-is-bundle-run.** A unit listed in a bundle record with two or more members is a bundle run, whatever its
  brief says. A run with `RM_WORK_BUNDLE` in its env is the run of that bundle.
- **bundle-of-one-counts-single.** A unit listed in a bundle record with one member is a bundle of one, counted with the
  single-ticket runs in the efficiency numbers and shown on its own line in the share.
- **unreadable-record-not-zero.** A run record that cannot be parsed is named in `unreadable`; it adds no run, and its
  tokens are not 0.
- **missing-source-unmeasured.** A missing source folder makes the numbers that need it `could not look` with the cause,
  never 0.
- **unpriced-run-not-zero-tokens.** A run with no token figure is counted unpriced and stays out of every token sum.
- **reopened-close-not-stayed.** A close with a reopen signal within 3 days does not stay closed; a younger close without
  one is pending; only an older close without one stays.
- **headline-tokens-per-stayed-close.** The headline is the weighted tokens of the priced runs over the distinct tickets
  those runs closed that stayed closed; a ticket closed twice counts once, by its worst close; the reopened tickets are
  named; it reads `pending` while any of those tickets is pending, and the count of runs is beside it.
- **program-filing-not-setdown.** A `not_now` that carries only `program` is a program filing, counted apart, never a
  set-down.
- **setdowns-by-class-and-role.** Set-downs are counted by their class and by the role of the run that filed them.
- **backward-moves-classed.** A move to an earlier or the same stage is a backward move; a move to a later stage is
  forward.
- **tokens-before-first-edit.** The tokens before the first edit sum the main-thread turns before the first Edit, Write
  or NotebookEdit; a run with no edit reads `no edit`, not 0.
- **bundle-live-ran-and-unrun.** A bundle's live work counts its live checks run and its UNRUN records apart.
- **judge-failure-could-not-judge.** A judge call that fails, or that returns no verdict line, reads COULD NOT JUDGE with
  the cause.
- **judge-told-no-spend.** The judge's and the report's prompts carry no spend figure of the monitor, and the call passes
  no budget flag.
- **page-section-no-tokens.** The page section shows no token or spend figure, and names the report's full Windows path;
  an unreadable reading says could not look.
- **digest-line-blind.** The digest line carries the counts and the report as a handle through the blind page; an
  unreadable monitor reads UNMEASURED.
- **baseline-same-system-before-first-bundle.** The baseline of a bundle system takes the single-ticket runs that
  ended in the 14 days before its first bundle and whose item is of that system: its home (the ledger's `home` events)
  is the system, or, for `mod:X`, its item names the mod.
- **report-needs-four-sections.** A report that lacks one of its four sections is not written as the report; the
  failure is written as `report_<date>.FAILED.md` and in `latest.json`. Only a written report renews
  `report_newest.md`, the one fixed reading of the item's live promise.
- **polish-then-fix-one-regression.** A polish commit of a bundle on a file, then a later fix commit by another run on
  that file within 3 days, counts as exactly one regressed file in the `polish` column.
- **no-polish-fix-counts-no-polish.** A file a bundle changed with no polish commit, then fixed later within 3 days,
  counts in the `no_polish` column.
- **regression-kinds-and-window.** A revert, a reopened member whose commit named the file and a nightly red of the
  file's selftest each count; a fix after 3 days, a ledger commit and "fix" or "reverting" in late prose do not; a run
  record (`*.jsonl`, ledger shard) is no file; a sha the unit printed as PUBLISHED is the bundle's; a file younger than
  3 days is pending, never clean.
- **before-rule-not-measured.** A bundle change before the `polish:` rule is in the `before_rule` column, never in
  `no_polish`; the polish count of a window that ends before the rule reads `not measured`.
- **polish-zero-needs-probe.** A window after the rule with no polish commit reads 0 only when the probe saw its one
  planted `polish:` commit; a failed probe reads could not look.
- **polish-findings-from-reader.** A polish change with a flag or a later "fresh read" commit on its file after it reads
  finding; with only a clean mark after it, read clean; with neither, no recorded read.
- **born-per-closed-per-bundle-and-day.** A bundle that files 3 tickets and closes 2 reads 1.5; the day reads born over
  closed of the whole ledger; a group with no close reads `no close`; an unread ledger reads could not look.
- **born-line-two-days.** The born line crosses only when bundle runs' born per closed is over 1 on the day and on the
  day before; the regress and polish measures draw no line.
- **lines-crossed-section.** A report whose reading has a crossed line, and that lacks `## Lines crossed`, is not
  written as the report.
- **polish-watch-on-page-and-digest.** The page shows the three measures and the line, with no token figure; the digest
  fields carry their counts, and the blind digest line renders them and the crossed line.

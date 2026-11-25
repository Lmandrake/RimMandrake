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

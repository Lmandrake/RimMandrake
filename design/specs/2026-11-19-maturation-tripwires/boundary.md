# BOUNDARY: the tuning tripwires T1 and T2 (maturation.py next, certificate --run), Design Version 0.1.0

Code: `src/RimMandrake/rimflow/maturation.py` (`number_only_constants`, `tripwire`, the `next` and `certificate`
commands), `src/RimMandrake/rimflow/check_margin.py` (the line a check prints), `src/RimMandrake/rimflow/judge_certificate.py`
(`run_offline` keeps the lines; `margin_rows`). Items `RIMMANDRAKE_FLAG_NUMBER_ONLY_DIFFS_IN_MATURATION_NEXT` (T1) and
`RIMMANDRAKE_LIST_THINNEST_MARGINS_IN_CERTIFICATE_RUN` (T2); design: the owner's order of 2026-11-16, §3 of
`D:\ClaudeWork\rimmandrake\conductor\role_prompt_upgrades_20261116.md`. Neither tripwire refuses anything: each prints a
fact in front of the builder. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_maturation_tripwires.py`, each watched failing on the base `09fffd6665`.

## ACCEPTS (the only inputs these parts are built for)

- **a-unified-git-diff.** T1 reads `git diff` text (unified, any context size). Its run's diff is
  `git diff <base> -- src/RimMandrake/<Mod> design/concepts/<Mod>` in the run's clone, where `<base>` is the last
  origin/main commit before the run began (`RM_DETACHED_UNIT`'s record `at`); `next --diff-file` gives one by hand.
- **one-run-per-mod.** Since `RIMMANDRAKE_GUARD_HAND_LAUNCH_AGAINST_DISPATCHER_TWIN_RUN`, one live run works a mod's
  stage at a time, so the mod's files changed since the run began are that run's.
- **a-margin-line.** T2 reads lines a check prints through `check_margin.line`:
  `MARGIN worst=<number> limit=<number> cases=<whole number>[ name=<text>]`, anywhere in its stdout.

## DOES NOT SURVIVE (not handled)

- **another-writer-on-the-mod-during-a-run.** A hand commit to the mod's files while a run works it is read as the
  run's own diff.
- **a-number-change-inside-a-logic-line.** A line whose only change is a number counts as a number change even when
  the number is a loop bound or an index, not a tuning constant: the reader sees text, not meaning.
- **a-check-that-prints-its-margin-another-way.** A check that prints worst and limit in its own words is "margin not
  printed" until it calls `check_margin.line`.

## PROMISES (each one is owed a test of the same name)

- **number-only-diff-is-named.** `number_only_constants(diff)` gives the sorted `file:NAME` keys a diff changes when
  every changed line differs from its pair only in numeric literals; `None` when any change is more than numbers (a
  line added or removed alone, a word changed); `[]` for an empty diff. NAME is the identifier before `=` or `:`, else
  the XML tag, else the line number.
- **tripwire-counts-the-item-history.** `tripwire(diff, item, hist)` gives, for a number-only diff, the constants, the
  count of number-only diffs this item has had on any of the same constants (this one included, each diff counted once
  however often `next` reads it), and the note "this diff changes only numbers in N constants; this item has had M such
  diffs on the same check. Map where each bar holds before the next one." A diff that changes logic gives no note and
  records nothing.
- **next-prints-the-tripwire-and-never-refuses.** `maturation.py next <Mod> --diff-file F --item I` prints the note
  when the diff is number-only, prints nothing about it otherwise, and exits as `next` exits without it. A diff it
  could not read prints "tuning tripwire: diff UNMEASURED (<cause>)", never as no note.
- **margin-line-round-trips.** `check_margin.line(worst, limit, cases)` prints one line that `check_margin.parse` reads
  back to the same three values; a line with a non-number or a missing field is not read as a margin.
- **certificate-run-lists-thinnest-margins-first.** `certificate --run` lists every offline test that printed a margin,
  thinnest first (|worst - limit| / |limit|), each with its worst, limit and cases, then the tests that printed none
  as "margin not printed". `run_offline` keeps each test's margin lines on its `runs_today` stamp (`margins`, `[]` when
  it printed none). The certificate's verdict and exit code are the same with or without these lines.

Later lists beside this page: `polish.md` (none yet); `next_version.md` (none yet).

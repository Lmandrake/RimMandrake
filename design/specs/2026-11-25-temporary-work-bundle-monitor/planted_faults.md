# Planted faults: each turned its selftest case red (measured 2026-11-25)

Each fault was a one-place change to `src/RimMandrake/rimflow/work_bundle_monitor.py`. With the fault in place,
`python3 src/RimMandrake/rimflow/selftest_work_bundle_monitor.py` exited 1 with the cases named; with the file restored
(byte-compared to the original), it exits 0 (17 promises, 0 failed). The harness was a small script that replaced one
string at a time; the before and after strings are given here.

| fault | what was changed | red cases |
|---|---|---|
| a bundle run counted as a single-ticket run (brief) | `kind_of` returns `"single"` | bundle-unit-is-bundle-run (3 checks) |
| an unreadable run record printed as 0 (brief) | `read_runs` adds an unparseable record as a run of 0 tokens | unreadable-record-not-zero (3 checks) |
| a ticket that reopened counted as a ticket that stays closed (brief) | `stayed` never returns `reopened` | reopened-close-not-stayed (2), headline-tokens-per-stayed-close (1) |
| a missing source read as zero runs | `read_runs` returns `src({})` for a missing folder | missing-source-unmeasured (2) |
| an unpriced run summed as 0 tokens | `kind_numbers` prices a run with no figure at 0 | unpriced-run-not-zero-tokens (3) |
| a program filing counted as a set-down | `setdowns` keeps a `not_now` with only `program` | program-filing-not-setdown |
| a same-stage road back counted forward | `move_kind` uses `>=` | backward-moves-classed (2) |
| a run with no edit read as 0 tokens | `first_edit_tokens` returns 0 for no edit | tokens-before-first-edit |
| a failed judge call read as SINCERE | `judge_row` returns SINCERE on a call error | judge-failure-could-not-judge |
| a token figure on the page | `page_md` prints a token figure in the share table | page-section-no-tokens |
| a report with a missing section written | `report_ok` checks only the first section | report-needs-four-sections (2) |
| the judge's spend in the report prompt | `report_prompt` keeps each verdict's `tokens` | judge-told-no-spend |
| a bundle UNRUN record counted as a live run | `live_work` counts every live run as run | bundle-live-ran-and-unrun |
| every set-down read as one role | `role_of` drops the Maturation stage | setdowns-by-class-and-role |
| the monitor's spend carried into the digest fields | `digest_fields` adds `monitor_tokens` | digest-line-blind |
| a failed report renews the newest copy | `daily` writes `report_newest.md` before the failure check | report-needs-four-sections (1) |
| a home's past runs not read | `baseline` matches only by mod name | baseline-same-system-before-first-bundle |
| a ticket closed twice counted twice | `kind_numbers` keys the closes by close event, not by ticket | headline-tokens-per-stayed-close |
| a lost transcript shown as no acts | `judge_row` passes an empty acts text | judge-failure-could-not-judge (seen red before the fix) |

## The polish watch (item RIMMANDRAKE_WATCH_POLISH_FOR_NEW_BUGS_HE_FEARS_THE_OLD_NOISE, measured 2026-11-25)

The harness is `polish_watch_mutants.py` in this folder (run it from the clone root). It mutates
`work_bundle_monitor.py` or `contracts/blind.py` in place, one string at a time, runs the selftest with no bytecode,
restores the file and byte-compares it. A row counts as RED only when the selftest exits 1 with a FAIL line of the
named promise. The unmutated control was green before and after. Result: 23 of 23 red on their promise.

| fault | red promise |
|---|---|
| the polish column lost (every file reads no_polish) | polish-then-fix-one-regression |
| fixes seen only on polished files | no-polish-fix-counts-no-polish |
| the window 5 days, not 3 | regression-kinds-and-window |
| a revert ignored | regression-kinds-and-window |
| a nightly red of the file's selftest not matched | regression-kinds-and-window |
| a reopened member ignored | regression-kinds-and-window |
| a pending file read as ripe | regression-kinds-and-window |
| "fix" anywhere in the subject (the first rule, before the real reading) | regression-kinds-and-window |
| a run record (`*.jsonl`) read as a file | regression-kinds-and-window |
| the PUBLISHED shas ignored | regression-kinds-and-window |
| a before-rule change put in no_polish | before-rule-not-measured |
| a pre-rule day read as 0 polish changes | before-rule-not-measured |
| the probe skipped | polish-zero-needs-probe |
| the probe accepts a blind reader | polish-zero-needs-probe |
| the reader's flag ignored | polish-findings-from-reader |
| a clean mark from before the change counted | polish-findings-from-reader |
| no close read as 0 | born-per-closed-per-bundle-and-day |
| a bundle's born read as the day's born | born-per-closed-per-bundle-and-day |
| the born line crossed on one day | born-line-two-days |
| the lines section not owed | lines-crossed-section |
| the page drops the watch | polish-watch-on-page-and-digest |
| the digest fields drop born | polish-watch-on-page-and-digest |
| the blind digest line drops the crossed line | polish-watch-on-page-and-digest |

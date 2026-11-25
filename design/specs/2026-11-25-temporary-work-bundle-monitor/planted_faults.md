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

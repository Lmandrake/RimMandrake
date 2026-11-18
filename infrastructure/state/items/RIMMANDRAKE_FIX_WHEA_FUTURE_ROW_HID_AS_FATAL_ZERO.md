# RIMMANDRAKE_FIX_WHEA_FUTURE_ROW_HID_AS_FATAL_ZERO

## spec
Split from `OPS_WATCH_FIX_BLIND_READINGS_STILL_ZERO` (Codex round 4, claim 3), verified red on 2d65550ae2.
`ops_watch.whea_reading()` keeps only rows with `now - DAY <= t <= now + 300`. A complete query whose row is dated
more than 5 min ahead of this clock (Windows' clock ahead of WSL's) silently drops that row, so a fatal WHEA 18 reads
`disk.whea_severe_24h` MEASURED 0 and `disk.whea_blind` 0. Fix: a row past the 300 s skew allowance means the two
clocks disagree, so the 24 h window cannot be placed: the reading is blind (both counts UNMEASURED, `disk.whea_blind`
1, cause naming the row's lead), never a measured count.

Addendum (Codex review of the fix, 2026-11-18, `D:\ClaudeWork\rimmandrake\scratch\ops_watch_whea_review_20261118\codex_review.md`): three more inputs in the same reader read as a
zero or crashed, each watched red: two END lines (`END|1`, `END|0`) read MEASURED 0; `END|²` passed `isdigit()` then
crashed `int()`; an undecodable byte raised UnicodeDecodeError past the OSError handler. All three now read blind.
Left as advice (not a flaw against a promise here): a Level 4 WHEA row counts as corrected though the comment says
corrected = Level 3.

## refs
file: src/RimMandrake/Utils/ops_watch.py
file: src/RimMandrake/Utils/selftest_ops_watch_whea.py

## verify
Acceptance test: `python3 src/RimMandrake/Utils/selftest_ops_watch_whea.py` exits 0 with 56 PASS, 0 FAIL.
Watched red on base 2d65550ae2 (throwaway `git clone --shared`, test file only): 51 PASS, 2 FAIL
(`a fatal row 10 min ahead: severe is not a measured 0`; `... corrected UNMEASURED too, whea_blind 1 naming the clock`).

## criteria
- a row dated more than 300 s ahead makes both counts UNMEASURED and `disk.whea_blind` MEASURED 1, cause names "ahead";
- a row within 300 s ahead still counts (the existing edge case stays green);
- a second END line, a non-ASCII digit in END, or undecodable output reads blind, never 0 and never a crash.

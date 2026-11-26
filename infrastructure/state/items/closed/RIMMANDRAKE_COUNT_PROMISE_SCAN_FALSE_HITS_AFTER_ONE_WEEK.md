## spec
Measure promise_scan's false-positive rate over the first week of real Conductor replies (from 2026-11-18, when the advisory notice went live with 0c4cac7a1d), as RIMMANDRAKE_SHOW_UNTRACKED_PROMISES_NEXT_PROMPT_FILE_AT_KILL's item asked: "Record the false-positive count over the first week of real replies on this item: the blocking decision waits on that number" (spec design/specs/2026-11-15-conductor-restart-loses-nothing.md §3 E2: blocking at the Stop hook is a later decision, taken only after a week's false-positive count).

Early reading, 2026-11-18 (backtest, not the live week): the 12 newest Conductor transcripts held 53 final replies; 25 would have drawn a notice, 36 hits in all. A random 25 of the hits read by the building run: about 2 false (a markdown table row matching "not launched"; a negative commitment "I will not release …"), the rest real deferred acts, many routine ("I will report when it lands"). Evidence: D:\ClaudeWork\rimmandrake\lane_c\promise_scan_backtest_20261118.txt. Advice from that read, not built: skip markdown table rows; consider whether "I will report when …" about a running helper is noise the window should not have to file.

## verify
After 2026-11-25: rerun the backtest over that week's Conductor transcripts (~/.claude/projects/-home-mandrake-rm-bench/*.jsonl), read every hit (or a stated random sample), and record hits, false hits and the rate on this item as a note.

## criteria
- A1: a note on this item names the week, the number of replies, hits, false hits and the rate, with the evidence path.
- A2: the blocking decision is put to the Conductor with that number; nothing blocks a turn before it.

## acceptance
Acceptance test: none, a measurement over a week of real replies followed by a decision that is the Conductor's (spec §3 E2).

# Why the Conductor window reads a run's out.json by hand after a wake (first step of `run_result`)

Item RIMMANDRAKE_FIND_WHY_WAKES_GET_460_HAND_READS_FIRST. Written 2026-11-27 by a work-bundle helper. Candidate 1 of
`one_page.md` (section 1). **Answer: the old wake told the window to read the file.** Before commit `c45e242f32`
(2026-11-23 9:31 PM PST) the wake gave only a path and the words "read each result". After it, hand reads fell from
about 96 a day to about 2 a day. The 460 are almost all from before that commit.

## What was measured
- Source: the Conductor transcripts on Archmagi, `~/.claude/projects/-home-mandrake-rm-bench/*.jsonl`, read over
  `ssh archmagi-wsl` on 2026-11-27 at 11:15 AM PST. All work files are in Archmagi scratch
  `D:\ClaudeWork\scratch\why460\` (no repo on Archmagi was written).
- The hand-read filter is the same as `measure/rows.py`: a Bash call that runs inline Python (`-c`, `<<` or `-`),
  names `.out.json`, and takes the `result` field. `measure/why_sample.py` finds each such call in its transcript,
  walks back to the last thing that came to the window (a turn, or a wake that came while the window was busy), and
  gives a class from what it finds. It is tested on a fake transcript with one read per class
  (`measure/why_fixture.py`, 9 of 9 classed as planted).
- **405, not 460, in the 7 days.** The 7 days of `one_page.md` are 2026-11-19 5:46 PM to 2026-11-26 5:46 PM PST. In
  that span there are 405 hand reads in 24 windows [measured]. The 460 took every call of each session that changed in
  the last 7.2 days (`extract.py`, mtime filter), so it also took calls from before the span. Over all transcripts
  (2026-11-18 12:58 PM to 2026-11-27 9:57 AM PST) there are 603 hand reads in 37 windows [measured].
- **The sample.** The 405 reads, in time order, are cut into 20 bins of equal count. One read is drawn from each bin
  (seed 1126); a window that is not yet drawn is preferred. Result: 20 reads, 17 windows, 6 days. Because the bins
  are equal in count, the sample follows the reads, and 19 of 20 fall before `c45e242f32`.
- For each of the 20, I read the wake text, the window's words between the wake and the call, and the call.

## The 20 calls
Transcript = `<window>.jsonl` in the folder above. "Old wake" = the wake before `c45e242f32`: one line per run with
"full result: <path>", under the head "read each result, act on it". "Reads" = the units that the call opens.

| # | date (PST) | window | wake line / call line | class | one line of evidence |
|---|---|---|---|---|---|
| 1 | 11-19 20:01 | 66b3b472 | 792 / 795 | A | old wake, 1 run; call prints `result[:4200]` of that run, nothing else |
| 2 | 11-20 00:14 | 18dca154 | 424 / 427 | A | old wake, 1 run; `result[:1800]`, then `seat_restart.py status` |
| 3 | 11-20 17:48 | f0f57f39 | 251 / 253 | A | old wake, 1 run; `result[:4500]`, then `./pipe show` |
| 4 | 11-20 23:14 | 8c581a3a | 1372 / 1382 | A | old wake, 1 run; `result[:2800]`, then `./pipe show` |
| 5 | 11-21 05:14 | 8678bb86 | 638 / 640 | A | old wake, 2 runs; reads both, `[:3500]` each |
| 6 | 11-21 13:35 | ca99be1a | 254 / 264 | A | old wake, 1 run; `result[:3500]` |
| 7 | 11-21 20:12 | 59f22db9 | 382 / 384 | A | old wake, 1 run; `result[:3800]` |
| 8 | 11-22 02:45 | 2c5e1f2d | 666 / 668 | A | old wake queued mid-turn (line 666), during an owner question |
| 9 | 11-22 08:38 | 3907fdef | 115 / 117 | A | old wake, 1 run; `result[:6000]` |
| 10 | 11-22 16:16 | 5e50f2e0 | 317 / 319 | A | old wake, 3 runs; one loop reads all 3 |
| 11 | 11-22 18:54 | e8ddbc2c | 367 / 369 | A | old wake, 1 run; `result[:3000]` |
| 12 | 11-23 00:25 | 933031a2 | 346 / 356 | A | old wake, 1 run; `result[:3000]` |
| 13 | 11-23 03:13 | 933031a2 | 1115 / 1117 | A | old wake, 1 run; `result[:3300]` |
| 14 | 11-23 05:28 | 30086451 | 216 / 218 | A | old wake, 1 run; `result[:5000]` |
| 15 | 11-23 07:32 | 30086451 | 781 / 791 | A | old wake, 1 run; `result[:2600]` |
| 16 | 11-23 11:15 | a5410a27 | 675 / 677 | A | old wake, 1 run; `result[:4000]`, then `./pipe show` |
| 17 | 11-23 14:14 | ef311d37 | 364 / 366 | A | old wake, 4 runs; one loop reads all 4 |
| 18 | 11-23 15:46 | ef311d37 | 907 / 909 | A | old wake, 1 run; `result[:3200]` |
| 19 | 11-23 18:56 | 6adf1d60 | 145 / 147 | A | old wake, 1 run; `result[:5000]` and `subtype`, `is_error` |
| 20 | 11-24 17:52 | 6f26a88c | 503 / 607 | B | new wake had 1 run; read 2 others, whose wake came later (713) |

Classes: **A** = the wake did not carry the result (old wake). **B** = a read of a different run than the wake carried.

## Class counts [measured]
- **Over the 20:** A 19, B 1. Read after a compaction or restart 0. A field that the wake leaves out 0 (every call
  takes `result`; #19 also takes `subtype` and `is_error`). A re-check of a claim 0. Habit (a read of a run that the new
  wake already carried) 0. In each of the 19 A rows the call opens exactly the runs that the wake named.
- **Over all 405** (same classes, by `why_sample.py`): A 393, a read with no wake before it 10, B 2.
- **Over all 603:** A 579, no wake before it 21, B 3.
- **Before and after `c45e242f32`, all transcripts:** 595 reads in about 5.4 days before; 8 reads in about 3.5 days
  after. Inside the 7 days: 399 reads in 4.16 days before (about 96 a day); 6 reads in 2.84 days after (about 2 a day).
- **The 8 reads after the change, each read by hand:**
  - 3 of class B. In 6f26a88c (line 607) and b165fcb3 (line 908) the window read a run that its wake gave only later
    (lines 713 and 955). In 6fa1d8fe (line 139) the run's wake went to another window, 8c4a5e56.
  - 1 of class A: 6adf1d60 line 1526, 2026-11-23 10:01 PM PST, 30 min after the commit, still got an old wake. The hook
    ran code from before the commit for that time.
  - 4 with no wake before them: two owner questions (860b300c line 465 "I thought I accepted the fire hawk already";
    4993e64a line 356, after an owner image); a fresh window after a restart (4e2ccb12 line 115); one read after a
    background task note that names no run (22539746 line 485).
- **The reads did not move to another route.** Calls that name `.out.json`: 424 of 2,509 calls before; 30 of 3,378
  after (23 inline Python, 3 Agent, 2 Write) [measured]. `detached_helper.py status/show/tail` calls went from 115 to
  235; those calls show run state, not the result text, so they are not hand reads of the result.

## What the 20 cannot tell
- **The window's reasons in its own words.** In all 20, the window wrote no text between the wake and the call, and the
  transcript keeps each thinking block as empty text with a signature [measured: `why460/between.py` over the 20].
  So each class comes from the wake text and the call, not from the window's words.
- **The world after the change.** Only 1 of the 20 is after `c45e242f32`, because the sample follows the reads. The 8
  reads after the change are therefore all read by hand above; that is a full count, not a sample.
- **Whether a short result made the window read.** No new-wake read of a carried run was found, so no case shows a
  wake that cut the text short.
- **An earlier count by this tool was wrong.** Before 2026-11-27 11:40 AM, `why_sample.py` saw only wakes that came as
  a turn. A wake that came while the window was busy (a queued attachment) was missed, and 50 of the 405 reads were
  put in "no wake before it". The fix and a fixture case for it are in this change. Other ways a wake can come that
  the tool does not know are possible [guess ~10%].

## Build recommendation for run_result
- **The read part: do not build it.** The wake fix (`c45e242f32`) already removed the hand reads: from about 96 a day
  to about 2 a day [measured]. Of the 8 left, none is a read that a `run_result` reader would stop: 3 read a run
  before its wake came, 4 came with no wake, 1 was the old code. A reader would save at most about 2 calls a day
  [guess ~85% that it saves less than 1 a day once the hook lag case is gone].
- **The claim check: this evidence does not ask for it.** No call of the 20, and none of the 8 after the change,
  re-checks a claim in the result. If the claim check is built, it must stand on other evidence (for example, a run
  that claimed a pass that was false), not on these reads [guess ~70% that it is worth building on its own merits].
- **A wake fix instead: none needed for these reads.** The 3 "read before its wake came" reads happen because a busy
  window gets the wake only when it stops; the window then reads the file to act sooner. That is a choice, not a
  fault. A wake fix would save about 1 call a day [guess].
- **The numbers in `one_page.md` for candidate 1 are from before the fix.** 460 a week was the old wake; the rate now
  is about 15 a week [measured: 6 in 2.84 days, 8 in 3.52 days]. The parent should rank candidate 1 again on that rate.

## To rerun (on Archmagi, about 2 min)
```
mkdir -p /mnt/d/ClaudeWork/scratch/why460/measure   # copy measure/*.py here first (scp from a clone)
cd /mnt/d/ClaudeWork/scratch/why460/measure; export SCAN_DIR=/mnt/d/ClaudeWork/scratch/why460
SCAN_DAYS=9 python3 -I extract.py                      # writes calls.jsonl, turns.jsonl into SCAN_DIR
python3 -I why_sample.py --n 20 --seed 1126 > ../why2.txt                  # the 7 days: counts + 20 prints
python3 -I why_sample.py --from-utc 2026-11-10T00:00:00+00:00 --to-utc 2026-11-29T00:00:00+00:00 --json ../all.json
```
Outputs of this run on Archmagi: `D:\ClaudeWork\scratch\why460\why2.txt` (the 20 prints) and `all.json` (all 603).
Fixture test: `python3 -I why_fixture.py <home>`, then the two commands in its docstring; it must print 9 classed
reads, `wake_without_result` twice.

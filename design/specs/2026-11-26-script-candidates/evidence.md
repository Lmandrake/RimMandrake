# Evidence for one_page.md: what the Conductor window does by hand (7 days to 2026-11-26 5:46 PM PST)

Item RIMMANDRAKE_SCAN_MODEL_CHORES_FOR_SCRIPTS_HE_ASKED_MORE. No script of the candidates is built. The only code here
measures. Rerun it:

    cd design/specs/2026-11-26-script-candidates/measure
    SCAN_DIR=<scratch dir> python3 -I extract.py     # 50 Conductor transcripts -> calls.jsonl, turns.jsonl (about 1 min)
    SCAN_DIR=<scratch dir> python3 -I rows.py        # every row below

## What was read
- `~/.claude/projects/-home-mandrake-rm-bench/*.jsonl`: the 50 sessions that carry the agent name CONDUCTOR and were
  written in the 7.2 days to now (other named sessions in the folder are not read). 5303 tool calls, 1508 turns.
  Window time of those sessions: 168.7 h wall, because windows chain end to end. Of that, 43.5 h are tool waits (15.2 h
  of them are AskUserQuestion: the owner thinking, not model time).
- `D:\ClaudeWork\rimmandrake\dispatcher\detached\*.json` and `*.out.json`: 1018 run records of the same 7.2 days (934
  hold an out.json). `cost_usd` fields are list dollars: a figure from them is `≈`, not weighted tokens (UNMEASURED in
  weighted tokens: the run records hold no per-field usage that this scan read).
- `D:\ClaudeWork\rimmandrake\conductor\*_brief_*.md`: 58 briefs of the 7.5 days (the whole folder holds 62).
- Not read: `D:\ClaudeWork\rimmandrake\conductor\log.md` (3.8 MB; its lines are written by the tools, not by the model:
  no repeated act of the model starts from it).

## Definitions (the instrument; read before you trust a number)
- **wall** = seconds from a tool call to its result: the time the window waited. **gen** = seconds from the previous
  event to the tool call: what the model took to think and write that call. gen is a lower bound: a final text reply with
  no tool call is not in it. Total gen over all calls = 7.6 h; all assistant turns = 15.9 h (measured apart).
- A compound Bash command that names two tools counts once for each tool it names, so category sums overlap. A row says
  when it is a bound.
- An episode is one turn plus the calls until the next turn. Turn kinds: `wake_run_end` (the Stop hook of
  `src/RimMandrake/rimflow/run_end_wake.py` returns a finished run to the window: 763), `human` (396), `task_notification`
  (187), `restart` (a fresh Conductor window, 37).
- The instrument can see: it found the 49 launches that the guiding-prose check of `guiding_prose.py` returned before their start (the returned text is in the results) and
  the 6 closes that were refused. A category count of 0 means measured 0 only where the row says "measured".

## The twelve guesses, one line each (rows below carry the numbers)
| # | guess | measured | where in the rows |
|---|---|---|---|
| 1 | ruling carried into rules | 68 owner turns in 7 days; median 5.4 min wall, 13 calls | section owner ruling |
| 2 | brief written by hand | 58 briefs; 13% to 21% of their lines repeat | section helper brief |
| 3 | launch returned by prose check | 49 returned of 196 launch attempts; 20 relaunched unchanged, 19 after an edit | section prose check |
| 4 | card answers noted by hand | 53 cards, 150 questions, 48 `--by-card` commands | section card answers |
| 5 | start of a window | 37 windows; 138,237 chars read in the first 14 calls; 2.2% exact repeat | sections start of a window, EXTRA wake |
| 6 | waiting for a launch or a publish | 198 landings, median 47 s; 935 state polls | sections waiting, NEW kinds |
| 7 | claims in a worker report | 763 wakes; 186 wake episodes with a sha or show check | section worker's report |
| 8 | reading an old ask or ticket | 435 `show` calls; purpose UNMEASURED | section old tickets |
| 9 | many tickets one by one | 0 episodes with 5 or more hand acts; bulk goes to helpers | section many tickets |
| 10 | search for opposite lines | 540 greps inside ruling turns; intent UNMEASURED | sections owner ruling, searching opposite |
| 11 | sizing a spend cap | 16 runs ended at the cap; 14 of 16 caps below the verb's p90 | section spend cap |
| 12 | close refused, second form | 6 of 64 closes refused; 5 redone in 8 to 33 s | section closing an item |

## Caveats that change a reading
- Owner ruling section: the span of a turn holds other work too (an upper bound). The greps in a turn are not all contradiction hunts.
- Waiting section: only 71 of the 198 publish commands that printed PUBLISHED name their paths in a way the scan could class (the "EXTRA publish" section of rows.py); the md-only median
  (46 s, n=13) sits between ledger-only (32 s, n=49) and code (93 s, n=9): too few to say that the publish check on code is the cause.
- Worker's report section: a wake already carries the run's whole last message (measured on one wake of 2026-11-26 7:11 PM: 890-char result,
  whole in the wake text). Yet 460 hand reads of a run's out.json result exist, 416 of them within 10 minutes after a
  wake. Why the window reads again: UNMEASURED (guess ~50%: the result is read again after a restart or for the cost and
  end state fields).
- Old tickets and searching sections: the call does not say why it was made. Not guessed.
- Spend rows are list dollars from `total_cost_usd`, marked `≈`.

## Rows (output of rows.py, run 2026-11-26 5:46 PM PST)

```

=== BASE: what the window did in the 7 days
conductor sessions 50 tool calls 5303
episodes by kind Counter({'wake_run_end': 763, 'human': 396, 'task_notification': 187, 'None': 114, 'restart': 37, 'sdk': 7, 'peer': 5, 'stop_hook_other': 1})
tool wait h (all calls) 43.5 | of which AskUserQuestion (owner thinking) h 15.2
model gen h (calls only) 7.6

=== G1 owner ruling carried into the rules
owner turns with --owner-said AND a rule-file touch: 68
  span min: median 5.4 p90 32.5 | calls: median 13 | model gen min: median 1.3 sum 113
  sum of those spans h (an upper bound: a turn also holds other work): 14.7
  turns with >=1 grep/owner_rulings search inside: 65 greps total 540 gen min on them 48.0

=== G2 helper brief written by hand
brief files written in the 7 days 58 median bytes 6034
  lines (>=25 chars) that appear in >=2 briefs: 816 of 3880 = 21%
  lines (>=25 chars) that appear in >=3 briefs: 616 of 3880 = 16%
  lines (>=25 chars) that appear in >=5 briefs: 488 of 3880 = 13%
Write of a brief file: 54 model gen min 19.4 | Edit of a brief file: 40 gen min 1.3 | heredoc brief in Bash: 89 gen min 33.9

=== G3 launch returned by the prose check
launch commands whose result holds 'DETACHED rm-detached' (a run started): 147 | returned before the start: 49
  relaunched after an edit: 19 | relaunched unchanged: 20 | no relaunch seen: 10
  fault kinds in the returns: {'undefined': 40, 'pronoun': 28, 'synonym': 7}
  model gen min between return and start (sum): 5.2 | median wall s 79
  the returned launches' own wait min: 19.8
  launch (started) wall s: median 64 p90 122

=== G4 card answers recorded by hand
AskUserQuestion calls 53 questions 150 | owner wait h 15.2 median min 4.9
commands carrying --by-card: 48 tool min 25.1 gen min 9.2
ledger writes within 15 min after an answer: 142 gen min 20.7 tool min 60.1

=== G5 start of a window
restart prompts (fresh Conductor windows): 37 | calls per restart: mean 14.4
first 14 calls of each restart read 5114775 chars in total (138237 per restart)
   Read conductor.md                        n= 35 chars= 1825152 (52147 avg)
   detached_helper.py status                n= 37 chars=  444052 (12001 avg)
   seat_restart.py wake                     n= 55 chars=  416842 (7578 avg)
   bash other                               n=105 chars=  411557 (3919 avg)
   cli.py queue                             n= 19 chars=  321416 (16916 avg)
   cli.py show                              n= 29 chars=  267396 (9220 avg)
restart -> last call of its episode: median 220 s, sum h 3.0
restart episode model gen min (sum): 30.8
the part printed more than once: see evidence.md (exact repeated lines of >=40 chars: 2.2%; repeated meaning UNMEASURED)

=== G6 waiting for a launch, a publish, a run
publish commands that landed (result holds PUBLISHED): 198 wall s: median 47 p90 167 max 590 | sum h 4.5
publish commands that start with ./publish and did not land: 33
helper status poll   n=319 wall h 2.49 median s 11 p90 s 73 gen min 26.9
pipe why             n=263 wall h 2.00 median s 10 p90 s 86 gen min 20.9
pipe show            n=227 wall h 0.76 median s 3 p90 s 24 gen min 18.1
sleep / wait loop    n=238 wall h 2.92 median s 19 p90 s 107 gen min 34.5
background Bash calls 129

=== G7 a worker's report: acts after a run-end wake
run-end wakes: 763 | zero-call replies: 133
wake episodes that contain a git log/show/cat-file/diff or a rimflow show: 186
  verification calls in them: 282 tool min 90.5 gen min 24.4
all wake episodes: wall h 14.3 median s 25 calls mean 2.3 gen min 130.6
  first call after a wake: [('other', 168), ('pipe', 116), ('publish', 106), ('ledger_show', 42), ('file_read', 33), ('ledger_file', 32), ('ledger_note', 31), ('helper_status', 29)]
  wake text chars: median 598 p90 7225

=== G8 reading old tickets / asks
rimflow show calls: 435 wall h 3.07 median s 9 p90 s 82 gen min 53.5
  result chars: median 2056 p90 7677
bursts of >=4 shows within 5 min: 4 calls in them 16
human turns whose first 300 chars say stale/stuck/old: 8
whether a show was meant to judge staleness: UNMEASURED (the call does not say)

=== G9 many tickets parked / re-homed / closed
episodes with >=5 distinct hand ledger acts (close/drop/wait/home/note...): 0
shell loops that write the ledger: 36
hand ledger writes by verb: {'note': 261, 'wait': 13, 'close': 65, 'home': 4, 'drop': 8, 'reopen': 1, 'supersede': 1}
detached runs in the 7 days: 1016 | bulk-style verbs: {'SWEEP': 10, 'CLEAR': 4, 'ROUTE': 46, 'PARK': 2, 'TRIAGE': 2, 'AUDIT': 1}

=== G10 searching for lines that say the opposite of a new ruling
recursive grep over rule / design / code trees: 235 wall min 40.1 gen min 13.2
inside the 68 ruling-carrying turns: see G1 (greps counted there)
whether a grep hunted a contradiction: UNMEASURED (the call does not say)
owner_rulings.py --grep calls: 40

=== G11 sizing a spend cap
run records 1016 with a cost 929 ended at the cap (error_max_budget_usd): 16 (dollar figures are cost_usd fields of the run records)
   cap hit: verb AUTOBUILD cap    15  verb p90  27.9  (n=4)
   cap hit: verb DRIVE     cap    30  verb p90  29.8  (n=44)
   cap hit: verb DRIVE     cap    30  verb p90  29.8  (n=44)
   cap hit: verb FADE      cap    15  verb p90  28.6  (n=2)
   cap hit: verb FINISH    cap    10  verb p90  13.7  (n=2)
   cap hit: verb FIX       cap    10  verb p90  12.0  (n=52)
   cap hit: verb FIX       cap    10  verb p90  12.0  (n=52)
   cap hit: verb JUDGE     cap    15  verb p90  15.4  (n=14)
   cap hit: verb MEASURE   cap    15  verb p90  19.1  (n=8)
   cap hit: verb MEASURE   cap    15  verb p90  19.1  (n=8)
   cap hit: verb REBUILD   cap    10  verb p90  23.9  (n=3)
   cap hit: verb STAGE     cap    10  verb p90  19.0  (n=9)
   cap hit: verb TRACE     cap    10  verb p90  13.5  (n=21)
   cap hit: verb TRACE     cap    10  verb p90  13.5  (n=21)
   cap hit: verb TRACE     cap    10  verb p90  13.5  (n=21)
   cap hit: verb WIDEN     cap    10  verb p90  11.6  (n=7)
caps hit that sat below the verb's p90 cost: 14 of 16
launch commands carrying --budget-usd: 351
launches refused for a missing cap: 5
distinct caps used by the 1018 records: [(120.0, 224), (0.0, 122), (12.0, 118), (10.0, 68), (8.0, 65), (60.0, 52), (80.0, 50), (40.0, 49)]

=== G12 closing an item
close commands: 64 refused: 6 redone in the window: 5 redo after s: [8, 20, 13, 33, 9]
close wall min 23.7 gen min 5.2

=== NEW kinds the data shows
inline python one-offs: 986 gen min 85.9 wall min 217.4
  run records: out.json cost / turns / result      n=490 gen min 40.4 wall min 45.9
  ledger events jsonl                              n= 50 gen min 3.7 wall min 14.9
  window transcripts (.claude/projects)            n= 28 gen min 2.3 wall min 1.7
  conductor log.md                                 n= 16 gen min 1.8 wall min 3.7
  item prose / queue                               n= 26 gen min 2.9 wall min 8.7
finding an item or file by words (ls | grep, git ls-files | grep): 109 gen min 6.2 wall min 19.7
./sync in the command: 233 wall min of those commands 70.2
state polls (pipe why/show/log, helper status, queue/next/incidents/seat, game_lock query, accounts, acct): 935 wall h 6.23 gen min 77.9 result chars sum 3074036
  polls per window-hour of tool time: n/a; polls by kind: [('detached_helper.py status', 208), ('./pipe why', 165), ('./pipe show', 139), ('cli.py queue', 65), ('game_lock.py query', 60), ('./acct', 52), ('cli.py file', 40), ('cli.py show', 33), ('cli.py note', 30), ('detached_helper.py launch', 27)]
rimflow file commands: 301 wall min 169.3 gen min 38.0 title/text chars mean 1548
namecheck calls 51 gen min 5.3

=== EXTRA publish by kind of path, file bursts, hand reads of a run result, cap-hit spend
publish ledger-only        n= 49 median s  32 p90 s 146 sum min 49
publish md/json/txt only   n= 13 median s  46 p90 s 237 sum min 22
publish has a code path    n=  9 median s  92 p90 s 585 sum min 40
rimflow file commands: 298 median s 16 p90 s 97 | within 3 min of another file command: 56 | carrying --publish: 28
hand reads of a run's result (inline python on *.out.json, reads 'result'): 460 gen min 37.9 wall min 40.7 | within 10 min after a run-end wake: 416
cap-hit runs 16 cost_usd sum 227 of all run cost_usd 6287 | items hit twice or more: 2

=== EXTRA wake: exact repeated lines in the first 14 tool results + SessionStart text of each window
chars in lines >=40 chars: 6773695 of which an exact repeat of an earlier line in the same window: 150670 = 2.2%
```

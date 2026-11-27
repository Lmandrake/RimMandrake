# Candidate scripts, ranked by the model time they would remove in a week

Item RIMMANDRAKE_SCAN_MODEL_CHORES_FOR_SCRIPTS_HE_ASKED_MORE. Written 2026-11-26 5:55 PM PST for the owner (the
Conductor brings it). The owner picks; nothing here is built. Numbers: the 7 days to 2026-11-26 5:46 PM PST, 50 Conductor
windows, 5303 tool calls, 1018 detached run records. Every row, its definitions and its caveats: `evidence.md` (rerun
with `measure/rows.py`; the section names below are its sections).

**How to read the minutes.** `gen` is the time the model took to think and write the calls that the script would replace
(a lower bound: a reply with no tool call is not counted). `wall` is the time the window waited for those calls. A
compound command that names two tools counts for both, so each figure is a bound, not a saving. Total for the week: gen 7.6 h
over all calls; wall 43.5 h, of which 15.2 h is the owner thinking on cards.

## The five that would remove the most

### 1. `run_result <unit|item>`: read what a finished run left, and check what it claims
- **Does:** prints a run's last message, end state, turns and cost from its out.json, then checks each sha (on
  origin/main?), item id (state in the ledger?) and path (on disk?) that the message names, and prints one line per claim.
- **Measured today** (sections "a worker's report" and "EXTRA" of `measure/rows.py`): 460 hand reads of a run's `out.json` result by inline python, 416 of them within 10
  min after a run-end wake: gen 37.9 min, wall 40.7 min. Beside them 186 of 763 wake episodes hold a `git log/show/cat-file`
  or `rimflow show` check: 282 calls, gen 24.4 min, wall 90.5 min. All wake episodes: 14.3 h wall, gen 130.6 min.
  Command: `python3 -I measure/rows.py`, the same two sections.
- **Exists already:** `src/RimMandrake/rimflow/run_end_wake.py` already delivers each run's whole last message with the
  state block (checked on the wake of 2026-11-26 7:11 PM: 890-char result, whole in the wake). `detached_helper.py status`
  lists runs; `close_check.py` checks closed items once a day. A check of the claims in a report: searched `rimflow/`,
  `Utils/`, `~/dev/MandrakeWorkflows`; none found.
- **Stays judgement:** whether the work meets the item, and whether "tested" in the report is honest. The script checks
  only that a named sha, item or path is real.
- **Size:** small for the read; medium for the claim check. **First step, before any build:** find why 460 hand reads
  follow a wake that already holds the message (UNMEASURED; guess ~50%: reads after a restart, or for cost and end state).
- **Rigour:** removes the mistake "the report names a sha that is not on origin/main". How often a report was wrong:
  UNMEASURED (the data does not say).

### 2. `now`: one screen of state in place of the poll round
- **Does:** prints runs in flight with their age, the pipe line, who drives each game, the accounts left, and the head of
  the Conductor queue, in one command.
- **Measured today** (section "NEW kinds" of `measure/rows.py`): 935 state polls (`detached_helper.py status` 319, `./pipe why` 263, `./pipe show` 227,
  `queue/next/incidents/seat`, `game_lock query`, `accounts`, `./acct`): gen 77.9 min, wall 6.2 h, 3.07 M chars of results.
  Waits by sleep or until-loop add 238 calls, 2.9 h wall. Share that one command would replace: UNMEASURED (a poll often
  waits for one event).
- **Exists already:** `run_end_wake.state_block()` builds exactly these lines for the wake text but has no command line;
  `./pipe show`, `MATURATION_NOW.md`, `rimflow next` each give a part. `waitalive.py` waits for a process. No `now`.
- **Stays judgement:** which run or mod needs an act. The script only prints.
- **Size:** small (a command line on code that exists).
- **Rigour:** none shown in the data.

### 3. `ruling_search "<his words>"`: the lines that may say the opposite
- **Does:** takes the key terms of a new ruling, greps the rule trees (`CLAUDE.md`, `standing_rulings.md`, `roles/`,
  `skills/`, `design/specs/*/boundary.md`) and prints file:line with the nearby negation words, for the model to judge.
- **Measured today** (sections "owner ruling carried into the rules" and "searching for lines that say the opposite" of `measure/rows.py`): 68 owner turns carried into rule files, median 5.4 min wall, 13 calls (p90 32.5 min);
  gen 113 min summed over the turns. Inside them 540 grep or `owner_rulings.py` calls, gen 48 min (a bound: some are not
  contradiction hunts; intent UNMEASURED). The fast part (record his words, place the hold, write the rule) is
  `RIMMANDRAKE_BUILD_RULING_FAST_PATH_SENTENCE_TOOK_NINETY_MINUTES`; this candidate is the search beside it.
- **Exists already:** `owner_rulings.py` (his words, dated), `conductor_closeout.py` (each answered message carries
  `--owner-said`), `guiding_prose.py` (meaning faults in new sentences). A search for opposite lines: none found.
- **Stays judgement:** whether a found line truly says the opposite, and the new wording.
- **Size:** medium. **Rigour:** removes the mistake of a rule line left standing against a new ruling; how often one was
  left: UNMEASURED.

### 4. `brief_new <kind> <ITEM>`: the standing parts of a helper brief
- **Does:** writes the lines that every brief of a kind repeats (skills to read, the two tests, the rules for the run, the
  report line), passed once through the prose check, and leaves the question and the "what to write" to the model.
- **Measured today** (sections "helper brief written by hand" and "launch returned by the prose check" of `measure/rows.py`): 58 briefs in 7 days, median 6 KB. 13% of lines repeat in 5 or more briefs, 16% in 3 or
  more, 21% in 2 or more (51 of 58 name the same `using-rimflow` skill line). Writing time: gen 19.4 min (Write) up to
  33.9 min (heredoc; includes the rest of its command), edits 1.3 min; so the repeat share removes about 7 to 12 min. The
  prose check returned 49 of 196 launch attempts (25%): 40 undefined terms, 28 pronouns, 7 synonyms; 20 started unchanged
  on the second try, 19 after an edit; gen 5.2 min, wall 19.8 min.
- **Exists already:** `brief_commands.py` (command lines filled), `item_packet.py` (item history), `guiding_prose.py brief
  FILE` (the check), `spend_talk.py`. A per-kind skeleton: none found.
- **Stays judgement:** the question, the files, what is enough, and when the helper stops looking.
- **Size:** small to medium. **Rigour:** a skeleton that passed the prose check once cannot be returned for its own
  standing lines; which share of the 49 returns named a standing line: UNMEASURED.

### 5. `card_note`: his card answers as one ledger note
- **Does:** after a question card, writes one note with `--by-card` on a named item, from the card store, so the model
  supplies only the item and the consequence sentence.
- **Measured today** (section "card answers recorded by hand" of `measure/rows.py`): 53 cards, 150 questions; 48 commands carry `--by-card` (gen 9.2 min, wall 25.1 min);
  142 ledger writes within 15 min after an answer (gen 20.7 min, wall 60.1 min; a bound, not all are card notes).
- **Exists already:** `card_capture.py` stamps the whole card from the card store; `card_reask.py`. The note text and the
  choice of item are still by hand.
- **Stays judgement:** the consequence of the answer and which item holds it.
- **Size:** small. **Rigour:** none shown in the data.

## Below the line (measured, smaller or not a script)
- **`cap_for <verb>` at launch** (section "sizing a spend cap" of `measure/rows.py`). Model time about 0 (UNMEASURED). The gain is rigour: 16 of 934 runs ended at
  the cap (≈ list dollars 227 of 6287), 14 of the 16 caps sat below that verb's p90 cost, 2 items hit the cap twice. 38
  launches already pass `--continue-on-cap`. Exists: `helper_budget.py` (slots), `spend_watchdog.py`. Size small.
- **`rimflow file` batch** (section "EXTRA" of `measure/rows.py`). 298 files, wall 169 min (median 16 s, p90 97 s), 56 within 3 min of another. Only
  the landing wait goes; the title and the acceptance test stay the model's. Size small to medium.
- **Wake pack** (section "start of a window" of `measure/rows.py`). 37 windows read 138,237 chars each in 14 calls (`conductor.md` 52,147 chars, 38%); gen 30.8 min,
  wall 3.0 h. Exact repeat is only 2.2%, so a de-duplicating script gains little. Which parts the window uses: UNMEASURED.
  A usage log of the wake comes first.
- **Publish wait** (section "waiting for a launch, a publish, a run" of `measure/rows.py`). 198 landings, median 47 s, p90 167 s, 4.5 h wall. md/json-only n=13, median 46 s; code n=9,
  median 93 s: too few to blame the publish check on rule and design text. The second half of `RIMMANDRAKE_BUILD_RULING_FAST_PATH_SENTENCE_TOOK_NINETY_MINUTES` (let rule and design text pass the publish check without the code checks) covers this wait.

## Dropped by the data (do not build)
- Many tickets parked or closed by hand (guess 9 of the Conductor in the brief of this item): 0 episodes with 5 or more distinct hand acts; bulk work goes to helpers
  (ROUTE 46, SWEEP 10, CLEAR 4 runs).
- A refused close then a second form (guess 12 of the Conductor in the brief of this item): 6 of 64 closes refused, 5 redone in 8 to 33 s; gen 5.2 min in the week.
- Reading an old ask or ticket to judge it stale (guess 8 of the Conductor in the brief of this item): 435 `rimflow show` calls, but only 4 bursts of 4 or more;
  purpose UNMEASURED; `queue_staleness_review.py` exists.

## UNMEASURED, with what would settle it
- Why the window hand-reads a result after a wake that carries it: read 20 of the 460 calls' preceding turns.
- How often a worker's report claimed a false sha, item or count: the transcripts hold no verdict; run candidate 1 in
  shadow for a week and count.
- Weighted tokens of any row: the run records hold `cost_usd` only.

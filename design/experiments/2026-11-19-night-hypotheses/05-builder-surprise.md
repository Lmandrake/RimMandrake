> HISTORY: retired era, see design/RimMandrake/retired_eras_index_2026-11-18.md. This file's mentions of Relentless, Artisan, Whittle, FOUNDRY, RimPulse or rimflow v3 are history (that machinery no longer runs); the rest is as current as its own status says.

# Replay: does a builder's own report say where a later check finds a fault?

Item: `RIMMANDRAKE_REPLAY_TWO_MORE_HYPOTHESES_SURPRISE_AND_LARGE_READS`. Tests the hypothesis
`RIMMANDRAKE_AUDIT_ON_SURPRISE_ONLY_PREDICTION_SEALED_FIRST` in `00-hypotheses.md`, in the form the Conductor's
brief gave it: an outside check is worth most where the builder's closing report admits a slip, a doubt, an
untested part or a surprise, and worth little where it does not.

## For the owner (2026-11-19, 3:00 AM PST)

- The test says no. A doubt in a builder's report does not show where later checks find faults.
- I read 149 helper runs from Tuesday 00:00 to now. 93 reports admit a doubt, a slip, an untested part or
  a surprise. 56 reports admit none [measured].
- Later work found a fault in 13 runs. 8 were runs with a doubt, 5 were runs without one [measured].
- That is 9% for both groups. My rule before counting said "against" if the two rates are within 1.5 times.
- I also counted the 11 unclear cases as faults. The rates are then 12% and 14%, so the result is the same.
- Most reports admit something because our rules make every helper name what it did not run. So an
  admission is the normal case and tells you little.
- Something later touched every run: a commit, a note, or another run. No run was left with "nothing looked".
- The sample is small. 13 faults cannot show a weak effect. They can show that the effect is not large.
- Both known cases were found. "23 of 23" was really 16 of 23. A commit left two selftests red.
- I recommend no change to how checks are chosen. Do not skip a check because a report sounds sure.

## Written before measuring (2026-11-19, 2:48 AM PST)

- **Population.** Every detached run whose record (`D:\ClaudeWork\rimmandrake\dispatcher\detached\*.json`) was
  launched on or after 2026-11-17 00:00 PST, finished, with a readable result text. One run is one row.
- **The mark, from the report alone.** A fixed list of word patterns over the run's result text, in four kinds:
  UNTESTED (untested, UNRUN, not tested / run / verified, could not verify, did not test), SLIP (my mistake, I
  missed, I broke, first attempt failed, had to redo, corrected), DOUBT (not sure, unsure, uncertain, unclear,
  might not, a `[guess` tag), SURPRISE (surprise, unexpected, turned out, contrary to). **FLAGGED** = any kind hits.
  A stricter mark, **FLAGGED-STRICT** = UNTESTED, SLIP or SURPRISE (no bare hedges), is reported beside it. The
  patterns live in `tools/builder_surprise.py` and are not changed after the first count.
- **What happened next, within 48 hours of the run's end** (clipped at the moment of measuring; the window each row
  had is reported). Three outcomes, kept apart:
  - **FAULT FOUND**: a later act found a fault in this run's work. Candidates come from the ledger (later events on
    the same item by anyone but this run, and items filed that name it or are `caused_by` it), the Conductor log
    (entries naming the item, except this run's own end lines), later runs' reports that name the item, and later
    commits that touch the files of this run's closing commit. A candidate must hold a fault word; each candidate
    is then judged by hand, **without seeing the run's mark**, as fault or not.
  - **LOOKED, NOTHING FOUND**: one of those later acts exists, and none was judged a fault.
  - **NOTHING LOOKED**: no later act of any of those kinds.
- **FOR the hypothesis:** among runs that were looked at, the fault rate of FLAGGED runs is at least twice that of
  unflagged runs and at least 15 points higher, and unflagged runs show a fault rate of 15% or less.
- **AGAINST:** the two rates are within a factor of 1.5, or unflagged runs fail more often, or more than half of
  all faults sit in unflagged runs.
- **TOO SMALL to say:** fewer than 5 faults in all, or fewer than 10 looked-at runs in either row. Then I say so
  and claim nothing.
- **Sanity probe.** Two cases are known to be faults before counting: a "23 of 23" claim that a later experiment
  showed was 16 of 23, and a first close that failed a selftest. If the instrument does not find both, it is blind
  and the counts are not reported as a measurement.

## What changed in the instrument after the first count, and why

The marks did not change. The outcome side changed twice, each time because it was blind or flooded. I record
both versions so a reader can judge whether I tuned towards an answer. Both changes came before any hand verdict
and before the marks were joined to an outcome.

1. **First version: links by item id and by the files of the closing commit.** It counted 148 of 149 runs as
   looked at, because the launcher's own bookkeeping notes ("detached run clone returned", "detached run ended",
   "pipe stop") were counted as looks. I dropped those notes. It also missed the "23 of 23" case: the experiment
   that broke it named `boundary_check.py`, not the item. That failed the sanity probe.
2. **Second version: three kinds of link.** (a) The same item, or an item the run closed. (b) A later text
   that cites one of the run's commits, which are its close and verify shas plus any hash in its report that is
   a commit made during the run. (c) A later text or commit that names a file the run changed and that at most
   three runs in the sample changed. This version found both known cases. With the broad fault words of the
   pre-registration (fail, refus..., bug) it gave 631 candidates. The words are this repo's own vocabulary
   ("refuses by name", "fails loudly"). I narrowed the gate to phrases that say earlier work was wrong (`not
   true`, `was wrong`, `stale test`, `went red`, `left ... red`, `slipped past`, `missed`, `regress...`,
   `double count`, `found N more gaps` and the like; the list is `FAULT` in the tool). That gave 184 candidates.
3. **Hand verdicts.** I judged all 184, shuffled, without the run's mark shown. A fault means the later text
   says that this run's delivered work was wrong, broke something, left something red, or missed a case it
   owed. The later run's own slips, a defect the run found and reported, or a feature description are not
   faults. 60 candidates were one template from the old-era sweep ("close refused (guard owed) ... its live
   promise broke N times") about old items' history. I read 13 of them and judged the class "not a fault".
   I checked attribution in git where a candidate named a fault but not its author. For example, `git log -S`
   shows that `1d7b17ad85` (`RIMMANDRAKE_APPLY_BARS_CARD_PATCH_WHEN_BLIND_JUDGES_END`) wrote the false
   "5 of 5 PASS live" line. `3b40731c4c` (`RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES`, the
   16:42 run) wrote the wrong "38 tests" count. Result: 24 fault, 149 not, 11 unclear. The verdicts are in
   `tools/builder_surprise_verdicts.json`.

## Counts [measured]

Population: 149 finished runs launched since 2026-11-17 00:00 PST (105 Opus, 40 Fable, 4 Sonnet). 143 of them
landed at least one commit. Tokens are each run's own part of its session, so a resumed run is counted once:
371.1 million weighted tokens in all.

| report says | fault found later | looked, nothing found | nothing looked | fault rate when looked |
|---|---|---|---|---|
| admits doubt, slip, untested part or surprise | 8 (17.3M tokens) | 85 (203.0M) | 0 | 8 / 93 = 9% |
| admits none of these | 5 (11.4M) | 51 (139.4M) | 0 | 5 / 56 = 9% |

Fisher's exact test on the four cells: p = 1.0. The other cuts agree:

- **Strict mark** (UNTESTED, SLIP or SURPRISE; a bare `[guess` tag does not count): 8 of 87 against 5 of 62
  (9% and 8%).
- **Only runs that landed a commit:** 8 of 92 against 4 of 51 (9% and 8%).
- **Unclear cases counted as faults:** 11 of 93 against 8 of 56 (12% and 14%).

By the rule written before measuring, this is **against** the hypothesis: the two rates are within a factor of
1.5. The sample clears my "too small" line (13 faults, at least 10 looked-at runs in each row). It is still small:
13 faults rule out a large effect, not a modest one. Only a strong signal would have shown here.

**The 13 runs with a fault, and whether the report flagged it.**

| run (item) | report flagged | what a later act found |
|---|---|---|
| `RIMMANDRAKE_BUILD_BOUNDARY_CHECK_PROMISE_WITHOUT_TEST_REFUSED` | yes ("untested") | "23 of 23 covered" was 16 of 23 |
| `RIMMANDRAKE_CHECK_PAGE_ONLY_EDIT_AT_PUBLISH_SLIPS_PAST` | yes ("untested") | the same "23 of 23" |
| `RIMMANDRAKE_EXTEND_VOID_TO_JUDGE_DESIGNER_AND_PILOT_COUNTERS` (02:46 UTC run) | yes | `4fe2af3f9e` left `selftest_incident` red |
| `RIMMANDRAKE_FIX_FOCUS_CAP_REFUSED_CLAIM_STILL_TAKES_LEASE` | yes | `797a08f5e7` left `selftest_known_reds` red and an alarm with no drainer |
| `RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS` (second run) | yes ("UNRUN") | `1cf299d075` let the ENDED line clobber role result JSON |
| `RIMMANDRAKE_SHARE_PROBE_RESULT_TYPE_NINE_FILES_ROLL_OWN` | yes | a fresh reader added a hole to its boundary page |
| `RIMMANDRAKE_REWRITE_SLEEPINGICE_TO_THEROT_UTINNI_LENS` | yes ("not verified") | false Stillsand roster row; the Rot design misread stockpiles |
| `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` (14:44 PST run) | yes ("turned out") | its reach tool missed `from rimflow import relentless_x` |
| `RIMMANDRAKE_SPLIT_LIVE_CODE_OUT_OF_RELENTLESS_NAMED_MODULES` (16:42 PST run) | no | the "38 tests" count was 17; a removed function was still called |
| `RIMMANDRAKE_BUILD_PIPELINE_CONTROL_ONE_LINERS_NO_BUILD_PROCESS` (first run) | no | Codex found a kill recorded as done, a look counted twice, and more |
| `RIMMANDRAKE_APPLY_BARS_CARD_PATCH_WHEN_BLIND_JUDGES_END` | no | wrote "5 of 5 PASS live" for a test that never ran |
| `RIMMANDRAKE_RECHECK_SLEEPINGICE_TO_THEROT_CHOICES` (two runs) | no | passed the same false Stillsand row |

**Precision of the mark.** I read the first matching phrase of 15 flagged reports drawn at random. 11 of 15
(73%) admit a doubt about the run's own work. The 4 misses describe a feature ("refuses a page with a new
untested promise"), a tool's output ("read 'did not run'"), or a fix to someone else's text ("corrected").

## Blind spots

- **Short windows.** Most runs ended late on 2026-11-18 or early on 2026-11-19. The median run had 8.5 hours
  of "later", not 48. Only 2 runs had the full 48 hours. Faults that surface in days are missing from both rows.
- **Recall of the fault search is unknown.** A fault counts only if a later text says so in a phrase on the
  list, near a link to the run. A fault fixed silently, or described in other words, is missed. A fault
  found by the owner in chat is missed. I did not measure the miss rate.
- **"Looked at" is loose.** A later commit that touches a file the run changed counts as a look, even if it
  never read the run's lines. 23 runs were "looked at" by commits only. That is why "nothing looked" is
  empty. With no empty cell, the second half of the claim ("an outside check is worth little where the report
  is sure") cannot be tested by this data.
- **Recall of the mark was not measured.** An unflagged report may still hedge in words outside the list.
- **One judge.** I wrote the marks and judged the faults. The marks were hidden while I judged, but I knew the
  hypothesis. A second judge would be the next check.
- **Lanes, not runs.** Several runs share one lane (the era split, the biome rechecks). Their faults are not
  independent, so the true sample is smaller than 149.

## What I would and would not do

- **Would not:** choose which work gets a second look by the tone of its report. Nearly two runs in three
  admit something, because the rules make every helper name what it did not run. A sure-sounding report
  failed later as often as a doubtful one.
- **Would not** spend more on this replay. A larger sample needs a week of runs with full 48-hour windows.
- **Would:** keep the two kinds of fault that showed up most and that a machine can catch. Four of the 13 are
  a count or claim that a later run measured differently ("23 of 23", "38 tests", "5 of 5 PASS live"). Two
  are a commit that left a selftest red on main. The first kind is what
  `RIMMANDRAKE_AUDIT_ON_SURPRISE_ONLY_PREDICTION_SEALED_FIRST` aims at, with an outside prediction instead of
  the builder's tone. That version stays untested.
- **Would:** look at the tool's link (b), a later act citing the run's commit, as a cheap "who touched my
  work" view for the Conductor. It found both known cases. I built nothing for it.

## Files

- `tools/builder_surprise.py`: the replay; pass 1 writes the candidates, pass 2 joins the verdicts.
- `tools/builder_surprise_verdicts.json`: the 184 hand verdicts (`true`, `false`, `"unclear"`).
- Scratch, not committed: `D:\ClaudeWork\scratch\replay_two_hypotheses_20261119\` (`candidates.txt`,
  `runs_final.json`, `table_primary.txt`, `table_unclear.txt`).

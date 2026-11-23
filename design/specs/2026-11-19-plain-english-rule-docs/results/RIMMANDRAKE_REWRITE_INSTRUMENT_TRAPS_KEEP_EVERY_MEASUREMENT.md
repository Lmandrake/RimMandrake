# Result: `RIMMANDRAKE_REWRITE_INSTRUMENT_TRAPS_KEEP_EVERY_MEASUREMENT`

Part 1 of 2 of batch `RIMMANDRAKE_REWRITE_TRAP_FACT_FILES_TWO_FILES` (`batch_plan.md`, order 9). File:
`infrastructure/state/facts/instrument_traps.md`. Run 2026-11-23. Special rule of the batch: keep each measurement.
The file is a home for evidence, so the STE target binds only its rule bullets.

Base: e6dd7e02a26cafa0c5535635a29e00455b133ea4

## Scores

| measure | before | after |
|---|---|---|
| bytes | 45,852 | 48,160 |
| words in linted prose | 6,910 | 7,294 |
| STE violations per 100 words (whole file, evidence included) | 4.20 | 2.84 |
| sentences over 20 words | 152 | 106 |
| flagged lines (mechanical) | 52 (50 shout, 1 pronoun, 2 bare-id) | 48 (48 shout) |
| lines that a cold reader cannot act on (hand count, by the writer) | 12 | 0 that this run could resolve; 4 listed under "Could not determine" |

The file grew by 5%.

The whole-file score is 2.84, above the 2.5 target. In this file each bullet holds a rule and its evidence in one
paragraph, so this run did not separate a "rule text" score. Most violations that stay are in evidence sentences with
code spans and figures. The 48 flags that stay are all `shout`: the 🔴 and ⚠️ marks at the start of a bullet (a
severity mark, kept) and the ALL-CAPS words inside the bold leads. Every bold lead stays word for word, because a lead
is the slogan of its entry. Inside sentences this run removed the 🔑 ⛔ ✅ ⚠️ ⇒ marks and lowered emphasis caps.

### The 106 long sentences that stay, by kind

The kinds are the writer's sort of the lint's `LONG` list. Line numbers are of the new file.

- **Two short sentences that the lint joined at a bold lead (71 rows).** The lint reads the bold lead and the first
  sentence after it as one sentence. Lines 33, 39, 47, 63, 74, 85, 96, 109, 132, 135, 139, 143, 151, 155, 164, 168,
  180, 184, 187, 190, 193, 196, 200, 205, 209, 214, 221, 227, 238, 244, 250, 258, 261, 266, 280, 289, 292, 295, 297,
  300, 304, 308, 314, 319, 322, 324, 340, 343, 349, 354, 358, 361, 364, 366, 370, 375, 377, 381, 386, 390, 397, 409,
  419, 422, 441, 446, 451, 456, 459, 463, 473.
- **A sentence that holds a command (about 20 rows),** for example line 8 (the sanity-probe rule), 53 (the sweep
  rule), 74 (scan every `About.xml`), 214 (the two ways to fix a generator), 324 (the deleter rule), 415 (the
  retired-donor inventory).
- **Evidence (the rest, about 15 rows):** a measurement whose figures and code spans must stay together, for example
  line 127 (the 1319 `unchanged since` runs), 168 (the owner's rule "a different agent tests what was built", kept with
  its quote spans), 280 (the 34% and 26% rates), 463 and 473 (the token figures).

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "text unchanged except heading levels" (header) | the line is false after this rewrite | rewritten: the header says when and why the text was rewritten |
| "until a sanity probe proves the instrument can see" (header) | what a sanity probe is, at first use | gloss from the zsh entry of the same file |
| "so queueing work here generates nothing" (artpipe) | where "here" is | "on the Mac" (the clause before names the Mac) |
| "Same family as the rule below" (GravTide) | the pointer: the sanity-probe rule is in the zsh entry, above | names the zsh entry above and the donor-name-scan entry below; both state the rule |
| "It had already solved the entire problem." / "He said …" | the subject of "It" / "He" | "GravTide had …" / "The owner said …" |
| "Now `mandrake.rm.flowworks`" | the subject | "FlowWorks is now `mandrake.rm.flowworks`" |
| "The GSS aerial census" | what GSS is | gloss: the GimmeSomeSlack mod (from the completion-measures entry) |
| "`preflight_bridge` O14" | a bare coded id | "`preflight_bridge` check `O14` (`effective_def_lint`)", from `src/RimMandrake/Utils/preflight_bridge.py:660` |
| "Tester probe P3o" | a bare coded id | `P3o` in a code span; the line already names its file |
| "(1) … (2) … (5)" in one paragraph (publishing rule) | five rules in one line | one bullet per rule, numbers kept |
| "27 of 27 resumed runs …" and "81,158,999 of 371,342,565 recorded weighted tokens" | what each figure counts | could not determine (below) |
| "OOB counters here" | what OOB means | could not determine (below) |

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the rewrite with `MLIE_FAUNA_ABSORPTION_1` removed, "**182** jobs" changed to "many jobs", `cade628c1` changed to "a commit" | 1 lost (the id), exit 1. Check 1 did not see the lost 182 or the lost sha. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 7 lost (182, the id, and 3 quote spans of the first draft), exit 1 |
| check 1 | the final rewrite | 116 items, 0 lost, exit 0 |
| check 2 | the final rewrite | 526 spans, 0 lost, exit 0 |
| `rule_doc_lint.py selftest`, `checkable.py selftest`, `batch_done.py selftest` | — | PASS; 19 of 19; GREEN 12 planted cases |
| `selftest_retired_era_gone.py` (`era_text.py` reads this file) | the new file | PASS |
| `selftest_agent_improve.py`, `selftest_agent_improve_steps.py` (from `git grep -l instrument_traps -- '*selftest*' '*accept*'`) | the new file | PASS, PASS |

The other selftests that the grep found (`selftest_ashkarr_weathersuite_listed.py`, `selftest_biome_density_classes.py`,
`selftest_plant_economy_census.py`, `selftest_no_owner_presence.py`) and the lesson file only cite the file name in a
docstring or comment. They do not read the file.

Check 2 found 3 lost "quote" spans in the first draft. The spans are the text between two quotes: `, a mutation run's`
and the text between `"wrong"` and `"a different agent tests what was built"`; also the text between `"doing"` and
`"work in flight"`. This run put those two passages back in their old form, so each owner-quote span stays whole.

Names of people: this run read the diff for names. Steve (2), owner (17 → 18; one "He" became "The owner"), Owner (1),
the Conductor (1), Mandrake (6), Cathar (1) and Graffiti (1) stay.

## What the meaning read found

A fresh Opus reader (rm-judge, model opus) read the old and the new text, bullet by bullet. It did not get the
writer's reasoning. It found 3 lines. The same reader then read only the repairs: 3 of 3 fixed, and 1 new finding,
caused by a polish restore. The writer fixed that one too. No reader read the last fix.

| first draft | why it was wrong | repair |
|---|---|---|
| "Each false ERROR is for a def whose parents live in an inactive mod." (`validate_patch.py --defs`) | reversed the claim: the old text says every such def gets a false ERROR | "The tool reports a false ERROR for every def whose parents live in an inactive mod." |
| "`preflight_bridge` check `O14` (`effective_def_lint`)" | a fact that the old text does not hold | kept on purpose: `batch_plan.md` allows a meaning taken from the code; the source is `preflight_bridge.py:660`. The reader accepted it. |
| "The sanity-probe rule of the zsh entry applies here too" (GravTide) | the old text pointed below; the zsh entry is above | names both: the zsh entry above and the donor-name-scan entry below |
| "Before any later scene, call `clear_live_fallen` and re-string. So the pawns of a later phase can be shocked there" (GSS aerial census; found on the second read) | "So" now followed the clean-up, as if the clean-up causes the shocks | the shock sentence now follows "`proof_all` leaves live fallen wires", and the clean-up command comes after |

The reader's polish notes, restored to the old words: "structurally identical files", "Otherwise a fix can 'win'",
"so the pawns of a later phase can be shocked". The tense change "when there were 9" stays.

## Conflicts (listed, not decided)

1. **A biome with zero tiles.** This file, entry "A biome is done when the PLAYER'S tiles carry the content": a biome
   def with zero painted tiles is not done, and hand-kept painted-def lists must come from the world CSV. Root
   `CLAUDE.md` §A biome with zero tiles is not a defect: a BiomeDef of ours on 0 tiles is the expected state until the
   planet is painted at the end, and a tile count is not evidence that something is or is not built. The Conductor
   decides.
2. **Does a glob error loudly?** Entry "`ls <dir> | wc -l` answers 0": "glob `*.json`, which errors loudly". Entry
   "`glob.glob` swallows directory-listing errors: an unreadable directory reads as zero files". The first can mean a
   zsh glob (zsh refuses a glob with no match); the second is Python's `glob.glob`. The file does not say which glob
   the first entry means.
3. **Which shell is "here".** Entry "The shell here is zsh" and entry "`grep` here is ugrep". Measured 2026-11-23 in
   this clone on Archmagi: the agent's Bash tool runs bash, where `grep` is ugrep 7.8.4; under `zsh -c`, `grep` is GNU
   grep 3.12. In bash, `for x in $NAMES` does word-split. So each entry is true for a different shell, and neither
   entry names its shell or machine.

## Could not determine

| line | question | who would know |
|---|---|---|
| "OOB counters here are cgroup ceilings, not RAM." | "OOB" is probably "OOM" (the entry is about OOM kills); this run kept the old word | the author of the entry (`git log -S "OOB counters"`) |
| "A glob ending `validation.py` matched 132 files but only 129 are mod harnesses (3 are `selftest_*_validation.py`, 2 more are hook files)" | 132 − 3 − 2 = 127, not 129; the figures do not add up | the author of the entry |
| "Measured 2026-11-19: 27 of 27 resumed runs …; on 2026-11-18 (PST) 81,158,999 of 371,342,565 recorded weighted tokens" | what each figure counts. Probably 27 of 27 runs were overcounted, and 81,158,999 was the excess over the corrected sum (`check_resumed_run_tokens.py` prints both sums). Not confirmed. | the author of `RIMMANDRAKE_COUNT_RESUMED_RUN_TOKENS_ONCE_SESSION_TOTAL_LOGGED`; or run the tool |
| "until the Desktop runs it" (artpipe) | which machine "the Desktop" is now (`mt-515497`, or Archmagi) | the Conductor |

## What this run did not test

- No agent read the new file in real work. No measurement shows that an agent avoids a trap more often on the new
  text.
- No reader read the last fix (the GSS aerial census sentence order).
- This run did not check whether each entry is still true today (for example "its checklist is VALIDATED with 12
  binding bars"). The rewrite keeps each claim as the old text stated it.
- The rule-text score (the STE score without the evidence sentences) was not measured.

## Second read of the repairs

Run 2026-11-23, item `RIMMANDRAKE_REREAD_REWRITE_REPAIRS_NO_READER_SAW_THEM`. One fresh Opus reader that made none of
these edits read each repair, restored line and late edit against the base text and the lines that travel with it. SAME
means that a reader of the new line acts as a reader of the old line. A gloss reads SAME when its source says the same.
His quotes: a script compared each quote of three words or more in the base with today's text, whitespace ignored. No quote differs (one match in the list was prose between two quotes).

| file | line read | verdict | what was done |
|---|---|---|---|
| instrument_traps | "The tool reports a false ERROR for every def whose parents …" | SAME | none |
| instrument_traps | `O14` (`effective_def_lint`) | SAME | true by `preflight_bridge.py` line 660 |
| instrument_traps | the GravTide pointer to two entries | SAME | none |
| instrument_traps | the GSS aerial census order, the fix that nobody read | SAME | none |
| instrument_traps | "structurally identical files" | SAME | none |
| instrument_traps | "Otherwise a fix can 'win'" | SAME | none |
| instrument_traps | "so the pawns of a later phase can be shocked there" | SAME | none |
| instrument_traps | late edit `ff6dc8e491`: the zero-tiles claim is removed | changed on purpose | none: the new line agrees with `CLAUDE.md` §A biome with zero tiles is not a defect |

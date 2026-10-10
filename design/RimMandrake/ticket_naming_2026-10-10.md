# Ticket naming: SUBJECT_INTENT_TWIST (2026-10-10)

Owner's request, 2026-10-10: replace `THREE_UPPER_SNAKE_WORDS_#` (whose number is stuck at
`_1` forever) with a naming convention that is comic and entertaining but still accurate:
it says **what the item is**, **what it sets out to do**, and adds **a twist on how it is
going**, so reading the queue is fun.

## Measured before designing

From `model.replay()` on 2026-10-10 (sanity probe: the census found the ledger's own
`SANDSTORM_WEATHER_TUNING_1`-style ids):

- **2,846** items in the ledger. **2,714 (95%) end in `_1`**; only 21 end in anything else,
  and 9 of those are one series (`DIRTY_CODE_REVIEW_LOOP_RESTART_2…10`). The number carries
  no information.
- 2,743 match the legacy `WORDS_#` form; 103 are older shapes (`B58`, `B-EMP1`,
  slug-with-hash ids from an import).
- Words before the number: 3 (1,119) or 4 (1,299) is normal; 5+ is rare (303).
- Length: median 27, p90 33, max 48 characters.

How ids are handled in code:

- **Minting** is by hand: `rimflow file <ID>` and `rimflow spawn --name <ID>`. Nothing
  generates ids. Collisions were already refused (`_apply_file`, `_apply_spawn`).
- **Validation on replay** is `model.ID_RE`. It is deliberately permissive, because it has
  to admit every id ever written.
- **Spotting ids in free text** depended on the trailing number: `model.NAMED_ID`
  (commit subjects and `Closes:` trailers in `gitindex.ids_in`, and queue headings in
  `is_item_heading`) and `citations_lint._ID_RE` (doc citations). This is the real cost of
  dropping the number. Without it, `MAX_FLIGHT_TIME` has the same shape as an item id.
- Templates that made up ids: `queue_lint.py`'s cross-seat hint (`CORRECT_<bits>_1`) and
  `l1_batch_manifest.py`'s line parser.

## The grammar

```
SUBJECT _ INTENT _ TWIST
  1-4 words  1 word   1+ words      3-7 words in all, <= 44 chars, A-Z 0-9 _ only
```

- **SUBJECT**: what the item is about, in the words someone would grep for:
  `BRIDGE_HANG`, `GREY_DEEP_ROSTER`, `TPS_TIMERS`.
- **INTENT**: one word from the bank below. It says what the item sets out to do. It is
  the **hinge**. The first bank word at position 1 or later, with at least one word after
  it, splits the name, so a reader (and the code) can always tell the subject from the
  flourish.
- **TWIST**: a true, specific, kind aside about the work. It can be the trap, the irony,
  the running count, or the lesson: `THIRD_TIME_LUCKY`, `NOT_A_DRILL`, `READ_THE_LABELS`.

## Examples

Every one of these passes `rimflow namecheck`, and the selftest checks them all
(`selftest_naming.py` `DOC_EXAMPLES`).

| id | what the twist is saying |
|---|---|
| `TPS_TIMERS_AUDIT_WATCHING_THE_WATCH` | auditing the instrument that measures overhead, which itself costs overhead |
| `BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY` | the bridge hang has been fixed twice before |
| `ARTPIPE_QUEUE_DRAIN_182_AND_COUNTING` | the artpipe pending queue held 182 jobs |
| `GREY_DEEP_ROSTER_CENSUS_READ_THE_LABELS` | a census by defName missed built creatures, so read descriptions |
| `OLD_NAME_GATES_EXCISE_SIXTEEN_DAYS_LATE` | rename gates cited a closed item for 16 days |
| `FIREHAWK_WINGS_REWIRE_FLAPPING_NOT_JIGGLING` | Spastic jiggle replaced by a real flip-book |
| `MODSCONFIG_COUNT_FIX_LI_TAGS_LIED` | `grep -c '<li>'` said 48 when the real count was 631 |
| `GREATBOLE_CORE_RESKIN_NOT_A_DRILL` | the core marker renders a retinted deep drill |
| `CHILL_DENSITY_RESCUE_FROM_ABSOLUTE_ZERO` | `animalDensity` 0 meant nothing ever spawned |
| `TICKET_NAMES_REDESIGN_NO_MORE_ONES` | this item |
| `FLYER_FLIGHT_VERIFY_BY_STATE_NOT_STARING` | check flight with a state read, not a screenshot hunt |
| `SETTINGSKIT_TESTS_MEND_STILL_RED` | the selftests are failing, and they still are at filing time |

A worked trap: `STALE_RENAME_GATES_EXCISE_…` parses as subject `STALE`, intent `RENAME`,
because `RENAME` is the first bank word. If a subject word is in the bank, rephrase it
(`OLD_NAME_GATES_…`). `namecheck` prints the parse so you can see the split.

## Accuracy rules

The humour serves the reader. It may never cost accuracy.

1. **The subject must survive a cold grep.** Someone looking for the bridge hang searches
   `BRIDGE`. Use the project's real nouns (mod, biome, def, tool names), and never a pun
   in their place.
2. **The twist must be true when filed.** `STILL_RED` is fine if it is red. `SINCE_TUESDAY`
   is fine only if it was Tuesday. A twist that is a guess or a prediction is a false
   statement with a permanent address.
3. **Specific beats generic.** `THIRD_TIME_LUCKY` carries a fact (two earlier attempts).
   `FUN_TIMES` carries nothing. The checker refuses the cheapest vague words (`MISC`,
   `STUFF`, `WIP`, `TODO`, …).
4. **Kind.** Never mock a person, a seat, or the owner. The joke is on the bug, the
   instrument, or the situation. The checker refuses a short list of insults. The rest is
   on the filer.
5. **No in-jokes that need context.** Cold readers include the next session, another
   machine, and the owner a month from now. If the twist only makes sense with this
   conversation in mind, rewrite it.
6. **The title still carries the ask.** The id is a handle. `--title` is the sentence
   that says what done looks like.

## Intent word bank

`rimflow namecheck --bank` prints it. The source is `model.INTENT_WORDS`.

```
investigate  AUDIT CENSUS MEASURE REMEASURE PROBE PROVE VERIFY VET JUDGE BENCHMARK BISECT
             DEBUG DIAGNOSE HUNT CHASE
make         BUILD CODE WIRE REWIRE FILL POPULATE INSTALL DEPLOY FINISH POLISH WIDEN SHRINK
repair       FIX MEND REPAIR UNSTICK UNTANGLE UNBLOCK HARDEN ENFORCE SILENCE CORRECT
             RECONCILE SYNC UNIFY MERGE DEDUPE
remove       EXCISE CULL PRUNE DELETE RETIRE
transform    SALVAGE RESCUE RESTORE REVIVE ABSORB MIGRATE RENAME RESKIN REDRAW
adjust       DRAIN TAME TUNE BALANCE
think        DESIGN REDESIGN RETHINK SKETCH DECIDE ASK HARVEST DOCUMENT EXPLAIN MONITOR
again        REBUILD RETRY
```

The bank deliberately leaves out words that are common **subjects** in this project:
PATCH, MAP, SHIP, PLANT, REVIEW, TEST, PAINT, PORT, SPEC, STAGE, CATCH, GUARD. Any of
those in a subject would split the name in the wrong place. To add a verb, add it to
`INTENT_WORDS` (one line), after checking it is not a common noun here. Twists are free
text, and fresh ones are encouraged. There is no twist bank on purpose.

## Phase is intent, not state

An id cannot change, but the state of the work does. **The intent word records what the
item set out to do when it was filed** (UNSTICK, AUDIT, EXCISE, SALVAGE). It never records
the live state. In the same way, the twist is true *as of filing*. The **live** state
lives in the ledger, and rimflow already prints it next to the id: the queue view puts
`state:` directly under each `## <ID>` heading, and `rimflow show` prints
`<ID>   doing  row -  needs …` on its first line. Nothing new is needed there.
`namecheck` on an existing id also prints its state.

If the intent turns out to be wrong (an AUDIT turns into a rebuild), do not rename the
item. File the rebuild as its own item, linked with `--caused-by`. That has always been
the ledger's rule for new work.

## Legacy ids

- **Never renamed.** All 2,846 existing ids (the `_1` ones, the other `_N` ones, `B58`,
  and the slug ids) stay valid forever. They replay, close, cite and match `Closes:`
  exactly as before.
- **No new legacy ids.** `rimflow file` and `spawn` refuse a new id that ends in a number,
  naming the reason. A sequel to a legacy series gets a fresh name with a twist
  (`COLD_LOAD_RUN_SHEET_4` would become something like
  `COLD_LOAD_SHEET_RETRY_FOURTH_PASS`).
- Legacy ids are still cited bare. B-style ids are still cited with their title
  attached, as before.

## What the machine enforces

Refused by `rimflow file`/`spawn`, through `model.mint_problems`:

- a character outside `A-Z 0-9 _`
- fewer than 3 or more than 7 words
- more than 44 characters
- a final `_<number>` (the legacy form), or a last word that is only digits
- no intent hinge (the intent is first, last, or missing)
- a banned vague or mean word
- a collision with any existing id

Not enforced, and left to the filer: whether the subject is greppable, whether the twist
is true, and whether it is kind beyond the short ban list.

## Where it lives in code

- `src/RimMandrake/rimflow/model.py`: `INTENT_WORDS`, `BANNED_NAME_WORDS`, `parse_name`,
  `is_new_name`, `is_named_id`, `mint_problems`. This is the grammar's only home.
  `ID_RE` (replay) and `NAMED_ID` (legacy shape) are unchanged.
- `src/RimMandrake/rimflow/cli.py`: `_mint_or_die` in `cmd_file`/`cmd_spawn`, and the new
  `rimflow namecheck [NAME] [--bank]`.
- `src/RimMandrake/rimflow/gitindex.py`: `ids_in` accepts both forms. A new-form token
  needs a hinge, so `MAX_FLIGHT_TIME` is not picked up. Cache `VERSION` 3 rebuilds it.
- `src/RimMandrake/rimflow/citations_lint.py`: a new-form token counts as a citation only
  when the ledger knows it.
- `.claude/hooks/queue_lint.py`: the cross-seat hint now suggests `<BITS>_ASK_<HOLDER>_<TWIST>`.
- `src/RimMandrake/Utils/l1_batch_manifest.py`: the line parser accepts both forms.
- Selftest: `src/RimMandrake/rimflow/selftest_naming.py`.

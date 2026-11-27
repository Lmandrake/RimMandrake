# Boundary: the standing parts of a helper brief, from one source (`src/RimMandrake/rimflow/brief_new.py`)

Item RIMMANDRAKE_BUILD_BRIEF_NEW_ONE_IN_FOUR_LAUNCHES_RETURNED, script candidate 4 of
`design/specs/2026-11-26-script-candidates/one_page.md`. Why: the Conductor wrote 58 briefs by hand in 7 days. In
those briefs, 13% of the lines repeat in 5 or more briefs. The prose check returned 49 of 196 launches before the
start. A skeleton whose standing lines passed the prose check once leaves the model only the lines that differ.

Code: `src/RimMandrake/rimflow/brief_new.py` (all of it). Tests: `src/RimMandrake/rimflow/selftest_brief_new.py`.

## ACCEPTS

- **a-kind-and-an-item.** `brief_new.py <kind> <ITEM> [--out PATH]`. The kinds are `build`, `review`, `measure`,
  `judge` and `operate` (the `KINDS` table). The kinds come from the titles of the 70 Conductor briefs of 2026-11-19
  to 2026-11-27: build or fix 19, operate 13, measure 9, review or fresh read 4, judge 2, and 23 others, most of them
  fixes.
- **an-out-path.** With `--out`, the tool writes the skeleton to a new file. Without `--out`, the tool prints the
  skeleton.

## DOES NOT SURVIVE

- **a-blank-left-unfilled.** The tool does not check the filled brief. A brief that still holds a `<<NAME: ...>>`
  blank launches with that blank. `brief_new.blanks(text)` names the blanks that a text still holds.
- **an-item-that-the-ledger-lacks.** The tool writes any item id. The prose check at the launch returns an id that the
  ledger does not hold (its `dead-item` fault).

## PROMISES

- **each-kind-skeleton-passes-the-prose-check.** The skeleton of each kind has no fault in the program half of
  `guiding_prose.py brief`, on every sentence of the skeleton (`check_files` with no reader). A planted fault is
  found, so the check can see. The selftest reads at least 15 sentences in each kind.
- **the-question-and-the-stop-are-left-as-blanks.** Each skeleton holds the blanks TITLE, QUESTION, FILES, ENOUGH and
  STOP once each. No standing line holds a blank. Each skeleton holds the polish route (CLAUDE.md: a brief that
  reviews or judges states the level that is enough, when to stop, and the polish route).
- **an-unknown-kind-is-refused-by-name.** An unknown kind exits 2, and the refusal names that kind and each known
  kind. The tool then prints nothing and writes nothing. An `--out` file that exists is kept, and the tool exits 2.
- **standing-lines-come-from-one-source.** Each standing line is in `LINES` once. A kind names the keys of its lines.
  No sentence of one line is in a second line. Each line is used by a kind. Each skeleton holds only those lines, its
  blanks and its headings. The test-2 lines are `fixer_rule.STATEMENT`, `fixer_rule.JUDGE_STATEMENT` and
  `fixer_rule.evidence_line()`, and `brief_new.py` holds no copy of their text. No skeleton states a spend or a cap.

## LIMITS

- The report line says "At most 10 lines". The 10 is the median of the 60 "At most N lines" in the 70 briefs above
  (10 in 20 briefs, 8 in 17, 12 in 15).
- The selftest's `RUN_S` (60 s) is a hang guard on one run of the tool. One run takes about 0.1 s (measured 2026-11-27).

## LIFE CYCLES

- **a hand brief:** the Conductor runs `brief_new.py <kind> <ITEM> --out <file>`, and the Conductor fills each
  blank in that file. Then `detached_helper.py launch` adds the footer, the item packet and the command lines, and
  runs the prose check before the start.

Later lists beside this page: `polish.md` (none yet).

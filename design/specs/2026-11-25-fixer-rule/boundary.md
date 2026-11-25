# BOUNDARY: one fixer statement and one test-2 list, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/fixer_rule.py` (`STATEMENT`, `JUDGE_STATEMENT`, `EVIDENCE`, `NOT_EVIDENCE`, `text()`),
cited by `src/RimMandrake/rimflow/detached_helper.py` (`FOOTER`), `src/RimMandrake/rimflow/maturation.py`
(`SELF_FIX_RULE`) and `src/RimMandrake/rimflow/maturation_autonomy.py` (`fixer_brief`, through `SELF_FIX_RULE`). Item:
`RIMMANDRAKE_CLOSE_POLISH_AND_FOOTER_DOORS_SIXTEEN_FENCES_CONTRADICT`. Report: wording 1 and Part 4, homes 2 to 5, of
`design/specs/2026-11-25-the-fixer-is-you/findings.md`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_fixer_rule.py`.

## ACCEPTS (the only inputs this is built for)

- **prose-homes-in-markdown.** The prose homes are Markdown files. A copy may wrap across lines; the check joins
  whitespace before it compares.

## DOES NOT SURVIVE (not promised)

- **a-home-not-in-the-list.** A new home that quotes the list is not checked until it is added to the selftest.
- **a-reworded-reason-with-the-same-meaning.** A stale reason in other words ("the run is too short") is not seen.

## PROMISES (each one is owed a test of the same name)

- **each-prose-home-holds-the-statement-and-list.** The root `CLAUDE.md`, `design/RimMandrake/standing_rulings.md` and
  the six `.claude/agents/rm-*.md` hold the statement (`rm-judge.md` also the judge statement), every evidence item and
  the not-evidence sentence, word for word.
- **no-home-keeps-a-stale-reason.** No home, the CHARTER included, says "would not finish", "more than this run" or
  "more than one run".
- **the-charter-points-at-the-rule.** The CHARTER points at `CLAUDE.md` §Touching code has a cost and keeps no copy of
  the list.
- **the-program-briefs-cite-the-constant.** The detached footer, `SELF_FIX_RULE` and each of the four fixer briefs carry
  `text()` and no stale reason.
- **the-check-sees-a-planted-drift.** A copy that drops a list item, or keeps the old reason, reads red.

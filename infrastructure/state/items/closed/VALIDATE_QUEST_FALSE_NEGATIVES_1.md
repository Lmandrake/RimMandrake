# VALIDATE_QUEST_FALSE_NEGATIVES_1 — validate_quest.py has false-negative risk on its two headline checks

Found during a full-file code review of `skills/rimworld-quests/scripts/validate_quest.py`
(844 lines) as part of the DIRTY_CODE_REVIEW_LOOP sweep.

## spec

1. **`main()` only reports unparseable XML for bare positional-arg files.** Files
   discovered via `--dir` (the documented primary usage, SKILL.md 324-325/416) hit the
   same `ET.ParseError` swallow in `_iter_quest_defs` (~228-229) with **zero report**.
   Reproduced live: a truncated XML file under `--dir` gave "0 checked, 0 errors", exit 0.
2. **`signal_ok` (~629) treats `known = written | CORPUS_SLATE` (~543) as proof a slate
   var exists**, but `CORPUS_SLATE` is generic shipped-quest vocabulary, not evidence
   THIS def stores that name — so a renamed `storeAs` away from a common name
   (asker/pawn/faction/site/prisoner…) goes undetected exactly where the skill's own
   doctrine says it silently breaks. Reproduced live: `storeAs=requester` + listening on
   dead `asker.Recruited` passed with 0 errors.
3. **`fires` (~494) models only 3 of the 4 documented firing routes** (SKILL.md §7) —
   omits the framework-scheduler route (e.g. VEF `QuestChainExtension`), producing a
   false "never-fires" WARN for legitimately scheduled quests.

Lower confidence: `collect_writes` (~380-383) adds both `prefix+v` and bare `v` to
`written` for prefixed sub-scripts, potentially masking a genuine unwritten-slate case;
`signal_ok`'s return value is computed but never consumed by its callers (dead return).

## verify

#1 and #2 were reproduced live during the review (see above); a fix should show a
truncated file under `--dir` reporting a parse failure, and the `storeAs=requester`
case failing where it currently passes.

## criteria

This is a **skill script** — per CLAUDE.md it is edited in a dedicated fresh-context
curation session, not ad hoc. This item exists so that session starts from
source-verified findings rather than re-deriving them.

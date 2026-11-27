# BOUNDARY: the Pre-Design Concepts store, its program and its line on MATURATION_NOW, Design Version 0.1.0

Code: `src/RimMandrake/Utils/pre_design_concepts.py`, and its calls in `maturation_now.py` (`read_concepts`,
`concepts_line`) and in `crystallize_weekly.py` (`concepts_card`). Item:
`RIMMANDRAKE_BUILD_IDEAS_LIST_AT_INTAKE_TWO_IDEAS_SAT_UNPLACED`. The store and its rules:
`design/pre_design_concepts/README.md`. The rule: `design/RimMandrake/standing_rulings.md` §Mods keep their own state,
"Pre-Design Concepts".

## ACCEPTS
- A folder of Markdown files. Every `*.md` but `README.md` is one concept. The head of a concept file is the bullet
  lines `- **<Field>:** <text>` before the first `## ` line, with the fields Name, Kind, Gets, Added, From ticket, Code,
  Last offered, His answer, and an optional Went to. Added is a date `YYYY-MM-DD`. Last offered is `never` or a date.

## DOES NOT SURVIVE
- A plain name that holds ` (` or `·`: the page line still prints it, but a reader of the page line cannot split it.
- Two concepts with the same Name: `offered <name>` writes the first one in file order.
- Two writers of one concept file at the same moment: `offered` replaces the file whole; the later write wins.

## PROMISES (tests of the same name in `src/RimMandrake/Utils/selftest_pre_design_concepts.py`)
- **check_passes_on_the_real_store**: `check` exits 0 on the real store, and each concept's body quotes his words. A
  concept file that lacks a field fails `check` (exit 1) with the file's name and the field.
- **page_count_equals_store_count**: MATURATION_NOW's line `Pre-design concepts: N · names` holds the count of concepts
  with no `Went to`, and each of their plain names. A concept added moves the page; a concept that went is not counted.
- **unreadable_store_reads_unmeasured**: a missing store, a file in the store's place, or a concept file that cannot be
  read gives `UNMEASURED` with its cause on the page line, never 0. An empty store reads a measured 0.
- **due_puts_never_offered_first**: `due` lists the concepts never offered first (oldest added first), then the ones
  offered longest ago; at most four; never one that went. `offered <name> --answer` writes today's date and his answer
  into the head and keeps the offer in `## Offers`, so the concept moves back in `due`. An unknown name is refused by
  name.

## THE WEEKLY LINE (its test is in `src/RimMandrake/Utils/selftest_crystallize_weekly.py`)
- **the-tick-writes-the-concepts-card-line-once-a-week**: the daily tick of `rm-crystallize.timer` runs `sweep`. Once
  per ISO week it appends `PRE-DESIGN CONCEPTS: card due` and the due concepts to the Conductor log
  (`<agent storage>/rimmandrake/conductor/log.md`). It writes the reading
  `<agent storage>/rimmandrake/pre_design_concepts/last_sweep.json` on every applied tick. A store that cannot be read
  writes no line and does not stop the tick. Listed on `design/specs/2026-11-25-weekly-crystallize-run/boundary.md`.

## LIMITS
- `DUE_MAX` 4: not a guard; the most options one question card holds beside "let them all sleep".
- The call to `agent_storage.py` and each child run of the selftest use `time_budget.CALL_S`: hang guard (class call).

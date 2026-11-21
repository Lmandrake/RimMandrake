# Map: where each section of the four rule files lives after the compression

Item `RIMMANDRAKE_CRYSTALLIZE_RULE_FILES_DOUBLED_IN_EIGHT_DAYS`. One row per section of the root `CLAUDE.md`,
`design/RimMandrake/standing_rulings.md`, `infrastructure/agents/CHARTER.md` and
`src/RimMandrake/rimflow/roles/*.md`. The rows are in `map_parts/` beside this file while the work runs.

base: `542106e6411d83befeb08e26f7f2c791e341b160`

The check that reads this map: `python3 src/RimMandrake/Utils/selftest_rule_files_lose_nothing.py check`.

## Classes

- KEEP: a rule or fact that an agent cannot guess and no program enforces. `unchanged` in the last cell means that no
  sentence of the section changes.
- MERGE: the section is a case of one principle that several sections state. The last cell names the section that
  states the principle afterwards.
- TOOL DOES IT: the line only restates what a hook, gate or tool does or prints. The tool was watched; the reading is
  in the part's "Tools watched" table.
- DUPLICATE: the same rule is in two files. The last cell names the home that keeps the text.
- MOVE: owner words, dates, measurements and history. The last cell names the evidence file that holds them, word for
  word.

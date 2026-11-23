# Result: `RIMMANDRAKE_REWRITE_SKILLS_README_AND_BY_WORK_MAP`

Part of batch `RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH` (`batch_plan.md`, order 17). Run 2026-11-23.
Files: `skills/README.md`, `skills/BY_WORK.md`.

Base: a3c86bb32466a59f38167dbb74f9b8fbca24f625

The `doc_roster` block of `skills/README.md` is byte-identical. Each heading of the two files is word for word the same. The
registration table of `skills/BY_WORK.md` is the same. No text moved to a home file.

## Scores

| measure | README before | README after | BY_WORK before | BY_WORK after |
|---|---|---|---|---|
| bytes | 14,777 | 16,733 | 8,244 | 9,365 |
| words in linted prose | 586 | 908 | 800 | 999 |
| STE violations per 100 words | 5.63 | 1.98 | 5.00 | 2.40 |
| sentences over 20 words | 10 | 3 | 4 | 1 |
| flagged lines (mechanical) | 3 | 1 | 0 | 0 |
| hand count (lines a cold reader cannot act on) | 10 | 0 | 9 | 0 |

- Long sentences that stay in README: the owner's quote of 2026-11-19; two pairs of short sentences that the lint joined at
  a bold mark (lines 9 and 33).
- The long sentence that stays in BY_WORK is the owner's quote.
- Most violations that stay in BY_WORK are `-ing` words inside skill names (`rimworld-debug-testing`) and fixed headings.

## The hand count

| file | old line | what a cold reader lacks | state after |
|---|---|---|---|
| README | "Each loads itself" | true only for a registered skill | split into registered and unregistered |
| README | "until it is wired" | what "wired" means | defined |
| README | "hands over that exact command" | which command of two | "the first command above" |
| README | "re-measures the set" | which set, and the line was false | names the two tools |
| README | "until then" (lessons) | the moment | "Until such a session" |
| README | "active files" | which files | defined |
| README | "if doubtful" | who doubts what | a condition before the command |
| README | "cannot see them; fix one" | the subject | "the general skills" |
| README | "the line" in "when you are about to do what the line says" | which line | "its line" |
| README | "Undo for one: the command in the last column" | the other two edits that the selftests demand | named |
| BY_WORK | "so a helper never sees" + "they too" | which skills | named |
| BY_WORK | "Whether each one is registered is the table at the end" | a subject | rewritten |
| BY_WORK | "(proof_all, validation_v2, LogTap)" | that they are code names | code spans |
| BY_WORK | "(bland world, situational envelope)" | what the envelope is | names `modcheck run --situational` |
| BY_WORK | "the three writers of the mod list" | who they are | RimWorld, RimSort, Steam |
| BY_WORK | "the general layer under it" | what "it" is | `rimworld-review-sheets` |
| BY_WORK | "his usual design order" | who "his" is | the owner |
| BY_WORK | "watch it go red" | what "it" is | the checker |
| BY_WORK | "recorded history before re-measuring" | an instruction | "Query the history before you measure … again" |

## The checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | README copy without `package_skill.py`, 2026-08-22 and the `skills.md` path | 2 lost, exit 1 (`package_skill.py` not seen) |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, exit 1 |
| check 1 | BY_WORK copy without one date and one skill path | 2 lost, exit 1 |
| check 2 | the same copy | 2 lost, exit 1 |
| check 1 | the real rewrites | README 39 items, 0 lost; BY_WORK 54 items, 0 lost |
| check 2 | the real rewrites | README 127 spans, 0 lost; BY_WORK 95 spans, 0 lost |
| `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_warn_skill_unwired.py`, `selftest_validate_skills.py`, `selftest_image_skills.py`, `selftest_retired_era_gone.py`, `selftest_game_names_prose.py` | final | pass |
| `skills/validate_skills.py` | final | 0 errors, 0 warnings |

Names of people: the old and the new texts name none. The diff was read for them.

## What the meaning read found

One fresh Opus reader (rm-judge) per file, one after the other. Neither got the writer's reasoning. The second reader also
read the README repairs against the old text, and the two side corrections.

| reader | finding | repair |
|---|---|---|
| README | the undo steps are false for the `review-sheets` row (no folder in `skills/`, no row in BY_WORK) | its own bullet |
| README | the definition of "active files" makes a repo's record folder active | the record folder is excluded |
| README | "loads for every project" is false where settings hide a skill | "unless the settings of that project hide the skill" |
| BY_WORK | no line lost, weakened or strengthened | none |
| BY_WORK | "this file does not declare" can read as BY_WORK | "`skills.md`" |
| BY_WORK | the closing print of `package_skill.py` disagrees with its new docstring | print corrected |
| third reader, the last-edited lines | "relaunches them" is false: a switch relaunches only the Fleet | corrected, from `skills/rimflow-operations/SKILL.md` |
| BY_WORK | `package_skill.py` counts two more lines than `validate_skills.py`, so it refuses a body of 499 lines | not changed: polish, one line here |

The first `./publish` (`2c07e7e0aa87`) printed 4 prose faults (undefined terms: the bland world, the situational envelope,
"stand windows down and up", "fresh-context curation sessions"). Each term now has its meaning, taken from
`northstar-validation`, `rimflow-operations` and `infrastructure/agents/CHARTER.md`. A third fresh Opus reader read those
lines and each line edited after the first two reads.

No reader read one line after its last edit: the two sentences about the Fleet in BY_WORK (the third reader's own repair).

## Conflicts and stale lines: settled

| two sides | decision | rule and evidence |
|---|---|---|
| README "Each loads itself" / 21 skills are not linked | only a registered skill loads itself | 1: `.claude/skills/` |
| README: general skills are "linked into `~/.claude/skills/` for every project" / `~/dev/Lodestar/claude/skills.md` demotes most | the table declares the links; a machine can hold more | 1: 8 of the 9 named skills are undeclared; Archmagi still links them |
| README: no description in the "Not registered" table is loaded / `review-sheets` has a machine-wide link | the row says so | 1: `~/.claude/skills/review-sheets`; row `all` in `skills.md` |
| README: `validate_skills.py` "re-measures the set" / the code reads no symlink | `selftest_skills_registered_or_listed.py` checks the set | 1: both files |
| BY_WORK: "the 13-mod minimal list" / the list held 27 mods on 2026-11-23 | 13 mods on 2026-08-19, larger now | 1: `conflicts_settled.md`, parsed `ModsConfig.MINIMAL.xml` |
| `infrastructure/STRUCTURE.md`: README holds the folder split and the caps / README holds neither | STRUCTURE.md names the tools that hold the caps | 1: `package_skill.py`, `validate_skills.py` |
| `infrastructure/STRUCTURE.md`: rebuild the archives at hand-off / README: only for claude.ai | only for claude.ai | 1 and 4: no code or hand-off step calls `package_skill.py` |
| `package_skill.py` docstring: skills are installed from a `.skill` archive / README: by symlink | by symlink | 1: `.claude/skills/` |

None goes to the owner.

## Could not determine

| line | question | who would know |
|---|---|---|
| the owner's quote of 2026-11-19 at the top of BY_WORK | `owner_rulings.py --grep enamored` finds no ledger event; the quote stays | the transcripts of 2026-11-19 |

## What this run did not test

- No agent used the new files in real work.
- The undo steps were read in the selftests by the reader, not run on a real row.
- The "nobody invoked in 30 days" count of 2026-11-19 was not measured again.
- `doc_roster.py` reads `OUT OF SYNC design/INDEX.md` before and after this run. That file is not in this item.
- The lesson `20261121T143626Z-BENCH-rule-file-size-measure-words-not.md` names `skills/README.md` as its home. This run did
  not fold it.

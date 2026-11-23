# Result: `RIMMANDRAKE_REWRITE_SKILL_RIMBRIDGE_COMPANION`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimbridge-companion/SKILL.md`. Run 2026-11-23.

Base: `7256ba3831`
Also: skills/rimbridge-companion/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 16,326 | 20,609 |
| words in linted prose | 1,710 | 2,298 |
| STE violations per 100 words | 4.33 | 1.91 |
| sentences over 20 words | 31 | 12 |
| flagged lines (mechanical) | 17 | 15 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 that this run could resolve; 3 listed under "Could not determine" |

Each sentence over 20 words that stays is two short sentences that the lint joined at a bold lead, a closing quote mark or an
emoji, except two: the first paragraph (59 of 91, with its figures) and the sentence that holds the quoted claim
"Unity corrupts rather than throwing". The front matter (`description` included), every heading and the §5 code are byte for byte. The §2
code changed in one place (`cancellationToken`).

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "(§ its own wait logic)" | which section | the line is gone (stale) |
| the three `D:\` and `D:/` commands | a command that bash can run | quoted, or run from the clone |
| "A background fork sharing this session's OS processes" | what a fork is, what is shared | "a background subagent"; one install, one DLL, one process |
| "Unity corrupts" claim | where the claim is made | the header comment is named |
| "My own zone builder" | whose | "An early zone builder of this companion" |
| "the invalidation recipe" | what it is | one plain sentence |
| "a probe", "a condition" | what each is | short gloss |
| two table rows below a paragraph in §4 | the table | the paragraph now follows the table |
| "the whole session" in §5 | which session | the 2026-08-19 session |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `ADVANCEUNTIL_WIRE_PER_TICK_STOP`, `expectTiles`, `revoke` and 21,872 | 1 lost (the id), exit 1. Check 1 did not see the other three. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1 | the final rewrite, with `--also` | 47 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 172 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_hugethings_test_races.py` | new text | PASS |
| the §1 block | `bash -n`; the first two lines and the guard, run for both games, with and without a stale `RM_GAME_INSTANCE=b` | syntax good; the guard stops only ArchBig in a shell that means ArchSmall |
| an unquoted `D:\` path in bash | `python.exe D:\Luke\...\tool_metadata.py` | fails: `can't open file 'D:\\LukedevRimMandrake...'`; the quoted path runs |

Names: no person is named in either text. The mark "FOUNDRY 2026-08-30" (a retired seat name) stays as a date mark. "BENCH, 2026-09-01" moved to the history file.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 14 items. All are repaired.

| finding | repair |
|---|---|
| §1 block: a lost `eval` makes `launch_and_wait.sh` kill ArchBig | one Bash call, a guard line, and a bullet that says why |
| §1 block: a refused `stop` did not stop the block | the lines are joined with `&&` |
| exit 1 read as proof of a failed load | exit 1 can leave a game up; only exit 0 settles |
| "token line" is false for ArchSmall | port line named, in `lifecycle.md` too |
| §5: "changes every launch" is false for ArchSmall | one line per game |
| "upper bound" and "exact" were wrong: `deepfire/` names are unseen, and quoted names are escaped | both corrected |
| rule 9: a grep "counts each quoted name" | only a grep with no opening quote mark |
| `get_defs`: a single nested object is left out, not returned as a type name | corrected |
| §5 `Coast` line read as a misreport | restored |
| the fork rule had become a rule for every fork | "that might touch" restored |
| "the roster is old" was weaker than "superseded" | says superseded |
| `cond_eval` item "dropped" read as abandoned | "dropped as DONE, because the work landed" |
| "first zone builder" was a new claim | "An early" |
| `extending-detail.md` held only ArchBig's deploy path | ArchSmall's path added |

A second fresh reader read the repaired parts once and found 2 items: `$GAME` is empty in a later Bash call, and the §6 row
said "ArchBig's deploy path" after both were in the file. Both are repaired. No reader read those last two repairs. After the first landing, the prose check
of `./publish` named 2 pronouns; both are repaired in the same run. No reader read those two either.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `taskkill.exe /F /IM RimWorldWin64.exe` / two games on Archmagi | `game_instance.py stop`, by process id | 1, 3 |
| unquoted `D:\` commands, `D:/` glob / what bash does | quoted, or relative to the clone | 1: measured |
| "one `RimWorld.exe` and one deployed DLL on the machine" / one install per game | per install | 1: `build.py` `aim()`; 3 |
| `launch_and_wait.sh` waits for truncation; its exit code is wrong / receipt launcher | the launcher of 2026-10-10. Also corrected in `extending-detail.md`, `lifecycle.md`, `run-checklists.md` | 1: `launch_ready.py`, `cbec3e5b54` |
| the cycle edits then builds / `--apply` refuses uncommitted sources | commit first, or `--allow-dirty` | 1: `build.py` `main` |
| "check for the word `deployed`" / the plan prints `not deployed yet` | the line that starts with it | 1: `plan_deploy` |
| rule 9 "avoid `jawa/` prefixes in descriptions" / rule 3 names `jawa/world_commit` in one | complete names only | 1: `tool_metadata.py`, `da7cef3c55`. Also in `traps/companion.md` |
| "a docstring made a phantom name" (guard table) / exact read | the row names the real causes | 1 |
| "two byte-scans, two different tolerances" / both exact | both exact for `jawa/` names; the calibration lesson stays | 1 |
| DRIFT "expected mid-session" / "Investigate before overwriting" | investigate | 1: `plan_deploy` text |
| `get_defs` has no deep read / `deep=true` | built 2026-09-01 | 1: `5d576b8568` |
| `cond_eval` PLANNED / in the source | built; live checks have no recorded pass | 1: `JawaBenchCondProbes.cs`, the ledger |
| "91 tools ship", "~95 candidates", five source files, "every `prove_*.py` opens the same way" | counts and the universal claim gone; kept in history | 1, 4 |
| sample `InvokeAsync` with no token / `traps.md` "always pass `cancellationToken`" | the sample passes it. 87 of 524 source calls match that shape (a text count) | 5: the later lesson |
| `--gm` "needs the owner's ruling" (`build.py` help) / the cycle uses `--gm` | the skill keeps `--gm`. The help text is code and was not changed | 1: `maturation.py` and `companion_stage.py` both pass `--gm` |

## Could not determine

| line | question | who would know |
|---|---|---|
| "1,225 BackstoryDefs, 2,129 ThoughtDefs, 336 TileMutatorDefs" | which dump. The line is of 2026-08-19, so the text gives that date | the dump of that day |
| "the original companion's own header comment" | whether it was more than today's header in `JawaBenchTerrainTools.cs` | git history of that file |
| "weather/incident/lord/social/mech-cluster … ~40 lines" | the exact set then. The source now gates 50 tools (a text count) | the 2026-09-19 session |

## What this run did not test

- No live game was driven. The stop, build, launch and prove lines of the §1 block were not run.
- No measurement shows that an agent builds a tool better with the new text.
- The trigger evals were not run, because the description did not change.

# Result: `RIMMANDRAKE_REWRITE_SKILL_CANON_REFERENCES`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-canon-references/SKILL.md`. Run 2026-11-23.

Base: `dc766fd503`
Also: skills/rimworld-canon-references/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 15,842 | 18,726 |
| words in linted prose | 1,962 | 2,330 |
| STE violations per 100 words | 5.45 | 2.23 |
| sentences over 20 words | 45 | 10 |
| flagged lines (mechanical) | 16 | 15 |
| lines that a cold reader cannot act on (hand count, by the writer) | 8 | 0 |

Of the 10 long sentences, one is an owner quote (the Q11a quote). The other 9 are two short sentences that the lint joined at a bold lead,
an emoji or a closing mark.

The front matter (`description` included) and every heading stay byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "Its composition and the owner's standing rules … `CLAUDE.md > What is where`" | the rules are not there | points at `standing_rulings.md` §What is where |
| "a donor mod ships a plausible-sounding name" | what a donor mod is | defined at first use |
| "a parser … raises on exactly the passing (zero-result) case" | which case is meant | says that zero results is a valid answer |
| "a value in the pool" | the subject of the sentence | "That thing is a gene, a field, or a value in the pool" |
| "Recorded as Q11a" | what Q11a is | title added |
| "brief §F" | what section F is | title added |
| "(`NAMING_SCHEME_EXECUTION_1` closed 2026-08-31)" | what the item is | "the one-time rename migration" |
| "It usually names a specific image FILENAME" | what to do when the file is gone | a bullet says it |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with 7 planted losses (`RSW_lifespan_nine`, 50,000, `Brylark tree`, the Olive quote, `NAMING_SCHEME_EXECUTION_1`, the 11 of "11 canon rows", `design/Jawa/fauna/sprites/`) | 2 lost (the quote, the id) |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 6 lost, exit 1 (one loss counts twice: the id as a code span and as a named id). It did not see the Olive quote or the 11. |
| check 1 | the final rewrite, with `--also` | 24 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 109 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work`, `selftest_skills_registered_or_listed`, `selftest_validate_skills`, `selftest_guiding_prose`, `selftest_game_names_prose`, `selftest_retired_era_gone` | new text | PASS |
| `selftest_canon_census`, `selftest_canon_homonyms_decided`, `selftest_species_skin_rulings`, `selftest_art`, `selftest_backfill_git_disk`, `selftest_subject`, `selftest_subjects_lead`, `selftest_canon_check` | the entry edits | PASS |

Names: no real person is named in either text (Star Wars characters only, inside file names).

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 2 real items, and
about 35 trivial items (most of them were checked TRUE).

| finding | repair |
|---|---|
| REAL: the §5 row banned a helper from writing down a ruling that the owner or the Conductor gave | the row now lets a helper record such a ruling |
| REAL: §4 still named only the owner, against §5 | §4 names the Conductor too |
| trivial: the aggression ramp is in `RM_MapComponent_VerminPopulation` | corrected |
| trivial: "every line counts", although a line that the facing cannot show does not count | narrowed |
| trivial: the two §6 checks were weaker than before; "may" became "can" | restored |
| trivial: "Some lines say so" had no source | removed |
| trivial: the history counts "40 of 68" and "133", the remark on `IsReconnected()`, the census pointer | reworded with the method |

The same reader then read the repairs and found 0 real and 5 trivial items. Two were repaired after that read: "visual
line" in §2, and the census remark in the history file. No reader read those two edits.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| 137 entries, 108 `none known`, 25 ruled / 266, 165, 68 | counts moved to the history file with dates | 1 and 3: the files; `CLAUDE.md` says do not cite a number |
| the library-wide rulings are in `CLAUDE.md` / in `standing_rulings.md` §What is where | the second | 3: `CLAUDE.md` points there |
| 3–6 `## Must show` lines (`AGENT_BRIEF.md`) / entries hold 4 to 9 | both are stated; each visual line that the facing can show counts | 1: the entries; `canon_check.py` |
| only the owner departs from canon or writes a ruling / the Conductor may do every act outside the five | the owner, or the Conductor as a recorded act | 2: owner 2026-11-19, `delegation_policy.md` §2 |
| a picture he kept is his alone / open exceptions exist | pointer to the exceptions | 1: `delegation_policy.md` §2 |
| `IsReconnected()` is the flood-fill / it calls `RM_PoolKernel.Reconnected()` | the second | 1: the code |
| the breeder holds both caps and the ramp / two other classes do | the second | 1: the code |
| `RUT_WardenMother` is only a comment example | kept; the shipped `RM_WardenMother` added | 1: `src/RimMandrake/Miasma/` |
| search `src/RimStarWars/` for a defName / some graded defs are elsewhere | search `src/` | 1: `RM_Ollathrix` |
| `rakata/` holds the bad image / deleted 2026-10-08 | "once held"; `AGENT_BRIEF.md` corrected too | 4: caa490d482 |
| `AGENT_BRIEF.md`: 70 xenotypes / 69 in the XML | the number removed | 1: the XML |
| the `mirialan` entry says that it "previously cited" the file that it cites now | the old name restored | 1: 252f8ff2e |
| the `wyyyschokk` entry: defName `Wyyyschokk`, patched by a file that does not exist / `RM_Ollathrix` | the second; `INDEX.md` regenerated | 1 and 2: `RSW_Shokk_OllathrixSkin.xml`, owner 2026-10-03; both names still resolve in `subject.py` |
| the Q11a quote was cut short | the owner's whole clause | `biome_rulings.md` |
| `useSkinShader` annotation quoted from an entry / the words are `AGENT_BRIEF.md`'s | the second | 1: no entry holds the words |

## Could not determine

Nothing in the rewritten text. The `description` still says 137 entries. A `description` changes only with the trigger
evals of `skill-creator`, and the number does not decide when the skill loads.

## What this run did not test

- No live game was driven, and no web request was sent. The Wookieepedia and Fetcher lines stand as written.
- That `IsReconnected()` is the swim-eligibility test is a design ruling (`miasma_fauna_roster_2026-09-23.md`). No
  shipped swim code that calls it was found.
- 133 backticked image names are not in their entry directories. Many lines record a deletion. The run did not read each one.
- The trigger evals were not run, because the description did not change.
- No measurement shows that an agent behaves better with the new text.

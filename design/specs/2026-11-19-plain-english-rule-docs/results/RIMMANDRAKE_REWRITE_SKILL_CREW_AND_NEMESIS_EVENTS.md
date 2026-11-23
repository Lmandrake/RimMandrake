# Result: `RIMMANDRAKE_REWRITE_SKILL_CREW_AND_NEMESIS_EVENTS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-crew-and-nemesis-events/SKILL.md`. Run 2026-11-23.

Base: `5a8cdff9b7984b237aee28af83eaa13c91c77015`
Also: skills/rimworld-crew-and-nemesis-events/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 8,267 | 11686 |
| words in linted prose | 993 | 1580 |
| STE violations per 100 words | 3.73 | 1.39 |
| sentences over 20 words | 16 | 2 |
| flagged lines (mechanical) | 3 | 3 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

The long sentences that stay are two short sentences that the lint joined: one at a bold lead, one at the quoted letter.
The 3 flags were there before: the id C07 (its title is beside it) and the two emphasis marks on the two worst traps.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "population intent (Randy: 1.0 at 4 colonists …)" | what population intent is, and what the numbers are | both are stated |
| "VERIFIED" | who checked what | defined at the top |
| "RM_Stranded can be recruited" | a quest cannot be recruited | the survivor in RM_Stranded |
| "decide which before shipping" | which two choices | set the flag, or close the recruit branch |
| "The We Are United shape" (one sentence with arrows) | the order of the parts | a list of four steps |
| "Restrict targets narratively" | what limit | kin, or pawns with no faction |
| "rotate by returnCount" | which way | the lowest count returns first |
| "Joiners that bypass the gate (above)" | where | §1 is named |
| "vanilla `ResurrectionUtility` on a pawn you kept alive" | cannot be done | corrected (below) |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without 248 files, ×0.75 and the letter quote | 2 lost (15% because `--also` was absent, 248 files). Check 1 did not see ×0.75 or the quote. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost, exit 1 |
| check 1, check 2 | the final rewrite, with `--also` | 8 items, 0 lost; 55 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the first draft: all seven; the final text: guiding_prose, skills_by_work, skills_registered_or_listed, validate_skills | exit 0 each |

Names of people: one, "Aldo" in the quoted letter, kept. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge) read every line of both texts without the writer's reasoning, and checked each correction.

| finding | repair |
|---|---|
| "resurrect, then pass to the world" fails: the pawn spawns where the corpse lies | `dontSpawn` added, with the reason |
| "must write its own record of who was taken": the tracker already holds the person | rewritten |
| the two-colonist correction was in one of three places | also in `crew_mechanisms.md` and the study |
| study idea 3 contradicted study §5 about who sets the default | the idea points at §5 |
| "The world keeps the pawn itself" reads as automatic | "Make the world keep the pawn itself: pin the pawn" |
| the whole-crew gate became a gate per path | both are named |
| minor: "changes that number"; "Make one promotion"; the Rimesis reason; "is gone"; the crew cap; the victim's name | all repaired |

A second fresh Opus reader read each repair (the first reader cannot be resumed in the foreground of this run). It found one
significant thing: `RecordEncounter` was named without its pawn. The writer repaired it with the reader's own wording (an
envoy or the faction leader, never null or the victim; or an envoy as the kidnapper) and dropped `noLord`, which has no
effect beside `dontSpawn`. No reader read those last repairs: the two routes in §3, the `dontSpawn` phrase, the changed
sentence in `crew_mechanisms.md` §4 and in study idea 19. Each repeats what the second reader measured.
After the first landing (9d279423a1), the prose check of `./publish` named one line, the joiners trap in §5. The writer
repaired that line. No reader read that repair.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| card C07 is open / answered 2026-10-10 | the second, also in three places of the study | 2: `OWNER_RULINGS.md` row C07 |
| all source mods retire / Tribute Demand stays | the second | 1: `ModsConfig.FULL.LATEST.xml`; rows C07 and C09 |
| a person in 15% of rolls / weight 0.15 of 1.8 | about 8%, also in two places of the study | 1: `IncidentWorker_Extortion.cs` `GenerateDemands` |
| the person branch needs two colonists / only a colonist does | the second, also in `crew_mechanisms.md` and the study | 1: the same file |
| OldFriends already records a demanded colonist / the patch returns on a null kidnapper | the second, also in `crew_mechanisms.md` and two places of the study | 1: `Patch_ColonistKidnapped.cs`; `KidnappedPawnsTracker.Kidnap` |
| `ResurrectionUtility` on a live pawn / it takes only a dead one | the second | 1: `ResurrectionUtility.TryResurrect` |
| Rimesis point factors stay near 1.0 / the armed raid is 1.5 | the ordinary factor is 1.0 | 1: study §2.7 |

None goes to the owner. The row C07 says "owner to confirm" that RM_Stranded stays. The obvious answer is taken: it stays
(it is on the mod list and in the registry as KEEP).

## Changed outside the skill file

`references/crew_mechanisms.md` (§4), `references/history.md` (new), `design/RimMandrake/event_quest_wisdom.md`.

## Could not determine

| line | question | who would know |
|---|---|---|
| "about five fields and three hooks" | which three hooks | the study names one postfix and, in another place, three Harmony points; its author |

## What this run did not test

- No live game was driven. Each engine fact was read in the decompiled 1.6 source or in the mod's own source.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.

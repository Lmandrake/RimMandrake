# Result: `RIMMANDRAKE_REWRITE_SKILL_CUSTOM_INCIDENTS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-custom-incidents/SKILL.md`. Run 2026-11-23.

Base: `f08ac5efc34eb9665ecaadf94dc6807dd9a0b54a`
Also: skills/rimworld-custom-incidents/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 8,600 | 12,205 |
| words in linted prose | 857 | 1392 |
| STE violations per 100 words | 3.85 | 1.01 |
| sentences over 20 words | 17 | 2 |
| flagged lines (mechanical) | 5 | 5 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 |

The two long sentences that stay: one is a list of mod names; the lint joined the other at a bold lead. The 5 flags
were there before: the emphasis marks on the five worst traps.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "stamps the cooldown and the ThreatBig clock" | what a stamp and that clock are | both are defined at the top |
| "every generic gate" | which gates | defined at the top |
| "a postfix on a boolean gate" | what that gate is | a method that returns yes or no |
| "cooldown groups via `tags` + `refireCheckTags` (same `minRefireDays` on every member)" | an instruction | "Give every member of the group the same" |
| "a ban written as an XML zero" | what is zero | a ban that sets one def to zero in XML |
| "Joiners without `populationEffect`" | the command, and what population intent is | both are stated |
| "Worker instance fields" | the command | "Do not set a field of the worker in ..." |
| "Per-faction data registered only at load" | what goes wrong | a faction that appears later has no data |
| "Study §6" | which study | the path is named |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without 1500, 33, `canKidnap` and "3-5 days" | 2 lost, exit 1. Check 1 did not see 1500, 33 or the code span. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 6 lost, exit 1 |
| check 1, check 2 | the rewrite, with `--also` | 9 items, 0 lost; 82 spans, 0 lost (check 2 also after the last repair) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the first draft | exit 0 each |
| `selftest_designer_cleanse.py` (names `next_version.md`) | the first draft | 288 checks, 0 failed |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-builder, read-only) read every line of both texts without the writer's reasoning, and checked each
correction in the decompiled 1.6 source.

| finding | repair |
|---|---|
| significant: a right-click or `Option_Close` removes a live demand, so the default branch never runs | `CanDismissWithRightClick` false, and our own Refuse option, in `SKILL.md` and `recipes.md` |
| the definition of a generic gate also covered `CanFireNowSub` | "a check that `parms.forced` skips" |
| the ThreatBig clock had no scope | one clock per target, unforced fires, Randy |
| "does not stay at about six" was more certain than the source | the old certainty; the chance never goes to zero under Randy |
| "one of four" closed an open list | "one or more of these" |
| history.md does not hold the evidence for each lesson | study §2 is named |
| the mod list had no date; C09 does not name two mods | dated; C09's scope is in history.md |
| eight letters test `ArchivedOnly`: nine do | nine |
| "never a direct worker call" was too wide; `mod_lessons.md` said the opposite | `def.Worker.TryExecute`; the `mod_lessons.md` line points at the queue |
| study: idea 21 and the C09 line | rewritten |
| `next_version.md`: guide and cut have the same fault | named |

A second fresh Opus reader (rm-judge) read each of those repairs and all changes outside `SKILL.md`.

| finding | repair |
|---|---|
| significant: after the timeout, a closed archived letter runs the default branch again | a Scribed `resolved` flag, in both files |
| significant: `Option_JumpToLocation` and `Option_ViewInQuestsTab` also remove a live demand | "no vanilla option that removes the letter", in both files |
| the vanilla precedents do not override `Removed()` | said in `recipes.md` |
| `Option_Reject` cannot hold a branch | "Write your own Refuse option" |
| the joiners trap had no command | `populationEffect` values, and what ignores the throttle |
| "dies with the map" reads as an engine fact | use a `MapComponent`, or delete the state |

No reader read the repairs of the second table. Nor did a reader read one added clause in study §1 (the `resolved` flag).
Each repair uses the words that the second reader proposed.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| all eight source mods retire / two are on the mod list | the second | 1: `ModsConfig.FULL.LATEST.xml` |
| only `Option_Close` removes the letter / four options do | the second | 1: `ChoiceLetter.cs` |
| a one-shot choice is safe when the letter is removed / the archive opens it again | the second | 1: `Letter.OpenArchived`, nine vanilla letters |
| `terrainAffordanceNeeded` is null for items / stuff items set it | null for most items | 1: `Items_Resource_Stuff.xml` |
| `forced` stamps nothing / `lastIncidentTick` is set | no cooldown and no ThreatBig clock | 1: `Storyteller.TryFire`, `StoryState.Notify_IncidentFired` |
| `bypassStorytellerSettings` needs no C# / it is a field of `IncidentParms` | the second; it also skips `earliestDay` | 1: `IncidentWorker.CanFireNow` |
| `recipes.md` §2: a direct worker call is allowed / `SKILL.md` §2: never | never; use the queue | 1: the flag acts only in `CanFireNow` |
| study: C09 is open / answered 2026-10-10 | the second, in two places | 2: `OWNER_RULINGS.md` row C09 |

None goes to the owner.

## Changed outside the skill file

`references/recipes.md` (§2), `references/mod_lessons.md` (one clause), `references/history.md` (new),
`design/RimMandrake/event_quest_wisdom.md`, `design/concepts/WeepingStones/cleanse/next_version.md`. The last file records a
fault of our walking condenser letter: it does not test `ArchivedOnly`, so the player can sell again from the archive. The
code was not changed, because the sale waits for the next version of that mod.

## Could not determine

None.

## What this run did not test

- No live game was driven. Each engine fact was read in the decompiled 1.6 source.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.

# Result: `RIMMANDRAKE_REWRITE_SKILL_QUESTS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-quests/SKILL.md`. Run 2026-11-23.

Base: `0e27683846f2bc5ecb19e023e766945e7e8424d9`
Also: skills/rimworld-quests/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 24,409 | 29,679 |
| words in linted prose | 2,580 | 3,490 |
| STE violations per 100 words | 4.07 | 1.43 |
| sentences over 20 words | 52 | 18 |
| flagged lines (mechanical) | 25 | 22 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 |

The long sentences that stay: lists of names, commands, and two short sentences that the lint joins at a bold lead.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "leave a branch that never arms" | what arms a branch | "never starts" |
| "Three consequences you will otherwise learn the expensive way" | nothing to do | "Three results of this model" |
| "Read the consumer before you name a variable" | which consumer | the node that consumes it |
| "The deadline ... Do not fake urgency you will not enforce" | what the fake is | kept, with its subject |
| "Every line is load-bearing" | what that means | "Each line is necessary" |
| "it is a ConfigError on a def that is not offerable at all" | which defs are offerable | the three conditions are listed |
| "reads the AMBIENT slate `inSignal` var" | what ambient is | the signal of the node around it |
| "Arming is easy to invert" | the act | "easy to start a branch at the wrong time" |
| "the storyteller turns [goodwill] into raids" | the condition | only if the faction becomes hostile |
| "Read those two before concluding" | which two | the two fields are named |
| "write it here" (§10, §11) | an agent may not edit the skill | file a lesson; a curation session adds it |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without "60000 ticks", `IncidentDef.cs:235`, 4,837, no `--also` | 3 lost, exit 1. Check 1 did not see 4,837 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 13 lost, exit 1 |
| check 1, check 2 | the rewrite, with `--also` | 21 items, 0 lost; 250 spans, 0 lost (also after the last repair) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the first draft | exit 0 each |
| `selftest_validate_quest.py` (new) | planted cases, old tool then new | 3 of 6 red, then green; 2 more red, then 8 green |
| `selftest_xmlonly_lint.py` (runs the validator) | after the repair | 7/7 ok |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) compared every line of both texts and the diff of each other file.

| finding | repair |
|---|---|
| significant: the advice to override `targetTags` kills the storyteller route | `World` stays unless a comp, tool or code fires the incident |
| significant: "the timeout still runs after success" is false | the timer runs on while the colony is on the site |
| significant: the validator's route test is blind to `isRootSpecial` alone, misses the star-rating ConfigError on a giver quest, and falsely warns on a decree | repaired in the tool, test first |
| significant: `design_and_community.md` still said an XML root has "no silent-drop trap" | corrected |
| the natural pool targets `World`, so the space test does not apply to it | corrected |
| the hidden-quest reason had no evidence line | added to `history.md` |
| an `<inSignal>` on `SendSignals` logs a red XML error | corrected |
| `<fallback>` was too strong; a factionless `factionOf` also drops the quest | corrected |
| `ERR` stated with no mention of the older live pass | added |

The reader's repair for the first finding (`World` plus `Map_PlayerHome`) would be a ConfigError
(`IncidentDef.ConfigErrors`); the repair says so.

A second fresh Opus reader (rm-judge) read each of those repairs, `history.md`, the validator and its selftest.

| finding | repair |
|---|---|
| significant: a giver quest of weight 0 passes the validator, and no giver picks it | tool, selftest, §7 |
| significant: a decree quest without `decreeTags` passes the validator | tool, selftest, §7 |
| significant: a storyteller comp that names the incident can fire a `Map_PlayerHome` one | §7 |
| `jawa/storyteller_fire` uses the current map, and its refusal is visible | §7 |
| the front matter still says that the text blanks | left: the description changes only with trigger evals |

No reader read the repairs of the second table, the §6 line on our own C# suffix (`site.RUT_SleepersWoken`), and the last
sentence splits in §9 and §10. Each repair follows what the second reader proposed.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| 151 shipped quests / 156 | 156 with 5 abstract parents | 1: the shipped `Data` folder |
| 249 `QuestPart` types / 244 | 244 | 1: the TypeDef table |
| the failed text is empty / `ERR: ` | `ERR: ` | 1: `GrammarResolver.ResolveUnsafe` |
| every `delayTicks` is whole days / short plain ticks | the second | 1: the shipped defs |
| `storeAs` has no signal / `asker.Destroyed` | the second | 1: `QuestUtility.AddQuestTag` |
| `SignalActivable` needs `inSignalEnable` / ambient default | the second | 1: `QuestNode_SignalActivable` |
| four listen modes / five | five | 1: `QuestPart.SignalListenMode` |
| `isRootSpecial` leaves the pool / it does not | the second, in four files | 1: `IsRootRandomSelected` |
| a throwing `TestRunInt` is silent / it logs | it logs | 1: `QuestScriptDef.CanRun` |
| `<inSignal>` on `SendSignals` parses clean / red error | red error | 1: `XmlToObjectUtils` |
| `arrivalMode` is an enum / a def with default `EdgeWalkIn` | the second | 1: `QuestNode_PawnsArrive` |
| `<choices>` may be optional / it throws when absent | required | 1: `QuestNode_GetRandomPawnKindForFaction` |
| the error is on `CreepJoinerArrival` / on `CreepJoinerArrival_Metalhorror` | the second | 1: the validator run |
| "write it here" / a skill edit only in a curation session | file a lesson | 3: `CLAUDE.md` §Skills |
| a load is 20-30 or ~25 minutes / `rimworld-load-round` figures | a pointer | 5 |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new), `references/vanilla_corpus.md`, `references/design_and_community.md`,
`references/mod_patterns.md`, `scripts/validate_quest.py` and `scripts/selftest_validate_quest.py` (new), a comment in
`src/RimMandrake/StrandedQuest/Defs/QuestScriptDefs/Quest_Stranded.xml`. The lesson
`20261112T044201Z-CLAUDE_ARCHMAGI_OFFLINE3-givequest-incident-world-target.md` is folded into §3 and §7, so its file is
deleted. The repaired validator now names `RUT_KyberDonationSmuggle`, which
`RIMMANDRAKE_FIX_GIVEQUEST_DEFS_TWO_SILENT_LOAD_TRAPS` already covers.

## Could not determine

None.

## What this run did not test

- No live game was driven. Each engine fact was read in the decompiled 1.6 source or counted in the shipped defs.
- The mod count figures of §9 (4,837, 410, ~40 mods) were not counted again.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.

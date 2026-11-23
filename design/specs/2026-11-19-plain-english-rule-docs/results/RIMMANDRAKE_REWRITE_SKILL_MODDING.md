# Result: `RIMMANDRAKE_REWRITE_SKILL_MODDING`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-modding/SKILL.md`. Run 2026-11-23.

Base: `2239895533256d2a8ca1382145bd3948cc5b3979`
Also: skills/rimworld-modding/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 29,064 | 40,118 |
| words in linted prose | 3,657 | 5,370 |
| STE violations per 100 words | 4.32 | 1.99 |
| sentences over 20 words | 68 | 47 |
| flagged lines (mechanical) | 36 | 28 |
| lines that a cold reader cannot act on (hand count, by the writer) | 35 | 0 |

The long sentences that stay are of four kinds: two short sentences that the lint joined at a bold lead; a sentence that holds a
command or a list of names; a kept slogan; one sentence of 21 to 25 words.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| 13 rule leads of §4 and 10 of §5b, each cut in mid-sentence | the rest of the rule | each is a whole rule, with the pointer to its full paragraph |
| "def", "patch", "minimal list", "def dump", "bridge" | what each word means | a table at the top |
| the two sentences about the decompiled tree | if the tree exists | one path, with a check |
| "Use it before inventing a Harmony patch target" | what "it" is | names `rimsage` |
| `mods/dev/RimDefDump`, `Utils/animal_inventory.py` | a path that exists | the live paths |
| "that always needed a real load" (hot reload never explained) | what hot reload is | defined |
| `python3 scripts/validate_patch.py` with `C:/` roots | a command that runs | a WSL command that runs |
| the "second failed hypothesis" rule (only named by `minimal-load.md`) | the rule, which §2 had lost | restored in §2 |
| "inspect the CONSUMER" | what a consumer is | defined |
| "append it to the matching topic file" | the legal route for a lesson | `lessons.py add` |
| the csproj build line | a path that exists | `winbuild.py` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without 2026-09-03, "181 of 744" and `modlist_swap.py` | 2 lost, exit 1 |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, exit 1 |
| check 1, check 2 | the rewrite, with `--also` | 61 items, 0 lost; 225 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py` selftests | none | pass; 19 of 19 |
| `selftest_validate_patch.py`, `selftest_close_evidence.py`, `selftest_detached_helper.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | the text after the first repairs | exit 0 each |
| `selftest_static_game_state.py` | the same | 5 of 150 FAIL: five unreviewed statics in FlowWorks C# (`RM_RaiderFetchFallen.cs`, `RM_SubmergeDraw.cs`). This run touched no C# |

Names of people: none in the old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-builder, read-only) read every line of both texts without the writer's reasoning. It checked the
engine claims in the local 1.6 decompile.

| finding | repair |
|---|---|
| significant: `traps.md` still told each agent to append to a skill file | now `lessons.py add` |
| "a patch that matches nothing logs nothing" is false for an unconditional patch | "a conditional" |
| the shared `Name=` case of one mod was left out | "in one mod or across mods" |
| the research-project rule lost its condition and "after a fresh cold restart" | both restored |
| `FindMod` was named without its key | "the exact About.xml `<name>`, never the packageId" |
| "absent mod logs nothing" holds only with no `<nomatch>` | stated |
| a true C# `Dictionary` has a third shape | stated here and in two reference files |
| zero grep hits: "no comp of that name exists" | "no vanilla def uses a comp of that name" |
| the validator can flag a correct vanilla `texPath` | stated |
| the fingerprint and `measure` had no pointer | pointers added |
| about 35k tokens, not more | corrected |

The same reader then read each repair and each reference edit. It found nothing significant and three minor lines: the research
recursion is conditional, `measure` is not on each PATH, and one reference line was too broad. The writer repaired the three.
No reader read those three repairs or the new ticket.
After the first landing (adc323949a), the prose check of `./publish` named 10 lines: pronouns, one "should", two undefined
names. The writer repaired them. No reader read those lines. "roster name" now means a name in the `<wildAnimals>` list.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `ParentName` needs an `Abstract="True"` parent / only a `Name=` | the second | 1: `XmlInheritance.TryRegister`; Core's `Stun` |
| a def with an unfound parent is discarded / loads alone | the second | 1: `XmlInheritance.ResolveXmlNodeFor` |
| a shared `Name=` in one mod is dormant / logs an error, second unregistered | the second | 1: `TryRegister` |
| a same-mod repeated defName is renamed / the second is skipped | the second | 1: `DefDatabase.AddAllInMods` |
| the shield belt has no comp / it has `CompProperties_Shield` | the second | 1: `Apparel_Belts.xml`, `CompShield.cs` |
| a wrong `GameComponent` constructor is silent / logs one line | the second | 1: `Game.FillComponents` |
| `FindMod` takes a packageId or a name / only the name | the second | 1: `ModLister.HasActiveModWithName` |
| filth refused on ALL natural terrain / one roofed exception | the second | 1: `FilthMaker.CanMakeFilth` |
| a mis-cased enum is silent / one line that names the file | the second | 1: `DirectXmlToObjectNew.DefFromNodeNew` |
| research recursion is unconditional / only for an unfinished project | the second | 1: `ResearchManager.FinishProject` |
| "Silence is success" / name a positive observation | the second | 3: "A patch that matches nothing logs nothing" |
| cold load 23-30 minutes / 15 to 30 | the second | 1: the measured table of `rimworld-load-round` §0 |
| mechanics enabled per biome / plain on/off with no biome | the second | 2: his card of 2026-11-21 |
| append a trap, re-package the skill / `lessons.py add` | the second | 3: root `CLAUDE.md` §Skills; `skills/README.md` |
| `get_defs` is scalar-only / `deep=true` | the second | 1: `JawaBenchTerrainTools.cs` |
| no local decompiled tree / one exists | the second | 1: md5 equal to the installed DLL |
| RimBridge has no `get_def` / it has | the second | 1: the bridge tools |
| the validator checks no `Defs/` / it does, but no field names | the second | 1: `validate_patch.py` banner |
| WSL `dotnet.exe build` on the clone / `winbuild.py` | the second | 1, 4: the old path is gone |

None goes to the owner.

## Changed outside the skill file

- `references/history.md` (new).
- `references/load-order.md`, `patch-operations.md`, `traps-xml-and-defs.md`, `traps-mods-and-managers.md`, `traps.md`: the false
  lines above, three cut fragments, one dead pointer.
- `research/RimMandrake/reference/rimworld_decompiled_source.md`: where the tree is.
- Filed `RIMMANDRAKE_FIX_OFFLINE_DEF_MERGE_REPLACES_WHAT_GAME_APPENDS` (the offline def scan replaces inherited lists; the
  engine appends them), with its red test. Not fixed here: the fix changes the output of several patch generators. The false
  comment and docstring of that tool describe its code, so they move with the fix.

## Could not determine

- "The def you are patching *around*" in the old §1. The new text says "each def that the patch relies on or works around".
- The old text gave no source for the measured share of "mod does nothing" reports. The line stays.

## What this run did not test

- No live game was driven. Each engine fact was read in the decompiled 1.6 source or in the game's XML.
- The order in which patch files of one folder load (the `ZZZ_` rule) was not traced.
- No C# was built.
- No measurement shows that an agent behaves better with the new text. The trigger evals were not run, because the
  description did not change.

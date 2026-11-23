# Result: `RIMMANDRAKE_REWRITE_SKILL_READING_RIMWORLD_GRAPHICS`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/reading-rimworld-graphics/SKILL.md`. Run 2026-11-23.

Base: `0ec3c3a8d2`
Also: skills/reading-rimworld-graphics/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 21,305 | 24,323 |
| words in linted prose | 2,738 | 3,157 |
| STE violations per 100 words | 4.67 | 1.74 |
| sentences over 20 words | 59 | 16 |
| flagged lines (mechanical) | 21 | 20 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0; 1 is under "Could not determine" |

Of the 16 long sentences, all but one are two short sentences that the lint joined at a bold lead or an emoji. The other
one is the "THIRD form" line, which is a bold lead joined to one sentence of 20 words. No long owner quote is in the file.

The front matter (`description` included) and every heading stay byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "a bug in your resolver" | what a resolver is | defined at first use |
| "the suffix ladder", "a rung" | what both are | both defined under "graphicClass changes what texPath means" |
| "a file STEM" | what a stem is | defined at first use |
| "the apparel disaster" | which event | named, with a pointer to the section that tells it |
| "The opposite mistake" with the pronoun "that" | which mistake | a subject in each sentence |
| "Read the checker's namespace assumption" | where the assumption is | `own_parent_exists` and `vanilla_uses` are named |
| "Without it every …" | what "it" is | "Without the letters" |
| "Check which side of that line you are on" | which line | stranded folder or resolver |
| "the own-mod rule … both bit" | what happened | "We paid for each one", then the two rules |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy with 7 planted losses (54, `Plant_HubbaGourd_Wild`, 373 of 397, `packsHoldingPath`, `VAEWaste_BaseInsect`, `DeathCuirass/Apparel`, 77,000) | 2 lost. Check 1 did not see the others. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 6 lost, exit 1. `Plant_HubbaGourd_Wild` is a new word, so no check looks for it. |
| check 1 | the final rewrite, with `--also` | 46 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 171 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_guiding_prose.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | new text | PASS |
| `test_resolve_texture.py` | the docstring edits | OK, 11 cases |

Names: no person is named in either text.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 4 real and about
20 trivial items.

| finding | repair |
|---|---|
| "One rung of `resolve_texture()` differs" (added line) was false: the loose rungs ignore the own mod, and the first rung that hits wins | three bullets say what the code does |
| the added definition of a fuzzy match made the apparel sentence false | definition removed; the cause is named |
| the added `no_graphicData` row did not match `plan_cells` | row and docstring corrected |
| the new code sample lost `.png` | restored, with Unity's own extension dropped |
| trivial: "renders in game", "say out loud", "not a small overstatement", `drawSize`, `dir_hint` classes, the validator conditions, `_m`, "reads nothing else" | repaired |

The same reader then read the repairs and found 0 real and 3 trivial items. Two were repaired (one sentence moved, one
history line). The third stays: "fuzzy" covers two kinds of match, and the instruction (leave it blank) does not change.

No reader read these later edits: the sentence that moved, that history line, the split of three long sentences ("Fuzzy
matching caused …", "Before you audit art", "For what to DO with the sheets"), and the docstring of `pnglib.py`.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `resources.assets` is on "the Windows machine" / several installs | Archmagi and SteveDesktop | 3: §There are several live games; the file is on ArchBig and ArchSmall |
| the validator treats a top folder as the mod's namespace / it compares the parent folder and Core defs | the second | 1: `own_parent_exists`, `vanilla_uses` in `validate_patch.py` |
| every manifest entry has `variant` / 238 of 239 do | each resolved entry does | 1: the manifest |
| the bundle ladder tries side suffixes for all / `dir_hint` limits a directory class | the second | 1: `resolve_texture()` |
| the def dump carries no `drawSize` / it does | it does, unless the dump is old | 1: `DefReflector.cs` `SafeUnityValueTypeNames`; two captures of 2026-11-23 hold 5,549 `drawSize` keys each in PawnKindDef |
| the sample saves as `m_Name` / never do that | the second | 1: `extract_bundle_textures.py` `rel_for` |
| `no_loose_png` means no loose file / no loose file and no bundled texture | the second; the docstrings in `animal_contact_sheet.py` and `thing_contact_sheet.py` too | 1: both `plan_cells` |
| only listed folders load / index the mod root also | both; a hit that only the root holds is checked against the list | 1: `ModContentPack.InitLoadFolders` (RimSage) |
| the own mod beats every other source / the loose rungs ignore it | the rule stands as advice; the code's scope is stated | 1: `resolve_texture()` |
| the reason table has 4 rows / the code has more | `no_graphicData`, `no_pawnkind` added | 1: both `plan_cells` |
| Pillow is not installed for WSL `python3` (in `thing_contact_sheet.py`, `rimworld-content-moderation/SKILL.md`, `WreckedMachines/Source/pnglib.py`) / it imports on Archmagi | "can be absent" in all three | 1: `import PIL` gives 12.3.0; UnityPy does not import |

## Could not determine

| line | question | who would know |
|---|---|---|
| "`0/3,469` on the game player's own file" | the current cache index holds 3,465 Core textures; the difference is either a game update or deduplication | a fresh run of `extract_bundle_textures.py` |

## What this run did not test

- No live game was driven. The lines on `jawa/thing_graphic`, `jawa/texture_audit` and `jawa/thing_explain` stand as
  written; the code agrees on `badTex` and `packsHoldingPath`.
- The code sample was not run. The frozen `official` dump was not read for `drawSize`.
- The trigger evals were not run, because the description did not change.
- No measurement shows that an agent behaves better with the new text.

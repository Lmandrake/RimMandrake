# Result: `RIMMANDRAKE_REWRITE_SKILL_START_PREP`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-start-prep/SKILL.md`. Run 2026-11-23.

Base: `b7e4a5a317dacf750fa52032b4aa1a23caf47a77`
Also: skills/rimworld-start-prep/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 26,486 | 31,030 |
| words in linted prose | 3,385 | 3,948 |
| STE violations per 100 words | 4.76 | 1.52 |
| sentences over 20 words | 71 | 23 |
| flagged lines (mechanical) | 30 | 27 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 |

The long sentences that stay are of these kinds: an owner quote (line of the ruling of 2026-08-15); a sentence that holds paths or a
list of writers or cases; and a bold slogan, kept word for word, that the lint joined to the short sentence after it. The flags that stay
are emphasis marks and a few pronouns.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "one game shared by five seats" | which game; the seats are gone | ArchBig named; ArchSmall named |
| "compare `Player.log`'s mtime to now" as the test that the game is down | which game, and the tool | `game_instance.py status` |
| "another seat" saved a stale view | who that is now | another window, or a tool by name |
| "(§7's verification)" | there is no §7 | `activeMods` count |
| "two traps" over a list of three | which two | three traps; which script each one bites |
| "OFFER THE MOD-STATE SYNC" / "Decide `--apply` yourself" | offer or decide | decide, and log it |
| "silencing that dialog is a judgement" | what to do | two conditions |
| "N mods … M" with no word that `--apply` writes every save | the scope of the write | `--saves` named |
| "Announce it" | how, and to whom | `game_lock.py query ArchBig`, then tell that window |
| "`loadBottom` is overriding `loadAfter`" (the triage table) | §2 of the same file says that it does not | the real causes |
| "append it to traps-mods-and-managers.md … add the title to the index" | a skill is edited only in curation | `lessons.py add` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the rewrite with a code span, a date, part of the quote and a version removed, no `--also` | lost items listed, the changed owner quote included |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 30 lost, exit 1 |
| check 1, check 2 | the first draft, with `--also` | 1 lost; 3 lost. Each one is restored |
| check 1, check 2 | the rewrite, with `--also` | 43 items, 0 lost; 145 spans, 0 lost (both run again after the last edit) |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_one_path_seam.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_validate_patch.py`, `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_checkers.py` | the draft | exit 0 each |
| `sync_mod_state.py` | `--help`; a bare run with games up (it refuses with the new text); a plan with `--saves none --force-running` | as described; nothing written |

Names of people: the old text holds none, and the new text holds none. The front matter is byte for byte the same.

## What was measured for the corrections

- **RimSort v1.13.1** (the installed version) was read as source. Its tier code ran on 20,000 random lists of 8 mods: 0 lists had a
  violated edge. With the spread step removed (the planted fault), 13,743 lists had one. The reader repeated both (0; 13,813).
- **RimWorld 1.6** was read with RimSage: `ModsConfig`, `ModLister.RebuildModList`, `Page_ModsConfig`, `Dialog_ModMismatch`,
  `PlayDataLoader`. The game was not driven.
- **The live files** (read only): RimSort settings and User Rules; `ModsConfig.xml` (327 lines, 315 active); `Version.txt`; the three
  newest DefDump manifests; the About.xml of Alpha Biomes.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning, and checked the new facts in
the RimSort source and our tools.

| finding | repair |
|---|---|
| "RimSort writes at no other moment" is false: Troubleshooting import, clear-mods, the missing file | the three cases named, in §1, §2, §3 and the history |
| `rimworld-load-round` §4 still named two write cases, and "what the game loaded" without the edit case | corrected there |
| `sync_mod_state.py` and `modsconfig_from_save.py` still said "rewrites on exit" | their text corrected |
| the list of writers left out `sync_mod_state.py --apply` and `loadsweep/` | added, and the list is worded as examples |
| "Hold the game" made the old "announce it" a lock, against the ruling of 2026-08-15 | "announce", query, do not wait |
| `--status` reads FULL or MINIMAL when no list was updated, not always UNRECOGNISED | said, here and in the modlists README |
| `v1_freeze/README.md` said that the rules hold the whole order | only the pairs they name |
| "Ten mods can each sit just after" against the sort by level | "load after"; after, not next to |

The same reader then read each repair and the whole of both files again. Three points came back, each repaired as the reader proposed:
`forbidden_mods.md` and `infrastructure/state/facts/operations.md` still said "only on a Save"; the clear-mods action empties the
`Mods` folder and can look like the recovery reset; the Troubleshooting tab can delete the config files. The writer read the
clear-mods and `_delete_game_configs` code before the repair.
No reader read these last repairs, nor the split of five long sentences after them (the opening paragraph, §5 step 5, and the
Scribe and `Version.txt` lines of §5a), nor the rewrap (the words of the rewrap were compared by program: identical).

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| the tier split deletes each `loadAfter` edge that crosses a tier; `loadBottom` + `loadBefore` is broken / the tiers spread first | no edge between active mods is lost; the tiers spread | 1: `sort_controller.py`, and the run above |
| ties break by graph traversal and input order / by name | topological level, then name | 1: `topo_sort.py` |
| §2 "redundant, not defeated" / §6 "`loadBottom` is overriding `loadAfter`" | redundant | 1 |
| the mod menu is "the only trigger" / the recovery reset, the mismatch dialog, four start cases | all listed | 1: game source |
| "RimWorld complains at launch" / only the verbose log names the entry | verbose log only | 1: `ModLister.RebuildModList` |
| "no 'unsaved changes' warning" / the Run button asks | both, each in its case | 1: `main_content_panel.py` |
| the watchdog sometimes updates the view / of what | mod folders and `.acf`, not the list | 1: `watchdog.py` |
| Community Rules source can be `None` / it is a git repository now | both cases | 1: `settings.json` |
| "every step is unreliable while the game runs" / "nobody blocks on game close for config files" | only Steam changes need the game down | 2: 2026-08-15 |
| "offer it, do not run it unasked" / "decide `--apply` yourself" | decide, and log it | 2: `delegation_policy.md` |
| "~23–30 minutes" / "15 to 30 minutes" | 15 to 30; the old figure is in the history | 1: the measured loads in `rimworld-load-round` |
| `grep -c` returns 6 / 320 | the layout depends on the writer | 1: measured |
| five seats, one tree, one install / four games, one clone each | the second | 4 |
| step 7 count / "`--status` compares counts" | `--status` compares ids in order | 1: `modlist_swap.py` |
| append to the trap file / a lesson is filed | `lessons.py add` | 3 |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new). False lines corrected in: `skills/rimworld-load-round/SKILL.md`;
`skills/rimworld-modding/references/load-order.md`, `references/traps-mods-and-managers.md`, `scripts/validate_patch.py` (one comment);
`skills/rimworld-start-prep/scripts/sync_mod_state.py` (docstring and two messages); `src/RimMandrake/Utils/check_declarations.py` and
`modsconfig_from_save.py` (docstrings); `infrastructure/state/modlists/README.md`; `deployed/config/v1_freeze/README.md`;
`infrastructure/state/facts/operations.md`; `design/Jawa/mods/REGROWTH_BOILING_LIFT_SPEC.md`; `design/Jawa/mods/forbidden_mods.md`;
`design/RimMandrake/world_remake_reinstate_list.md`; `design/V2_DREAMS.md`.

## Could not determine

- Whether RimSort's sort code of 2026-08-19 had the spread step. Nobody ran that version. RimSort's git history holds it.
- Why `koth.isid` is in ArchBig's list and not installed (`sync_mod_state.py` printed it). The run that holds ArchBig set that tier list.

## What this run did not test

- No live game, RimSort window or Steam client was driven. The Steam claims (§4) stay as they were measured earlier.
- `sync_mod_state.py --apply` was not run.
- No measurement shows that an agent behaves better with the new text.
- The trigger evals were not run, because the description did not change.

# Result: `RIMMANDRAKE_REWRITE_SKILL_DEPLOY`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-deploy/SKILL.md`. Run 2026-11-23.

Base: `ea11291de7`
Also: skills/rimworld-deploy/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 24,334 | 33,324 |
| words in linted prose | 2,861 | 4,395 |
| STE violations per 100 words | 4.89 | 1.39 |
| sentences over 20 words | 61 | 14 |
| flagged lines (mechanical) | 30 | 25 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 that this run could resolve |

Of the 14 long sentences, 12 are short sentences that the lint joined at a bold lead, an emoji or a code span. Two are single
sentences: the old bold rule "When enabling a mod that leans on another mod's C#", kept word for word, and the last sentence of
the gated-out bullet (21 words). The front matter (`description` included) and every heading are byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "`<repo>/custom_patches/<ModName>/`" | a folder that exists | `src/<tier>/<ModName>/`, with the tiers |
| "tell CHECK before any shutdown" | who CHECK is | the reboot gates, by section |
| "safety net (§ below)" | the section; it is in another skill | the skill and its heading |
| "a spike" | what it is | "a small test list" |
| "`--live <dump>`" | which folder | the `DefDump` folder |
| "drift", "load-set", "fingerprint", "derived", "coverage", "companion" | what each means here | one plain sentence each |
| "Minimum viable folder:" two paragraphs above its figure | the figure | the line is at the figure |
| "It is PER-FILE" | what to do with it | the next bullet says what not to infer |
| "published by the seat that measures them" | which seat | `game_paths.py`, `refresh.py`, `observed/LIVE.md` |
| "`tool_surface()` over both DLLs" | which DLLs | the built one and the one in `BridgeTools` |
| "If it does not say 578" | a count that is true today | the count of the list that the game will load |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy of the first draft without `801bd127`, 23–30 and one `MayRequire` | saw none of the three. Its one loss was a real loss of that draft (a quote), now repaired. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | the 3 planted losses seen (4 lines), exit 1. It also saw two real losses of that draft, now repaired. |
| check 1 | the final rewrite, with `--also` | 47 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 171 spans, 0 lost |
| selftests of `rule_doc_lint.py`, `checkable.py`, `batch_done.py` | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_hugethings_test_races.py` | the text before the last repairs | PASS |
| the `selftest_deploy_*` files under `src/RimMandrake/Utils/`, `selftest_game_instance.py`, `selftest_game_paths_env.py` | after the tool fix | PASS |
| `validate_patch.py`, one patch file | a `C:/` root in WSL | `UNMEASURABLE`, no verdict |
| the same | the three `/mnt/c` roots and `FULL.LATEST` | 0 errors, 4 min 4 s |
| `deploy_custom_mods.py --gate --mod Pits`, `--mod Contagion` | none | `no such mod in the repo`; refused as folded |
| the §4 `diff` | today's two lists | no difference |

Names: no person is named in either text. "CHECK", "BUILD" and "BENCH" stay only as date marks or in the history file.

## What the meaning read found

A fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. The report had 25 entries. Some
entries only confirm a new fact. Each defect is repaired:

| finding | repair |
|---|---|
| §3: a `kept` line is not always a hand edit (a newer clone's file) | named, with "level your clone first" |
| §7: the announce rule was lost, and a pre-launch gate was put before the close | bridge, owner's play, deploy, preflight, announce, in that order |
| §9: "no `~` line means the same bytes" is false for `+`, `H` and a run with no `--mod` | limited |
| §2, §9: "every mod" is false for folded biome members | `--compose biomes` named |
| §2: an uncommitted file has no log | said |
| §8: the load-round waiver was lost; "one mod at a time" was weakened | both restored |
| §5: the plan line for a hold with no reason contradicted itself | split: hold with no reason, no hold |
| §3: the heading against its body; deletes after a refusal; `--pull` brings back deleted files | each said |
| §7b: fingerprint order; "coverage"; `DEF_DUMP` against `DUMP_ROOT`; "the one way" | corrected |
| §4: a limit on the spike rule; "each XML that it did not list" | restored; reworded |
| §1: the Player.log route to the loaded copy was lost | a route that today's log supports |
| §9: "early measurements" was not in the old text | "readings run from ~15 to 23–30 minutes" |
| companion: names only; `--gm`; no DLL path; gated out against absent | each said |

The plan asks the same reader to read the repairs. A resumed helper runs in the background, and this run ends with its turn. So
a second fresh Opus reader read the repaired parts once. That reader found 5 things. Four are repaired:

- `VERIFIED in sync` does not count a kept `-` file.
- The `defs.sqlite` row was wrong. The reader probed `_staleness` on temporary folders.
- The `git log` line had no limit.
- The §3 table did not fit the composed target.

The fifth is not repaired. argparse takes an abbreviation such as `--inst ArchSmall`, and the early reader of `--instance` does
not see it, so that run would write ArchBig's folder. Nobody has reported it, and no doc that this run read writes that form: not
worth the touch. No reader read the last four repairs. After the first landing
(`19b2b9bbaf`), the prose check of `./publish` named 19 lines: 16 pronouns, 2 terms and 1 state. All are repaired in the same run, the
slogan "It is PER-FILE, not per-mod" included (now "A hold is PER-FILE, not per-mod"). No reader read those repairs.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `custom_patches/` / `src/<tier>/` | `src/<tier>/` | 1: `SRC_TIERS` |
| "Adding mandrake.jawa.patches(...)" on every launch / the log | the XML messages `[File: ...]` | 1: 0 matches in `Player.log` of 2026-11-23 |
| "Five seats share this tree" / a clone per run | clones, one `Mods` folder per game | 3: §Git |
| "tell the owner before you write" / the Conductor decides | the Conductor | 3: §Only five acts stay his |
| packageId "in the owner's path" / the same | the Conductor, with `NAMING_SCHEME_PLAN.md` | 3 |
| a `-` file "that `--apply` is about to destroy" / the tool keeps it | three kinds of `-` line; `~` is the danger | 1: `_run`, `repo_deleted` |
| `C:/` roots / WSL | `/mnt/c` | 1: measured |
| "never `Defs/`" / the tool reads both | both | 1: `validate_patch.py` |
| "If it does not say 578" / 315 | the count of the list that will load | 1: parsed |
| hold paths "relative to `src/`" / `<ModFolder>/...` (`traps.md`) | `<ModFolder>/...`; the header of `src/DEPLOY_HOLD.txt` is corrected too | 1: the key in `split_held` |
| "A reason is REQUIRED" / the tool accepts none | both said | 1: `_run` |
| a folder with no packageId deploys / refused | refused | 1: `_run` |
| the silent lock failure / `FAILED to write` | the lesson stays; today's output is named | 1: `copy` |
| "tell CHECK" / retired seat | the reboot gates. `rimworld-load-round` §6 still says CHECK; its own item `RIMMANDRAKE_REWRITE_SKILL_LOAD_ROUND` holds that file | 4 |
| "md5 is the only way" / the plan compares bytes | both routes | 1: `same_bytes` |
| "One mod at a time" / load-round §3 "Batch by ambiguity" | one mod, unless the load is shared on purpose | 5: the line cites §3 |
| a byte scan / an exact read | exact; the scan lessons are in history | 1: `tool_metadata.py` |
| dump facts in `observed/LIVE.md` / its last dump entry is of 2026-09 | location and freshness from the code; holes from `LIVE.md` | 1 |
| `refresh.py` row "current" for a pruned capture / `_staleness` | STALE today; the lesson stays | 1: probed |
| "one game", "23–30 minutes" / several games, ~15 | both readings | 3, `CLAUDE.history.md` |

## A tool fault found and fixed in this run

`deploy_custom_mods.py --instance ArchBig` raised `InstanceError` at import, although root `CLAUDE.md` says that every tool takes
a game name. The test is `deploy_takes_every_game_name` in `selftest_game_paths_env.py`: red before the fix (5 passed, 1 failed),
green after (6 passed). The second reader read the fix.

## Could not determine

| line | question | who would know |
|---|---|---|
| "An in-place `open(dst, "r+b")` write lands byte-identical" | which tool did it; git shows no such code in `deploy_custom_mods.py`. The text says that the tool has no such route | the session that measured it |
| `measure` on the Mac laptop | is it still true today? The text keeps its date | a session on that laptop |

## What this run did not test

- No deploy was applied and no live game was driven.
- `--defs` with `C:/` roots under Windows python was not run.
- No measurement shows that an agent deploys better with the new text.
- The trigger evals were not run, because the description did not change.

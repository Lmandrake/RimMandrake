# Result: `RIMMANDRAKE_REWRITE_SKILL_LOAD_ROUND`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-load-round/SKILL.md`. Run 2026-11-23.

Base: `6cd5f791849c6089176babd456c757442fbe018e`
Also: skills/rimworld-load-round/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 26,955 | 32,400 |
| words in linted prose | 3,596 | 4,452 |
| STE violations per 100 words | 4.31 | 1.86 |
| sentences over 20 words | 71 | 34 |
| flagged lines (mechanical) | 27 | 26 |
| lines that a cold reader cannot act on (hand count, by the writer) | 12 | 0 that this run could resolve; 3 listed under "Could not determine" |

Kinds of the sentences over 20 words that stay: an owner quote (2 rulings on test lists, the 2026-10-24 quote); a sentence that
holds a command, a path, a log string or a list of names; two short sentences that the lint joined at a bold lead or a colon.
A few fit no kind, by one or two words each: the lines on content mods, saves and screenshots, the ModsConfig timestamps, the
bare-start cause and the triage order. The front matter (`description` included) and every heading are byte for byte.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| the §4 code block | the pointer line "More traps" stood inside the bash block, as a command | the pointer follows the section |
| `.../Config/ModsConfig.xml`, `.../workshop/...` | a path that runs | `$CFG` and `$WORKSHOP` |
| the dump marker command | a command that bash can run (the old one was cmd.exe syntax) | the `/mnt/c` path |
| "tells CHECK" (§6, §9) | who CHECK is: a retired seat | the stamp, and the search for waiting assemblies |
| "tier" | what a tier is | one sentence at first use |
| "decision strings" | what one is | one sentence in §2 |
| "signature" in §3 | what one is | one sentence |
| "Never mix the two families" | which families | "undo a swap with the tool that made the swap" |
| `jawabench-init-line-is-lazy.md` | the file: it is not in the repo | the source file is named |
| "read the mechanism note there" | where | `check_config_errors.py` and the note at the check |
| "That line used to say it did" | which line | history file |
| "per-seat queues", "`traps-*.md`" | where a finding goes now | `rimflow file`, `lessons.py add` |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `COLD_LOAD_STATIC_CTOR_STALL_1`, 81.6%, one `sweep_load.sh` and `RaceProperties` | 2 lost, exit 1. Check 1 did not see `RaceProperties`. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 4 lost (the id counts twice), exit 1. Neither check saw the one lost copy of `sweep_load.sh`. |
| check 1 | the final rewrite, with `--also` | 72 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 182 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work`, `selftest_guiding_prose`, `selftest_skills_registered_or_listed`, `selftest_validate_skills`, `selftest_game_names_prose`, `selftest_retired_era_gone`, `selftest_hugethings_test_races` | new text | PASS |
| `selftest_modset_builder_restore`, `selftest_modset_builder_mods_tier`, `selftest_modset_biomes_sprint`, `selftest_modset_reset_repair` | the changed docstring and refusal text | PASS |
| the §4 block | the parse and `stat` lines, run on the live file | 23 active; mtime printed. `grep -c` gave 6 and `grep -o` gave 28 on the same file, as the block says |

Names: no person is named in either text.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 14 items. All are repaired.

| finding | repair |
|---|---|
| the preflight line checked the full list for every load, and did not say game down | one form per list, game down, `--seat` |
| the `modset_builder.py` guard left no next act, and its list was incomplete | both guards named, with the next act |
| `harvest_log.py` exit codes were partly false | corrected, for a run without `--show` |
| "the note at that check" is not printed by `--show` | `check_config_errors.py` |
| "a companion that failed to load never writes the line" invites a false verdict | absence is UNMEASURED; `--list-tools` settles it |
| the waiver was widened; the bisection cost had become conditional | both restored |
| §6 heading "announce" against "no window gets a message"; companion DLLs missed | the stamp is the announcement; the companion run is named |
| `game_instance.py stop` refuses and needs `--instance`, `--force` | added |
| the direct start also follows a silent Steam | added |
| "in two cases" is exhaustive | "two cases are known" |
| "`acc_2026*` tiers add 31-46" | the old words, with what is UNMEASURED |
| "the only time the previous `Player.log` exists" | one old generation stays, by name |
| "15 to 30 minutes, measurements in §0" | measured 15 to 25; plan for 15 to 30 |
| "one hazard remains" | two hazards |

The same reader then read each repair and the code diff once. It found 7 faults. Six are repaired: the wait on an old dump
manifest (§8), one remedy for two guards (§4, the bridge gate read in `model.py` `bridge_gate`), `--deep` and the list first
(§9), the stamp after the close (§6), three gaps of `launch` and `stop` (§10), and the two code texts. The seventh asked for a
new §6 heading; the heading stays word for word, because other files cite it, and the text below it now says what the
announcement is. No reader read these last repairs. They are: the guards bullet (§4), the announcement bullet (§6), the two
exit code 2 sentences (§8), the preflight bullet (§9), the Steam, "already running" and `--instance` sentences (§10), the
`harvest_log.py` comment, and one refusal sentence of `modset_builder.py`. The prose check of `./publish` then named 9 lines (7 pronouns, the beggars
patch, "the ledger stamp"). All are repaired in a second landing. No reader read those either.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.
The item's step 2 says "list the conflict; do not pick". `batch_plan.md` says to settle each conflict, and it is the later text.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| "one game shared by five seats" / several games | several games | 3, 4 |
| a load costs 23–30 min / ~15 min (2026-09-07), 18.5-21, ~14.5 | each figure with its date | 1: `load_policy.json`, `game_instance.py`; `conflicts_settled.md` |
| §10 "never the bare `.exe`", `steam.exe -applaunch 294100` always / the tool starts ArchSmall, and sometimes ArchBig, directly | the tool decides; the heading stays; a start by hand stays forbidden | 1: `game_instance.py` `fire_a`, `launch` |
| `Stop-Process -Force` on the image name / two games on one machine | `game_instance.py stop` | 1, 3 |
| the JawaBench line appears on the first tool call / at game load since 2026-10-10 | dated both | 1: `JawaBenchInit.cs` |
| `Bridge token:` is the ready signal / ArchSmall writes a port line | both named | 1: `logwait.py` |
| RimWorld rewrites the list only in-game / a recovery reset also writes it | two known cases | 1: §0, `references/traps.md` |
| "no config file waits" / `modset_builder.py` refuses while the game runs | the ruling binds agents; the tool's guard is named with its next act | 1, 2 |
| `modset_builder.py` docstring and `harvest_log.py` comment "rewrites on exit" / measured false | both corrected; the refusal text of `modset_builder.py` too (it named a 3-minute rule that is gone) | 1 |
| a new assembly rides solo / the three-assembly waiver | solo, with the waiver as its exception | 2: the waiver; `spending-a-load.md` |
| tell CHECK / CHECK is retired, a relay is stamp-only | the stamp and a search for waiting assemblies | 3, 4 |
| findings to per-seat queues / the one list | `rimflow file`; lessons with `lessons.py add` | 3 |
| `mandrake.inhabited` loads last / `mandrake.rm.inhabited`, not last | corrected | 1: `ModsConfig.MINIMAL.xml` |
| "the minimal list does not have the content mods" / it holds a few | "most" | 1: the same file |
| "~60 s/cycle on the minimal list" / `gen_config.py` writes its own 9-mod base | "a small list" | 1 |
| delete throw-away saves / canonical and option saves stay | the rule names what it never covers | 3 |
| `refresh.py` full-load need / the `official` dump is frozen | pointer added | 3: `GAME_STATE_WORKFLOW.md` |
| the log that persists is in `rimbridge/references/traps.md` / `traps/lifecycle.md` | corrected | 1 |

## Could not determine

| line | question | who would know |
|---|---|---|
| the three-assembly waiver | whether the waiver covers more than three. Round 6 rode five (2026-10-26). No ledger ruling matches "batch it" | the owner; the text dates from 2026-08-13 |
| "`acc_2026*` tiers 31-46" | added mods or a total | a count after dependency closure |
| "a pre-flight census would catch" | no tool for the type-token half was found; `preflight_bridge.py` does other checks | the author of the 65-DLL pass |

## What this run did not test

- No live game was driven. The launch, stop, swap, sweep and dump commands were not run.
- No measurement shows that an agent spends a load better with the new text.
- The trigger evals were not run, because the description did not change.
- Whether Steam Cloud restores saves of ArchSmall is UNMEASURED.
- `skills/rimworld-deploy/SKILL.md` §7 still says "tell CHECK before any shutdown". A live run holds that file
  (`RIMMANDRAKE_REWRITE_SKILL_DEPLOY`, the rewrite of the deploy skill), so this run did not edit it. A note is on that item.

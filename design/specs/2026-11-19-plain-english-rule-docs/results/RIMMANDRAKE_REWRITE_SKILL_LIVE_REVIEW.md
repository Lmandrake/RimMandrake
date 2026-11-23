# Result: `RIMMANDRAKE_REWRITE_SKILL_LIVE_REVIEW`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-live-review/SKILL.md`. Run 2026-11-23.

Base: `78750f480b`
Also: skills/rimworld-live-review/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 29,533 | 32374 |
| words in linted prose | 4,018 | 4591 |
| STE violations per 100 words | 4.23 | 1.57 |
| sentences over 20 words | 77 | 28 |
| flagged lines (mechanical) | 25 | 23 |
| lines that a cold reader cannot act on (hand count, by the writer) | 9 | 0 that this run could resolve; 4 listed under "Could not determine" |

The long sentences that stay, by kind. Owner quotes: the walkthrough rule and §8d items 1 to 5. Sentences that hold a
command or a code name: the `settlement_attack`, `refresh_rect` and `clear_log` lines. The others are two short sentences
that the lint joined at a bold lead, a closing quote mark or an emoji.

The 🔴, ⚠️ and ⛔ marks that stay cause the flags. The 🔑 mark and the `⇒` marks are gone.

## What stays byte for byte

The front matter (`description` included), every heading, every owner quote. In the command block, three comments changed.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "nothing fighting it" | what fights a subject | four named examples below the line |
| "pattern: trimmed list = …" as one clause | that this is the live-scene recipe | a bullet under the live scene |
| "that is the signal" | which signal | the signal is named first, then the act |
| "a reload is the reliable way" beside two routes | which route comes first | two bullets, with the fallback named |
| "takes that entry path" | which path | the way a player enters a map |
| "that split is the single most important framing choice" | which split | "`--layout` … picks art or mood" |
| "(§4)" for weather and ash drifts | the section is wrong | §5 |
| "Two more from the same family" | a second full copy of §5 | a pointer to §5 |
| "It is safe … unless" in one long clause | the two limits | two bullets |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `BRIDGE_MAPGEN_STALE_FINALIZE_1`, `debugRotLocked`, `PawnRenderNodeProperties_Spastic`, the 149 and the 62.6 | 2 lost (the id, the 149). Check 1 did not see the other three. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 6 lost, exit 1 |
| check 1 | the final rewrite, with `--also` | 67 items, 0 lost |
| check 2 | the final rewrite, with `--also` | 199 spans, 0 lost |
| `rule_doc_lint.py`, `checkable.py`, `batch_done.py` selftests | none | PASS; 19 of 19; GREEN, 12 cases |
| `selftest_skills_by_work.py`, `selftest_guiding_prose.py`, `selftest_skills_registered_or_listed.py`, `selftest_validate_skills.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py` | new text, before the meaning read | PASS |

Names: no person is named in either text. Each creature and race name is as often in the new text as in the old.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read both texts without the writer's reasoning. It found 8 real and 18
trivial items. The reader wrote that the quotes of the walkthrough rule and §8d are word for word.

| finding | repair |
|---|---|
| §8b: the refusal covers any loaded map, and `why` is optional | both corrected |
| history: the wrong commit for the finalize step | `2b235a8960` |
| §3: "blocked" narrowed to black maps; "no bridge route" narrowed | wording closer to the old line; both recorded in the history file |
| §3: the heading says "home map", the text says otherwise | the text now says that the map does not become one |
| §3: "two things keep the map" is incomplete | "two things that you can arrange"; the full list is named |
| §5 against the comments of the command block ("midday") | the comments corrected |
| `lightspeed-authoring.md` lost "pause, then read the state back" | restored |
| strength or cause moved: pause keeps the map, "fall back", "freely", "should", "staring", "end-to-end", "throwaway", framing args | restored |
| `--kill-hostiles` change had no record; Player.log "last of its sources" was false | record added; corrected |
| added words: "the other nine", "the cause is not known", "zooms out", "on that list" | removed |

The same reader then read each repair. One repair had added a false statement: `pyre_clear.png` "(clear)". `--two-pass`
sets no weather before its first shot. The comment now says "the running weather", and §5 says to add `--weather Clear`.

No reader read the last four edits: that comment, the `--weather Clear` sentence of §5, and two reasons in the history file. Not
repaired (the reader called each one polish): "every step below" in the helper section (old wording), "on a pawn" in §5,
the dropped "which is the whole reason it exists" of §8a, the place of one date in §3.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 2 his later ruling; 3 root `CLAUDE.md`; 4 the thing is gone; 5 the obvious answer.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| a paused barrier is PLANNED / it is built | built. Also corrected in `lightspeed-authoring.md` §8 | 1: `JawaBenchShotSettleTools.cs`, `rimbench/shotsettle.py`; live pass 2026-11-06 |
| `references/traps.md`: unpause ~1 s before a shot / a shot that costs no tick | `settled_shot` | 1: the same |
| "each generated map is non-home" / the call makes a player settlement | depends on the map parent; read `parentFaction` | 1: `JawaBenchSocietyTools.cs`, 33854f6f5c |
| "colonists make it a home map" / they block its removal | they block its removal | 1: `Settlement.ShouldRemoveMapNow`, `Map.IsPlayerHome` (RimSage) |
| "downed colonists un-home the map" / a live colonist counts, downed or not | a dead colonist does not count | 1: `MapPawns.IsValidColonyPawn` |
| "suspect until you call `jawa/map_commit`" / the call finalizes itself | read `mapFinalize.failedSteps` | 1: 2b235a8960 |
| "no bridge route enters a map as a player does" / `jawa/settlement_attack` | no known route; the tool is named as UNMEASURED | 1: `JawaBenchGroupTools.cs` |
| `--daylight` steps toward midday / it steps 14,000 ticks | the second | 1: `stage_review.py` `daylight()` |
| `--clear chunks` clears rock / it clears every Item | the second | 1: `stage_review.py` `clear()` |
| `--two-pass` shoots a clear pass / it sets no weather | the second | 1: `stage_review.py` `main()` |
| `--kill-hostiles` clears every one / it stops after six rounds | the second | 1: `kill_hostiles()` |
| `time_set_ticks` is safe on a staged scene / it is refused beside a colonist | both limits stated | 1: `JawaBenchResearchTimeTools.cs`, `JawaBenchVitals.cs` |
| "swap … and back after a load" / no restore step | no restore | 3 |
| the endpoint comes from Player.log / several sources | several | 1: `resolve_endpoint` |
| one pawn per XenotypeDef / `--per` 3 | 3 side by side | 1: `stage_xenotype_grid.py` |
| step "freely" / the rule on a long advance | pointer added in §2 | 2: `debug_process.md` § "A long clock advance" |
| the memory file `generated-map-culled-unless-home` / no such file | moved to the history file | 4 |

The three faults of `stage_review.py` are a ticket: `RIMMANDRAKE_FIX_STAGE_REVIEW_MIDDAY_IT_READS_NO_HOUR`.

## Could not determine

| line | question | who would know |
|---|---|---|
| "MINIMAL + content mods + overrides" | which mods are the overrides | the author of the first art walk (2026-09-14) |
| "The combined review list loads in ~80 s" | which list it is | the author of the 2026-09-17 campaign note |
| rootSize 11 is "Closest"; `references/traps.md` says 8; the station capture asks ~6 | the number depends on the camera mod of the list (`CameraDriver.CurrentZoom` compares with `sizeRange.min`) | a live read of `get_camera_state` on each tier |
| "caught all four" in §8a | whether a parameter guard can catch a tool name that does not exist | the session of 2026-09-20 |

## What this run did not test

- No live game was driven. Each bridge claim that the code does not decide stands as written.
- No measurement shows that an agent stages a better shot with the new text.
- The trigger evals were not run, because the description did not change.
- The three lessons in the inbox whose home is this skill were not folded in: the item covers the rewrite only.

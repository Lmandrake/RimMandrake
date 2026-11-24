# Result: `RIMMANDRAKE_REWRITE_SKILL_WORLD_EDITING`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/rimworld-world-editing/SKILL.md`. Run 2026-11-23.

Base: `e9794709b8494333529b88c45c8b06cd2e15a2e6`
Also: skills/rimworld-world-editing/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 25,228 | 29,138 |
| words in linted prose | 2,644 | 3,195 |
| STE violations per 100 words | 4.46 | 2.35 |
| sentences over 20 words | 45 | 27 |
| flagged lines (mechanical) | 46 | 44 |
| lines that a cold reader cannot act on (hand count, by the writer) | 11 | 0 |

The long sentences that stay are mostly two short sentences that the lint joined at a bold lead, a quote or a code span. Six
are single sentences that hold a command, a list of code names or a bold lesson of the old text. The flags are emphasis marks
that were there before.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "The world screen", "the bridge", `rb`, "NRE" | the meaning of each term | defined in the head |
| "that is how the no-op in §3 was caught" | §3 holds no such no-op | the no-op is named in the line |
| "CHECK built 25 companion `[Tool]` methods" | who CHECK is; the tool list is incomplete | history.md; the other registered tools are listed |
| "DONOR def" | what a donor is | "the original biome def that ours replaced" |
| "Ordering is ours to police" | which order | "landmarks before settlements" |
| "The four traps" (5 entries), "Five more" (6 entries) | a count that is wrong | the heading stays; a line says the number |
| "`LIVE.md`" | the path | `observed/LIVE.md` |
| "`world_features_set` … needs that `uniqueID`" | the parameter to pass it in | `featureId` |
| "it is inert on the frozen world" | what is inert | "the worker does nothing" |
| "`jawa/clear_ui` does not close these" | what "these" are | says which windows |
| "the fix is regenerating, not editing" | who decides | step S7 of the runbook |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`), with `--also` | a copy without one path, "30 s" and "2026-09-12" | 4 lost spans listed, exit 1 |
| check 2 (`rule_doc_lint.py keep`), with `--also` | a copy without "0.1", "295,732", `AncientRuins` and `LIVE.md` | 4 lost, exit 1 |
| check 1, check 2 | the rewrite | 60 items, 0 lost; 245 spans, 0 lost |
| the selftests of `rule_doc_lint.py`, `checkable.py`, `batch_done.py` | none | pass; 19 of 19; GREEN, 12 cases |
| `selftest_warn_skill_unwired.py`, `selftest_guiding_prose.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_game_names_prose.py`, `selftest_retired_era_gone.py`, `selftest_validate_skills.py` | the first draft | exit 0 each |
| `selftest_tidal_lock_guard.py` (it reads the runbook) | the `runbook` step only | 5 PASS. The full run did not end in 8 minutes: UNMEASURED |

Check 2 found two losses in the first draft (`*_validate`, one quoted phrase). Both are repaired. Names of people: none in the
old text or the new text. The front matter is byte for byte the same.

## What the meaning read found

A fresh Opus reader (rm-judge, read-only) read every line of both texts without the writer's reasoning: 1 significant finding,
11 minor.

| finding | repair |
|---|---|
| significant: "Close what is left" in §4 would close the landing page, and the world is lost | close only your own dialog; never `Page_SelectStartingSite` |
| "ten derived columns, which no tile field holds" (`riverDist` is a field) | "ten more columns" |
| the raw bridge no longer drops every undeclared name | `JawaBenchArgGuard.cs`; the two cases that still drop |
| runbook row S7 says settlements read `None` | `settlementCount` |
| `silent-failures.md` §6 ("cannot be checked offline") held a fact that can be checked | that entry is removed |
| `*_validate`, direct `AddMutator`, the ice field: changed, not recorded | rows in history.md |
| `sw_Sarlacc` "has no mutator at all" weakened | restored, with the mutator's name |
| `displacedMutators` stops at 25 | `displacedMutatorCount` |
| the cache audit skips temperatures by default | `includeTemps=true`; tiles or `all=true` |
| "there is no other lever" lost | restored |
| "did or did not land" lost | restored |

The same reader then read each repair and found none wrong. After that read the writer split three sentences to reach the STE
target (the first paragraph, the cache reset, the two cases of the raw bridge). After the first landing (`02855348ba3b`)
the prose check of `./publish` named 13 lines, and the writer repaired each one. One repair corrects a false date: the frozen marker
of the tiles CSV says 2026-09-07. No reader read the three splits or those 13 repairs.

## Conflicts and stale lines: settled

Rules: 1 the code or the live tool; 3 root `CLAUDE.md`; 4 the thing is gone.

| conflict or stale line (side 1 / side 2) | decision | rule and evidence |
|---|---|---|
| `isValidTile` after the add / before the add | before; not a gate | 1: `JawaBenchWorldTools.cs`; the same order on 2026-08-26 |
| `allowRoads`/`allowRivers` absent from the dump / present | present, 61 of 61 | 1: capture `2026-11-24T00-35-54Z` |
| each read stops at 100 rows and hides it / `limit` is a default and the cut is reported | the second | 1: the tool code |
| `list_factions` cannot count settlements / `settlementCount` | it can | 1: the tool code |
| a wrong roster needs a new world / `jawa/faction_create` | both routes; S7 decides | 1: `JawaBenchFactionTools.cs` |
| `clear_ui` does not close a dialog (measured 2026-08-15) / the default call closes `Window_Dev` | both stated; not tested live | 1: 1.6 source `Dialog_Debug : Window_Dev` |
| only a reload clears `Tile`'s caches / `jawa/world_tile_cache_reset` | the tool | 1 |
| all terrain comes from `terrainsByFertility` / patch makers and rock first | the second | 1: `MapGenUtility.TerrainFrom` |
| water never freezes from temperature / fresh water does | sea water never freezes | 1: `FreezeManager`, `Terrain_Water.xml` |
| plant density has no other factor / `plantDensityFactor` and game conditions | the second | 1: `GetDesiredPlantsCountAt` |
| `Current.Game` is null at the landing page / it holds the world | it holds the world | 1: `Page_CreateWorldParams`, `WorldGenerator.GenerateWorld` |
| `CLAUDE.md`'s "world remake is the last step" / the heading of today | cites the heading of today | 3 |
| `biome_probe` fails with Alpha Animals / Alpha Animals is retired | both stated | 4: `retired_mods.json` |
| Geological Landforms filters mutators / it is not on the full list | both stated | 4: `ModsConfig.FULL.LATEST.xml` |

None goes to the owner.

## Changed outside the skill file

`references/history.md` (new); `references/traps.md`, `mutators-and-objects.md`, `road-networks.md`, `river-networks.md` beside it;
`skills/rimbridge/references/silent-failures.md`; `design/Jawa/worldbuilding/WORLDMAP_BRIDGE_SURFACE.md` and
`rimworld_worldmap_loadsavecreate.md`; `06_remake_runbook.md` and `15_conductor_plan.md` in
`design/RimMandrake/world_remake_2026-10-19/`.

## Could not determine

- Why the save call NREs at the landing page. The 2026-10-20 run names `Find.GameInfo/TickManager`; nobody read the cause.
- Why `clear_ui` read `closedCount: 0` on 2026-08-15. A live call with `Dialog_Debug` open would show it.

## What this run did not test

- No live game was driven.
- The description still says 33 tools and "the 100-row limit cap". The code registers 37. A description changes only with the
  trigger evals of `skill-creator`, which were not run.

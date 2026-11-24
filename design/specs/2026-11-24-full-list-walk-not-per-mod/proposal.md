# The full mod list is not a step of each mod's road

Item `RIMMANDRAKE_PROPOSE_FULL_LIST_WALK_NOT_PER_MOD_ARCHBIG_IS_THE_LINE`. Measured 2026-11-24, 8:31 to 9:00 AM PST.
State: the owner said "go" to option 1 (ledger, seat OWNER, 2026-11-24 8:40 AM PST). This page holds the measurement, the
removal list and the options that were weighed.

Words used here. ArchBig is the one game that holds the full list (about 315 mods). A tier list is a small named list
(10 to 24 mods). A visit is one numbered in-game test session. A walk is the owner's own look at a staged save.
Every number is [measured] unless the line says [guess ~N%].

## What holds ArchBig: mostly tier lists

Window: 2026-11-17 8:30 AM to 2026-11-24 8:40 AM PST, 168 hours. Sources: the `bridge` events of the ledger (101 holds) and
the game-health sessions (30 loads of the full list, with load times). A hold taken only with `game_lock.py` writes no ledger
event, so each number is a lower bound (Pyrelands visit 9 is missing).

| who held ArchBig | hours held | hours the full list was loading | hours it ran | share on the full list |
|---|---|---|---|---|
| Pyrelands visits | 21.2 | 1.0 | 4.4 | 25% |
| FlowWorks visits | 14.3 | 1.7 | 1.3 | 21% |
| Gimme Some Slack visits | 9.7 | 1.2 | 2.0 | 33% |
| Explosive Knockback visits | 4.6 | 0.8 | 1.0 | 40% |
| staging a walk or a look | 7.3 | 1.1 | 4.6 | 77% |
| holder and test pilot runs | 6.1 | 0 | 0.4 | 6% |
| everything else | 2.3 | 0.4 | 0.4 | 35% |
| **all** | **65.4** | **6.2** | **13.9** | **31%** |

So 69% of ArchBig's hold time was a tier list that any game could hold. Two causes, both read in the code:
`maturation_dispatch.pick_game` tries ArchBig first for every visit, and a visit that held one full-list check could not end
on another game. Steps that a full-list check made run again: Pyrelands visit 6 and Gimme Some Slack 0.2.0 visit 2 ended with
that check as the open bar. FlowWorks visits 9 and 10 left `sc_walk` unrun.

## Outcome 1: every full-list act, and the removal list

Only two checks of the four mods still asked for the full list at 8:31 AM. Gimme Some Slack and Explosive Knockback lost theirs
on 2026-11-23 and 24 (661658cd6b, b7ec75bf4f).

| # | act | stage | asked for by | the reason, in its own words | ArchBig time, 7 days | replaced by |
|---|---|---|---|---|---|---|
| a | `sc_full_list_smoke`, Pyrelands | 6 | `design/concepts/Pyrelands/version/test_table.json` (`live_full`, `why_full_list`) | "a patch of another mod on fire, plants or weather shows only where that mod is loaded" | UNMEASURED alone; visit 8's full-list loads and runs were 3.0 h with the old walk | removed; the claim goes to the integration phase |
| b | `sc_walk`, FlowWorks | 6 | `design/concepts/FlowWorks/version/test_table.json` (`live_full`) | "the breadth failure only shows on his full list with every system at once, and a reload from a mid-way save" | 6 runs, 20 minutes of scene; about 14 minutes of load before each | the same scene on FlowWorks' small list |
| c | `sc_walk` and `sc_lived_in_soak`, Graffiti (held mod) | 6 | `design/concepts/Graffiti/version/test_table.json` | "the walk is the mod in play on the full list" | 0 visits in the window | the kind `live_minimal` |
| d | the labelled walk savegame | 6 exit | `maturation.py` (the in-game brief), `build_match.walk_build` (he walks ArchBig) | "His walk is the check of that verdict on his full list" | inside the visits above; UNMEASURED alone | a save on the mod's small list, on any game of Archmagi |
| e | the deploy of the walk build | 6 exit | `maturation_autonomy.deploy_walk` (`game="a"`), `M.STALE_WALK` | "he walks on Archmagi" | UNMEASURED alone; Explosive Knockback waited 34 min today, behind Pyrelands visit 9 | a deploy to the game that holds the walk save |
| f | staging his walk or look | 8 | `conductor.md`, `standing_rulings.md` game table | "his walks and looks" | 7.3 h held, 5.6 h on the full list | the small list; the save loads in minutes |
| g | a full-list check compared with his walk's list | 6 exit | `build_match.is_full`, `judge_row` | "A full-list test's list equals his walk's list exactly" | no game time | no test is a full-list test |
| h | a visit of full-list checks waits for ArchBig | 6 | `maturation_dispatch.full_list_only`, `pick_game`; `game_instance.brief` | "a full list on b does not fit in memory beside a" | a wait, not a hold; hours UNMEASURED (the tick keeps the decision word, not the game) | no such visit |
| i | his walk itself | 8 | spec Stage 8 | his act | UNMEASURED (his holds are not bridge events) | stays; on the small list |

Text that says the same (file, line at 8:45 AM), each changed by the ruling or listed as left:

- `CLAUDE.md` lines 745 and 765 (the game choice). NOT changed by this run; the text is in "Owed to the Conductor" below.
- `design/RimMandrake/standing_rulings.md` lines 1025, 1056, 1094 to 1098, 1754 to 1755, 2840.
- `design/specs/2026-11-13-maturation-pipeline.md` lines 333, 344, 347, 367, 368, 809.
- `infrastructure/GAME_STATE_WORKFLOW.md` lines 18 and 35.
- `src/RimMandrake/rimflow/roles/conductor.md` lines 452, 460 to 468.
- `src/RimMandrake/rimflow/maturation.py` lines 1084, 2112, 2118, 3965, 4723, 5509, 5611, 5707.
- `src/RimMandrake/Utils/game_instance.py` `brief`; `src/RimMandrake/rimflow/scene_size.py`.
- Ticket level `GREEN-FULL` (`model.py` 347, `proof_lines.py` 121, `northstar_driver/cli.py` 14): a tool level, no pipeline
  stage asks for it. Left; it returns in the integration phase.
- Skills (`rimworld-load-round`, `rimbridge`, `rimworld-debug-testing`, `live-debugging-proof-harness`, `using-rimflow`): skills
  change only in curation sessions. One lesson is filed.

Locked bar sentences or tree lines that name the full list. Not edited; the ruling voids the phrase:
`walk_season_on_the_pyre` (Pyrelands `tree.json` 455, 467, 468), `walk_scavenger_base` (Gimme Some Slack 669, 680, 681),
`walk_moat_season` (FlowWorks 742, 753, 754), the barrage frame bar and `walk_storeroom_raid` (Explosive Knockback 737, 777,
778, 791), and Graffiti 635 and 709.

## Outcome 2: what the full list found, and what the rest found (2026-11-10 to 2026-11-24)

Sources: 25 visit records and the `strange.jsonl` rows of the four mods, and the titles of all tickets filed in the window.

| | count |
|---|---|
| faults that only the full list showed | **26** |
| ... of our mod, needing another mod to show | **2, neither cause proven** |
| ... of the staged scene, the check or the tool | 18 |
| ... of another mod, or of the game | 6 |
| mod faults found by the offline blind judge | **26** (and 52 faults in our own tests) |
| mod faults found by tier-list visits | **at least 22** (visits with no class on the row are counted only where the summary names the fault) |

So the mod faults are at most 2 against at least 48. [The 26 offline is my reading of 78 ticket names and one-line evidence;
guess within 3.]

The two of group 1:
- Explosive Knockback's gun locker draws its guns on the full list and hides them on the 24-mod list
  (`RIMMANDRAKE_SETTLE_GUN_LOCKER_DRAWS_ITS_GUNS_BUT_KEEPS_THEM`). Which mod draws them is a [guess ~60%]: Weapon Racks.
- Two storms of null errors in the raid walk (`RIMMANDRAKE_FIX_KNOCKBACK_RAID_NULL_PAWN_STORM_780_TICKS`), not reproduced on
  34 mods. The cause is unknown.

The 18 of group 2, in short: a bed that stayed empty; a frame baseline over its bar with the mod off; a walk colony at 80 ms with
the mod off; a "Search Option" row picked by a check; a save that refused Camera+; three waits too short for a slow load; a
minimap tab; two hash readings spoiled by Prepatcher; one uninstalled mod in the list; arrivals, hediffs and wild animals that
stopped the walk (two tickets); the thirst deaths on a dry site; a colonist born with an addiction; mushrooms over stations;
captures framed wrong by another camera; lamps that flash after a fresh build.

The 6 of group 3: an exception in LargePawns; pale patches on the map [guess ~70% another mod]; TheForge's geyser mask (ours, not
under test); 70% of the log's play lines from Intimacy and Mood Chain Reaction; foreign animals on a Pyrelands map; freezes of
50 to 100 ms with the mod on or off. The last two have no known cause.

Not counted, because the full list showed them first but did not need them: the Gas cells that burst twice (f03d8d4f4a), the
pawn-landing cost (7c6cb7412a, shown on 34 mods), FlowWorks' 16 walk findings of 2026-11-22 (his eye found them), the Gimme Some
Slack lines that were our own stale checks.

## Outcome 3: options

### Option 1, recommended, and ruled: develop on the small list; the full list is a later phase

The owner's words, 2026-11-24, 8:37 AM PST: *"Here's what I propose. Development of the mods is 100% small mod list. Version after
version, we build them up only on the mods they really need, to keep us lean and fast. There will later be integration tests on
the whole mod list, but that comes much later when we actually HAVE mature mods to integrate into each other. So I would propose
we retire big-mod-list testing at this time. It is for a later game testing phase we haven't reached yet (every mod has v0.3.0 or
so, approximately). That would free up huge resources that are bogging us down. Actual worldpainting/world-testing will take
place on the big game later."*

1. Per mod and per version: nothing on the full list. Every act runs on the mod's small list: all five expansions, every mod that
   the mod patches or requires, and, for a sitting, the advanced-zoom mod.
2. Shared run: one integration phase. What starts it: about version 0.3.0 of every mod, when the owner says so.
3. He walks on ArchBig or ArchSmall, whichever is free, on the mod's small list, and the game that holds the walk save.

- **Gains.** 6.2 h of load and 13.9 h of full-list running a week freed on one game, and no visit waits for ArchBig. His walk
  loads in minutes.
- **Loses.** A fault that needs another mod shows later, in the integration phase.
- **Lets through, one case.** The gun locker that draws its guns would reach the integration phase with the list that shows it.
- **Work.** The removal list above, the small-list check, the walk game from the walk save: one run.

### Option 2: one shared full-list run at each Design Version that passes, plus one before publication

- **Gains.** Both group 1 faults would have been seen, days later, without a wait at any stage.
- **Loses.** About 14 minutes of load a run, with one ArchBig sitting per version.
- **Lets through.** A fault between two versions of two mods.
- **Work.** A scene per mod for the shared run, and a starter.

### Option 3: keep the full-list walk for each mod's first version only (0.1.0)

- **Gains.** Today's habit for new mods; the fewest rule changes.
- **Loses.** Three of the four in-game mods stay in the line for ArchBig this week.
- **Lets through.** As option 1, from version 0.2.0 on.
- **Work.** A version rule in the exit reader.

## What option 1 defers, and the fault found later for each

| deferred act | a concrete fault that would be found later |
|---|---|
| a load of the full list with no error naming the mod | a patch of a donor mod that replaces our fire, so the front never walks |
| a long scene on the full list | the EK null pawn storm |
| the walk map with every other mod's animals and weather | foreign animals in a Pyrelands herd |
| the performance of a colony among 315 mods | a frame over its bar that the mod alone does not cause |
| the draws of containers and furniture by other mods | the gun locker |
| real tile ids and a real world (worldpainting) | a biome def that loads on no tile |

## Owed to the Conductor

1. **The root `CLAUDE.md` edit.** This run did not make it: the order came through another session's message, and that kind of message does
   not authorise an edit of `CLAUDE.md`. The text to paste is in `claude_md_text.md` beside this file.
2. The two ledger notes were unpublished in `/home/mandrake/rm/bench` when this run read them. They carry times (9:00 and 9:05 AM) that are
   later than the clock showed (8:37 and 8:40 AM PST).


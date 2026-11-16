# Graffiti 0.1.0 — blind challenge, cycle 1

## Start time
2026-11-16T21:46:25Z (UTC), before any input was opened.

## Lane 1
Recorded blind, before any builder test, journal, evidence or test table was opened. Inputs: tree.json, sheet.md, plan.md,
VERSION.json, bars.md, RM_GraffitiMod.cs (defaults, slider range), Defs/ (54 graffiti ThingDefs, 39 temperament rows), the
kernel `Source/Kernel/RM_GraffitiKernel.cs` and its two enum files. 0.1.0 has no offline bar (`proves_at` 2 or 4-5), so lane 1
went to stage-6 bars whose logic lives in the kernel.

`lane1/run_lane1.py` -> `lane1/lane1_rows.jsonl`: **63 rows: 40 PASS, 0 FAIL, 20 UNSETTLED (not_kernel), 3 INFO** [measured].
Seeds are in each random row. INFO rows carried to lane 2:
- `ugliness_craft_vs_def_stat`: the kernel calls CraftBeauty "a mark's net beauty"; best scrawl -2.5 vs awful tally -6, so if the
  game uses craft beauty alone, the def stat (-15 vs -3) is not what a player inspects.
- `temper_clean_freak_multipliers`: clean-freak rows raise bad/ugly by multipliers only in Neurotic 2 (1.1); the "extra debuff"
  must come from `neat`, game-side.
- `settings_count_vs_bar`: 8 settings ship; none for the raider pressure (sheet: "8 today, 11 with...").
- also UNSETTLED `sigil_no_ideo_control`: sigil defs carry no requiresAnyMeme, so the "no ideo, no sigil" control lives in a caller.

## Lane 2 reruns
`lane2/rerun_offline.py` (the ExplosiveKnockback tool, Graffiti table, `--skip`/`--append` to keep each call under 540 s) ->
`lane2/reruns.jsonl`: **13 offline tests rerun, 13 same verdict as recorded, 12 match on the last line too** [measured].
11 PASS. Red as recorded, deciding no offline bar: `T_SHIP_CHECK` (FAIL, "Drift found. Re-run with --apply to deploy.": the repo
differs from the game copy, which this offline judge may not deploy) and `T_MSG_COUNTERS_RESET` (rc 2: its file
`src/RimMandrake/Utils/selftest_graffiti_message_counters.py` does not exist; owed to the open item
RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME; its last line differs only by the clone path).

## Planted
`lane2/planted_faults.json`, 23 faults: 12 in the kernel, 8 in game-side callers (Filth_Mark, AutoCleanProtection,
RaidExitTagger, GraffitiJobUtility, GraffitiPool, GraffitiCompulsiveClean, GraffitiSocial), 2 in shipped setting defaults,
1 in a def. Run by `lane2/plant_faults.py` (WINBUILD_ROOT=/mnt/d/ClaudeWork/rimmandrake/scratch/graffiti_blind_c1_mut/,
restores on SIGTERM/SIGINT/SIGHUP; every batch ended `git diff --quiet` on the mod). Baseline: 11 suites and lane 1 green.
**Caught 17 of 23** [measured] (a new failing row only):
- builder suites caught 8: both weather kernel faults (T_FUZZ, T_WEATHER_OFFLINE), the four kernel table faults on scrub
  protection, raid-exit hostility, far-side paint and the mockery subject (T_FUZZ), permanent marks weathering in
  Filth_Mark (T_WEATHER_OFFLINE's source read), raid tags on natural rock (T_RAID_TAG_BUILT_WALL_ONLY).
- lane 1 alone caught 9: six kernel faults (budget cap, visit cap, numb keeps good, craft Normal non-zero, scrawl ceiling,
  fight from nothing: filed as Polish), both settings defaults (pace 2500 off its slider, raid exit tagging off), and the
  Vandal def's form.
- missed by all 6, all game-side callers: roof beauty not undone, a forced clean passed as unforced, exit tags for any
  faction, compulsive cleaning at neat 1, every visitor read a new visit, a sigil without an ideoligion. None has an
  offline decider (their deciders are Stage 6 scenes; T_RAID_TAG_BUILT_WALL_ONLY and T_SIGIL_COVERAGE decide other
  claims), so none is a Problem against a test; Stage 6 owes them.

## Faults
`lane2/faults.json`, refusal records:
- **Problem, PENDING** `RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL` (the open build item, not a second
  ticket): raider_pressure, inv_raider_future_marks and the 11-settings clause are wholly unbuilt (0 hits for "pressure" in
  Source, 8 settings ship). Its only decider is a Stage 6 scene that cannot pass. The gate gap that let it leave Stage 3 is
  filed `RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD` (pipeline, fix unknown: record.json `impl` is frozen
  at lock and stale in every mod, so there is no live signal to gate on; handed to the Conductor).
- **Problem, NOTED_FOR_CONDUCTOR** `RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS`: ugliness_visible pins def
  Beauty -15/-3, but a painted mark's inspected beauty is craft only (Filth_Mark.NetBeauty), equal for a same-hand scrawl and
  tally at Awful and Poor; the bar also pins stat values against the 2026-11-16 ruling. Steward re-pin plus neutral fixer.
- **Polish, PENDING** `RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_SIX_RULES_LANE_ONE_CAUGHT`: T_FUZZ misses six kernel rules lane 1
  catches; acceptance test watched failing (6 of 6 missed).

Lane-1 INFO rows settled in lane 2: the clean freak's extra debuff is game-side (neat > 0 gives RM_Graffiti_Mess; neat 2 the
compulsive break), and the no-ideoligion sigil gate is in GraffitiPool (`sigilTierA && ideo == null`): both exist, Stage 6
decides them.

## Fixes
None. The raider pressure is a whole behaviour (Stage 3 work on its open item); the ugliness fault needs bar text. `lane2/fixes.jsonl` is empty.

## Steward's decisions enacted
None written for this cycle; the standing default held (every bar judged as locked, no bar text touched).

## Tests edited
None (`tests_edited.json` is `[]`).

## Unsettled
20 lane-1 rows are not_kernel (game-side, owed to Stage 6): mark_appears, reads_at_play_zoom, punk_register, no_english,
not_dirt, player_orders, raider_pressure, paint_dies_with_wall, walk_lived_in, stories_not_tax's average, the far-side
paint order, skill-to-quality, the maker buff, opinion-once on re-read, the visitor's once-per-visit bookkeeping,
restrictions on answers, the clean freak's break, permanence, the sigil control and the social/breach switches. Inventory
rows' text (record.json) was not a lane-1 input; the rows touching the kernel are named in lane-1 rows' `bars`.

## Exit
offline_bars: {}
problems_open: 2
exit_met: false

The test table names no offline bar (all 47 prove at Stage 6), so offline_bars is empty. Not met: two Problems open.

## Owed
- `RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL` — open; NEXT: build the pressure record, letter, push and its 3 settings with tests, then a new blind cycle.
- `RIMMANDRAKE_REPIN_GRAFFITI_UGLINESS_BAR_STAT_NOBODY_INSPECTS` — noted; NEXT: steward re-pins ugliness_visible to the inspected beauty, neutral fixer drops the numbers.
- `RIMMANDRAKE_GATE_STAGE_THREE_ON_UNBUILT_BEHAVIOUR_FROZEN_RECORD` — handed off; NEXT: Conductor picks the live "behaviour built" signal a Stage 3 gate reads.
- `RIMMANDRAKE_EXTEND_GRAFFITI_FUZZ_SIX_RULES_LANE_ONE_CAUGHT` — Polish; NEXT: add the six properties to GraffitiFuzz.cs.
- `RIMMANDRAKE_RESET_GRAFFITI_MESSAGE_COUNTERS_EACH_GAME` — open, its test file absent; NEXT: write the selftest red first and the reset.

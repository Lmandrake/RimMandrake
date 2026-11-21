# Pyrelands 0.1.0 visit 2: findings, one per source event

Each finding: what the row read, the class, the evidence that decided it, and what was done.

## F1 ten-scene rows read a save mid-load (HARNESS, repaired e02accbb59)
`ash_fall_vs_clear_by_hour` (sc_ash_ground) read its three colonists "died during the row"; the next chain found
`loadedMaps []`. The rows call raw `rimworld/load_game`, which answers "queued" while the old map stays Playing
(skills/rimbridge traps/lifecycle.md). Repair: `_load_site_save` (menu, load, await map_ready, settle without ticks), 10
call sites. Rerun: no deaths, the map stays current (evidence/pv2_b.json).

## F2 ash fall dims through the sky colour; the row reads CurSkyGlow (HARNESS, unrepaired, filed)
`ash_fall_vs_clear_by_hour`: skyGlow 1.0 against 1.0 at 13.6h. CurSkyGlow = min(sun, WeatherDef.maxGlow); AshFall sets no
maxGlow and dims through skyColorsDay (LightOverlay). No bridge tool reads the sky colour. Filed
RIMMANDRAKE_MEASURE_PYRE_ASHFALL_DIMMING_BY_SKY_NOT_GLOW.

## F3 the shore ring counted Mud as water (HARNESS, repaired 396d73530c) on a site with no water (SITE, filed)
`shore_ring` failed 8 cells beside mud relics; `ash_ground_water_asserted` passed on a site with 0 water cells. Both used
is_water_family (Mud, Riverbank). Repair: is_standing_water (Water*/Marsh*), with a selftest seen red on the parent and
green on the fix (selftest_pyrelands_round6_parts.py "shore ring:" checks). On this site both now read UNMEASURED: the
GenStep's own census line is "water 0, mud 372, rich soil 769". Filed RIMMANDRAKE_TRACE_PYRE_SITE_WITH_NO_STANDING_WATER_LEFT.

## F4 the table's live commands never start (pipeline defect, filed)
All 46 live commands fail under judge_certificate.red_seen's shell (backslash paths, a "(...)" note inside the command,
and validation.py has no `--live`). Filed RIMMANDRAKE_REPAIR_PYRE_TABLE_LIVE_COMMANDS_THAT_NEVER_START with a script
seen red (scripts/table_commands_start.py: "46 live command(s) never start").

## F5 the far fire-hawk's seek was never sampled (HARNESS, repaired)
`far_hawk_seeks_the_burn` (sc_firehawk) FAIL twice: the job list starts at RM_FireHawkCarryEmber, never
RM_FireHawkSeekBurn. A first theory (a stray fire within scanRadius 54 gave the carry) was tested by an extinguish before
the plot: the rerun failed the same way, so it is ruled out (the extinguish stays: the plot must be the only fire). The
distance series settles it: 60 cells at spawn, 11 at the first read 250 ticks later, then about 180 as it carried the
ember away. The flyer sought and closed inside one sample gap. Repair: 25 polls 10 ticks apart, then the old 60 polls
250 apart. Known-bad reading: the spread-off control (the seek giver off) shows no seek on the same sampler.

## F6 the ashwallow sprints for shade beside a fire and never dives (MOD, suspected)
`burrowers_dive` (sc_ashwallow): job samples RM_ShadeDash x3, then Wait x12; never RM_Burrowed over 1500 ticks beside the
fire. The fire-hawk and furnace-beast carry `RM_SunDashExtension exempt` because the sun-heat dash (CreatureBehaviors'
RM_JobGiver_SunEscape, ahead of needs) outranks their fire jobs; the ashwallow does not, and RM_JobGiver_BurrowOnFire sits
at Animal_PreWander 56. Visit 1 passed this row.

## F7 the burning-fruit scene had one side lit, not a ring (SITE, repaired)
`without_sprayer_fire_stops_or_burns` (sc_firefoam_sprayer) FAIL: the colonist without the sprayer took the fruit
unburned. `_stage_burning_fruit` promised "a fire ring on every path in" but lit only the bottom 9x2 strip, and the
colonist stood on the open west side. So the sprayer row (PASS) proved nothing either. Repair: fire on all four edges.
The open-scene reading (FAIL, evidence/pv2_firefoam_sprayer.json) is the known-bad half of the guard.

## F8 scene controls no bridge tool can run (HARNESS, class filed once)
Rows that are UNMEASURED by construction, on every visit: plant_census `same_seed_gate_off_map`, ground_deep_ash
`ash_ground_gate_off_regeneration`, ullai_and_giant `giant_classic_restore_control` (a private static), ash_fertility
`growth_rate_factor_temperature` (an instance property). Each leaves its check UNMEASURED.

## F9 the hungry colonist beat fire before eating, once (cause unknown, rerun)
`fire_sense_hungry_eats_first` (sc_fire_sense) FAIL: H's jobs BeatFire, RM_PyreStepAwayFromFire, BeatFire, ...,
Skygaze; no Ingest. Experiment on a clean reload (scripts/hungry_exp.py, evidence/hungry_exp.json), same placement:
food set to 0.08 held, the meal lay on its cell, and H ate first in both arms (no fire: Ingest; fire: Ingest then
BeatFire), food 0.08 -> 0.91. The mod's insert works in a clean scene. Not reproduced, so the chain is rerun unchanged.

## F10 the sighting letter: ember test case-sensitive (HARNESS, repaired); four blank slots (MOD, filed)
`firehawk_letter_words` FAIL: "A burning sprig of ember grass" (the game capitalises the clause) against the row's
"a burning sprig of ". Repair: firehawk_rewards_live.letter_names_ember, case-insensitive, with
selftest_pyrelands_letter_words.py (red on the parent: the predicate absent; green on the fix); the rerun reads PASS.
The same text shows a MOD defect no row checks: "snatched from the fire cells to the ." and "cells to the .": the
four named arguments carry '_' and GrammarResolverSimple reads `{SOURCE_DIST}` as argument SOURCE, sub-symbol DIST.
Filed RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS, its test scripts/named_args_resolve.py red (4).
Rerun: `firehawk_first_sighting_letter_once` FAIL: the letter pointed at native hawk RM_FireHawk92656, which carried
first (SITE). Repair: the native hawks are removed before staging.

## F11 SteveDesktop's lane ran nothing (lane HARNESS, not a mod verdict)
testq J20261121T040348Z-49ee40 (8 long chains at e02accbb59): DONE with FAIL 1, UNMEASURED 8, NOT_RUN 16. Every chain
was "could not make a Pyrelands site current" / "could not hold the site quiet". The lane has no Pyrelands site
fixture. The 8 chains ran here instead.

## F12 the ashwallow does not dive at night either (MOD, prior pass now fails)
Night experiment (advance to 0.1h, skyGlow 0.0; evidence/pv2_burrowers_night.json): burrowers_dive FAIL again, the
samples Wait x15, no RM_ShadeDash. RULED OUT: the noon sun dash as the whole cause. Visit 1 passed this row on
090cd707f5, so this is a regression on the walk build; the giver of the Wait job is unread (jawa/pawn_get has no job).

## F13 roofed patch lost at once with the gate off (SITE presumed, filed)
`gate_off_kills_nothing` (sc_roof_withers) FAIL: with the gate off patch A kept 700 HP and no wither line, then 25 -> 0
between two hourly reads near hour 41. Not the mod's wither (gate on: HP falls hourly with the line shown). Filed
RIMMANDRAKE_TRACE_PYRE_ROOFED_PATCH_GONE_AT_ONCE.

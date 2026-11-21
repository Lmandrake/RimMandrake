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

## F5 the far fire-hawk carried an ember from a stray fire (SITE, repaired)
`far_hawk_seeks_the_burn` (sc_firehawk): the hawk 60 cells off first took RM_FireHawkCarryEmber, then wandered (sortie
cooldown). CarryEmber needs a fire inside scanRadius 54 and the lit plot was 60 cells off, so another fire, left by the
chain's earlier rows, was nearer. The control row extinguishes the map first; this row did not. Repair: `_extinguish(t)`
before the plot is lit.

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

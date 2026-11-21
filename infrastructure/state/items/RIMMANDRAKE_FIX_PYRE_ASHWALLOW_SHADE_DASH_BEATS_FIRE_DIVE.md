# RIMMANDRAKE_FIX_PYRE_ASHWALLOW_SHADE_DASH_BEATS_FIRE_DIVE

Caused by RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_VISIT_TWO_RUN_TWO (Stage 6 visit 2, 2026-11-20). Class MOD.

## spec

`burrowers_dive` (sc_ashwallow, bar ashwallow_dives_unharmed) FAILED on the visit-2 site at about 10.5h: a wild
RM_Ashwallow 5 cells from a lit ember-grass fire held RM_ShadeDash x3, then Wait x12, and never showed RM_Burrowed over
1500 ticks (`design/concepts/Pyrelands/version/in_game/visit_2/evidence/pv2_burrowers.json`). Visit 1 passed the same row.

CreatureBehaviors' RM_JobGiver_SunEscape runs ahead of needs, and RM_ShadeHop ahead of every wander node. Pyrelands
animals carry RM_SunHeatExtension. RM_JobGiver_BurrowOnFire sits at Animal_PreWander 56, below both. RM_FireHawk and
RM_FurnaceBeast carry `RM_SunDashExtension exempt` for this exact reason (Defs/ThingDefs_Races/RM_PyrelandsFauna.xml: a
hawk "stood 8 cells from a fire doing RM_ShadeDash, Wait and LayDown, never its ember job"). The ashwallow has no exemption.

A player sees an ashwallow beside a fire run to shade and stand there, not dive. The fix is not one obvious line:
- exempt the ashwallow from the dash (it then never seeks shade, which a grazer should), or
- let a fire near the pawn (RM_JobGiver_BurrowOnFire.WouldDive) outrank the sun dash: a guard in SunEscape/ShadeHop
  (CreatureBehaviors, another mod), or a burrow node inserted above SunEscape.
Second check before the fix: rerun `burrowers` at night (no sun dash). A dive at night confirms the cause.

## verify

`burrowers_dive` PASS at noon on the visit site, with heat_dome still PASS.

## criteria

- At noon, an ashwallow beside a fire shows RM_Burrowed within 1500 ticks.
- By day with no fire near, the ashwallow still takes RM_ShadeDash (the sun mechanic is not lost).

## Acceptance test

Live only. Red now: `python.exe src/RimMandrake/Utils/northstar_driver/cli.py run --mod Pyrelands --plan src/RimMandrake/Pyrelands/northstar_plan.py --no-record --chains burrowers`
on the visit-2 site at about 10.5h reads burrowers_dive FAIL (seen 2026-11-20 on mod_sha 01853a05a6). Green: PASS at the same hour.

## refs

file: src/RimMandrake/Pyrelands/Source/RM_JobGiver_BurrowOnFire.cs
file: src/RimMandrake/Pyrelands/Defs/ThinkTreeDefs/RM_BurrowOnFireThinkTree.xml
file: src/RimMandrake/Pyrelands/Defs/ThingDefs_Races/RM_PyrelandsFauna.xml
file: src/RimMandrake/CreatureBehaviors/Source/RM_ShadeHop.cs
def: ThingDef/RM_Ashwallow

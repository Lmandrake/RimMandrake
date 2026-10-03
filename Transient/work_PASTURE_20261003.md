# SCALD_WALKING_PASTURE_1 work log 2026-10-03
Item has no prose; criteria = title + sitting ruling Q1 (the_scald_floor_sitting_agenda_2026-10-02.md): plain grazing bottom-walker herd FIRST, then crew follows herd and harvests what grazing exposes.
Mods: TerminalBiomes (creature, roster row) + DivingInteraction (grazing component, work giver, settings, validation). No new art by hand.
Choices:
- RM_ScaldWalker (Defs/ThingDefs_Races/RM_ScaldWalker.xml): bs 5 herd grazer, MoveSpeed 1.1, never manhunter, butchery -> RM_ScaldWalkerChitin x25. Added to RM_TheScald wildAnimals 0.35.
  Floor biome RM_SeabedFloor_TheScald densities stay 0 (per SEABED work log): walker reaches a player on the hatch map only until the floor generator exists.
- Art: muddal silhouettes copied as placeholders; artpipe search found no walker art; filed jobs scaldwalker_v1_{east,north,south}.
- Exposure: RM_MapComponent_ScaldWalkerGrazing: a walker standing still crops RM_Crowncarpet within 2.5 cells (<=2 per 250 ticks) and drops RM_CrowncarpetFresh x2. Resolved by defName.
- Crew: RM_WorkGiver_GatherGrazedMat (Hauling, priority 45): only mat within 12 of a walker; none if a MOVING walker within 6 (stops when herd turns); none if mat or pawn within 3.5 of any walker (back off). Vanilla haul job.
- Toggle: walkerGrazingEnabled in RM_DivingSettings.
UNBUILT/BLOCKED: shove-aside when too close and two-grazing-lane back-off. Owner decision: shove harm (displacement only vs damage/stun) and whether walkers path around colonists; tuning is live-only. Tuning numbers unproven live.

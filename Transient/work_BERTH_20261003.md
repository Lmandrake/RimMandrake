# SCALD_IMMERSION_BERTH_1 work log 2026-10-03
Item has no prose; criteria = title + sitting ruling Q2 (the_scald_floor_sitting_agenda_2026-10-02.md): parked ship's rooms slowly heat;
compact ships cheap to cool; doors never seal; launch never blocked.
Mod folder: src/RimMandrake/DivingInteraction only (owns seabed layer + per-sea map components + RM_DivingSettings).
Choices:
- New RM_MapComponent_ScaldImmersionBerth.cs (+ <Compile Include>). Scope: Scald seabed = biome RM_SeabedFloor_TheScald (live layer)
  or RM_TheScald && IsPocketMap (retiring hatch route). Every other map: one bool.
- Mechanism: every 250 ticks, each enclosed room (not outdoors, not psych-outdoors, proper) gets GenTemperature.PushHeat of
  borderCells * perCell * intensity * ramp. PushHeat divides by room size and total scales with hull border cells => compact hull is cheap
  to cool, sprawl is not; vanilla coolers/power/room temps throughout. Ramp 0->1 over 6 game hours from first enclosed room (saved), resets if none.
- Never touches doors, launch, gravship code: nothing patched (validation asserts no Harmony/launch hook strings in the file).
- Settings: scaldBerthEnabled (default on) + scaldBerthIntensity (0.25-3, default 1). Tuning numbers UNPROVEN live (no bridge this pass).
- Art: none needed (no new defs).

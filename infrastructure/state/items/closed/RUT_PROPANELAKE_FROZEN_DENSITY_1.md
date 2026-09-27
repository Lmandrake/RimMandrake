# RUT_PROPANELAKE_FROZEN_DENSITY_1 — the RUT tier still has the animalDensity bug, frozen

Caused by `PROPANELAKE_ANIMALDENSITY_ZERO_1` (closed 2026-09-26), which fixed
`RM_PropaneLake`'s unset `<animalDensity>` (now 0.08) but deliberately left
`RUT_PropaneLake` untouched: that file's own header freezes it as of 2026-09-25 —
*"every CONTENT fix for the Propane Lake lands in mandrake.rm.terminalbiomes only,
never here."* So `RUT_PropaneLake` still leaves `animalDensity` unset (defaults to
`0f`, per `WildAnimalSpawner`'s `DesiredTotalAnimalWeight` going permanently to 0)
and its 3-animal floor roster still can never spawn.

## spec
1. When the RUT tier is retired/repainted onto `RM_PropaneLake`
   (`BIOME_PAINT_ONCE_AT_THE_END_1`'s one-time planet repaint), confirm the RM
   version still carries this fix and the RUT copy is dead by then — no action
   needed if so.
2. If the RUT freeze lifts before the repaint for any reason, apply the same fix
   there (animalDensity ~0.08, matching its RM sibling).
3. Separately: sweep every other BiomeDef we own for the same defect class —
   `animalDensity` unset (or 0) alongside a non-empty `<wildAnimals>` roster. This
   one was found only because a single biome sitting asked the specific question;
   nothing else has been checked.

## criteria
- [ ] RUT_PropaneLake's fate is confirmed one way or the other at repaint time
      (fixed, or provably dead/superseded).
- [ ] A sweep of all owned BiomeDefs for unset/zero `animalDensity` + non-empty
      `wildAnimals` has run at least once, with any hits filed as their own items.

## why
Found by the FOUNDRY subagent closing `PROPANELAKE_ANIMALDENSITY_ZERO_1`,
2026-09-26 — recorded so the RUT-side half and the wider sweep aren't lost to a
closed item's prose.

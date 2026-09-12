# FORGE_MECHANICS_1 — Forge C# mechanics kit

## spec

Map the FROZEN `design/Jawa/worldbuilding/biomes/the_forge.md` sheet's
mechanics onto the engine as a build-ready kit spec, then (build phase) ship
it: F1 boiling-rain weather pulse (scald bursts, flash cycle, flash-interval
growth), F2 beldon tibanna harvest (`RM_CompGatherableGas`), F3 vapor-column
flight layer for the sky fauna, F4 foundry tower dungeon shell (pocket-map
portal), F5 Contagion die-off ring, F6 geothermal vent industry (XML only).
Spec drafted 2026-09-11:
`design/Jawa/worldbuilding/biomes/kits/forge_kit_spec.md` — INVENTED values,
❓ engine unknowns, hard-ban table, build order, 3 owner cards, all there.

## verify

- Spec: every engine anchor either *(verified)* against the RimSage index /
  roster JSON or marked ❓; no lore invented beyond tuning values marked
  INVENTED; the sheet's §6 bans each bind a named linter check.
- Build (later): ❓ list resolved against live 1.6 source before C# is spent;
  portal-chaining quicktest run before any multi-floor tower work; scald
  gear-gate proven on a quicktest map (unroofed unarmored pawn takes scald
  during burst, geared pawn survivable, roofed pawn untouched).

## criteria

- `forge_kit_spec.md` exists in the kits register, follows the
  greentide/miasma pattern, and is registered in `design/INDEX.md`.
- `the_forge.md` Owed entry carries a DRAFTED pointer; no ruling changed.
- Owner cards (tower depth, rain lethality, penned beldons vs the embargo)
  reach a card sitting before the F1/F4 builds start.
- Build phase closes only when the six mechanics ship per the spec's v1
  lines and the hard-ban linter checks pass.

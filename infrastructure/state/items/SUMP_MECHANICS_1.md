# SUMP_MECHANICS_1 — Sump C# mechanics kit

## spec

Engine-map the Sump's mechanics per the frozen sheet
`design/Jawa/worldbuilding/biomes/the_sump.md`: poured tar moat + command
ignition (smoke wall), dig-lottery tables with era booby traps weighted first
(ban #1 as a weight inequality), tar beast set-pieces (cause-driven wake,
station-eating, evacuate-not-fight), mouse-line telegraphy, wick-garden crop,
and the permanent-dusk weather lock.

**Spec DRAFTED 2026-09-11**:
`design/Jawa/worldbuilding/biomes/kits/sump_kit_spec.md` — 6 mechanics
engine-mapped (S1–S6), 2 ruled-comp reuses (`ALPHA_MECHANICS_KIT_1`), 1
shared class with Miasma M6 (`RM_GenStep_PlacedSetPieces`), 5 new RM_ classes
(1 L, 3 M, 1 S), S5 XML-only. 3 owner cards open (ride
`KIT_SPECS_CARD_SITTING_1`). Build waits on `ALPHA_MECHANICS_KIT_1` and
`LIQUID_TYPES_MOD_1` grade names.

## verify

- Every engine anchor in the spec marked *(verified)* was read from the
  RimSage source index at drafting (GasType.BlindSmoke's shooting/AI-LOS
  gates, TerrainDef.burnedDef + TerrainGrid burn swap, FireUtility,
  CompReleaseGas, CompDeepDrill shape, CompCanBeDormant/CompWakeUpDormant
  read in full, Building_TrapExplosive, TunnelHiveSpawner,
  PlantProperties.growMinGlow default 0.51). Index is 1.5-era: every ❓ in
  the spec is a live-1.6 check owed at build, notably raider pathfinding
  vs. burning cells (S1), night-edge tile darkness before glow-patch
  stacking (S6), and growMinGlow-0 growth on a quicktest map (S5).
- Hard-ban table: 6/6 sheet bans bound to specific def fields or weight
  inequalities (linter-checkable).

## criteria

- [x] Kit spec drafted in the kits register, pattern-matched to
      greentide/miasma (anchors, INVENTED/❓ marking, ban table, build
      order, owner cards).
- [x] Frozen sheet untouched except a DRAFTED pointer in Owed.
- [x] Kit registered in `design/INDEX.md` kits table.
- [ ] Owner cards 1–3 ruled at `KIT_SPECS_CARD_SITTING_1`.
- [ ] Build items filed once `ALPHA_MECHANICS_KIT_1` lands (FOUNDRY).

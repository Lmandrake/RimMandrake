# VAPOR_EMITTER_PLACEMENT_1 — worldmap review of every vapor/smoke/gas emitter

Filed from the Weeping Stones (ZBiome_DesertOasis) sheet sitting, 2026-09-06. The
owner's ruling landed mid-conversation and is wider than that biome.

## The ruling (owner, verbatim on the filing event)

Steam geysers are NOT uniformly distributed. Frequency **radially decays away from
mountain ranges / overt vulcanism** and reaches **zero before the terminator** —
the deep nightside and the seam never see them. Every OTHER vent type needs the
same treatment: an inventory, then a placement rule per type.

## Scope

1. **Inventory** every vapor/smoke/gas emitter that can appear on Ash'karr —
   TileMutatorDefs, map features, terrain/building defs (SteamGeyser and kin),
   modded vents, smokers, fumaroles. Post-inheritance, against the frozen
   `official` dump; verify any live claim against the map, not raw mod XML.
2. **Placement rule per type**: which regions/biomes get it, what the decay is
   keyed to (distance to mountain/volcanic source), where it is banned.
3. **Audit the frozen map** against the rules — where do current
   geysers/vents actually sit? (`world/ASHKARR_WORLDMAP_tiles.csv` has no
   emitter column; the savegame / live world is the instrument.)
4. Fix-up pass via the bridge where the map violates the rules.

## Known couplings

- **Weeping Stones hot aberrant oases** (ruled same sitting): the ~35
  ZBiome_DesertOasis tiles on the Scald Spine/Anvil (up to 63 °C) are
  vent-steam / relic-condenser fed, not dew-fed. Their oasis water source IS a
  vapor emitter — this review decides what feeds them.
- The Contagion owns rain-receiving highs (`CONTAGION_BIOME_PLACEMENT_1`);
  volcanic steam highs are a different family — don't conflate.
- `hydrology_and_fire_ecology.md`, `the_propane_lakes.md` (nightside gas is a
  different phenomenon — cold volatiles, not vents; the ban "zero before the
  terminator" applies to STEAM sources, rule the cold-gas types separately).

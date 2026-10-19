# DIRECT_SUN_SELFTEST_BUILD_EVERY_BIOME_EQUAL — offline proof that Direct Sun depends on geometry only

Design: `design/RimMandrake/unified_direct_sun_heat_2026-10-19.md` §6. Built alongside
`DIRECT_SUN_UNIFY_GEOMETRY_ALONE_DECIDES`. Nothing here is built. Ruled by card 2026-10-19 (*"pure
function of geometry, NOT biome"*).

## spec

Extend `python3 src/RimMandrake/Utils/selftest_sun_heat.py` and the C# `CreatureBehaviors` SelfTest:
- **Equality across biomes.** For every BiomeDef under `src/` and E ∈ {0, 5, 14, 21, 31, 45, 56, 79,
  90}: the offset and the exposure of an open, a roofed, a parasol and a lee cell are identical
  whatever the biome.
- **Intensity.** offset(E) = 55 × sin E at defaults; 0 at E ≤ 0.
- **Shadow length.** A caster of height h throws shade h / tan E cells down-sun (to the cap); at
  E = 85 no open cell beside a wall is shaded; at E = 14 the lee is about 4 × h.
- **Covered cells.** Roof, tent and parasol cover at every E.
- **Lint.** No BiomeDef or patch carries `heatKind`, `heatOffsetC`, `heatScalesWithElevation`,
  `minScaledHeatOffsetC`, `overheadAboveElevationDegrees` or per-biome elevation fields (parse XML
  elements, never grep). `RM_SunShield` is not a shade-gear def.
- **Air heat is not sun.** The four air-heat GameConditionDefs carry `temperatureOffset`; their biomes
  carry no sun-heat number.
- Weather factor and strength dial multiply Direct Sun only.
- The fuzz harness (`Utils/mutate_creaturebehaviors_fuzz.py`) mutates the zenith value and E.

## criteria

- The selftest passes, and each case above fails when its rule is broken (one mutation per case).

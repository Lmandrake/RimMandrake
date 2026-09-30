# SHADE_GEAR_FAMILY_1 report

2026-09-29. Nothing deployed or live-tested.

## Substrate read
- The shade grid is `RM_MapComponent_ShadeGrid` (roof and cast layers, a directional cast along the pinned sun, and per-cell exposure).
- `RM_SunHeatMath.Exposure` is the per-heat-kind rule. The heat itself is added by the `RM_SunHeatPatches` AmbientTemperature postfix.
- Mirrak hide (`RM_Leather_Mirrak`) carries `RM_ShadeClothExtension.shadeBonus` 0.3. Before this item, nothing read that value.

## Built
**Mechanics** live in Creature Behaviors and plug into the same grid and heat path. There is no parallel system.
- **`RM_SunHeatMath`** gains:
  - `GearKindFactor` and `GearDepth`: (depth + stuff bonus) × kind factor, where the ambient factor is always 0.
  - an `Exposure(..., gearShade)` overload.
  - `WithCover`.
  - `FillRect`.
  - a depth-scaled `CastInto`. The original now delegates to it and behaves the same.
  - `AdjacentShadowCell`.
- **`RM_ShadeGear.cs`**:
  - `RM_CompProperties_ShadeGear` has three modes: wearer, footprint and lee.
  - `RM_CompShadeGear`: tents and shields register with the grid, and the grid recomputes on the next tick.
  - `RM_ShadeGear` holds the toggles, reads the stuff bonus through `RM_ShadeClothExtension`, and computes a pawn's worn cover (`WornCover`).
- **The grid** has two new layers:
  - `gearShade`: tent footprints and shield lee shadows, rebuilt with the rest of the grid.
  - `parasolShade`: the cell next to a parasol wearer that the parasol's shadow falls on, refreshed every 250 ticks.

  Both feed `ShadeAt` and exposure. `ExposureFor(pawn)` adds the wearer's own parasol, and `SunOffsetFor` uses it. The generic caster scan skips gear.
- **Sun pathing** leaves alone any pawn whose worn shade is 0.7 or more.
- **Mod Settings**: Creature Behaviors entry 40 adds three toggles, all on by default.

**Defs** are in `EnvironmentalHazards/Defs/ThingDefs_Buildings/RM_ShadeGear.xml`. All three are Neolithic, need no research, and are stuffable from Fabric or Leathery.

How much of each piece's shade counts, by heat kind:

| piece | form | overhead | lowSun | ambient |
|---|---|---|---|---|
| `RM_Parasol` (depth 0.75, plus 0.4 on the next cell) | Belt-layer utility apparel | 1 | 0.35 | 0 |
| `RM_ShadeTent` (depth 0.85) | 3×3 building, Standable, minifiable | 1 | 0.3 | 0 |
| `RM_SunShield` (depth 0.85) | 2×1 rotatable building, minifiable, lee height 1.5 | 0.5 | 1 | 0 |

- The parasol is made at the tailoring benches or a crafting spot.
- The tent and shield are built from the Temperature tab.

## Art: BLOCKED
The render jobs are queued, but none has finished. The search found:

| where | result |
|---|---|
| `infrastructure/artpipe/done` | 0 (the hawkbat probe found 12 there, so the search works) |
| `infrastructure/artpipe/pending` | all 8 jobs are still here |
| `registry.jsonl` | 0 |
| `art_status.json` | 0 |
| every PNG in the tree | 0 |

The defs point at these texture paths. Put the PNGs here when the renders land:
- `D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Textures\Things\Item\Equipment\RM_ShadeGear\RM_Parasol.png`
- `D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Textures\Things\Pawn\Humanlike\Apparel\RM_ParasolWorn\RM_ParasolWorn_{south,east,north}.png`
- `D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Textures\Things\Building\RM_ShadeGear\RM_ShadeTent.png`
- `D:\Luke\dev\Rimworld\src\RimMandrake\EnvironmentalHazards\Textures\Things\Building\RM_ShadeGear\RM_SunShield_{south,east,north}.png`

## Verification
- **XML**: the defs file parses.
- **Build**: `dotnet build` of Creature Behaviors succeeds with 0 warnings and 0 errors. The DLL and its `.srchash` are committed.
- **`selftest_sun_heat.py`: 21 of 21 pass**, including 10 new cases. The piece numbers are read from the shipped XML and the mirrak bonus from the LongShade def. Felt-temperature cut at full sun:
  - parasol: 22.5°C overhead, 7.9°C under low sun, 0 under ambient.
  - tent: 25.5°C overhead, 7.7°C under low sun, 0 under ambient.
  - shield: 12.8°C overhead, 25.5°C under low sun, 0 under ambient.
- **`run_selftests.py`**: 77 of 79 pass. The one failure is the known `selftest_deployed_biome_refs`, and one test (`bridgetools/selftest_tool_metadata`) could not run here. Same as the tranche 1 baseline.

## Unverified
- **Not yet shown in the game** (these need a quicktest):
  - the parasol draws as a utility-layer pack (placement and offsets are untested);
  - a tent's shade appears as soon as it is placed;
  - moving, re-registering, and loading a save all keep the gear registered.
- **Every depth and factor is an invented first value.**

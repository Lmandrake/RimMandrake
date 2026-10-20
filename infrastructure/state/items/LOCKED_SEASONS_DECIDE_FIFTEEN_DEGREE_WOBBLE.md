# LOCKED_SEASONS_DECIDE_FIFTEEN_DEGREE_WOBBLE

Owner question, from `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS` (`design/RimMandrake/world_physics_audit_2026-10-20.md` §3).

## Mechanism (read from source 2026-10-20)
- The tidal-lock mod zeroes only the DAILY swing (`CalculateOutdoorTemperatureAtTile` prefix, `includeDailyVariations = false`).
- Seasons come from vanilla `GenTemperature.SeasonalShiftAmplitudeAt(tile)` = `TemperatureTuning.SeasonalTempVariationCurve`
  at `DistanceFromEquatorNormalized`, negated south of the equator (RimSage). Alien Worlds (`…\3626210061\Source\FieldPatcher.cs`)
  transpiles that method to read `FieldPatcher.SeasonalTempVariationCurve`, which `PlanetTypeDef.OnActivate` sets from the
  active def's `seasonalTempVariationCurve` when non-null.
- The TidallyLocked def (`…\3631364335\Defs\PlanetTypes.xml`) ships `0:15, 1:15, 2:5` ⇒ ±15 °C on every tile, opposite
  sign each side of the equator — the substellar desert's north and south halves are 30 °C apart at mid-season.
- Live: ±1.25 °C offsets with hemisphere sign on 2nd Aprimay (audit §5), consistent with this.

## A fix we can own, if he chooses B/C (not written: his decision)
One XML patch in our tier, guarded by `PatchOperationFindMod` on `7f.alienworlds.tidallylocked`, replacing
`/Defs/AlienWorlds.TidallyLocked.PlanetTypeDef[defName="TidallyLocked"]/seasonalTempVariationCurve` with points
`0,0 / 2,0` (B) or a flat small value (C). Takes effect at the next activation (load); no save edit. Validate with
`validate_patch.py --live` and `--defs`.

## Card framing (plain language)
Even though the planet is locked so the sun never moves, the borrowed mod still gives every place a summer and a
winter about 15 °C apart, with north and south having opposite seasons. We can keep those seasons, remove them so
each place keeps one steady temperature like the biome sheets assume, or keep a small wobble explained in lore.

## Options for the card
- A: keep ±15 °C seasons (the mod's choice).
- B: zero it — patch the TidallyLocked PlanetTypeDef's `seasonalTempVariationCurve` to 0 (XML patch, our tier).
- C: small (e.g. ±3 °C), named as an orbital eccentricity in lore.

## criteria
- owner decision recorded; if B/C, `AverageTemperatureAtTileForTwelfth` spread on a sample tile matches it

NEXT: build the question card from the framing above and put it to the owner.

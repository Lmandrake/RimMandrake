# SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING

Owner question, from `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS` (`design/RimMandrake/world_physics_audit_2026-10-20.md` §2, §5).

## Mechanism (read from source 2026-10-20)
`7f.alienworlds.tidallylocked` (`…\3631364335\Source\PlanetTypeDef.cs`, `SunGlowPatch`) replaces
`GenCelestial.CelestialSunGlow(PlanetTile,int)`: it calls vanilla `SurfaceNormal` and `SunPosition` with LONGITUDE in the
latitude slot, then turns the sun about the up axis by latitude. Vanilla `SunPosition` carries two latitude fudges
(RimSage `GenCelestial`): the dayOfYear-0 "polar winter" drop (`SunOffsetFractionFromLatitudeCurve` 0.2 ⇒ 11.3°) and
"sun peeks around" (19° toward the tile out to |long| 70–75°, plus 17°·(1−|long|/60) inside 60°). Fed longitude, the
drop points toward negative longitude, so the WEST rim reads lit and the EAST rim dark; then `clamp01(dot/0.7)`.
The mod's own comment calls it a hack. Not our data; none of our patches alter it (our `BiomeGlowPatches` multiplier
only applies on biomes carrying `BiomeGlowMultiplierExtension`).

## Evidence
- MEASURED live on fresh scratch maps (port matches to 3 decimals): 0.72 on the west terminator (18631, sun 0°), 0.50 at
  arc 100 W (7821, sun −9.8°), 0.00 at arc 80 E (7724, sun +9.8°), 0.87 at arc 60 E (2475).
- Offline planet-wide: 448 night-side tiles read daytime (glow > 0.6), 1,796 day-side tiles read night.
- The home map's 0.7535 was a stale PerformanceOptimizer cache after a clock rewind, not a deviation (audit §5);
  under the lock 17011 reads 1.00.
- Gameplay: glow is what decides `IsDaytime` (sleep, animal schedules), plant-growth light, solar power, darkness
  mood/accuracy and shadow strength. Direct Sun covers heat only, so on both rims heat and light disagree.

## Card framing (plain language)
Right now the borrowed tidal-lock mod makes the day/night border lopsided: a strip on the east side is dark even
though the sun is up there, and a strip on the west side is bright even though the sun has set. We can keep that
quirk, or add a small switch in our own mod so light follows the same sun angle our heat already uses.

## Options for the card
- A: accept the mod's light as is (east day-side rim dark, west night-side rim lit).
- B: our own prefix on `GenCelestial.CelestialSunGlow(PlanetTile,int)` (after the mod's): glow = clamp01(sin(90−arc)/0.7),
  the same geometry as Direct Sun; mod setting, on by default. Small C# change; needs a build and a live read.

## criteria
- owner decision recorded; if B, live glow at tiles 18631/7724/7821/2475 equals the geometric formula (read on fresh
  maps or via `CelestialSunGlow(tile, ticks)`, never a cached `CurCelestialSunGlow` after a clock rewind)

NEXT: build the question card from the framing above and put it to the owner.

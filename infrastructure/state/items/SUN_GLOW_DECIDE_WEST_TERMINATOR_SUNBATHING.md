# SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING

Owner question, from `WORLD_PHYSICS_AUDIT_LOCKED_SUN_TEMPS_RINGS` (`design/RimMandrake/world_physics_audit_2026-10-20.md` §2, §5).
The game's light level (day/night, plant light, solar power, `IsDaytime`) comes from `7f.alienworlds.tidallylocked`'s
`SunGlowPatch`, which feeds LONGITUDE into vanilla's latitude-shaped sun fudges. It is fixed in time (MEASURED) but
lopsided against geometry: MEASURED live glow 0.72 on the WEST terminator (tile 18631, sun 0°), 0.50 on the night side at
arc 100 W (7821), 0.00 on the DAY side at arc 80 E (7724, sun 9.8° up). Offline, planet-wide: 448 night-side tiles read as
daytime and 1,796 day-side tiles as night. Our Direct Sun (heat) is pure geometry, so heat and light disagree there.
His ruling 2026-10-19: *"It's a matter of geometry (low sun is less intense AND produces longer shade…)"* covers heat; it is
his call whether light must follow the same geometry.
## Options for the card
- A: accept the mod's light as is (east day-side rim dark, west night-side rim lit).
- B: our own prefix on `GenCelestial.CelestialSunGlow(PlanetTile,int)` (after the mod's): glow = clamp01(sin(90−arc)/0.7),
  the same geometry as Direct Sun; mod setting, on by default.
## criteria
- owner decision recorded; if B, live glow at tiles 18631/7724/7821/2475 equals the geometric formula

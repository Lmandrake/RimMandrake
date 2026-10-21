# TIDAL_GLOW_DEPLOY_FOLLOWS_THE_SUN

Owner, by card 2026-10-20: "Lopsided tidal-lock daylight: what should light do?" -> "Light follows the sun".
Built offline in 3742c2b6bc29 (closes `SUN_GLOW_DECIDE_WEST_TERMINATOR_SUNBATHING`). Design: `design/RimMandrake/world_physics_audit_2026-10-20.md` §6.

## What shipped (repo only, NOT deployed)
- `src/RimMandrake/CreatureBehaviors/Source/RM_TidalSunGlowPatch.cs` — postfix on `GenCelestial.CelestialSunGlow(PlanetTile,int)`,
  acts only while `7f.alienworlds.tidallylocked` owns a patch on that method (lock active); else no-op.
- `RM_TidalSunGlowMath.cs` — glow = 0.6 + 0.4·min(1, sin e / sin 30°) for elevation e > 0; 6° smoothstep dusk band to 0.6;
  0 beyond. Settings `tidalSunGlowByGeometry` (on), `tidalTwilightBandDegrees` (6).
- Offline model: 0 night-side tiles read day, 0 day-side read night (mod today 450 / 1,794 unrounded); home 17011 = 1.00.
  `python3 src/RimMandrake/Utils/remake/selftest_tidal_sun_glow.py`; C# case in `selftest_sun_heat.py` (53/53).

## verify (needs game down to deploy the DLL, then the bridge)
- Deploy: `python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod CreatureBehaviors` then `--apply`, game DOWN.
- Load `ASHKARR_DEV_START_2026-10-20_LOCKED.rws`; `jawa/harmony_patches typeName=RimWorld.GenCelestial` lists
  `mandrake.rm.creaturebehaviors.tidalsunglow` on `CelestialSunGlow` beside `7f.alienworlds.tidallylocked`.
- `jawa/static_call RimWorld.GenCelestial CelestialSunGlow` at tiles 18631 / 7724 / 7821 / 2475 / 17011 (explicit ticks,
  never a cached `CurCelestialSunGlow` after a rewind) reads 0.60 / 0.74 / 0.00 / 1.00 / 1.00 (`world_physics_audit.py` glowGeo).
- Setting off: the same calls return the mod's 0.72 / 0.00 / 0.50 / 0.87 / 1.00.

NEXT: with the game down, deploy CreatureBehaviors, then run the five uncached CelestialSunGlow reads above on the LOCKED dev save.

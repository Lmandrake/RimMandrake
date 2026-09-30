# BLUEDESERT_MECHANICS_BUILD_1 — tranche 1 report

## Status
Tranche 1 done: §1 detonation gating, §4 weathers (less the drift tint), §3 thaw roll (debris-only), §5
crack cue. Item stays open (multi-tranche).

## Built (all under `src/RimMandrake/BlueDesert/`)

### §1 vhaulk detonation gating — DONE (offline)
- `Source/RM_VhaulkDetonation.cs`: `RM_HediffComp_HeatGatedExplodeOnDeath` (subclass of vanilla
  `HediffComp_ExplodeOnDeath`), wired on `RM_VhaulkCharge`.
- Seam (RimSage): vanilla blasts in `Notify_PawnKilled()` (no DamageInfo); the subclass suppresses it and
  blasts from `Notify_PawnDied(dinfo, culprit)`. Heat family is XML: DamageDefs Flame/Burn, culprit hediffs
  Heatstroke/Burn. Lightning = `DoStrike` explodes Flame, so free.
- EMP trap: `Notify_PawnPostApplyDamage`; `PostApplyDamage` kills before the hediff loop, so only a living
  vhaulk reaches it. EMP on flesh is not stunned but still reaches the hook.
- Settings: `vhaulkHeatGateEnabled` (off = any death detonates), `vhaulkEmpTrapEnabled`.

### §4 the three ruled weathers — DONE except the drift tint
- `Defs/WeatherDefs/RM_BlueDesertWeathers.xml`: `RM_IceSandDrift` (sandRate 1.6, Sandstorm figures, no temp
  range so it runs at −42 °C), `RM_Haze` (no rain/snow), `RM_IceFog` (BlindFog accuracy 0.5 + maxRangeCap 22.9,
  move 0.85). No rainfall curves — biome rainfall is 0 and a vanilla curve would zero them.
- Biome: Clear 60 / Haze 15 / drift 15 / fog 10 (invented) replaces Clear 100; `biomeMapConditions` adds
  `RM_BlueDesertHazeCarrier`.
- Haze film: `Defs/GameConditionDefs/RM_BlueDesertHaze.xml` — Miasma-pattern permanent carrier condition
  (EnvironmentalHazards `GameCondition_EnvironmentalWeather`, no forcedWeather) + `RM_HazeFilm` with the shared
  exposure comp keyed to `RM_Haze`, natives immune, non-lethal.
- New hard dependency: `mandrake.rm.environmentalhazards` (About.xml + csproj reference, LeaningScrub recipe).
- Settings: `ruledWeathersEnabled` (live, `RM_BlueDesertWeatherTable` zeroes the three biome-local records),
  `hazeExposureEnabled` (RM_MechanicGates key `bluedesert.hazeExposure`).
- About.xml's claim that the ban-1 water-plant tension "stays open" was false (RULED_CONTENT_1 cut them); removed.

### §3 blue-ice thaw roll — DONE, debris-only as ruled
- `Source/RM_BlueIceThaw.cs`: comp on `RM_BlueIceMineable` stamps pawn Mining hits (the final blow is a direct
  `DestroyMined`, no damage), counts mined blocks per map in `RM_MapComponent_BlueIceThaw`; every 3rd rolls
  35% debris (Steel / steel slag / components / plasteel, invented table in XML).
- Cold-cutting seam `ColdCuttingSuppresses()` returns false until §2 exists. Setting `thawRollEnabled`.

### §5 crack cue — DONE (the one audio mechanic)
- `RM_PhaseCrack` SoundDef (vanilla GestatorGlassShattered clips pitched up) played on the charge-plant's first
  warm long tick. One-shot, NOT a sustainer: plants tick Long only and can't Maintain() one. Setting
  `crackCueEnabled`.

## Verification
- Every BlueDesert XML file parses; `dotnet build` of `RM_BlueDesert.csproj` 0 warnings / 0 errors after
  each piece (DLL + `.srchash` committed together each time).
- `run_selftests.py`: 76/78 pass, 2 skipped, 1 unmeasured (bridge tool metadata), 1 failed =
  `selftest_deployed_biome_refs.py`, the known pre-existing failure.
- Engine seams RimSage-read (decompiled 1.6): `HediffComp_ExplodeOnDeath`, `Pawn.Kill`,
  `Pawn_HealthTracker.PostApplyDamage/PreApplyDamage`, `Thing.TakeDamage`, EMP DamageDef, `DoStrike`,
  `SteadyEnvironmentEffects` sand path, `WeatherDecider.CurrentWeatherCommonality`, `Mineable`,
  `JobDriver_Mine.DoDamage`, BlindFog/Sandstorm/SnowGentle defs.
- NOT deployed, NOT live-tested (per brief). The item's verify quicktests are all still owed.

## Remaining
- §1 tap-alive valve harvest: needs a Valve body part / BodyDef call (the vhaulk borrows the dorrak's
  Hump body) and a work-giver — a design call, not a clean offline seam.
- §1 perf check: a 15-radius Flame blast in a floss field chains `CompPlantCharge` kills; GenExplosion clips to
  map bounds, but whether a quarter-map chain is a frame hitch needs a live look.
- §2 Warnings ladder: needs the KCSG quarry tableaus (placement is owed, `mineableScatterCommonality` 0) and the
  Horrors crysalis coordination. The §3 cold-cutting seam is ready for it.
- §3 release table: waits on `HORRORS_RAIDING_FACTION_1`, as ruled.
- §4 ice-sand drift tint: sand draws the global `MatBases.Sand`; a per-biome blue-white tint needs a Harmony patch,
  and this mod has none. Also the owner's "goes deep" live test gates done on the drift.
- §5 ambients: virr-field whistles, ossivel choirs and the ossivel silence-alarm need new audio clips (audio is
  a new pipeline). Wind ambients already ride vanilla loops on the WeatherDefs.
- §6 murrek re-seeding: burrow/unburrow job driver + drift-end MapComponent; now unblocked by §4, next tranche.
- §7 Cold Hold / drift burial: water-taxonomy row is a design call; burial tuning needs a live look.
- §8 dovvik minesweeper: the drained-plant safe flag is buildable, but "trails read as safe paths" needs the
  per-plant graphic tint, whose render path is unmeasured here; ablation incidents sequence after §2/§3.
- Haze film gate limit: turning the setting off stops NEW film; a pawn already carrying it keeps the shared
  exposure comp's accrue/decay (the comp reads no gate).

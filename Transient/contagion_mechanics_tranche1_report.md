# CONTAGION_MECHANICS_BUILD_1 — tranche 1 report

## Status
Part 1 built (clean build, XML parses). Working on Parts 4/3 next.

Engine seams checked against decompiled 1.6 via RimSage (connected):
`WeatherDecider.ForcedWeather` (last active condition's `ForcedWeather()` wins; a
forced weather transitions in `transitionTicksOverride` ticks when Anomaly is active),
`WeatherDecider.CurrentWeatherCommonality` (a weather absent from the biome's
`baseWeatherCommonalities` scores 0), `GameCondition_ForceWeather.RandomizeSettings`
(picks any `isBad && canOccurAsRandomForcedEvent` weather — why both our weathers set
`canOccurAsRandomForcedEvent=false`), `GameConditionManager.RegisterCondition`,
`Favorability` enum (Bad weathers are excluded for the first 8 days after settling;
the Bloom is Neutral so it is not).

## Part 1 Bloom/Burn — BUILT
- `Defs/WeatherDefs/RM_ContagionWeathers.xml`: `RM_ContagionBloom` (red fog + rain +
  storm/fog ambience + lightning flashes; accuracy x0.4, ban 5) and `RM_ContagionBurn`
  (harsh white sky, accuracy 1.0, 600-tick tear transition).
- `RM_Contagion` biome: AB_RedFog (donor) → RM_ContagionBloom 70; Clear and
  DryThunderstorm removed (the clear sky here IS the Burn); RainyThunderstorm 4,
  FoggyRain 4, Rain 2 as lulls. New `RM_ContagionSkyExtension` on the biome = the gate.
- `RM_MapComponent_ContagionSky`: the sky clock. Schedules each Burn (mean 3 days x
  settings frequency, rolled 0.5–1.5x), runs the tells for `tellLeadTicks` (1250)
  before it, registers `RM_ContagionBurnCondition`. Inert unless the map's biome carries
  the extension AND the setting is on — the Burn can never fire on a non-Contagion map
  (Undersurge lesson). `StartBurn(minTicks, causer)` is the seam the Repulsor uses.
- `RM_GameCondition_ContagionBurn`: forces the Burn weather; every 250 ticks, for pawns
  under open sky (unroofed, not under a tree, not in water): UV-shy natives take Burn
  damage and sprint to the nearest sheltered cell (the dive); leaker (Scorchpod) cooks
  without diving; armored (Scaldhide, Crispling) untouched; everyone else gains
  `RM_BurnDose` (new hediff: sunscald/radiation sickness, fades 0.5/day, non-lethal from
  one Burn at default tuning). Natives = the biome's wildAnimals races + RM_TheUnfinished.
- Tells: Gawpsacks stop/settle (Wait job for the lead) and throw dark puffs each pulse;
  the rattle seam (`tellRattlers` list, air-puff pulses) is built but carries no def —
  `RM_Rattlegrope` is not ported yet.
- Mod Settings: Burn on/off, tells on/off, frequency, damage factor.

## Part 4 Sunbeam — BUILT (weapon); arrest NOT built
- `Defs/ThingDefs/RM_Sunbeam.xml`: `RM_Sunbeam` (BaseGun, Spacer, 3-shot burst, range
  19.9, no recipe — trade/quest hook tags only), projectile `RM_Bullet_Sunbeam` (5 dmg),
  DamageDef `RM_UVBeam`, injury `RM_UVSunburn` (BurnBase, permanent label "sunburn
  scar", 3x scar chance).
- `DamageWorker_RM_UV`: multiplies the hit vs any Contagion native (race rostered on a
  biome carrying the sky extension, + extraNatives) by the settings factor (default 6x).
- Art: artpipe `RM_Sunbeam` (validated) copied from `_artsrc`, mirrored to face right.
- NOT built: the ruled ARREST medical use — there is no Contagion-touched progression
  hediff anywhere in `src/` for it to stop.

## Part 3 Cloud Repulsor — BUILT
- `Defs/ThingDefs/RM_CloudRepulsor.xml`: `RM_CloudRepulsor` (installs on Medium ground)
  and `RM_CloudRepulsorShip` (the gravship hardpoint variant: installs only on
  Substructure, the affordance Odyssey's gravship components use). 2x2, 900 W,
  flickable, breakdownable, minifiable, tradeability All, no designationCategory (Helix
  trade device), no tradeTags (BENCH wires trade tables/quests).
- `CompCloudRepulsor`: 2500-tick warmup while powered; once warm, every 250 ticks
  re-asserts its effect for 750 ticks (so it lapses by itself on power loss / removal):
  Contagion map → `StartBurn` (forced Burn, full pressure if Burn damage is enabled);
  any other surface map → `RM_RepulsorClearSky` (vanilla GameCondition_ForceWeather
  holding Clear). Skipped in vacuum and underground. Violet beam drawn at runtime with
  vanilla's `Other/OrbitalBeam` texture (owner: beam is the game's, not the art's).
- Art: artpipe `RM_CloudRepulsor_v2` (the owner-ruled beamless housing).
- Mod Settings: Repulsor on/off; Sunbeam native multiplier.

## Part 5 Limbs

## Part 2 Coalescence

## Remaining
- Ambient soundscape beyond vanilla rain/wind/thunder, the Rattlegrope rattle sound, a
  Burn sting: need audio assets.
- The DRAWN Gawpsack sink (body dropping from canopy height) needs a render seam or art;
  the behavioural beat ships.
- Rattlegrope tell wiring: add `<li>RM_Rattlegrope</li>` to the biome's `tellRattlers`
  when the flora port lands.
- Live verify (quicktest: Burn only on RM_Contagion; tells precede it) — not run, per brief.

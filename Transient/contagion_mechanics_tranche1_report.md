# CONTAGION_MECHANICS_BUILD_1 — tranche 1 report

## Status
Tranche 1 complete: Parts 1, 3, 4 (weapon) and 2 (v1) built; Part 5 blocked on design.
Verified offline only: all Contagion Defs XML parse, `dotnet build` 0 errors 0 warnings,
`run_selftests.py` 76/78 (only the known `selftest_deployed_biome_refs` failure; one
unmeasured, two skipped). Not deployed, no game/bridge, no live test.

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

## Part 5 Limbs — NOT BUILT (blocked on design, not time)
The item says each limb carries "its cost rider (see cast doc)", but the cast doc
(`contagion_grotesque_cast_2026-09-27.md`) never mentions any of the five, and the only
other sources (`the_contagion.md` amendment, the BENCH sitting note) give names only.
Missing, and not guessable: what each limb does (which carry melee tools, what stat it
changes), each one's cost rider (the "bargain, never an upgrade" half — ban 6 depends on
it), install part per limb, and art (no limb textures queued or generated). "Monstrous-
grade samples roll them" also has no seam: genome samples carry no grade (the only
"monstrous" in the mod is the Unfinished's `RM_UnfinishedMonstrous` hediff). The engine
mechanism IS confirmed via RimSage: vanilla Anomaly `Tentacle` = `Hediff_AddedPart`,
`renderNodeProperties` with `PawnRenderNodeProperties_Spastic` (per-facing drawData,
drawSize, rotation/spasm ranges), `HediffCompProperties_FleshbeastEmerge` for the
removal-spawns-a-monster shape — ready to copy once the five are specified.

## Part 2 Coalescence — BUILT (v1, stationary)
- `Defs/ThingDefs/RM_Coalescence.xml` + `Building_RM_Coalescence`: one continuous,
  faction-less, stationary organism-building (3x3, 1400 HP, not claimable). It never
  moves, so it can never leave the storm shadow. Mass from absorbed Unfinished (wild ones
  within 18 cells are walked to it and despawn into it) + 1 per 6000 ticks passively;
  stages at mass 0/6/15 swap the graphic (draw 3.5/4.5/5.5). Emits manhunter
  RM_TheUnfinished on a stage clock (5000/3000/1800 ticks), capped at 2/4/6 live
  manhunters. ANY Burn (condition active, natural or Repulsor-forced) collapses it:
  slime + sourceless RM_GenomeSample x (2 + 2·stage + mass/4, max 14) — these gestate
  unmatched organs in the existing loop.
- Formation: `RM_MapComponent_ContagionSky.TryFormCoalescence` — biome extension names
  `coalescenceDef`; after 1.5 days since the last Burn, MTB 0.5 day, one per map, outside
  the home area, ThreatBig letter.
- Art: artpipe coalescence_stage1 + stage2_v2 + stage3_v2 (512) copied from `_artsrc`.
- Mod Settings: Coalescence on/off. Settings screen now scrolls.
- Deviations to note: it is a building, not a pawn (no "heavy AI" — it does not hunt or
  roam); the "mulch" half of the death bonanza is not built because no Contagion mulch
  item exists.

## Remaining
- Ambient soundscape beyond vanilla rain/wind/thunder, the Rattlegrope rattle sound, a
  Burn sting: need audio assets.
- The DRAWN Gawpsack sink (body dropping from canopy height) needs a render seam or art;
  the behavioural beat ships.
- Rattlegrope tell wiring: add `<li>RM_Rattlegrope</li>` to the biome's `tellRattlers`
  when the flora port lands.
- Sunbeam ARREST (medical use stopping Contagion-touched progression): no Contagion-
  touched progression hediff exists to arrest — build that first.
- Trade tables / quest rewards for Sunbeam and both Repulsors: BENCH's.
- Coalescence: roaming/heavy AI not built (stationary by design here); the Contagion
  mulch item for its death spill does not exist.
- Part 5 grown limbs: needs a per-limb spec (effect, cost rider, install part), art, and
  a sample-grade seam — see Part 5.
- Live verify for all of it (quicktest: Burn only on RM_Contagion; tells precede it;
  Coalescence grows/absorbs/emits and dies to a Repulsor-forced Burn) — not run, per brief.

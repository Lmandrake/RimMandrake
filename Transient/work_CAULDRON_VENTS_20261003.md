# CAULDRON_VENT_ENRICHMENT_HOOKS_1 work log 2026-10-03

Mod folder: src/RimMandrake/Cauldron only. Nothing outside it edited.

## What existed (searched src/ first)
- NO vent ThingDef anywhere in Cauldron (item's open question, owned by CAULDRON_MECHANICS_BUILD_1 part 3, still blocked on the gas grid).
  Other vents in the repo: RUT_ScaldVent (DivingInteraction, Scald floor), RUT_Vent* buildings (Utinni). Not reusable: different biome/mod.
- RM_MapComponent_VentBloomExposure: map-wide metal-load tax during RM_VentBloom (becomes vent-weighted here).
- RM_CompVexxissBehaviour: fire warden + poison water only; NO vent drinking.
- RM_CondensateHabitatExtension (RM_CondensateGardens.cs): shoreOf only; crystal flower / blood bouquet / giant toxic flower exist as plants with NO extension.
- Artpipe searched before any art (see end).

## Choices (the design calls this item needed)
1. WHAT A VENT IS (my call, so the hooks have something to hang on; part 3 can still replace the gas half): ThingDef RM_CauldronVent
   (Building_SteamGeyser-shaped natural building, 2x2, class RM_Building_CauldronVent) spawned by RM_MapComponent_CauldronVents.MapGenerated
   on RM_Cauldron maps only. It carries STATE (temperament Stable/Leaking, lastBlowoutTick, suppression, silencedUntil) and emits air puffs
   scaled by output. NO real gas and no GasType (part 3). Existing saves/maps get no vents (mapgen only) = old map-wide exposure.
2. Falter foreknowledge (open design call on CAULDRON_MECHANICS_BUILD_1 part 1): NO foreknowledge of the next roll is needed. The engine sets curWeather
   at transition START and TransitionLerpFactor ramps 0->1; the vents go hushed (output x0.1) for that whole ramp, then bloom output (x2.5) once lerp==1.
   Public API only, no Harmony, no reflection. The tell is therefore real but short (one weather transition), not a day's notice.
3. Weather multipliers: data on the vent def (RM_VentWeatherOutputExtension): ScatterDusk 1.0, VentBloom 2.5, VapourBank 0.8, Dewfall 0.6.
4. Vent-local exposure: weight 1 within 8 cells of a live vent, falling to a 0.1 floor by 45 cells; silenced vents contribute their recovery factor
   (0 while silenced). Maps with no vents keep the old map-wide tax. Heat: NO new hediff, NO heat. The existing RM_VentMetalLoad is the only effect.
5. Vexxiss vent-drinking: wild vexxiss only. Comp scans every 250 ticks (radius 40; 80 while faltering/blooming = "follows the groans"),
   starts job RM_VexxissDrinkVent; each drink tick adds suppression; at 1.0 the vent is silenced for ventSilenceDays (default 4) then recovers over 1 day.
   Output (puffs + inspect line + exposure) is visibly proportional to recovery.
6. Gardens: RM_CondensateHabitatExtension gains ventHabitat (StableRing | ChronicLeak | RecentBlowout) + ventRadius. Crystal flower = StableRing,
   blood bouquet = ChronicLeak, giant toxic flower = RecentBlowout (blowout = bloom onset stamped on the vent; recent = 10 days).
   Gardens MapGenerated forces vent generation first (one idempotent call) because MapComponent order is not guaranteed.
7. Toggles (RM_CauldronSettings): ventsEnabled (worldgen), ventWeatherEnabled, ventFalterMessage, ventLocalExposureEnabled,
   vexxissDrinksVentsEnabled, ventGardensEnabled, ventSilenceDays (slider).

(results appended below)

## Results
- Files (all Cauldron): Source/RM_CauldronVents.cs (new, in csproj), RM_CauldronMod.cs (7 settings + UI), RM_VentBloomExposure.cs (DefOf + vent weight),
  RM_CompVexxissBehaviour.cs (drink), RM_CondensateGardens.cs (vent rings), RM_Cauldron.csproj; Defs/ThingDefs_Buildings/RM_CauldronVent.xml,
  Defs/JobDefs/RM_VexxissDrinkVent.xml, 3 flora extensions in RM_CauldronFlora.xml; Textures/Things/Building/RM_CauldronVent.png; validation.py + selftest_cauldron.py.
- winbuild Cauldron: BUILT 0 err. validate_patch (--defs Core + src): 0 errors; 7 advisory texPath warnings are the pre-existing plant art paths.
- Load-log checks: vent def uses only Core fields copied from SteamGeyser + BuildingNaturalBase parent; JobDef fields defName/driverClass/reportString/casualInterruptible;
  no SoundDef, no Trainability, no butcher/plant nutrition changes, no patch operations, no FindMod use.
- Art: artpipe done/RM_CauldronVent.json (CAULDRON_BEDAZZLE_SITTING_1, facts PASS, 256x256) wired as-is; no owner decision recorded on it.
- selftest_cauldron.py: 52 components, healthy 52/52, 49 breaks each reddening only its own component. Live: UNMEASURED (no bridge run).
- Not built / owed: real vent gas + gas-tap scaffold (part 3); mapgen of vents on a new Cauldron map unproven live; vent flower rings unproven live;
  walk doc design/validation_walks/RimMandrake/Cauldron.md (outside Cauldron) has no lines for the vents chain yet; the settings window may now
  overrun its panel (no scroll in DoWindowContents); the campaign twin RUT_PoisonForest gets no vents (biome check is RM_Cauldron only).

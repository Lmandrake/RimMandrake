# Grey Sea floor checks 2026-10-08 (GREYSEA_FLOOR_PASS_1, offline)

## 1 Weather - FAIL, FIXED
- A seabed-layer floor map's biome is RM_SeabedFloor_GreySea (tile PrimaryBiome). Its baseWeatherCommonalities was EMPTY; RM_SeabedFloorLife.CopyLife copies flora and cast only.
- RM_GreySaltSnow (real def, TerminalBiomes/Defs/WeatherDefs) was listed only on RM_GreySea, i.e. the retired hatch pocket-map path. On the layer floor: Clear only, salt snow never fell, hull-crust salt-snow multiplier never fired.
- Fix: DivingInteraction/Patches/RM_SeabedFloor_GreyWeather.xml adds Clear 12 / RM_GreySaltSnow 6 to the floor biome, guarded by the WeatherDef existing. Fog deliberately dropped.
- Other floors (Scald, Twilight, Chill) also have empty weather: out of scope, noted for BENCH.
- All weather defs referenced (Clear, RM_GreySaltSnow) resolve. Unverified: salt-snow overlay on a layer map (live sitting).

## 2 Settings - PASS
- RM_DivingSettings: seabedFloorContentEnabled, seabedFloorLifeEnabled (restart), seaFloorBandsEnabled, greyPoolDefenceEnabled, greyPoolSentinelEnabled, greyElderDischargeEnabled, greyElderTradeEnabled; all default true, all Scribed, all with UI checkboxes. TerminalBiomes: greySeaEnabled, hull crust + salt-snow multiplier, lamp toggles.
- Gap (judgement): the new weather patch has no toggle (patches cannot read settings). Acceptable; BENCH may want a gate.

## 3 Robustness - PASS
- animalDensity/plantDensity 0 on the floor XML is by design; Reassert restores from the sea (0.1 x factor, 0.22) at FinalizeInit (Map Designer reset was handled).
- RM_GreySea: wildAnimals uses shorthand elements, no <li>; animalDensity 0.1; plantDensity 0.22; fishTypes present, 11 catch rows incl. rare table, maxFishPopulation 60.
- No <Operation MayRequire> in DivingInteraction or TerminalBiomes patches.
- validate_patch.py: 0 errors (4 intentional add-if-missing warnings). Not run with --defs (no live dump used).

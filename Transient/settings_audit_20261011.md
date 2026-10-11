# Settings audit (offline, static)

Offline static audit of SettingsKit screens. NOT live verification: no screen has been opened in the game.

- csproj scanned: 195; with a Mod/ModSettings class: 105; using SettingsKit: 103
- OK: 105; FAIL: 0
- failing check (1): 0
- failing check (2): 0
- failing check (3): 0
- failing check (5): 0
- check (4) label keys: kit screens use literal English strings; mods calling Translate(): 8 (no translation keys required by the kit)
- check (5) pairs compared (field initialiser vs Scribe default): 1819

## Failures

| mod | csproj | failures |
|---|---|---|

## All mods with settings

| mod | status | kit | defaults pairs | notes |
|---|---|---|---|---|
| RimMandrake/Abyss | OK | True | 31 |  |
| RimMandrake/AcousticScanner | OK | True | 0 |  |
| RimMandrake/Aftermath | OK | True | 4 |  |
| RimMandrake/BiomesShell | OK | True | 0 |  |
| RimMandrake/BlueDesert | OK | True | 25 |  |
| RimMandrake/Cauldron | OK | True | 27 |  |
| RimMandrake/Contagion | OK | True | 14 |  |
| RimMandrake/CreatureBehaviors | OK | True | 121 |  |
| RimMandrake/DivingInteraction | OK | True | 36 |  |
| RimMandrake/EnvironmentalHazards | OK | True | 83 |  |
| RimMandrake/ExplosiveGrowth | OK | True | 25 |  |
| RimMandrake/ExplosiveKnockback | OK | True | 25 |  |
| RimMandrake/FeverWood | OK | True | 53 |  |
| RimMandrake/FlameStatues | OK | True | 7 |  |
| RimMandrake/FloodedCanyon | OK | True | 32 |  |
| RimMandrake/FlowWorks | OK | True | 100 |  |
| RimMandrake/GelatinousSlime | OK | True | 26 |  |
| RimMandrake/GimmeSomeSlack | OK | True | 52 |  |
| RimMandrake/Graffiti | OK | True | 6 |  |
| RimMandrake/GravshipLanding | OK | True | 1 |  |
| RimMandrake/Greentide | OK | True | 34 |  |
| RimMandrake/HugeThings | OK | True | 30 |  |
| RimMandrake/Inhabited | OK | True | 3 |  |
| RimMandrake/KeelHoist | OK | True | 19 |  |
| RimMandrake/KineticArms | OK | True | 23 |  |
| RimMandrake/LanternDeeps | OK | True | 41 |  |
| RimMandrake/LeaningScrub | OK | True | 59 |  |
| RimMandrake/LoadTracer | OK | False | 0 | no SettingsKit use (bespoke screen); (3) no committed DLL stamp |
| RimMandrake/LongShade | OK | True | 17 |  |
| RimMandrake/LoreStages | OK | True | 1 |  |
| RimMandrake/LuminousPigment | OK | True | 56 |  |
| RimMandrake/Miasma | OK | True | 18 |  |
| RimMandrake/MovingDunes | OK | True | 8 |  |
| RimMandrake/NightsideIce | OK | True | 13 |  |
| RimMandrake/Ninefold | OK | True | 7 |  |
| RimMandrake/OasisMaker | OK | True | 11 |  |
| RimMandrake/Oracle | OK | True | 0 |  |
| RimMandrake/ProximityHatch | OK | True | 4 |  |
| RimMandrake/Pyrelands | OK | True | 33 |  |
| RimMandrake/RaidRedesigner | OK | True | 4 |  |
| RimMandrake/RimProperty | OK | True | 11 |  |
| RimMandrake/RustCathedral/Source/Hum | OK | True | 26 | settings-only assembly; Mod subclass lives in a sibling assembly of the same mod; (3) no committed DLL stamp |
| RimMandrake/RustCathedral/Source/RustCathedral | OK | True | 13 | (3) no committed DLL stamp |
| RimMandrake/RustCathedral/Source/Walls | OK | True | 4 | settings-only assembly; Mod subclass lives in a sibling assembly of the same mod; (3) no committed DLL stamp |
| RimMandrake/RustChrome | OK | True | 0 |  |
| RimMandrake/SacredGraffiti | OK | True | 2 |  |
| RimMandrake/Scarlands | OK | True | 83 |  |
| RimMandrake/SeaShores | OK | True | 0 |  |
| RimMandrake/ShipVermin | OK | True | 8 |  |
| RimMandrake/SolarMirrors | OK | True | 25 |  |
| RimMandrake/Stillsand | OK | True | 41 |  |
| RimMandrake/StructureInjections | OK | True | 1 |  |
| RimMandrake/TerminalBiomes | OK | True | 52 |  |
| RimMandrake/TheBazaar | OK | True | 7 |  |
| RimMandrake/TheForge | OK | True | 44 |  |
| RimMandrake/TheRot | OK | True | 41 |  |
| RimMandrake/TheSump | OK | True | 18 |  |
| RimMandrake/Visibility | OK | True | 3 |  |
| RimMandrake/Warcasket | OK | True | 7 |  |
| RimMandrake/Wasteland | OK | True | 33 |  |
| RimMandrake/Watchers | OK | True | 19 |  |
| RimMandrake/WeatherSuite | OK | True | 6 |  |
| RimMandrake/Webwork | OK | True | 14 |  |
| RimMandrake/WeepingStones | OK | True | 8 |  |
| RimMandrake/Wreckage | OK | True | 7 |  |
| RimMandrake/WreckedMachines | OK | True | 12 |  |
| RimStarWars/Armoury | OK | True | 29 |  |
| RimStarWars/Bacta | OK | True | 7 |  |
| RimStarWars/BrainWorms | OK | True | 4 |  |
| RimStarWars/DesertVehicleReskin/Source/Fuel | OK | True | 1 | (3) no committed DLL stamp |
| RimStarWars/Droidworks/Source/Droidworks | OK | True | 30 | (3) no committed DLL stamp |
| RimStarWars/GizkaStowaway | OK | True | 11 |  |
| RimStarWars/JawaIonWeapons | OK | True | 9 |  |
| RimStarWars/JawaRules | OK | True | 9 |  |
| RimStarWars/SWBestiary/Source/BeastMechanics | OK | True | 6 | (3) no committed DLL stamp |
| RimStarWars/SWBestiary/Source/JawaIkee | OK | True | 1 | (3) no committed DLL stamp |
| RimStarWars/SWBestiary/Source/Livestock | OK | True | 4 | (3) no committed DLL stamp |
| RimStarWars/Sarlacc | OK | True | 12 |  |
| RimStarWars/TrophyCraft | OK | True | 2 |  |
| RimUtinni/Antiquities | OK | True | 4 |  |
| RimUtinni/Atlas | OK | True | 9 |  |
| RimUtinni/CathedralPass | OK | True | 1 |  |
| RimUtinni/DroidRepairJobs | OK | True | 2 |  |
| RimUtinni/EggReckoning | OK | True | 1 |  |
| RimUtinni/EmpirePursuit | OK | True | 13 |  |
| RimUtinni/FallLineArrivals | OK | True | 15 |  |
| RimUtinni/FungalSoilTrade | OK | True | 4 |  |
| RimUtinni/KyberTradePlot | OK | True | 1 |  |
| RimUtinni/LongHunger | OK | True | 4 |  |
| RimUtinni/PlantGrowth | OK | True | 1 |  |
| RimUtinni/PropaneLakeMechanics | OK | True | 0 |  |
| RimUtinni/PyrelandsMechanics | OK | True | 3 |  |
| RimUtinni/RestrainingBolts | OK | True | 3 |  |
| RimUtinni/RiverColors | OK | True | 1 |  |
| RimUtinni/ScarlandsLadder | OK | True | 3 |  |
| RimUtinni/ScavengerEvents | OK | True | 10 |  |
| RimUtinni/ShipMemory | OK | True | 2 |  |
| RimUtinni/ShipShields | OK | True | 13 |  |
| RimUtinni/ShokkweaveEconomy | OK | True | 1 |  |
| RimUtinni/StructureInjectionsRUT | OK | False | 3 | no SettingsKit use (bespoke screen) |
| RimUtinni/UnfinishedLine | OK | True | 42 |  |
| RimUtinni/UtinniPatches | OK | True | 8 |  |
| RimUtinni/UtinniStatues | OK | True | 3 |  |
| RimUtinni/WasteRun | OK | True | 12 |  |
| RimUtinni/WildsteamEggBounty | OK | True | 1 |  |

## Sanity probe

ShipMemory (known to have a SettingsKit screen) found: True

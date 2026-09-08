# Fire Ecology — validation walk
subject: src/RimStarWars/FireEcology  (packageId mandrake.rsw.fireecology)
deps: brrainz.harmony (hard), Ludeon.RimWorld base (declared modDependency, always present)
list: minimal   # no third-party mod dependency; the ash ladder/terrain/weather all ride vanilla mechanisms
status-hint: generic desert-savanna fire-ecology engine — scorchable-ground → ash-ladder terrain chain, a Black Rain weather that follows and extinguishes a large fire, fire-triggered fulgurites/scorch-fruit, a firefoam sprayer + firebreak strip. Campaign wiring (which biome uses it) lives in RimUtinni, not here.

## must be true
- The four scorchable-ground TerrainDefs (RSW_FE_Ground_Sand/Gravel/Soil/SoilRich) each burnedDef-chain into RSW_FE_Ash_Trace, and Trace→Light→Heavy→Deep chain forward with pathCost climbing (1→2→9→16) and fertility falling (0.5→0.25→0.05→0.0) at each rung.
- RSW_FE_BlackRain (WeatherDef) has rainRate 1.1 and isBad true — it rides vanilla's ChanceFactorRainOnFire/FireWatcher.LargeFireDangerPresent mechanism unmodified, so this mod defines no eventMakers.
- RSW_FE_FirefoamSprayer exists with a working verb, and RSW_FE_FirebreakLine is a buildable zero-fertility terrain.
- RSW_FE_Plant_ScorchFruit never appears in any biome's wildPlants list (it only spawns via the C# fire-tick hook) and rots via CompProperties_Rottable (daysToRotStart 1.1) if unharvested.
- The one C# hook (FireEcologyHookMod, Harmony ID mandrake.rsw.fireecology) patches WeatherEvent_LightningStrike.DoStrike (fulgurite spawn on sand-family ground, 35% chance) and Fire.TickInterval (loose-ash dusting + rare scorch-fruit seeding on scorchable ground, capped at 40 live scorch-fruit per map) — both postfixes, both no-op safely if their def targets are missing.
- ⛔ KNOWN, INTENTIONAL Config errors — do NOT flag these as failures: RSW_FE_Ash_Trace/Ash_Light/Ash_Heavy each log "Config error in RSW_FE_Ash_<x>: burnedDef is flammable" (vanilla's ConfigErrors() assumes burnedDef is terminal; the ash ladder deliberately isn't), and each of the four RSW_FE_Ground_<x> terrains logs the same about burnedDef pointing at RSW_FE_Ash_Trace. That is 7 expected Config error lines total, named in the .xml files' own comments.

## the walk
1. [L] Player.log after load contains exactly the 7 known "Config error in RSW_FE_..." lines named above (4x RSW_FE_Ground_*, 3x RSW_FE_Ash_Trace/Light/Heavy) and no OTHER "Config error in mandrake.rsw.fireecology" or "Config error in RSW_FE_" line, and no XML error naming AshLadder.xml, Firebreak.xml, ScorchableGround.xml, BlackRain.xml, Fulgurite.xml, ScorchFruit.xml, or FirefoamSprayer.xml
2. [L] Player.log contains both Harmony arm lines verbatim: "[RimMandrake.StarWars.FireEcology] fulgurite-spawn: armed; strikes on sand-family ground may leave a fulgurite" and "[RimMandrake.StarWars.FireEcology] fire-tick-ash-scorchfruit: armed; burning cells on scorchable ground may dust loose ash and rarely seed a scorch-fruit pod" (their absence means AccessTools.Method returned null — a game-version rename, not a config error)
3. [D] def read-back: TerrainDef RSW_FE_Ash_Trace.burnedDef = RSW_FE_Ash_Light; RSW_FE_Ash_Light.burnedDef = RSW_FE_Ash_Heavy; RSW_FE_Ash_Heavy.burnedDef = RSW_FE_Ash_Deep; RSW_FE_Ash_Deep.burnedDef is unset (chain terminates)
4. [D] def read-back: TerrainDef RSW_FE_Ground_Sand/Gravel/Soil/SoilRich each have burnedDef = RSW_FE_Ash_Trace
5. [D] def read-back: WeatherDef RSW_FE_BlackRain has rainRate=1.1, isBad=true, no eventMakers field set
6. [D] def read-back: ThingDef RSW_FE_Plant_ScorchFruit has plant.harvestedThingDef = RSW_FE_ScorchFruitYield, comps includes CompProperties_Rottable with daysToRotStart=1.1
7. [D] def read-back: ThingDef RSW_FE_FirefoamSprayer resolves with a verb entry; TerrainDef RSW_FE_FirebreakLine has fertility=0
8. [B] jawa/set_terrain {terrain: RSW_FE_Ground_Sand} on a test cell → jawa/get_terrain_batch on that cell → expect RSW_FE_Ground_Sand read back
9. [B] jawa/spawn_thing {def: RSW_FE_Fulgurite} → expect a live thing (proves the def itself instantiates cleanly outside the Harmony hook's own rare-chance path)
X. [S] (human pass) ash-ladder terrain visual ramp (Trace→Deep) and Black Rain's sky-color/overlay read — out of scope here

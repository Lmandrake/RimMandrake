# LongHunger — validation walk
subject: src/RimUtinni/LongHunger  (packageId mandrake.rut.longhunger)
deps: Ludeon.RimWorld.Anomaly (modDependencies + loadAfter)
list: minimal+Anomaly     # RUT_LongHungerSurfaces/RUT_LongHungerContract need no other third-party defs
status-hint: Ash'karr's VAST-tier dune leviathan — a Building-class world entity (no <race>) that erupts, pulses tremor damage, then submerges dropping salvage; reached only through a QuestScriptDef contract, never the wild storyteller pool.

## must be true
- RUT_Groundcaller and RUT_LongHunger both load with no XML config error naming LongHunger.
- RUT_LongHungerSurfaces has baseChance 0 (never fires from the natural incident pool) and a workerClass of LongHunger.IncidentWorker_LongHungerSurfaces.
- RUT_LongHungerContract offers as a normal quest (rootSelectionWeight 0.4) and its QuestNode_CreateIncidents references RUT_LongHungerSurfaces with points inside that IncidentDef's 0..99999 threat-point range, so TestRunInt never rejects it.
- Spawning RUT_LongHunger on a map triggers an immediate eruption explosion (GenExplosion, radius 4.5, Bomb damage 90) in LongHungerThing.SpawnSetup, then tremor pulses every 600 ticks (radius 3, damage 45) until it submerges at 2500 ticks and drops loot from Reward_ItemsStandard (marketValueRange 600–1400) before destroying itself.
- RUT_Groundcaller is buildable (costList Steel 60 + ComponentIndustrial 2, WorkToBuild 800) and has a MinifiedThing minifiedDef, so it can be built, uninstalled and reinstalled like any other prop.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.longhunger" and no XML error naming ThingDefs_LongHunger.xml, IncidentDefs_LongHunger.xml, Quest_LongHunger.xml, or WeatherDefs_LongHunger.xml
2. [D] def read-back: ThingDef RUT_LongHunger exists; thingClass = LongHunger.LongHungerThing, statBases.MaxHitPoints = 2000
3. [D] def read-back: ThingDef RUT_Groundcaller exists; costList Steel = 60, ComponentIndustrial = 2, minifiedDef = MinifiedThing
4. [D] def read-back: IncidentDef RUT_LongHungerSurfaces exists; baseChance = 0, workerClass = LongHunger.IncidentWorker_LongHungerSurfaces, minThreatPoints = 0, maxThreatPoints = 99999
5. [D] def read-back: QuestScriptDef RUT_LongHungerContract exists; rootSelectionWeight = 0.4, expireDaysRange = 2~4
6. [D] def read-back: WeatherDef RUT_DuneHaze exists; isBad = true, favorability = Bad
7. [B] rimworld/spawn_thing {defName: "RUT_LongHunger", x, z} → thing spawns; jawa/list_things confirms RUT_LongHunger present on the map immediately after (eruption explosion is not separately observable through a bridge tool — read the Player.log for the resulting damage/kill messages instead)
8. [L] after step 7, wait ~2500+ ticks in-game and check Player.log / jawa/list_things for RUT_LongHunger's disappearance (Destroy(DestroyMode.Vanish)) and new loot items placed near its former cell, confirming Submerge() ran
9. [S] (human pass) the eruption/tremor VFX and the PitGate-borrowed placeholder art read as intentional, not broken

Live check of IncidentDef RM_ShadeStampede ("stampede for your roof", LONGSHADE_STAMPEDE_ROOF_1, closed `--none-owed`, never run in game). Needs the bridge and an RM_LongShade home map with a roofed home-area cell and a herd.

## criteria
With stampedeEnabled=true on an RM_LongShade map, a herd (>=6 same-def wild herdAnimals within 25 cells, >=50% with AmbientTemperature > SafeTemperatureRange().max) makes the incident canFireNow=true; firing it sends the letter "An overheated herd is bolting for your roof" and every runner gets a Sprint Goto job to a roofed home-area cell, re-issued every 120 ticks until each has cooled or 6000 ticks pass. Without a herd or roof, canFireNow=false. With stampedeEnabled=false, canFireNow=false.

## verify
1. `jawa/get_defs` defs="IncidentDef/RM_ShadeStampede" fields=defName (STRING arg; check success/foundCount).
2. Scene: `jawa/spawn_pawn` 8 of a herdAnimal PawnKind from the biome roster (`jawa/spawn_pawn` returns spawnedCount/failedCount; require spawnedCount 8), home area with a roof built over a cell; raise heat or accept it: if none overheated, canFireNow stays false (that IS a valid control).
3. `jawa/fire_incident` incidentDef=RM_ShadeStampede dryRun=true: require canFireNow=true. Then fire for real (the capability matrix says dryRun is the proven path; the real fire may report fired=false, so confirm by `jawa/letter_list` containing the title above and `jawa/pawn_get` on a runner showing CurJob Goto).
4. Toggle control: `jawa/mod_settings_field` action=set field=stampedeEnabled value=false, dryRun again, require canFireNow=false.
UNMEASURED looks like: map biome not RM_LongShade; spawnedCount < 8; dryRun canFireNow=false with the reason unknown (no herd hot enough) and no way to force heat; a fired=false result with no letter. Say which, never call it passed.

# b5 Webwork + Warcasket SettingsKit retrofit (2026-10-10)
Changed: Webwork/Source/RM_WebworkMod.cs + RM_Webwork.csproj; Warcasket/Source/RM_WarcasketSettings.cs + RM_Warcasket.csproj; both Assemblies DLL+.srchash. Build 0 errors both. Selftest 193/193 ok (scratch deleted).
Dead settings: none (all read). False labels: none corrected (scopes in text were accurate); Webwork egg-relay/emergent sliders no longer hidden behind their toggles.

## Webwork groups
- World generation (WORLDGEN-AFFECTING) NewMapsOnly: generateOnWorldgen (BiomeWorker score)
- Emergent spawn Now: emergentSpawnEnabled, emergentSpawnChanceMultiplier (comp on destroy)
- Guaranteed nest (WORLDGEN-AFFECTING) NewMapsOnly: nestEnabled (GenStep)
- Egg economy Now: eggRelayIntervalMultiplier (timer roll)
- Creeping front and thrixweave (restart) NextGameStart: frontCreepEnabled, frontCreepIntervalMultiplier, thrixweaveTraderStripEnabled, webHarvestEnabled (StaticConstructorOnStartup gate)
- Urraveth remains: new maps (WORLDGEN-AFFECTING) NewMapsOnly: urravethSiteChance
- The dead giant (urraveth remains) Now: urravethEnabled (mixed: also gates new-site roll, tooltip says so), urravethThrixweavePerPiece, urravethWarningHours, urravethCollapseDamageMultiplier

## Warcasket groups
- Warcasket master switch Now: masterEnabled
- Suit failure and hazardous water Now: compoundFailureEnabled, terrainImmersionEnabled
- Sarcophagi Now: sarcophagiEnabled (also gates scatter)
- Cask bay and core dose Now: caskBayShieldingEnabled, coreDoseEnabled
- Sealed corpses on new maps (WORLDGEN-AFFECTING) NewMapsOnly: sealedCorpseScatterEnabled (GenStep only)

## MODS entries
    "Webwork": ("RM_WebworkMod.cs", "RM_Webwork.csproj", {
        "World generation (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Emergent spawn": "Now",
        "Guaranteed nest (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Egg economy": "Now",
        "Creeping front and thrixweave (restart)": "NextGameStart",
        "Urraveth remains: new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "The dead giant (urraveth remains)": "Now",
    }, ()),
    "Warcasket": ("RM_WarcasketSettings.cs", "RM_Warcasket.csproj", {
        "Warcasket master switch": "Now",
        "Suit failure and hazardous water": "Now",
        "Sarcophagi": "Now",
        "Cask bay and core dose": "Now",
        "Sealed corpses on new maps (WORLDGEN-AFFECTING)": "NewMapsOnly",
    }, ()),

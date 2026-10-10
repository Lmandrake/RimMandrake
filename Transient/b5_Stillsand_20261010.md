# b5 Stillsand SettingsKit retrofit 2026-10-10

Five separate Mod subclasses = five MODS entries (all in one RM_Stillsand.csproj, kit Compile Include added once).
Changed (Source): RM_StillsandMod.cs, RM_SkeletonSettings.cs, RM_GlassChainMod.cs, RM_StillsandEventsMod.cs, RM_DuneGaleSettings.cs (NEW: settings+Mod moved out of RM_DuneGale.cs, because the selftest scans the whole file for Scribe_Values), RM_DuneGale.cs (settings tail removed), RM_PreciousCaveSettings.cs/RM_StillsandWater.cs/RM_Thumper.cs/RM_DuneTrackEraser.cs (Draw removed; controls inlined into main screen; DrawRows kept for cave rows), RM_MapComponent_Zuurrik.cs (zuurrik* now static), RM_Stillsand.csproj; Assemblies DLL+.srchash.
Dead settings: none (all read). False labels: none; Dust-settled letter no longer hidden behind the warnings toggle. Scribe keys unchanged.
Scopes: NewMapsOnly = skeleton placement, cave carve/yardang/tor/drip/wall ring/tribal mark/cave rows; NextPulse = water-debt incident weighting, horizon warning+hours+passers, leviathan toggles+odds, den quest, gale+frequency, dust devils+frequency; rest Now.
Build: 0 errors. Selftest (scratch deleted): 273/273 ok incl. planted defects.

## MODS entries
```
    "Stillsand#Main": ("RM_StillsandMod.cs", "RM_Stillsand.csproj", {
        "Zuurrik (blood on the sand)": "Now",
        "Precious cave: carving and set pieces (fixed at map generation)": "NewMapsOnly",
        "Precious cave: what it holds (fixed at map generation)": "NewMapsOnly",
        "Nothing rots in the cave": "Now",
        "Water on the sand": "Now",
        "Water debt weights the sand's events": "NextPulse",
        "Under the sand: thumper, fishing and swimmers": "Now",
        "The Listening": "Now",
        "Footprints in moving sand": "Now",
    }, ("genStepEnabled", "yardangShapingEnabled", "torEnabled", "torChance", "dripEnabled", "wallRingEnabled", "tribalMarkEnabled", "rowEnabled", "rowWeight", "preservationEnabled", "bloomOnPour", "ledgerEnabled", "ledgerIncidentWeighting", "thumperEnabled", "thumperRadius", "sandFishingWakeEnabled", "sandFishingWakeChance", "driftSwimEnabled", "driftSwimDepth", "listeningHissEnabled", "listeningSingingEnabled", "listeningWarningEnabled", "singingWarningCells", "listeningRumbleEnabled", "duneErasesTracks")),
    "Stillsand#Skeletons": ("RM_SkeletonSettings.cs", "RM_Stillsand.csproj", {
        "Giant skeletons on new maps (fixed at map generation)": "NewMapsOnly",
        "Giant corpses become skeletons": "Now",
        "Bone harps and dune burial": "Now",
        "Dust on the horizon": "NextPulse",
        "Dust-settled letter": "Now",
    }, ()),
    "Stillsand#GlassChain": ("RM_GlassChainMod.cs", "RM_Stillsand.csproj", {
        "Sun-fed work tables": "Now",
        "Sand sieve": "Now",
        "Solar and wringing stills": "Now",
        "Sun lance": "Now",
        "Geophone": "Now",
        "Recipes": "Now",
    }, ()),
    "Stillsand#Events": ("RM_StillsandEventsMod.cs", "RM_Stillsand.csproj", {
        "Leviathan incidents": "NextPulse",
        "Muurrok mirror beam": "Now",
        "Krayt horn": "Now",
        "Krayt den quest": "NextPulse",
    }, ("leviathanDisabled", "leviathanOdds")),
    "Stillsand#DuneGale": ("RM_DuneGaleSettings.cs", "RM_Stillsand.csproj", {
        "The dune gale": "NextPulse",
        "Gale effects": "Now",
        "What the wind uncovers at gale end": "Now",
        "Dust devils": "NextPulse",
    }, ("emergenceOff",)),
```

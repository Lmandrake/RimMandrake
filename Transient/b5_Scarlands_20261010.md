# b5 Scarlands retrofit (2026-10-10)
Changed: src/RimMandrake/Scarlands/Source/RM_WarscarMod.cs, RM_Warscar.csproj (kit Compile lines), Assemblies/RimMandrake.Warscar.dll + .srchash (winbuild).
Only one settings class (RM_WarscarSettings); no others in file.
Dead settings: none (all 83 read; crossBiome* via Governs/Coverage on MapComponent ticks). No "Not wired yet" group.
False labels corrected: enableWreckLichenSeeder tooltip + cross-biome title claimed "Worldgen-affecting" but read in MapComponentTick (Now); removed. Totchak/hospice/pools/chotrix master-switch tooltips now say both effects (live + new maps).
Groups split by scope (enabled switches read on tick AND gen stay in the Now group; per-map counts moved to "placement" NewMapsOnly groups).
Build: 0 errors. Selftest: 185/185 ok.
MODS entry:
    "Scarlands": ("RM_WarscarMod.cs", "RM_Warscar.csproj", {
        "Biome rarity (WORLDGEN-AFFECTING)": "NewMapsOnly",
        "Broken turrets": "Now",
        "Old-line turret tuning": "NextGameStart",
        "Totchak (wall colossus)": "Now",
        "Inscribed panels: placement (old tongue)": "NewMapsOnly",
        "Inscribed panels: reading": "Now",
        "Hospice (kneeling chassis and cradle)": "Now",
        "Hospice: chassis placement": "NewMapsOnly",
        "Rainbow pools": "Now",
        "Rainbow pools: placement": "NewMapsOnly",
        "Chotrix (invisible hunter)": "Now",
        "Chotrix: placement": "NewMapsOnly",
        "Lacquered cloaks": "Now",
        "The Settling (calm-triggered war fallout)": "Now",
        "War dust and buried shells": "Now",
        "Buried shells: placement": "NewMapsOnly",
        "Geiger choir (Warscar soundscape)": "Now",
        "The Warscar mark": "Now",
        "The Warscar mark: trade": "NextGameStart",
        "The chatrak's snap": "Now",
        "The chatrak's snap: turning speed": "NextGameStart",
        "Loosened wall panels": "Now",
        "Loosened wall panels: placement": "NewMapsOnly",
        "Aerosol screens": "Now",
        "Projector rings": "Now",
        "Projector rings: placement": "NewMapsOnly",
        "Species (restart required)": "NextGameStart",
        "Bileworm gas": "Now",
        "Wreck-lichen": "Now",
        "Cross-biome opt-in": "Now",
    }, ()),

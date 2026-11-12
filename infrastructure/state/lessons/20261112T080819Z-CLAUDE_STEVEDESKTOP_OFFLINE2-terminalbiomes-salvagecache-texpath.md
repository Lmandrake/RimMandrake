lint_terminalbiomes_defs.py reports a pre-existing ERROR texpath-resolves: TerminalBiomes/Defs/ThingDefs_Buildings/RM_FoundrySalvageCache.xml points texPath at Things/Building/Production/RUT_FoundrySalvageCache, with no PNG in TerminalBiomes/Textures (the def file was last touched by BIOME_TIER_CLEANUP_1, 8577860419, which renamed RUT_ defs to RM_; the texture path likely kept its RUT_ name, or the art never moved). Magenta in game. Found 2026-11-12 while linting the ship-gift art batch; not caused by it.
item: BIOME_SHIP_CONTRIBUTIONS_1
home: NONE

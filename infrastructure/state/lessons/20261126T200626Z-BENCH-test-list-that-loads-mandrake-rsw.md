A test list that loads mandrake.rsw.patches (StarWarsPatches) without mandrake.rsw.starwarsraces generates no colony map: StarWarsPatches/Defs/PawnKindDefs/AlienSpawnEnablers.xml has 13 PawnKindDefs that inherit RimMandrake_ColonyPawnKind from StarWarsRaces with no MayRequire, they load with no race, and vanilla ScenPart_StartingAnimal throws an NRE in map generation (Steve1, J20261126T193905Z-e58a2a). The proof then reads 'No current map'. Name StarWarsRaces in live-mods beside StarWarsPatches.
item: FASCINATING_WORLD_JUNK_1
home: skills/rimworld-load-round

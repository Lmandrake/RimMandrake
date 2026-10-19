# Tail donor mods: art-bearing retirement census, 2026-10-18

FOUNDRY, offline. Instruments: `donor_retire_census.py srctex|refs|deps` (HEAD after `7a2254bf1`). Owner scope (coordinator
relay): the eight art-bearing tail mods; Alpha Memes and VGE stay. All art is stand-in or accepted as rendered; re-review later.

| mod | art served to us | defName/patch dependence | effort | state |
|---|---|---|---|---|
| grimterra.biomesmod | none left (GRim tortoise/bullfrog/pinkbird + dessicated copied to `StandIn/` by `7a2254bf1`) | `MandrakePatches/GrimTerraTexPaths_Fix.xml`, `AnimalDessicatedTexPaths_Fix.xml` (FindMod-guarded); RUT biome rows name GRim animals (RUT_Wasteland/BlueDesert/CrackedLands/Greentide, MegafaunaYield, WildAnimals_Warscar, Thornvine_Edible, RM_ElectricGryllotalpa) | medium | art done; retire = repoint roster/yield rows to RM_ twins, then drop the two fix patches |
| aoba.fortress.industrial | none: `Things/Building/Linked/Wall` (SolarMirrors RM_SunVaultWall) is a Core appearance folder; census credits Aoba only because it adds `Wall_Atlas_Concrete` | no refs in src (no About, no MayRequire) | trivial | nothing owed; can leave the modlist |
| who.vfee.isopodageneline | none (Electrictick copies done) | `SW_Electrictick` MayRequire row in RUT_Wasteland; AnimalTolerances_Ashkarr; Warscar casts an RM_ twin; About loadAfter MandrakePatches/Doctrine/UtinniPatches | medium | roster row + tolerance patches to port |
| regrowth.botr.core | ChunkStone (FlowWorks, tool skips FlowWorks: still donor) ; Berries is a retexture of vanilla | RG_ plants/animals: PlantTolerances_Ashkarr (7 plants), AnimalTolerances, MegafaunaYield, BiomeCastEvictions, 4 MayRequire rows in RM_LeaningScrub, RUT_AridShrubland/Wasteland/Webwork; ResearchRetag + Armoury load order | large | Rimclaw already ported; FlowWorks ChunkStone owes a hand stand-in |
| oskarpotocki.vfe.insectoid2 | Megascarab (retexture of vanilla; RM_ShipVermin, BrainWorms) | VFEI2_ rows: FeverWood, Miasma, RUT_{FeverWood,Greentide,Miasma,Wasteland}, WildAnimals_Greentide FindMod, AnimalTolerances, MegafaunaYield, ResearchRetag TechprintGating (Hivetech), Armoury HiveEmitter; SWBestiary modDependencies row | large | Swarmling/Megathrips need RM_ twins; Hivetech research needs a port |
| mlie.horrors | none | Visceral (RM_Cauldron, RUT_Cauldron, ArtFold, Cauldron prized-meat patch), Terrorworm (RM_LeaningScrub, RUT_AridShrubland, tolerances), UtinniPatches forceLoadAfter | medium | two creatures to twin |
| lingluo.cockroach | none | Ling_Cockroach: RUT_RustCathedral row, tolerances, evictions, MegafaunaYield; RM_EatCleanableExtension.cs comment only; RM_CathedralRoach is already the clone | medium | drop rows (RM_CathedralRoach exists) + patches |
| sarg.alphagenes | none (Abyss ports AG_Gamma/Septimum as RM_) | PawnFlavor thought patches (~25 AG_ thoughts), Armoury AG_Forsaken* armour ratings, BlackstarCompany + FactionSlate (AG_XenohumanPirates, AG_OutlanderCivilUnion), Tolerances | large | gene/thought/faction content; port or cut by decision |

## Done this pass
- Stripped loadAfter rows that gate nothing: Abyss (alphagenes), Miasma (insectoid2), Scarlands (regrowth), Cauldron (horrors);
  none of those four mods patches a donor def.
- Art: every donor-served texPath of these eight except FlowWorks ChunkStone is already copied or core-served.
## Not done and why
- Remaining rows are live patches/MayRequire rows on donor defs (not dead while the donor loads); removing them is port work.
- Hard dependency probe: SWBestiary About lists insectoid2 under modDependencies (the census deps probe reads only other mods).

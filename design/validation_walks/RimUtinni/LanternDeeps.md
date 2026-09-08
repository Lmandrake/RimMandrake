# LanternDeeps — validation walk
subject: src/RimUtinni/LanternDeeps  (packageId mandrake.rut.lanterndeeps)
deps: BiomesTeam.BiomesCaverns (modDependencies + loadAfter, for BMT_CrystalCaverns and
BMT_CrystalsGenerator); m00nl1ght.GeologicalLandforms (loadAfter only, no hard need found
in this mod's own code/defs). The GenStep's own biome allowlist (BiomeGRimond,
RUT_NightsideIce, RUT_PropaneLake) names biomes shipped by grimterra.biomesmod (GRiNDTerra
Biomes, third-party) and this campaign's own src/RimUtinni/UtinniPatches — neither is
declared as a dependency here, so on any mod list missing all three the GenStep silently
never scatters (string-equality gate against `map.Biome.defName`, not a defOf reference).
list: full     # def/load checks only need minimal+BiomesCaverns, but proving the biome
                # gate actually fires needs a map on RUT_NightsideIce/RUT_PropaneLake/
                # BiomeGRimond, which only exist under the full campaign list
status-hint: Ships the persistent underground "Lantern Deeps" dungeon layer
(LANTERN_DEEPS_INJECTION_1): a natural-emergence entrance building that scatters onto
qualifying nightside/cold-biome maps and, when entered, generates a permanent pocket map
on Biomes! Caverns' BMT_CrystalCaverns biome. Ships no cave biome or crystal logic of its
own.

## must be true
- ThingDef `RUT_LanternDeepEmergence` ("lanternstone geode") is a `MapPortal`
  (`thingClass`), 6x6, `Impassable`, `holdsRoof=true`, `destroyable=false`; its
  `portal` block points `pocketMapGenerator` at `RUT_LanternDeepGenerator`, `exitDef` at
  `CaveExit`, `pocketMapSize` at 66.
- `GenStep_ScatterCavePortal` (extends vanilla `GenStep_ScatterGroup`) only scatters onto
  maps whose `Biome.defName` is exactly `BiomeGRimond`, `RUT_NightsideIce` or
  `RUT_PropaneLake` (a hardcoded `HashSet<string>`, because `GenStepDef` has no biome field
  and vanilla ships no `ScattererValidator_Biome`), and even then only rolls
  `Rand.Chance(chancePerMap)` = 0.08 (8%, FOUNDRY's placeholder density) before calling
  `base.Generate`. Every other biome's maps get a silent no-op.
- `GenStepDef RUT_LanternDeepEmergence_Scatter` (order 320) is patched into
  `MapGeneratorDef[@Name="MapCommonBase"]/genSteps` globally
  (`RUT_LanternDeepEmergence_MapGenPatch.xml`, `PatchOperationAdd`) — every map generation
  in the game runs this GenStep, and the biome self-gate above is what keeps it from
  affecting maps outside the three allowed biomes.
- `MapGeneratorDef RUT_LanternDeepGenerator` is `isUnderground=true`, `forceCaves=true`,
  `ignoreAreaRevealedLetter=true`, `disableCallAid=true`; its `pocketMapProperties` fix the
  pocket map's biome to `BMT_CrystalCaverns` at a constant `temperature` of 17; its
  `genSteps` list includes `BMT_CrystalsGenerator` (Biomes! Caverns' own crystal-placement
  step) alongside the standard underground terrain/rock/plant/fog steps.
- Sealing the portal (`CompProperties_Sealable`, `destroyPortal=true`) permanently destroys
  it and, on destruction, `CompProperties_LeaveFilthOnDestroyed` drops `Filth_LooseGround`
  filth at thickness 2 — anything or anyone left below is lost per the seal-comp's own
  confirm text.
- Placeholder art only: the ThingDef's own comment flags it reuses vanilla's
  `Things/Building/CaveEntranceA` texture pending real lanternstone-geode art
  (LANTERN_DEEPS_INJECTION_1).

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.lanterndeeps" and no
   XML error naming `RUT_LanternDeepEmergence.xml`, `RUT_LanternDeepGenerator.xml`,
   `RUT_LanternDeepEmergence_Scatter.xml` or `RUT_LanternDeepEmergence_MapGenPatch.xml`
2. [D] def read-back (minimal+BiomesCaverns): ThingDef `RUT_LanternDeepEmergence` exists;
   `thingClass=MapPortal`; `portal/pocketMapGenerator=RUT_LanternDeepGenerator`;
   `portal/exitDef=CaveExit`; `portal/pocketMapSize=66`
3. [D] def read-back (minimal+BiomesCaverns): MapGeneratorDef `RUT_LanternDeepGenerator`
   exists; `isUnderground=true`; `forceCaves=true`; `pocketMapProperties/biome=BMT_CrystalCaverns`;
   `pocketMapProperties/temperature=17`; `genSteps` contains `BMT_CrystalsGenerator`
4. [D] def read-back (minimal+BiomesCaverns): GenStepDef `RUT_LanternDeepEmergence_Scatter`
   exists; `order=320`; `genStep` Class =
   `RimMandrake.Utinni.LanternDeeps.GenStep_ScatterCavePortal`
5. [D] def read-back (minimal+BiomesCaverns): MapGeneratorDef `MapCommonBase`'s `genSteps`
   list contains `RUT_LanternDeepEmergence_Scatter` (confirms the global patch landed)
6. [B] (full list, quicktest map on a QUALIFYING biome — `RUT_NightsideIce`,
   `RUT_PropaneLake` or `BiomeGRimond`) repeat `jawa/run_genstep`
   `genStepDef=RUT_LanternDeepEmergence_Scatter` enough times to beat the 8% roll, checking
   `jawa/list_things` `defName=RUT_LanternDeepEmergence` after each — expect ≥1 result
   eventually (confirms the scatter itself works once the biome gate passes)
7. [B] (full list, quicktest map on a NON-qualifying biome, e.g. vanilla `Desert`) repeat
   `jawa/run_genstep` `genStepDef=RUT_LanternDeepEmergence_Scatter` the same number of times
   → `jawa/list_things` `defName=RUT_LanternDeepEmergence` returns 0 results throughout
   (confirms the biome gate, not just luck, is what step 6 exercised)
8. [L] Player.log after both steps 6 and 7 contains no exception naming
   `GenStep_ScatterCavePortal` or `RimMandrake.Utinni.LanternDeeps`
9. [S] (human pass) walk a colonist onto a scattered `RUT_LanternDeepEmergence` and use its
   "Enter" interaction to confirm the pocket map actually generates and reads as a crystal
   cavern in play, then test the "Collapse lanternstone geode" seal command — no bridge tool
   opens a MapPortal or generates a pocket map directly, so this step is genuinely
   interactive/visual and out of scope for the automated walk.

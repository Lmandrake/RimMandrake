# Seafloor chain audit (offline, read-only), clone /home/mandrake/rm/claude-offline4, 2026-11-11

## Status: DONE

The chain is gravship descent, then the floor map and its fauna, then shore fishing. Seas covered: RM_TheScald, RM_GreySea, RM_TwilightSea, RM_TheChill.

RimSage was NOT available. Every engine fact below is marked [engine-assumption]. The scratch instruments are in this directory:
- scripts/index.py builds idx.pkl (9188 defs).
- scripts/seas.py writes seas.txt.
- scripts/temps.py writes temps.txt.
- scripts/props.py writes items.txt.

## Findings

### F1. The floor layer is mirrored once per save and never re-mirrored. Severity HIGH, all four seas.
- Where:
  - src/RimMandrake/DivingInteraction/Source/RM_SeabedLayer.cs:231 generates only when `layer.Tiles.Count == 0`.
  - :88 shows that MirrorSurfaceOnto has a single caller, the WorldGenStep.
  - :359-397 is PopulateTile, which picks the biome at :383 (FloorBiomeFor, else RM_SeabedUnavailable) and the hilliness.
  - There is no other caller of PopulateTile or MirrorSurfaceOnto anywhere in src (grep).
- What the player sees: a floor tile keeps whatever biome it got when its save first built the layer.
  - (a) Saves that built the layer between 2026-09-26 (2db33bf237, phase 1, placeholder only) and 2026-10-03 (1a4737b42c, per-sea wiring): every RM_ sea floor is the generic RM_SeabedFloor. It has no RM_SeabedFloorExtension, so ChooseFor returns null and the map is a vanilla Encounter, with density 0 and none of the sea's animals, terrain or dressing.
  - (b) The planned repaint (big_repaint_plan_2026-10-21, jawa world_tile_import) re-stamps surface biomes on an EXISTING save. Floors under newly painted RM_ sea tiles stay as they were: RM_SeabedUnavailable if the tile was land before (impassable, so no landing), or RM_SeabedFloor if it was water before.
  - So the known "RUT_ falls back until the repaint" exclusion is NOT cured by the repaint on the dev save. Only a fresh world fixes it.
- Confidence: the code path is MEASURED. That the dev save actually carries a stale layer is INFERRED; check with the bridge seabed_layer_probe on the save. [engine-assumption] PlanetLayer tile biomes are scribed with the save.
- Suggested fix: re-mirror at load, inside WorldComponent FinalizeInit. For each floor tile whose biome differs from `SurfaceHasFloor ? FloorBiomeFor(above) : Unavailable`, call PopulateTile. Do not touch a tile that has a MapParent on it.

### F2 (minor, LOW). A stale comment.
RM_SeabedFloorBiomes.xml header says "Propane Lake is a RUT_ Utinni biome and is not wired here". It misleads anyone who reads it, but players do not see it. MEASURED.

## Non-findings (checked, OK)
1. Mapping (check 1):
   - Patches/RM_SeabedFloorBiomeWiring.xml has 4 Conditionals whose defNames match RM_TheScald, RM_GreySea, RM_TwilightSea and RM_TheChill exactly.
   - The 4 floor biomes RM_SeabedFloor_<Sea> exist, and each names RM_SeabedGenerator_<Sea>, which also exists.
   - [engine-assumption] Patches run over the combined XML of all mods, so load order does not matter, and a Conditional on an absent def does not abort the sequence.
2. Fauna (check 2):
   - RM_SeabedFloorLife copies the sea's wildAnimals and animalDensity ×30 onto the floor. It re-asserts this at FinalizeInit, in ChooseFor and in GenStep 890.
   - GenStep_SeaFloorFauna seeds at least 1 animal, about 20×density: Scald ~19, Twilight ~12.6, Grey ~6.6, and Chill a weighted draw of 3.
   - All wildAnimals pawnkinds exist (seas.txt).
   - Standable floor:
     - The Scald base is RM_SeaFloorGround and the Chill base is RM_ChillIceBedrock (bands 5–17 %, then the EnsureWalkable pass).
     - Grey and Twilight have no bands extension, so they fall to RM_SeaFloorGround (GenStep_SeaFloorTerrain.cs:49-53).
   - Temperatures (temps.txt): every race's comfort range contains its floor's constant temperature.
     - Scald 55 against a 15/20–95+ range.
     - Grey 12 against −10–55.
     - Twilight 8 against −10–50.
     - Chill −110 against −150 to −30.
3. Genstep attached (check 3): all four generators list RM_SeaFloorFauna, RM_SeabedLifeReassert, RM_SeabedAnimalsGated, Plants and Fog, with isUnderground false.
4. Descent (check 4):
   - FloorTileOf and SurfaceTileOf are arithmetic twins.
   - Fuel = depth × 0.2/m, clamped 0–2, and is the same in both directions (RM_SeabedDescentKernel.cs).
   - There is no hard-coded sea list. The only literal is "RM_TheChill" for the Chill weighted draw.
5. Shore (check 5):
   - The RM_SeaCoast TileMutatorDef exists (SeaShores/Defs/TileMutatorDefs/RM_SeaCoast.xml).
   - Shore terrains:
     - Scald: RM_ScaldWaterOcean*, Saltwater.
     - Grey: RM_WaterBrine* (MayRequire flowworks) and RM_SaltCrustShore.
     - Chill: RM_PropaneDeep/Shallow, Saltwater, from FlowWorks without MayRequire. This is OK because FlowWorks is always built.
     - Twilight: vanilla ocean, resolved through PrimarySeaFor because the ambiguous keys are dropped.
   - The Scald's freshwater-only table on Saltwater terrain is covered by the BandFor empty-band fallback (RM_SeaShoreUtility.cs:219).
   - Chill propane is fishable: it is Saltwater and providesCatch defaults to true.
   - [engine-assumption] FishingUtility.GetCatchesFor arg1 is the cell that the transpiler reads.
6. Catches (check 6):
   - All 36 catch and rare ThingDefs (items.txt) are items: parent FishBase ×34, ResourceBase ×2, and none has a `<race>`.
   - Every RM_*Catch race is in its sea's wildAnimals.
   - RM_Saal (Scald) has a written reason: its body is RM_Noohm (RM_ScaldFloorFauna.xml:31; RM_ScaldFish.xml:124). RM_Noohm is in wildAnimals.
   - The other rare entries are non-catch loot: Silver, Chemfuel, RM_SaltCameo, RM_LampBlack, and Corpse_RSW_ColoClawFish (already tracked as COLOCLAW_DECIDE_APEX_ALIVE_OR_CORPSE_ONLY).
- Known exclusions, not re-reported: RUT_ frozen sea tiles, and the absence of live proof.
- Edge case, not a defect: a land tile next to BOTH vanilla Ocean and Twilight keeps vanilla Coast (RM_TryAddMutator). Its WaterOcean cells may then serve the Twilight table through PrimarySeaFor. This is INFERRED and would be invisible to most players.

## Selftests (`--only --workers 1`; outputs st_run1.txt, st_run2.txt, st_swim.txt)
- PASS (7): seashores_proofs, sea_catch_alive, sea_floor_no_rain, sea_text_no_surface_place, divinginteraction_lint, seabed_descent_wiring, seashores_lint.
- swim_shore_reach:
  - FAIL under the runner (320 s; that run's tail hit the 520 s timeout).
  - PASS when run directly (3/3 shore cases, 12/12 mutants red). So the runner verdict is a time-budget artefact, not a code defect.
- selftest_seashores: FAIL, an environment problem. The staged build failed with 59 CS0246 errors (no RimWorld assembly refs on this seat), and the runner itself says "env/build failure, not a selftest verdict".
- CRASH (3): divinginteraction_fuzz, seashores_fuzz and terminalbiomes_fuzz all hit FileNotFoundError '/mnt/d/Luke/dev', the winbuild interop path, which is absent on this seat. These are environment crashes with no verdict.
- Owed: rerun the 4 build-dependent tests on a seat that has the game assemblies and the D:\Luke\dev path.

## Progress log
- Reads, index, seas/temps/items checks and selftests are done. Audit complete.

# Donor retirement: save residue and morning deploy plan, 2026-10-19

FOUNDRY, offline. Instruments: `donor_retire_census.py refs|srctex`, `save_adoption_check.py` (checked save:
`CANONICAL_ASHKARR_START_2026-09-12.DONORFREE_CANDIDATE_2026-10-18.rws`, list `ModsConfig.FULL.CANDIDATE_DONORS_RETIRED_2026-10-18.xml`).
The owner's canonical save was NOT edited.

## State of src/ (after `53a82ce37`, `0cd150154`)
- Live donor refs outside FlowWorks, json/py tooling and the two STAY mods (Alpha Memes, VGE): **0** XML/C# hits. 94 dead
  `MayRequire`/`loadAfter` rows for SWAC, Alpha Animals, Alpha Biomes, Caverns and others were stripped from UtinniPatches (the
  game dropped them anyway). C# prose naming Cockroach / alphabiomes edited; CreatureBehaviors DLL rebuilt (+`.srchash`),
  selftests 3/3 green. `JawaBench.BridgeTools` string edited, **DLL not rebuilt** (companion `build.py`, needs the game down: BENCH).
- FlowWorks (Bench's): 44 hits, untouched (`FLOWWORKS_AB_FINDMOD_DELETE_LAST_HOLDOUT`).
- Textures (`srctex`): MISSING x4 = three `BMT_Caverns/.../Dessicated_*` in `AnimalDessicatedTexPaths_Fix.xml` and
  `BMT_Caverns/Terrains/MycelialSoil` (`RUT_FungalSoil.xml`): Caverns art, no stand-in source on disk; owed.
  DONOR `Things/Building/Linked/Wall` (Aoba) is a Core appearance folder: false positive. DONOR_BUNDLE `Outland/Genes/Horns/Common/Bulb`
  (`SW_Genes.xml` texPathFemale): planner found no source (extract is `bulb_east.png` etc. under `observed/inventory/bundle_textures`);
  needs a hand `art install`. DONOR_INACTIVE `Things/Plant/Echeveria/EcheveriaA` (Greentide fish items): the art ledger REFUSED the copy,
  because the owner rejected that picture on the twilightsea sheet; needs his ruling or new art.

## Save residue the canonical save still carries (live repair steps for BENCH)
Game up with the donor-free list, save loaded, bridge held:
1. Landmarks (unresolved; 14 tiles): AB_TarLakes (tiles 994, 457, 476, 1859, 1866, 2637, 10015), AB_MagmaticQuagmire (2540, 7405, 7400),
   AB_QuicksandPits (1415), AB_PropaneLakes (x2: list with `save_adoption_check.py --json`). Remove each with `jawa/world_landmarks_set`
   (clear) then `world_commit`, or set to a provided LandmarkDef. The load drops them with an error otherwise.
2. Biomes with AB_ names (10 tiles-groups: AB_FeraliskInfestedJungle, AB_GallatrossGraveyard, AB_GelatinousSuperorganism,
   AB_MechanoidIntrusion ...): `world tileBiome` lostOnLoad hashes 59367 x1135, 65189 x546, 58457 x222: repaint those tiles
   (`world_tile_set`) to a provided biome; this is the planned one-time repaint, so just record it.
3. tileMutatorDefs: AB_DerelictClusters x171, AB_AmbientRadiation x104, AB_FeraliskNest x70, AB_AncientFreezingVent x61, WildTattooinePlants x1403:
   clear with the mutator setter, then `world_commit`.
4. Things: 91 AB_Mech_Ruined* buildings on maps plus ~400 unresolved AB_/AA_ Thing names: Scribe drops each with one error line.
   Either `jawa/destroy_batch` on ids from `save_adoption_check.py --json`, or accept the drops and re-save once.
5. Pawns: AA_Eyeling669122 (Marquee, (175,0,134)) is re-homed to Alpha Memes: destroy, spawn RSW_Ikee, re-create Bond with Yeku
   (Human470530). World pawn AA_Eyeling657692: leave or remove (owner's call).
6. Re-save under a new name; rerun `save_adoption_check.py` expecting 0 unresolved.

## Morning deploy plan (dry runs only; nothing applied)
- `deploy_custom_mods.py --mod UtinniPatches`: + 11 new, ~ 73 changed, - 9 deletions (prune), 10 held. Needs `--prune` to remove the
  game's stale Patches (BugTurretRetexture_GeonosianHive, Campaign_SumpNoTarRain, FeverWood_Rename, Greentide_Rename,
  Horrors_NihilRename, JawaTerrain_HorrorWastes ...).
- `deploy_custom_mods.py --compose biomes` (CreatureBehaviors is folded in): + 62, ~ 68, - 2 (TheSump RM_SumpTarRainLock, RM_TarRain
  stay unless `--prune`), 5 held. Includes the rebuilt CreatureBehaviors DLL: game must be DOWN to write it.
- One step: game down, then `deploy_custom_mods.py --mod UtinniPatches --apply --prune` and `--compose biomes --apply`; re-run
  both dry (expect clean), then `modcheck`.

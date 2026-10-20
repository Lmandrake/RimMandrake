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
1. Landmarks (unresolved; 11 tiles): AB_TarLakes (tiles 994, 457, 476, 1859, 1866, 2637, 10015), AB_MagmaticQuagmire (2540, 7405, 7400),
   AB_QuicksandPits (1415). Since 2026-10-19 each has a port
   (`RM_TarLakes`, `RM_MagmaticQuagmire`, `RM_QuicksandPits`; map `design/RimMandrake/retired_mutators_port_map.json`): set the
   port with `jawa/world_landmarks_set` then `world_commit`, or use the offline-renamed copy (WORLDMAP_REPAIR note).
   The load drops an unrenamed one with an error.
   **`AB_PropaneLakes` is NOT a landmark (gate G10, settled 2026-10-19, MEASURED):** `save_adoption_check.py --save
   CANONICAL_ASHKARR_START_2026-09-12.rws` (read-only; sha256 prefix 1ff329161abeaa8c before and after) finds its 2 rows at
   `worldGenerationData/biomeCommonalities/keys/li` ×1 and `worldGenerationData/biomeScoreOffsets/keys/li` ×1 — the world-creation
   biome sliders — and 0 rows under `landmarks/values/li/def`, 0 in the landmark worklist. The earlier "x2 landmarks" came from the
   tool's summary bucket `WorldObject/landmark`, which groups by owner kind, not by save path. It is on no tile; on a fresh world it
   does not arise (the slider key exists only if Alpha Biomes is loaded at creation, and it is off the PAINT list).
2. Biomes with AB_ names (10 tiles-groups: AB_FeraliskInfestedJungle, AB_GallatrossGraveyard, AB_GelatinousSuperorganism,
   AB_MechanoidIntrusion ...): `world tileBiome` lostOnLoad hashes 59367 x1135, 65189 x546, 58457 x222: repaint those tiles
   (`world_tile_set`) to a provided biome; this is the planned one-time repaint, so just record it.
3. tileMutatorDefs: AB_DerelictClusters x171, AB_AmbientRadiation x104, AB_FeraliskNest x70, AB_AncientFreezingVent x61, WildTattooinePlants x1403
   and the rest: since 2026-10-19 rename each to its port per `design/RimMandrake/retired_mutators_port_map.json`
   (`save_donor_rewrite.py --mutators-only` does it offline on a copy); clear only the four with no port (AB_DerelictArchonexus,
   AB_DerelictBioLab, AB_DerelictKemeticTemple, WildDantooinePlants) or leave them for the owner's repaint call.
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

## Class names, not just def names (2026-10-19, FOUNDRY)
`save_donor_census.py` and `save_adoption_check.py` read defNames in element TEXT. A save also names C# TYPES in
`Class="..."` attributes, and a retired donor's type there is invisible to both. It broke every test site and every
canonical candidate: `<li Class="VFEInsectoids.Area_Hive">` in `<areaManager><areas>` loads as a null area, the whole
AreaManager is discarded, Vehicle Framework NREs and the map never finishes (`Transient/vf_nre_rootcause_2026-10-19.md`).

- **Checker:** `src/RimMandrake/Utils/save_class_census.py <save>...` resolves every `Class=` against the TypeDef tables
  of every DLL of the live ModsConfig list (dnfile; cache `~/.cache/rm_save_class_census_types.v2.json`, first run ~15 min
  over /mnt/c, then seconds) and grades each unresolved one: **FATAL** (an Area: kills the AreaManager), **SKIPPED**
  (a map/world/game component: dropped, harmless), **OTHER** (comps, hediffs, pawn parts: review). Exit 1 on any FATAL.
  `--strip-fatal OUT` writes a copy without the FATAL elements (byte-level, CRLF kept, never in place). It refuses to
  report when its probe cannot see `RimWorld.Area_Home`/`Verse.Area`, and names any DLL dnfile could not read.
- **Fixed copies** (originals untouched; backups + md5 in `D:\Luke\dev\_rmscratch\saves_backup_20261019_areafix\`,
  `MD5_ORIGINALS.txt`, `fixed\MD5_FIXED.txt`, `fixed\VERIFY.txt`): the five `RM_TestSite_*_v1`, `CANONICAL_ASHKARR_START_2026-09-12`,
  its `.DONORFREE_CANDIDATE_2026-10-18`, `_donorfree`, `_donorfree_p6b`, and `CANONICAL_ASHKARR_START_2026-10-18_DONORFREE` and
  `_REPAIRED`, each saved beside the original as `<name>_AREAFIX.rws`. One element removed each (an empty 250x250 grid; no
  save references the area id), areas 7->6 (test sites) or 13->12 (canonicals), well-formed, 0 FATAL on re-census.
  `RM_TestSite_calm_v1.before_fw11_rebuild_20261018.rws` also carries it and was left as is (a backup).
- **Other unresolved classes, all non-fatal (SKIPPED unless noted), left alone:** retired donors: `VFEInsectoids.GameComponent_Insectoids`
  (all 11), `AlphaBiomes.Map/WorldComponentExtender` (test sites + 2026-09-12 family), `AlphaGenes.*` x5 and
  `ReGrowthCore.MapComponent_SmartFarming`/`WallSnowManager` (canonical family). Not on the retired list but absent from
  the 535 list: `AlphaBehavioursAndEvents.MapRoomUpdater` (calm, river, canonical 09-12) and
  `AlphaBehavioursAndEvents.ChameleonSkins` x4 (**OTHER**, river_v1 world pawns: those pawns lose that part); our own
  `RimMandrake.FloodedCanyon.*` x3 (test sites; mod inactive) and old-namespace `RimMandrake.*Pyrelands*`/`DryRooms`
  (09-12 family); stale types of still-active mods (`RimTunes.Storage.*` x4, `Fortified.MapComponent_ModificationIndex`,
  `MoreIncidents.Settings.WorldComp`, `VanillaTradingExpanded.TradingManager`, `WallFridgePatch.*`,
  `VanillaQuestsExpandedCryptoforge.*`). The 2026-10-18 DONORFREE pair carries only the AlphaGenes, ReGrowth and
  VFEI2 components. Full table: `D:\Luke\dev\_rmscratch\saves_backup_20261019_areafix\class_census.txt`.
- **Rule:** before calling a retirement save-safe, run `save_class_census.py` on the save as well as the def census.

## Removed defs, not only donor defs (2026-10-19, FOUNDRY)
A test-site save kept `RM_TreeMartyr`, a def of OURS cut the day before (9a8fc0edf): 1528 plants in `RM_TestSite_cauldron_v1_AREAFIX`
gave 1534 'Could not load reference' lines and 100 'Exception spawning loaded thing null'. The donor census only knows the retired-donor
list, so any def WE remove is invisible to it. **Before removing a def, run `src/RimMandrake/Utils/save_def_census.py <saves>` and read
the THING rows** (a THING is an element with `<def>` and `<id>`; they throw at spawn, other refs are dropped with one log line).
- Index: every `<defName>` under the 536 active mod folders (Steam Mods/workshop + Data/<DLC>); `--src` marks defs present only in `src/`.
  `--strip-things OUT` writes a copy without plain thing blocks (not nested, id not referenced elsewhere), byte-level, never in place.
- Measured on the 11 `_AREAFIX` saves (`D:\Luke\dev\_rmscratch\saves_backup_20261019_areafix\areafix2\def_census.txt`): unresolved THINGS
  = cauldron RM_TreeMartyr x1528 + AB_PsychotropicFungus x1; calm VCE_Plant_* x55; the five 2026-09-12 canonical-family saves AB_Mech_Ruined*
  Buildings x91 + RG_Boulder* Mineables x11 + VFEI2_RoyalInsectJelly x1 (the unflagged 09-12 `_AREAFIX` also Scavrat pawns x3 and
  world-pawn li entries WompRat/WarWyrm/Lothcat/Mynock/Kreetle); the two 2026-10-18 DONORFREE x11; river world pawns AA_* x43 (ChameleonSkins);
  leaningscrub VFEI2_Swarmling x1; contagion none. Pawns and the items inside containers are LISTED, not removed.
- `_AREAFIX2` copies (things removed, originals and `_AREAFIX` kept) sit beside them: cauldron, calm, and the six canonical. The cauldron copy
  still lists `RM_TreeMartyr` in six `<li>` def-name lists (not things; Scribe drops them with a log line).

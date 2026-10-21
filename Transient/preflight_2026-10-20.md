# Pre-reload preflight, 2026-10-20 (FOUNDRY subagent, offline only)

Scratch evidence: `D:\ClaudeWork\rimmandrake\scratch\preflight\` (plan_all.txt, plan_biomes.txt, validate_today.txt, selftests.txt, review_status.txt).
Nothing was applied. The game was not touched.

## 1. Deploy state (dry runs; whole-tree plan finished with its final "Drift found" line, 139 s)

Not yet deployed (repo newer than `Mods\`), 17 files in 4 mods:

| mod | files | repo commit | needs |
|---|---|---|---|
| StarWarsRaces | 12 head PNGs (Lasat, Mimbanese, Nelvaanian, Ortolan x south/east/north) | 6d77ea123 (head refit, 16:56) | game may be up (textures load at start, so they take effect next load) |
| GreentideRaidAnt | `Defs/FactionDefs/RUT_Faction_GreentideAnt.xml` | d0601bcd5 (01:24) | game may be up; XML takes effect next load |
| FlowWorks | `Assemblies/RimMandrakeFlowWorks.dll` + `.srchash` | 660d437a6 (pit cover deconstruct drops riders, 16:38) | **game DOWN** (DLL) |
| HugeThings | `Assemblies/RM_HugeThings.dll` + `.srchash` | e588023b7 (walls memo, 08:37) | **game DOWN** (DLL) |

Already in sync (deployed): everything else touched today, including UtinniPatches (banned factions, label patches, biome faces), ResearchRetag, the Ortolan `*m.png` masks, and the whole composed `RimMandrake.Biomes` mod (`--compose biomes`: new biome faces, sea-floor hide fix, DivingInteraction, CreatureBehaviors stars).

Unexpected `-` lines (game-only, kept; never `--prune`, never needed):
- UtinniPatches: `Defs/IdeoSymbolDefs_placeholder` (in game, not in repo).
- Biomes compose: `Biomes/TheForge/Textures/StandIn/Things/Plants/AB_TinkleGrass.png` and `AB_TinkleGrass_Leafless.png`.
Neither is a hand edit worth rescuing (no `--pull` made).

Other seats' files: none of the four drifting mods has uncommitted edits in this clone; all four trace to committed work.

WARNING, not ours to fix: `src/RimMandrake/BiomesShell` has UNCOMMITTED work in this clone (`RimMandrake.Biomes.dll` + `.srchash`, `RM_Biomes.csproj`, `RM_BiomesMod.cs`, untracked `RM_WorldLook.cs`). The composed-biomes plan reports it IN SYNC, i.e. that uncommitted DLL is what is in the game folder now. Whoever owns it must commit it (with its `.srchash`) before the next reload or the repo and the game disagree.

### Apply commands, in order (run from `/home/mandrake/rm/foundry`)

Can deploy while the game is up:
```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod StarWarsRaces
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod GreentideRaidAnt
```
Needs the game shut down (DLLs cannot be written while it runs):
```
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod FlowWorks
python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod HugeThings
```
Then re-run the bare plan (redirect to a file; confirm the final `Everything in sync` or only the `-` lines above).

## 2. validate_patch (12 Patches files changed today; `--live` capture 2026-10-20T23-55-49Z, 325 mods; `--defs` Data+Workshop+Mods; `--mods-config` FULL.LATEST)

- 0 errors: BiomeAnimalDanglingRefs_Fix, RM_TheForge_GroundCoverDrawLayer, RSW_Smelter_Alloys (12 advisory warnings), Grithe_LabelPatch, Grutt_LabelPatch, JawaWorld_BiomeMix.
- Errors, all of ONE class: "def does not exist in the LIVE game", each behind a def-existence Conditional (graceful no-op), 306 distinct absent defNames, nearly all retired donors:
  - PawnFlavorPhase2_ThoughtDef (3626), RUT_ResearchRetag (585), StatNorm_CaravanAdventures_BossStatsNeutral (27), CreatureResize_Ashkarr (12; VAEWaste_Pestigator, GR_Paraceramuffalo), BannedFactions (25; all `CASacrilegHunters`, Caravan Adventures is not in the 325 list, so that ban is a no-op by design).
- REAL FINDING: PlantTolerances_Ashkarr (1139 errors): 18 OURS, `RUT_Arpeau, BleedingTooth, Brightbell, CrimsonCap, Dewshrooms, FlakespireFungus, FruitingBodies, GreyLady, MortalMorelPlant, Nogtyl, Nuitae, Pusmelon, RustPuff, Sagecrust, Shinecap, Skulltop, VioletWimple, Wrinklecap`. No def of those names exists in src (retired into `RM_` twins 2026-10-16) and the patch has no `RM_` rows, so those RM_ plants get no refitted temperature band. The generator is `design/Jawa/mods/plant_tolerances.py`. NEXT: regenerate with the RM_ names (not done here: generator and the owner's biome rosters are not mine).
- Defs files changed today (11): parse clean; static validate 0 errors, 28 advisory (icon paths of vanilla xenotype icons, no `--defs` for Defs). The validator reads Patches only, so field correctness of new Defs is UNMEASURED.
- BannedFactions live proof (`banned_factions.py check-dump <capture>`) is still owed after the reload: UNMEASURED until then.

## 3. Code review (127 code files changed today under src/; 18 CLEAN, 109 DIRTY)

Reviewed in full, defects fixed (3d9ef590e), then marked CLEAN: `banned_factions.py` (inventory crashed on a save with no allFactions/worldObjects), `biome_worldfaces.py` (neighbour check crashed on a non-RGB face), `world_physics_audit.py` (start tile taken by row position, now by id), `world/_mountain_plan2_2026-10-20.py`, `world/_mountain_apply2_2026-10-20.py` (it committed the world after failed set calls; now aborts first), `Patch_SeabedLayerCoplanarHide.cs`, `RM_WorldStarsMath.cs`, `RM_WorldStarsPatch.cs`.
Not verifiable offline: the 4-argument reflection call to `GenCelestial.SunPositionUnmodified` in `RM_WorldStarsPatch.cs`. It fails safe (logs `world stars: fixed sun read failed`, uses the start vector). Current Player.log has no such line (literal scan, MEASURE_ALLOW_SCAN=1).
NOT reviewed, still DIRTY (someone else moving or out of scope): `fit_head_canvas.py` is being edited right now by another agent (uncommitted `numpy`/`ImageDraw` imports); the other ~100 dirty files are other seats' tooling and FlowWorks/GSS/art-pipeline code. NEXT: a review sweep per owning seat.

## 4. Selftests (24 files for code changed today)

22 PASS at first run. Two FAILs, both fixed (3d9ef590e) and re-run green:
- `selftest_rmpaths.py`: the rmpaths.py docstring itself named `D:\Luke\dev\_rmscratch`; reworded.
- `selftest_placeholder_detect.py`: its negatives (`AloeVera`, `JadePlant`, `ScorchedStars` under UtinniPatches) were retired/moved on 2026-10-16, so the probe saw 3 sprites not 10 (an instrument gone blind). Repointed to the RM_ScorchedStars dirs.

## 5. Mod lists (parsed with ElementTree)

- Live `ModsConfig.xml` (what the next load reads) = `ModsConfig.FULL.LATEST.xml`: 325 = 325, identical set and order. It is the 324 Wave-4 list plus `rwnodetree.rwplanetatmosphere` (Rings), re-added by e5c10aa8a. Every id resolves to an installed About.xml.
- SHIP 276, DEV 117, TEST 152, AUTHORING 171, PAINT 83 (RULED_2026-10-20): each is an order-preserving subset of FULL (PAINT has its own order, as designed), every id resolves, **Rings is on none of them**. SHIP has no dev tools (rimdefdump, loadtracer, birthhatchdemo are FULL-only). AUTHORING and PAINT carry `oblitus.mylittleplanet`, which FULL does not (tooling mod).
- ResearchRetag `forceLoadAfter` (43 ids): 28 present live; three declared "load before ResearchRetag" mods sit AFTER it in every list: `mandrake.rsw.patches`, `mandrake.rut.patches` (and `mandrake.rm.wreckedmachines` except PAINT). Measured: none of the three defines a ResearchProjectDef that RUT_ResearchRetag.xml targets, so no retag is lost; the About.xml text is just not true of the order. NEXT: owner/BENCH either drops those three from `forceLoadAfter` or moves ResearchRetag after them.

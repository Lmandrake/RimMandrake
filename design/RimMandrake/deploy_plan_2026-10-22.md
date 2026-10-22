# Deploy plan, 2026-10-22 (dry run only, nothing applied)

Measured offline from `/home/mandrake/rm/foundry` while the game was up and BENCH held the bridge.
Raw output (seat scratch, not committed): `/home/mandrake/.seat-tmp/FOUNDRY/dry_all.txt` (whole walk, ended on
`Drift found`), `dry_compose.txt` (`--compose biomes`), `vp_patches.txt` (validate_patch). The live game
runs 14 mods (minimal list); `ModsConfig.FULL.LATEST.xml` has 330 entries, the Wave 4 list 329 `<li>` (the "324" is a
doc figure: count by parse before citing). Every mod below reads "not enabled in ModsConfig" except the 14 live
ones, which is expected.

## Blockers and flags (read first)

1. **DLLs need the game DOWN.** Drifting DLL mods: Biomes composite (about 20 DLLs, below), FlowWorks, Armoury,
   Ninefold, JawaRules, Sarlacc, StructureInjections, StructureInjectionsRUT.
2. **Renames need `--prune`.** The Wave 1 rename (`80e0635c3`) leaves 135 `Biomes/Wasteland/*`, 24
   `Biomes/NightsideIce/*` and 2 `Biomes/TheForge/Textures/StandIn/.../AB_TinkleGrass*.png` files as `-` lines
   (in game, not in repo; they are repo-side removals/renames, not hand-edits, so no `--pull`). In UtinniPatches 12 more
   `-` lines (RUT_Wasteland biome/terrain/items, `NightsideIce_Rename.xml`, `WildAnimals_NightsideIce.xml`,
   `WildAnimals_Wasteland.xml`). Without `--prune` both the old and new biome defs load: duplicate-def storm.
   Apply those two with `--prune` only after confirming each `-` path is a rename leftover (the lists above are all of
   them; none is a path git never tracked).
3. **FlowWorks source is dirty.** `src/RimMandrake/FlowWorks/Source/RM_MapComponent_Excavation.cs` is modified and
   uncommitted by another agent. Before applying the DLL, confirm the committed `.srchash` matches the source that
   built it (`deploy_custom_mods.py` reports it); do not rebuild over their edit.
4. **FlowWorks MayRequire rewrite** (5 guards in 2 files, deployed copy only) is the tool's normal behaviour, not drift.
5. **Another seat's / unrequested mods in the plain walk**: Droidworks (new `Patches/FlowWorks_DroidsDigDeep.xml`,
   `About.xml`; 3 misrouted PNGs HELD), SWBestiary (21 race defs drift, 96 files HELD), Cuisine, Graffiti,
   FungalSoilTrade, TrophyCraft, PawnFlavor, Pyrinth, RustCathedralRoaches, Shokk, ShokkweaveEconomy
   (About + a def + a patch). All XML-only. Nobody has claimed these in this plan; apply only with the owner's word or
   a seat that owns them. GimmeSomeSlack: in sync (160 files held, no drift).
6. **Stale DEPLOY_HOLD lines** (match nothing): `src/DEPLOY_HOLD.txt` 227 `Pyrelands/diag/*`, 451
   `Cauldron/northstar/*`, 452 `LeaningScrub/northstar/*`, 459 `TheForge/Staged/*`, 460 `Contagion/Staged/*`. Harmless; fix
   the paths or delete the lines in a separate commit.
7. **No mod lacks About.xml or packageId** in the walk (none flagged). Held-on-purpose files (not deployed):
   Armoury `Armour_Ratings.xml`, `Warcasket_HazardRetune.xml` (owner SHIP NEITHER); FlowWorks 231 and
   GimmeSomeSlack 160 northstar result JSONs; the composite holds 11 files.

## Validation (validate_patch.py, BOTH `--live` and `--defs`)

Run against the 2026-10-21T21-46-23Z capture (325 mods, 50,702 defNames) and `ModsConfig.FULL.LATEST.xml`; 18 changed
patch files: 11 OK, 7 FAIL, 134 errors. **Every error is "def does not exist in the LIVE game", and the two causes are
both expected**; none is a typo found:

| cause | files | meaning |
|---|---|---|
| `RM_Wastes`, `RM_SleepingIce`, `RM_WastesAshStorm`, `RM_WastesPlasmaStorm` absent | Wastes/RM_AcousticPayload_Wastes, RM_WastesBrine_ScatterRegister, RM_Wastes_MovingDunesBinding; SleepingIce/RM_AcousticPayload_SleepingIce; Scarlands/RM_AerosolScreen_PollutedBiomes | the capture predates the rename; these resolve only after the composite deploys. Re-run after deploy. |
| `AA_*` (AnimaColossus, Wildpod, Wildpawn, MycoidColossus, Agaripawn, Agaripod, Swarmling, AngelMoth) and `Beldon` absent | TheRot/RotSpecies_NamesAndSizes (113), UtinniPatches/BiomeFaunaStatAdjustments_Generated (2) | donor creatures not in the capture's 325-mod set (Alien Worlds is in LATEST). UNMEASURED whether the Wave 4 list carries them: re-run `--live` against a post-deploy capture; the patches are Conditional-guarded so they no-op, not error, at load. |

OK: UtinniPatches AshStorms_Pyrelands, MechClusterBiomes_AmbientDoctrine (2 warnings), WildAnimals_BlueDesert /
CrackedLands / LongShade / TheForge; ShokkweaveEggBlackMarket (1 warning); Droidworks FlowWorks_DroidsDigDeep (1
warning); Wastes RM_Wastes_GroundCoverDrawLayer; Webwork RM_Thrixweave_Resale (1 warning); TheRot
RotSpecies_WoundSharing. Changed Defs files (ShokkweaveHarvestNodes, Cuisine, Graffiti, FungalSoil, TrophyCraft items)
were not validated: run `validate_patch.py <file> --live ... --defs ...` on each before applying them.

## Ordered apply list

Window: `rimflow bridge take --for "deploy window"`, then `./game --why "deploy window" down` (BENCH holds the bridge:
do nothing until BENCH releases). Dry run each line first; refuse any line you did not expect. One command at a time.

**A. XML-only (game may stay up, but the live game reads Mods at load, so do these with the DLLs):**

1. `python3 src/RimMandrake/Utils/deploy_custom_mods.py --apply --mod UtinniPatches --prune`: 15 changed defs/patches,
   12 rename `-` lines pruned. Check: 12 listed `-` paths gone; `RUT_Wasteland.xml` absent, `RUT_Webwork.xml` present;
   re-run dry run: `in sync`.
2. `--apply --mod ShokkweaveEconomy`: About, harvest nodes, egg black market patch. Check: in sync; `validate_patch` on
   the def file first.
3. Only with an owner or seat go-ahead: `--mod Droidworks`, `Cuisine`, `Graffiti`, `FungalSoilTrade`, `TrophyCraft`,
   `PawnFlavor`, `Pyrinth`, `RustCathedralRoaches`, `Shokk`, `SWBestiary`. Check: each dry run reads `in sync`.

**B. DLL mods (game DOWN):**

4. `--apply --compose biomes --prune`: builds `RimMandrake.Biomes` from `Biomes.compose.json`: Wastes and SleepingIce are
   new folders (135 and 24 files), TheRot +2 / Webwork +6 / LeaningScrub +6 added, about 20 DLLs updated, renames pruned.
   Check: dry run `in sync`; `.srchash` of every listed DLL equals the deployed one; `Biomes/Wasteland` and
   `Biomes/NightsideIce` gone; then Load 1 `jawa/running_mods` and re-run the 7 FAIL patch files with `--live` on a fresh
   capture (expect the `RM_Wastes`/`RM_SleepingIce` errors to clear; the `AA_*` ones stay until the Alien Worlds question
   is settled).
5. `--apply --mod FlowWorks`: after blocker 3. Check: assembly sha equals `RimMandrakeFlowWorks.dll.srchash`
   (runbook row 1.0).
6. `--apply --mod Armoury`, then `--mod Ninefold`, then `--mod StructureInjections`, `--mod StructureInjectionsRUT`,
   `--mod JawaRules`, `--mod Sarlacc` (the last four only if the owner wants them; they are not in the handoff list).
   Check per mod: `.srchash` match, dry run `in sync`.
7. GimmeSomeSlack: nothing to apply (in sync). Pyrelands deploys inside the composite (`FireEcologyHook.dll` and 4 more
   files); it has no stand-alone folder in the plain walk.
8. Wave 4 list: `ModsConfig.FULL.WAVE4_324_2026-10-20.xml` goes in only per `rimworld-start-prep` (RimSort
   Refresh/Save, never by hand-copy over a running game), after steps 1 to 6.
9. Last: `python3 src/RimMandrake/Utils/deploy_custom_mods.py` (plain walk, to a file) must end `Everything in sync`
   apart from the held files; then `./game` measures state.

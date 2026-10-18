# Walk pre-check, offline half, 2026-10-18 (BENCH helper)

Method: every def's texPath resolved in `src/` and in the deployed game copy (`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods`, composed biomes under `RimMandrake.Biomes\Biomes\<Mod>`), sha256 compared, alpha/edge/duplicate checks (`file_checks.json`, scripts `scan.py` `contact.py` `build.py` beside this file), contact PNGs read by eye. No bridge, no launch, no ModsConfig change.

Fact that shapes every live check: the live `ModsConfig.xml` (parsed) holds 15 mods and only FOUR of ours: GimmeSomeSlack, FlowWorks, LuminousPigment, RimMandrake.Biomes. SWBestiary, Cuisine and UtinniPatches are NOT active, so the brine tank, Dragonsnake, every provisional creature install and every `RUT_` biome texture cannot render until the list is changed (FOUNDRY/owner, not me).

| subject | state | evidence | fix / note |
|---|---|---|---|
| TAOZIN_BRINE_TANK_BUILD_GRUB_GOES_PALE | OK offline; CAN'T CHECK live | `01_brine_tank_and_grub.png` | Tank + grub (normal / Brined white / Dessicated) textures exist in src and deployed, sha equal; deployed SWBestiary DLL contains `CompTaozinBrining` and the `taozinBrineTankEnabled` setting. Tank is a stand-in barrel, one identical image for south/east/north (owner has since granted real art: cosmetic, pending). SWBestiary + Cuisine inactive in ModsConfig. |
| SPRINKLER_HEADS_BUILD_PUMP_REQUIRED | OK offline | `02_flowworks_sprinkler_weir_river_hose.png` | 4 looks + spray mote resolve, deployed, sha equal, real alpha. COSMETIC for owner: Industrial head is the smallest/darkest (29% x 56% of canvas vs 37-41%). Judged in game only (his ruling). |
| RIVER_WEIR_ART_JUDGE_CODEX_SQUINTS | OK offline | same sheet + `zoom_river_stake_ferry.png` | 4 looks x 4 headings (128x256 / 256x128 correct transposition), stake, silt trap, ferry post, sluice, panning, hose reels all resolve and deployed, sha equal. Edge contact on weirs/stake is intended (joins neighbours). COSMETIC: hose reel apparent size differs by look: Scrapper 46% and Industrial 39% of the 2.8-cell canvas vs Modern 76% and Futuristic 79% (about 1.2 cells vs 2.2 cells wide). |
| VENOMVINE_BUILD_SCRUB_GROWS_TEETH | OK offline | `03_venomvine.png`, `zoom_venomvine_d.png` | 15 defs, every pool folder deployed and sha equal, real alpha, no stray files. Tall forms drawn 1.8-2.4 cells. Note for live: every form's `_d` is a squat/lying shape (Sworn_d is a woven hedge, deliberate) in the same random pool as the tall `a/b/c`, so a 2.4-cell quad will sometimes hold a low shape; judge in game. |
| TITANOSLIME_SLIME_BIOME_1 | OK offline | `04_titanoslime_gelatinous.png` | Stage art (drawSize 4/5/6/7.5/9) south/east/north exist, deployed (GelatinousSlime in composed Biomes), sha equal, real alpha; slime has no face so north reads fine. Gate 7 (stage 1 + stage 5 staging) is live-only. |
| ARTPIPE_FACING_COHERENCE_1 | CAN'T CHECK OFFLINE (partial) | this audit | Its open halves are regen backlog + in-game eyes, not code. This audit found 4 more live instances of the defect (see facing rows). Do not close. |
| INSITU_ART_JUDGE_SAVES_KEPT_WARM | OK offline; saves present | `07_provisional_creature_installs.png` | All 83 provisional installs in `Transient/afk_2026-10-17/art_installs.md` exist in src with the recorded sha and are deployed identical. Walk saves present in Saves: `RM_walk_20261017_{sprinklers,thinwater,weirs,venomvine,creatures}.rws`, `RM_titano_gate2.rws`, `RM_fw_scene_S6_*.rws`. The ledger KEEP marks on them remain provisional per the item note; nothing changed. |
| 11 tree Graphic_Random pools (afbd112603) | OK | `06_trees_pools.png` | All 11 texPaths are folders holding only intended pool files (3/2/3/2/4/2/3/3/3/4/3), deployed, sha equal, no leftover files inside any pool. Deployed copy keeps one stale SIBLING `Things/Plant/RM_Veluthar/RM_Veluthar_a.png` outside the pool folder: harmless, game never reads it. COSMETIC: Zhorrel pool mixes two trunk designs (b vs c/d); Tumbel reads murky. |
| RSW_Dragonsnake A/B/C/D | DEFECT (facing) cosmetic; CAN'T CHECK live | `05_dragonsnake.png`, `zoom_dragonsnake_ABCD_swim.png` | texPaths resolve, deployed, sha equal, S/E/N complete, alpha real; base+3 alternateGraphics wired, dessicated present. DEFECT vs the 2026-09-15 ruling: all four norths are a TOP-DOWN dorsal view (head up, tail down), not a rear view; major-axis spread across S/E/N is 21-22% for A and D (4-7% for B, C). Also `Dragonsnake_Swimming_*` (3 files) are unreferenced by any def (intended: swim art owed). Owner approved the variants on the sheet 2026-10-18, so regen is his call. |
| Biome world textures | OK offline; was NOT DEPLOYED, fixed | `Transient/biome_worldtex_2026-10-18/sheet.png` | 59 defs read from XML: every `texture` resolves in src (opaque 512 RGB, intended) and deployed with sha equal. The 27 `RUT_` textures + repointed `RUT_` BiomeDefs were missing from UtinniPatches: deployed with `deploy_custom_mods.py --mod UtinniPatches --apply` (plan read first: only committed repo content, incl. CrackedLands rename and TreeMartyr cut; mod is not in ModsConfig, so no effect on a running game). Composed `RimMandrake.Biomes` was already in sync. COSMETIC: Pyrelands, Abyss, LeaningScrub nearly flat. UtinniPatches inactive in ModsConfig. |

## Facing findings on the provisional creature installs (cosmetic, owner's call; none changed)
- Whisperbird north shows a FACE (owl head, eyes, beak toward viewer): breaks "north = no face". Its south is new art, east/north older (major-axis spread 54%).
- North is a top-down dorsal view, not a rear view: Varactyl_m, Strill, OpeeSeaKiller, Yobshrimp (and Dragonsnake A-D above).
- Lothcat_f: new north/south are a white zebra-striped cat, the untouched east is an orange spotted cat (different animal across facings).
- TeeMuss: new 512 north/south vs older east, spread 51%. Grank 32%, MastiffPhalone 27%, Narglatch_f 27% (north symmetry 0.36), Varactyl_m 20%, Lothcat_m 18%.
- Correct rear views seen: Lothcat_m, Zakkeg, BanthaW, Grazer_f, GraniteSlug, Narglatch_f.
- No duplicate-facing files, no opaque boxes, no checkerboards in any set checked (182 files in `file_checks.json`).

## Still needs a LIVE look (once the bridge frees; several need the mod list changed first)
1. Sprinklers: 4 looks spraying on a live map (save `RM_walk_20261017_sprinklers.rws`); Industrial head size.
2. Weirs: joined run in each look on a river (`..._weirs.rws`); hose reel look-to-look size (tank, pump, reel side by side).
3. Venomvine: tall forms in islands on a Scrub map (`..._venomvine.rws`); squat `_d` forms in the tall pool; perf.
4. Titanoslime stage 1 and stage 5 (`RM_titano_gate2.rws`), light and scale beside a colonist.
5. Brine tank: needs SWBestiary + Cuisine in the list; grub whitening, real tank art later.
6. Dragonsnake variants incl. swim stand-in and the north view: needs SWBestiary in the list.
7. The 11 tree pools (random pick mix, canopy zoom fade, 5-11 cell sizes beside a colonist).
8. Biome world-map textures: world view (tiling at planet scale); RUT_ ones need UtinniPatches active.
9. The facing-defect creatures above, only if the owner wants them walked.

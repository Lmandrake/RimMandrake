# ABYSS_SHEET_DONOR_PORT_1 — port pass 2026-10-06 (FOUNDRY helper, offline, uncommitted)

One line per row, roster order of the item's table. Each = own def file + PawnKindDef (creatures) + RM_Abyss row
swapped at the same commonality + RUT_Abyss twin row swapped (`MayRequire="mandrake.rm.biomes"`). Donor-only
references (VEF comps, AA_ bodies/leathers/capacities/eggs, AlphaBiomes placeWorkers, donor harvest items) were
replaced by vanilla or dropped; every substitution is named in each file's header and marked PROVISIONAL.

## creatures (src/RimMandrake/Abyss/Defs/ThingDefs_Races/)
- [x] AA_Nightling -> RM_Sesserith (0.2). Quill-throw ability dropped (VEF), owed as ours; egg-laying -> live birth.
- [x] AA_NightRam -> RM_Olumetha (0.09). useMeatFrom -> RM_Aveluthia.
- [x] AA_NightMule -> RM_Aveluthia (0.5). Pack animal; no female/calf art (owner's picks were donor art).
- [x] AA_Murkling -> RM_Lirrith (1.0). Plague bite (FO_PlaguedBite) folded into vanilla ToxicBite 0.9; corpse-decay dropped.
- [x] AA_CrepuscularBeetle -> RM_Moravatha (0.35). No leather (PROVISIONAL); gestation 10 PROVISIONAL; low-rest hediff owed.
- [x] AA_DarkVandal -> RM_Ossumatha (0.15). Boar body; truffle-digging dropped.
- [x] AA_DuskProwler -> RM_Ysvaltha (0.2). Ninetails tail flurry DROPPED (no vanilla tail group); blade/tail attack owed.
- [x] AA_Darkbeast -> RM_Nevarithia (0.005). Dark-on-death + dark bolt dropped; owed on RM_MapComponentDark.

## plants (src/RimMandrake/Abyss/Defs/ThingDefs_Plants/)
- [x] AG_Gamma -> RM_GlowGlobe (0.5). x2: visualSizeRange 0.6~3.0.
- [x] AB_GiantGamma -> RM_GiantGlowGlobe (0.5). Sunlamp overlight 7 kept; donor placeWorker dropped.
- [x] AB_ToxicGamma -> RM_SicklyGlowMushroom (0.6). Faithful parent PollutionTreeBase = WILD ON POLLUTED GROUND ONLY (owner question).
- [x] AG_Septimum -> RM_PaddleVine (0.25). Harvest AG_Ultima -> Cloth (PROVISIONAL).
- [x] AB_GiantSeptimum -> RM_GiantFibreStalk (0.2). x2: visualSizeRange 2.6~5.0.
- [x] AB_GiantStikehr -> RM_TreeMushroom (0.3). x4: visualSizeRange 8~15.2.
- [x] AB_WildRadagast -> RM_GlowberryBush (0.5). Harvest AB_RawRagadast -> RawBerries (PROVISIONAL).

## art awaiting install (all finished in D:\Luke\dev\_artpipe\done unless noted; mod Abyss, rel under Textures/)
| job | install rel |
|---|---|
| abyss_sesserith_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Sesserith/RM_Sesserith_{east,south,north}.png |
| abyss_olumetha_v3 east/south (NORTH FAILED, requeue) | RM_Abyss/Things/Pawn/Animal/RM_Olumetha/RM_Olumetha_*.png |
| abyss_aveluthia_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Aveluthia/RM_Aveluthia_*.png |
| abyss_lirrith_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Lirrith/RM_Lirrith_*.png |
| abyss_moravatha_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Moravatha/RM_Moravatha_*.png |
| abyss_ossumatha_v3 one facing (NORTH+SOUTH FAILED, requeue) | RM_Abyss/Things/Pawn/Animal/RM_Ossumatha/RM_Ossumatha_*.png |
| abyss_ysvaltha_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Ysvaltha/RM_Ysvaltha_*.png |
| abyss_ugrothar_v1 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Nevarithia/RM_Nevarithia_*.png |
| abyss_bulgra_v1 / glowglobe_b_v2 / glowglobe_c_v2 | RM_Abyss/Things/Plant/RM_GlowGlobe/RM_GlowGlobe_{a,b,c}.png |
| abyss_greatbulgra_v1 / giantglowglobe_b_v2 / _c_v2 | RM_Abyss/Things/Plant/RM_GiantGlowGlobe/RM_GiantGlowGlobe_{a,b,c}.png |
| abyss_blightbulgra_v1 | RM_Abyss/Things/Plant/RM_SicklyGlowMushroom.png |
| abyss_paddlevine_v1 | RM_Abyss/Things/Plant/RM_PaddleVine.png |
| abyss_elderskeddra_v1 | RM_Abyss/Things/Plant/RM_GiantFibreStalk.png |
| abyss_morkhul_v1 / treemushroom_c_v2 | RM_Abyss/Things/Plant/RM_TreeMushroom/RM_TreeMushroom_{a,b}.png |
| abyss_vettrig_v1 / glowberrybush_b_v2 / _c_v2 | RM_Abyss/Things/Plant/RM_GlowberryBush/RM_GlowberryBush_{a,b,c}.png |

Until installed every new def renders a placeholder (validate_patch flags exactly these texPaths, nothing else).

## also changed
- RM_Abyss.xml / RUT_Abyss.xml: 15 rows each swapped, comments + RM_Abyss header corrected.
- Patches/Abyss_Rename.xml: 8 superseded donor label blocks deleted (item step 7).
- About/About.xml: description no longer claims 14 donor fauna rows / vrakk-kessik labels.

## validation
- `src/RimMandrake/Abyss/validation.py`: all 12 static checks PASS.
- validate_patch.py on the 15 new def files + both BiomeDefs (installed Data + workshop + Mods): both BiomeDefs clean;
  the only findings are the 15 missing-texture paths above (7 ERROR plant texPaths, 24 WARN pawn texPaths).
- Abyss_Rename.xml: 4 xpath-0 errors on the REMAINING (untouched) blocks against the live 10-mod list; pre-existing.

## left on the item
- AB_GlowingGrass port (glowinggrass_{a,b,c}_tint_v1), art installs above, 3 failed facings requeue,
  #3 Krizzak B–F / Summing B installs, #4 C# "durrgak"/"Skarnixes"/"Drokattaks" strings + rebuild.
- Owed mechanics named in headers (quill throw, dark-on-death, low rest, tail/blade attack, festering disease).
- Outside Abyss: RimUtinni/Doctrine/Patches/MegafaunaYield.xml still tunes the donor defs (yield for the ports is lost);
  RUT_CrackedLands still casts AA_Murkling (now labelled "murkling" again: its rename block died with the port).

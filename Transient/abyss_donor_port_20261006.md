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
| abyss_olumetha_v3 east/north (SOUTH FAILED, requeue) | RM_Abyss/Things/Pawn/Animal/RM_Olumetha/RM_Olumetha_*.png |
| abyss_aveluthia_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Aveluthia/RM_Aveluthia_*.png |
| abyss_lirrith_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Lirrith/RM_Lirrith_*.png |
| abyss_moravatha_v3 east/south/north | RM_Abyss/Things/Pawn/Animal/RM_Moravatha/RM_Moravatha_*.png |
| abyss_ossumatha_v3 east (NORTH+SOUTH FAILED, requeue) | RM_Abyss/Things/Pawn/Animal/RM_Ossumatha/RM_Ossumatha_*.png |
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

## follow-up pass 2026-10-06 (FOUNDRY helper, offline, uncommitted)
- (a) ART INSTALLED via artledger.install(reason=artpipe-collect), RIMFLOW_SEAT=FOUNDRY: 37 PNGs (the table above, minus the
  failed facings, plus RM_GlowingGrass_{a,c}). Each checked first: in done/, alpha, transparent corners, coverage 0.17-0.50,
  zero magenta; contact sheet looked at. `art.py guard worktree`: 0 unledgered. The 37 ledger events were already committed
  by another window at 308a1c269; the PNGs under src/RimMandrake/Abyss/Textures/ are still UNTRACKED; commit them with the defs.
- Correction: olumetha's failed facing is SOUTH, not north. All three failures (olumetha south, ossumatha north+south) are
  failed_canon ("charcoal, not pitch black") after the daemon's own retry, so they were not installed. Requeued as NEW jobs via
  fill_queue.py, derived from the accepted v3 east: abyss_ossumatha_v4_{north,south}, abyss_olumetha_v4_south (rows in
  Transient/biome_ffar/abyss_v4_requeue_jobs_2026-10-06.json). Until they land, Graphic_Multi falls back: olumetha south
  uses north; ossumatha north/south use east, drawn at a -90 degree offset (Graphic_Multi.Init), so they read wrong.
- (b) RUT_CrackedLands + RM_FloodedCanyon (WildAnimals_CrackedLands.xml) still cast the donor AA_Murkling, so its
  "kessik" label/description block is restored verbatim in Abyss_Rename.xml; header updated. RM_Lirrith stays Abyss-only.
- (c) The generated files (MegafaunaYield.xml, AnimalTolerances_Ashkarr.xml, PlantTolerances_Ashkarr.xml) say do-not-hand-edit and
  their generators read the def dump, which has no ports yet, so I added hand-written COMPANION patches that carry the donors'
  values onto the ports, PROVISIONAL (delete each once its generator emits the ports):
  Doctrine/Patches/MegafaunaYield_OwnedPorts.xml (6 ports' Meat/Bone, aveluthia milk 16);
  UtinniPatches/Patches/AnimalTolerances_OwnedPorts.xml (5 comfy bands, e.g. moravatha -10 -> -35.7: temperature is a spawn gate);
  UtinniPatches/Patches/PlantTolerances_OwnedPorts.xml (6 plants' four growth temps). NOT carried: glow globe and paddle vine,
  whose donor refits target a hot biome (26.9..70.8), and lirrith's band, which is the Cracked Lands fit. BoneAmount in an RM_
  def would hard-depend on the bones mod (StatModifier has no MayRequire, read in RimSage), which is why this lives in campaign patches.
  An offline apply simulation over the Abyss defs confirms that every op lands.
  Not touched: RM_ExplosiveGrowthRoster.xml still lists AB_GiantStikehr (a roster, not tuning; should RM_TreeMushroom join it?).
- (d) RM_GlowingGrass ported (donor label/description kept, since no rename was asked; Graphic_Random). RM_Abyss and RUT_Abyss rows
  swapped at 1.0, so no donor row is left in RM_Abyss. b's tint failed the sprite validator (footprint +3.9%) and is requeued as
  abyss_glowinggrass_b_tint_v2. About.xml + RM_Abyss header updated.
- Checks: Abyss validation.py static 12/12 PASS. validate_patch: the port texPath warnings are gone. Remaining: 4 pre-existing
  Abyss_Rename xpath errors (Ops 4/6/8/10, not the restored block) and companion-patch "0 nodes" findings. Those are because the
  live ModsConfig does not load the undeployed RM_ defs; the simulation above covers them.
- Left: install the 3 v4 facings + grass b when they land; #3 Krizzak B-F / Summing B; #4 C# strings (skipped); owed mechanics.

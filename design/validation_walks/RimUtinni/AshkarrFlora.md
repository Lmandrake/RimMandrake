# AshkarrFlora — validation walk
subject: src/RimUtinni/AshkarrFlora  (packageId `mandrake.rut.ashkarrflora`)
deps: none (modDependencies is Ludeon.RimWorld only); loadAfter also names three soft/optional mods this mod defends against: ChaoticEnrico.BetterTrees, Qux.Comigo.BetterTreesMod, Maal.BetterTreesMod
list: minimal
status-hint: TREE_GRAPHICS_OWNERSHIP_1 — ships `RUT_SweetlineTree`, a brand-new huge/ancient desert tree ThingDef with its own generated art and its own `plant.visualSizeRange`, structurally immune to the three subscribed BetterTrees mods' defName-keyed rescaling; carries a defensive (currently no-op) patch as insurance against a future collision.

## must be true
- ThingDef `RUT_SweetlineTree` loads with ParentName=TreeBase (not DeciduousTreeBase — this is a fixed-sun world with no season cycle).
- `plant.visualSizeRange` = 7.7~10.0 (a canopy 7.7-10 tiles wide at full growth, raised from an earlier 5.0~6.5 cap per the owner's "ten cells wide" ruling — "huge, ancient" per the owner's ruling, well above vanilla's biggest common tree).
- SWEETLINE_WOOL_HARVEST_1 (2026-09-21): harvest is non-destructive — `plant.harvestedThingDef`=RUT_SweetlineWool, `plant.harvestYield`=20, `plant.harvestAfterGrowth`=0.05 (makes `HarvestDestroys` false), `plant.harvestTag`="Standard", `plant.forceIsTree`=true. Was TreeBase's inherited destructive wood harvest (harvestYield 160, harvestedThingDef WoodLog).
- `statBases.Flammability` = 0.1 (down from TreeBase's 0.8 — arid_shrubland.md's hard "no flammable living flora" rule, not a balance judgment).
- `plant.mustBeWildToSow` stays true (inherited from TreeBase, undeclared here) — the tree can never be planted by a colonist.
- The BetterTrees immunity patch (`Patches/BetterTrees_SweetlineTree_Immunity.xml`) matches nothing today by design — RUT_SweetlineTree is absent from every BetterTrees template — so it is expected to log nothing, on the minimal list (donor mods absent) and equally on a list where the donor mods are active.
- 🔴 **Currently FALSE, blocking**: the ThingDef's `texPath` (`Things/Plant/RUT_SweetlineTree`) points at a texture folder that exists but is EMPTY on disk — no PNG has been placed there despite the About.xml's description claiming "its own generated art". Candidate art sits unmoved in `src/RimUtinni/AshkarrFlora/_artsrc/sweetline_orphans_2026-09-06/` (11 PNGs, a CONTACT_SHEET.png and a README.md, no recorded selection). This mod cannot ship a visible tree until that gap is closed.

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rut.ashkarrflora" and no XML error naming RUT_AshkarrFlora_Plants.xml or BetterTrees_SweetlineTree_Immunity.xml
2. [D] repo check: `Textures/Things/Plant/RUT_SweetlineTree/` contains >=1 `.png` file — CURRENTLY FAILS (0 files; see the blocking bullet above)
3. [D] def read-back: ThingDef RUT_SweetlineTree exists; ParentName=TreeBase, plant.visualSizeRange="7.7~10.0", statBases.Flammability=0.1
4. [B] jawa/get_def {defType: "ThingDef", defName: "RUT_SweetlineTree"} → expect resolved statBases.MaxHitPoints=650, statBases.Mass=900, statBases.Flammability=0.1 (post-inheritance from TreeBase)
5. [B] jawa/get_def {defType: "ThingDef", defName: "RUT_SweetlineTree"} → expect resolved plant.mustBeWildToSow=true, plant.growDays=240, plant.harvestedThingDef=RUT_SweetlineWool, plant.harvestYield=20, plant.harvestAfterGrowth=0.05, plant.wildOrder=4
6. [L] on the minimal list (BetterTrees mods absent), Player.log contains no reference to "TreeScaleTemplateDef", "TreeTextureTemplateDef" or "RUT_SweetlineTree" from BetterTrees — confirms the conditional patch is a true no-op when the donor mods aren't even loaded
X. [S] (human pass) once art lands: confirm the sweetline tree renders as a huge ancient canopy in-world at the authored scale, and that no BetterTrees console line ever mentions it with the donor mods active — separate MOD_HUMAN_EXPLORATION_PASS_1 item.

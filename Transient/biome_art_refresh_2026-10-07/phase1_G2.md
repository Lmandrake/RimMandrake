## leaningscrub_sheet_2026-10-05
Leads: 30 keep_not_live rows (9 defs: 1 donor-plant pair, Venomvine, Bantha/FrilledGorg/Gorg/LongtailGorg variants, Scurrier, Vurra) + 24 redo_done + 4 redo_failed. Close note says its install script covered only rows whose graphic has an existing Textures path, so every `_byname` pick and every `variants` column was skipped.

### A. UNEXECUTED-MECHANICAL

**A1. RSW_Vurra _byname B (render gapall_RSW_Vurra_v1)** - ruling c66dc2358dc84c12bc9c. Main A is the donor in-game (mlie.horrors Terrorworm, `art.py status RM_Vurra`: "variants donor 6", no owned art), so lead "A" is a false positive; B is the finished render (artpipe `done/gapall_RSW_Vurra_v1_{east,north,south}`, art `_artsrc` present). Def `RM_Vurra` (renamed from RSW_ by 818c513d9) still wears the donor placeholder.
```
art_i() { python3 src/RimMandrake/Utils/art/art.py install src/RimStarWars/SWBestiary "$@"; }
art_i Things/Pawn/Animal/RM_Vurra/RM_Vurra_east.png d69453ddae76999c2f877c00d99c94065faf4e6f9c8419a37919268c083c5aa7 --ruling c66dc2358dc84c12bc9c
art_i Things/Pawn/Animal/RM_Vurra/RM_Vurra_north.png 60dcb8daee30a33b1621618a9269f9cf167d4bf282bffb444671fe3b203daa7c --ruling c66dc2358dc84c12bc9c
art_i Things/Pawn/Animal/RM_Vurra/RM_Vurra_south.png e95dc4defd553f749b8532d7bbb6ff31ca5c30d8328316ab8dbda1ca539b22bf --ruling c66dc2358dc84c12bc9c
```
Wiring: in `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Races.xml` lines 127, 134, 141 (the RM_Vurra PawnKindDef lifeStages) change `Things/Pawn/Animal/Terrorworm/TerrorWorm` to `Things/Pawn/Animal/RM_Vurra/RM_Vurra`, and drop the "TEMP PLACEHOLDER" comments above them. Then `placeholder_detect.py` over the three PNGs. (Caveat: his main click was the prefill A; the B pick is the only deliberate click on the row.)

**A2. RM_VenomvineThicket _byname C (render RM_VenomvineThicket_v2)** - ruling 74428c23b952f388f426, note "variations". He also "kept" main B (ls_regen_RM_Venomvine_v1, 02098c35dc6a) but purged that same sha, so C is the only surviving pick. Not on disk anywhere under src. The Thicket and its sibling venomvines share one Graphic_Random folder (`Things/Plant/RM_Venomvine`, live only `_a` = 9e0e6c1d33b1), so adding `_b` is additive and needs no XML change:
```
python3 src/RimMandrake/Utils/art/art.py install src/RimMandrake/EnvironmentalHazards Things/Plant/RM_Venomvine/RM_Venomvine_b.png 29ae79060e162f6fc7259a748839739ae3472935fbd61ae52058afa4ab11ff96 --ruling 74428c23b952f388f426
```
(The shared folder means the other seven venomvine defs gain the variant too; the 2 variation jobs `leaningscrub_venomvinethicket_b/c_v1` were filed separately.)

**A3. Plant_Brambles B and RG_Plant_CreepStern B (renders gapbs_Plant_Brambles_v1 / gapbs_RG_Plant_CreepStern_v1)** - rulings 05910019c49584570f84 and f8ce83ddbbb5f69cd3d4, note "more variations" (jobs `leaningscrub_brambles_{b,c}_v1`, `creepstern_{b,c}_v1` queued). The A column is ReGrowth's own donor art (no loose file), so there is nothing to overwrite; the owned ports are `RSW_Thornscrub` (Brambles) and `RSW_TanniVine` (CreepStern) in `src/RimStarWars/SWBestiary/Defs/DesertPort/RSW_DesertPortMisc_Plants.xml`, both Graphic_Random on the placeholder `Things/Plants/AB_Aaklac`:
```
art_p() { python3 src/RimMandrake/Utils/art/art.py install src/RimStarWars/SWBestiary "$@"; }
art_p Things/Plant/RSW_Thornscrub/RSW_Thornscrub/RSW_Thornscrub_a.png 58af11776394ddbf2c6cce91451b258d0e5a7276bf5408fb79c0496aae25fb95 --ruling 05910019c49584570f84
art_p Things/Plant/RSW_TanniVine/RSW_TanniVine/RSW_TanniVine_a.png 563867645a1991b811e2a6569eaace7445db125477552b95093aba59645ca0b0 --ruling f8ce83ddbbb5f69cd3d4
```
Wiring: change `<texPath>Things/Plants/AB_Aaklac</texPath>` to `Things/Plant/RSW_Thornscrub/RSW_Thornscrub` in the RSW_Thornscrub block (about line 244) and to `Things/Plant/RSW_TanniVine/RSW_TanniVine` in the RSW_TanniVine block (line ~119); delete the two TEMP PLACEHOLDER comments. Caveat: the biome roster `src/RimUtinni/UtinniPatches/Defs/BiomeDefs/RUT_AridShrubland.xml` lines 203/208 still spawns the donor defs `Plant_Brambles` / `RG_Plant_CreepStern`, so this changes in-game art only once those rows are repointed to the ports (owner/FOUNDRY call; not part of the art ruling).

**A4. Creature variant columns kept via `variants` (17 columns, 51 PNGs)** - Bantha E-H (render longshade_rsw_bantha_v1..v4), FrilledGorg C,D,F, Gorg C,D,F,G, LongtailGorg C,D,F,G,H,I. All are finished renders with 3 facings, all have keep rulings (ids in the commands), none are on disk. Precedent: Twilight Sea close installed Nuudal variant C as `RM_NuudalC_*` + `alternateGraphics` (`RM_TwilightSeaFloorLife.xml:242`). Naming below is `<Sp>Var<Col>`; "failed canon check" renders are included because he kept them explicitly (labels on the sheet). The live columns (Gorg B, FrilledGorg B, LongtailGorg E) and east-only/swim columns are excluded (see B/C below).
```
art_i() { python3 src/RimMandrake/Utils/art/art.py install src/RimStarWars/SWBestiary "$@"; }
# RSW_Bantha variant E  render longshade_rsw_bantha_v1 — failed canon check  facings=east,north,south
art_i swanimals/Bantha/BanthaVarE_east.png 4350080aa8a79f46d23e29677b4d0e2d1b6f44b6947883960d5184aec4422ae9 --ruling 5f89cbbb7b6a987349ec
art_i swanimals/Bantha/BanthaVarE_north.png 6af441e81822dbee1f0708cc151a41204f760bf10573e2833d03b923a29cd16c --ruling 5f89cbbb7b6a987349ec
art_i swanimals/Bantha/BanthaVarE_south.png 95075596f9498905c714cf75c4752cdaf087486ca6653487afef43e98c244535 --ruling 5f89cbbb7b6a987349ec
# RSW_Bantha variant F  render longshade_rsw_bantha_v2  facings=east,north,south
art_i swanimals/Bantha/BanthaVarF_east.png 6077aeca1b132c3e840ad80090a059dcc30077e23d2450307319a73e6077c099 --ruling c5b323129e82c0749228
art_i swanimals/Bantha/BanthaVarF_north.png ec8e236e1cb82eef53ee73525631c84e4f258669ac6a05604e1dba5e4a65e663 --ruling c5b323129e82c0749228
art_i swanimals/Bantha/BanthaVarF_south.png 89c7de46f54d40f7562ca57549d66ac4a6022fb0a63a891b633f3e570fc24849 --ruling c5b323129e82c0749228
# RSW_Bantha variant G  render longshade_rsw_bantha_v3 — failed canon check  facings=east,north,south
art_i swanimals/Bantha/BanthaVarG_east.png a8a17698510e12145500936345c837c640c5765f4c583328fced65b6bb371e76 --ruling 2eef4c36df306c4365eb
art_i swanimals/Bantha/BanthaVarG_north.png f5ba9dbde7881347453a192a7fe822410e1ae0c27b02f94dc72d9e9268a2272d --ruling 2eef4c36df306c4365eb
art_i swanimals/Bantha/BanthaVarG_south.png ccb4302f09e86541c2ddd2e64d3aaf4de685cfc8fe820e0c3d42706141c3997a --ruling 2eef4c36df306c4365eb
# RSW_Bantha variant H  render longshade_rsw_bantha_v4 — failed canon check  facings=east,north,south
art_i swanimals/Bantha/BanthaVarH_east.png eb68da09a6e6e4408e9d44f1b6354527f7ac015a4f052e475da83c17238465da --ruling e860cf0d9c8a5844cf49
art_i swanimals/Bantha/BanthaVarH_north.png 2b86e472d073a580434e2976cc6448faa0657604ade31116d9d843fda75bed1f --ruling e860cf0d9c8a5844cf49
art_i swanimals/Bantha/BanthaVarH_south.png 9701636912ce4d4a3cd449a7ca29e4c35567a0d3ad1f0e0ea844b111eedc59b1 --ruling e860cf0d9c8a5844cf49
# RSW_FrilledGorg variant C  render longshade_rsw_frilledgorg_v3  facings=east,north,south
art_i swanimals/FrilledGorg/FrilledGorgVarC_east.png 02243eb8e1dfaafb706fe72eda0971ca07786946697803f5ce63e269fc7ca435 --ruling 8bfe8c40d61c8971b5f5
art_i swanimals/FrilledGorg/FrilledGorgVarC_north.png 520b9529573a86fae16ae22e880bea0aee3423be3aa45d1ad1d3257478ed7b4e --ruling 8bfe8c40d61c8971b5f5
art_i swanimals/FrilledGorg/FrilledGorgVarC_south.png c56f2a1c9ccce5cda1acb87efd772cf424696da40a1e565bbacb3ce01a23c67a --ruling 8bfe8c40d61c8971b5f5
# RSW_FrilledGorg variant D  render longshade_rsw_frilledgorg_v6 — failed canon check  facings=east,north,south
art_i swanimals/FrilledGorg/FrilledGorgVarD_east.png 71552ef6c03bec3dfb61fb10bd2e9fe87ac74ef2c0f8d38b8a92d3f6cd3287ec --ruling 3ed3bca8d47d2a4e9e87
art_i swanimals/FrilledGorg/FrilledGorgVarD_north.png d636eff2bdbc00feb04893601a3ca70a03aefeeb978e6634c1ae8be9516abd4f --ruling 3ed3bca8d47d2a4e9e87
art_i swanimals/FrilledGorg/FrilledGorgVarD_south.png 83de19e5b2f24752d9ae91bddbdcac23009f2f41120d6f65c73a8e61685e0b05 --ruling 3ed3bca8d47d2a4e9e87
# RSW_FrilledGorg variant F  render longshade_rsw_frilledgorg_v4 — failed canon check  facings=east,north,south
art_i swanimals/FrilledGorg/FrilledGorgVarF_east.png b538f7d50010a7a90b5c6681c134b023c5fecb1e4b380420df11125038e8f990 --ruling 8a6a3e3588b7815ba973
art_i swanimals/FrilledGorg/FrilledGorgVarF_north.png 54fece3dc9a8d919ea56be4b7f1f78717f0f68c2aced3992a71961dc12f9deb9 --ruling 8a6a3e3588b7815ba973
art_i swanimals/FrilledGorg/FrilledGorgVarF_south.png 90c40f0be650f52940e3b7431f4ef60ddffc3afc5982682437763d77a7e1e69f --ruling 8a6a3e3588b7815ba973
# RSW_Gorg variant C  render longshade_rsw_gorg_v3  facings=east,north,south
art_i swanimals/Gorg/GorgVarC_east.png 0553a966f94e40888ea582c79175c8b7487ef4f3d28390a3eb997507677e2141 --ruling c15962efebd8ae0f9fb7
art_i swanimals/Gorg/GorgVarC_north.png ff6bfde3ce59ed30e408f8aa46e9de6a3c4776196cfd06d2c3f41c296d023d7f --ruling c15962efebd8ae0f9fb7
art_i swanimals/Gorg/GorgVarC_south.png a8a77ac6e04042083b6083651bdd5605847fda23a02c92ad9ceff893a13ed894 --ruling c15962efebd8ae0f9fb7
# RSW_Gorg variant D  render longshade_rsw_gorg_v6 — failed canon check  facings=east,north,south
art_i swanimals/Gorg/GorgVarD_east.png 499434c89c03f58d1e505f6c0a874702c6a1a493b4539cd35ae4116981550e91 --ruling 8eca9107972e0e79a504
art_i swanimals/Gorg/GorgVarD_north.png 46816f531940eb563b42cfaaef050f29a4d46f507cf68e9bd37e1c0217edc843 --ruling 8eca9107972e0e79a504
art_i swanimals/Gorg/GorgVarD_south.png e2e78cde43d2fa8046e3f03aa0649677560a35611e2af8f029c2d1b4dc8ad470 --ruling 8eca9107972e0e79a504
# RSW_Gorg variant F  render longshade_rsw_gorg_v2 — failed canon check  facings=east,north,south
art_i swanimals/Gorg/GorgVarF_east.png e1ec5d438f72bcfbb0876b2afa7aa693a278535fa5c31701a19ad3457b60dadd --ruling 255a1deb70ef80c789f3
art_i swanimals/Gorg/GorgVarF_north.png f81090ac86b87ec86bf5347e070ad770d99f991a9c7114a79a60c34d89789a9b --ruling 255a1deb70ef80c789f3
art_i swanimals/Gorg/GorgVarF_south.png deb5fdde6d0a24d33e53c747c909d2f44ecfd92b0dc63de3018188ae3ec7400a --ruling 255a1deb70ef80c789f3
# RSW_Gorg variant G  render longshade_rsw_gorg_v4 — failed canon check  facings=east,north,south
art_i swanimals/Gorg/GorgVarG_east.png db6ad9689f8e4f5f2ad6774b31e17f20935c42e9ec25237b85d052f186fa472c --ruling 7ea825a598622d472bd5
art_i swanimals/Gorg/GorgVarG_north.png cfd0064b8d598a8fd496b73215276f118777ba690466da8e598ccca18db07510 --ruling 7ea825a598622d472bd5
art_i swanimals/Gorg/GorgVarG_south.png 22a37ffa0f37a6f45692da9a081e9a4288c7c35b101d5cc71540fa6f04fbdf11 --ruling 7ea825a598622d472bd5
# RSW_LongtailGorg variant C  render longshade_rsw_longtailgorg_v1  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarC_east.png c37397bd2d5c309f089bcf804ae601e1ebe928d4a81ac0f5d078d220530ea316 --ruling 89ca9ef7efbe32328d98
art_i swanimals/LongtailGorg/LongtailGorgVarC_north.png b690aebb5166461428d3a7c55f9c4a9c7f6f94c5c38dc0831297ced1fee53293 --ruling 89ca9ef7efbe32328d98
art_i swanimals/LongtailGorg/LongtailGorgVarC_south.png 2cb6096cfef81812aa7e6577ef19d9a26ea9b1989d6d5691ce028335084d1a90 --ruling 89ca9ef7efbe32328d98
# RSW_LongtailGorg variant D  render longshade_rsw_longtailgorg_v2  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarD_east.png a689db478c1ba40f409cee7dcefc6628cab17e74d5c4e7ba21af51fadcf1d0e8 --ruling 09e66d80ff20d76d0ab8
art_i swanimals/LongtailGorg/LongtailGorgVarD_north.png 3a6a1a8efc91cc92cd5d859ebd8964389dab865480892bd3eb69752dee3f1e54 --ruling 09e66d80ff20d76d0ab8
art_i swanimals/LongtailGorg/LongtailGorgVarD_south.png f01ec92b6ca1b2a978d48291864a11495292fcecaab22eaf34f28bafb64573fc --ruling 09e66d80ff20d76d0ab8
# RSW_LongtailGorg variant F  render longshade_rsw_longtailgorg_v4 — failed canon check  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarF_east.png 7d765b4e5cfaa4a9007b48837cdbb2e50a44c0eef0ee99b25030d60fe315f0d8 --ruling 8addcdcaacf5a0b3246a
art_i swanimals/LongtailGorg/LongtailGorgVarF_north.png 593713551df225dce4717d36b62e7f9e5e546dff77ebc9b1a6f6b4870cb954a1 --ruling 8addcdcaacf5a0b3246a
art_i swanimals/LongtailGorg/LongtailGorgVarF_south.png 404320615879e39af5c214a8c239560304f00d06d6a1f27d9b11828e36aad516 --ruling 8addcdcaacf5a0b3246a
# RSW_LongtailGorg variant G  render longshade_rsw_longtailgorg_v5  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarG_east.png beee62668832199955fa0076dcc80ea162634c9a3ccf474676d38120fcfc55bf --ruling cc5c8d39086a21e08963
art_i swanimals/LongtailGorg/LongtailGorgVarG_north.png a29455b5b8182d689e2fce25c2323ff856d1d4b6d9ab0c29e00b0897af8c6262 --ruling cc5c8d39086a21e08963
art_i swanimals/LongtailGorg/LongtailGorgVarG_south.png 47e54403e4871a7028969fe2aadf3bb708f331fe08722c75319d66c15eea9ac9 --ruling cc5c8d39086a21e08963
# RSW_LongtailGorg variant H  render longshade_rsw_longtailgorg_v6  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarH_east.png ab4d592ab2bbdbe695218e768d7248359f25dcbd655236862b6f35441c383f32 --ruling eecd05f84ee04e148c7c
art_i swanimals/LongtailGorg/LongtailGorgVarH_north.png e010dcef817cbc7c40330cd78aad32e7d385e68f647123426083d6c91fb127fa --ruling eecd05f84ee04e148c7c
art_i swanimals/LongtailGorg/LongtailGorgVarH_south.png 0feb85d378cbbf31c69501f185e2b42c9e89ff66a178e76ae053410421ac22de --ruling eecd05f84ee04e148c7c
# RSW_LongtailGorg variant I  render desert_swaca_longtailgorg  facings=east,north,south
art_i swanimals/LongtailGorg/LongtailGorgVarI_east.png d99538682a448084a448ea2f8bd8c2522e770053ee6a6d9a22cae032fdc93967 --ruling eef7050392698d402545
art_i swanimals/LongtailGorg/LongtailGorgVarI_north.png b1af40525b8033f45c21405495c25c26225ee8163d58e1d2f141231290450a21 --ruling eef7050392698d402545
art_i swanimals/LongtailGorg/LongtailGorgVarI_south.png 57f4519230ba07c20fe89d91c9acc286d7a3d9932f6449efcc19bb2faf4b4153 --ruling eef7050392698d402545
```
Wiring: in each `src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_<Sp>.xml` PawnKindDef `<alternateGraphics>` (Bantha line 163, FrilledGorg 179, Gorg 173, LongtailGorg 197) add `<li><texPath>swanimals/<Sp>/<Sp>Var<Col></texPath></li>` per installed column (existing entries also carry `<swimmingTexPath>`; the new variants have no swimming art, so omit it and confirm the engine falls back rather than drawing magenta before deploy - one live look needed). Then `placeholder_detect.py` and `sea_shadows.py` are not needed (land animals).

### B. Redo rows whose jobs only partly finished (lead said "done")
`redo_done` only checked that some job file was newer than the decision. Facing check against artpipe `done/` vs `failed/`:
- RSW_Anooba: east, north done; **south failed** (canon check).
- RSW_Kreetle: east, south done; **north failed**.
- RSW_Massiff: east done; **north, south failed**.
- RSW_Qormot: east done; **north, south failed**.
- The other 20 redo_done rows (RM_Fuzzrunner, Fuzzviper, Zellik, 3 grasses + WildHealroot plant a, RSW_Bantha, Cannok, Chikka, Convor, Corinathoth, FeralNerf, Igitz, KowakianMonkeyLizard, Kybuck, Pikobis, Porg, Urusai, Voorpak): EXECUTED, all facings in `done/`.
The 4 partial rows are NEEDS-OWNER (not regen): the failed facings are real PNGs in `_artsrc/leaningscrub_<x>_v1_<facing>/` flagged `worker_status: failed_canon` (e.g. massiff north "canon check FAIL 3/4 after one corrected retry"); the choice is show-with-failed-label vs requeue the facing as a `derive_from` job. Do not mark these rows closed.

### C. redo_failed (4) - none has a later successful render
- RSW_Grank (all 3 facings failed_canon 5/6), RSW_Lothcat (3 facings failed), RSW_Whisperbird (3 facings failed), RSW_Plant_Nysyllin_Wild (a,b,c failed): NEEDS-OWNER. Finished-but-canon-failed PNGs exist in `_artsrc/leaningscrub_*`; the older `done/` renders (grank_v1, desertportb_grank, desert_swaca_lothcat, whisperbird_v1/canon_whisperbird_v1, nysyllin_v1_r2) all predate his redo and are the ones he rejected. So this is not a PROPOSED-REGEN (art exists); the decision is show-failed-render vs requeue with a stronger brief.

### D. Other leads
- RSW_Scurrier _byname C (render stillsand_regen_RSW_Scurrier_v2): NEEDS-OWNER. Rulings 4476946991300d5b9b83 (A, Scurrier_f live), b3dfb56175a80ce1f1d3 (B, Scurrier_m live) and ae1acf10b4c0c42d386b (C, _byname) all keep, so he kept both live donor sets and a new render; there is no slot for C. Ask: replace f/m with C, or add as an alternate? (If alternate: same recipe as A4.) 
- RSW_Gorg variant E (`longshade_rsw_gorg_swim_v1`) and RSW_LongtailGorg variant B (`longshade_rsw_longtailgorg_swim_v1`): NEEDS-OWNER - swimming-pose renders kept as main-body variants; install would put a swim sprite on land animals. Probably belongs in the `*_Swimming` alternate set.
- RSW_FrilledGorg variants E, G and RSW_Gorg variant H: PROPOSED-REGEN (north/south only): the render exists for east only (1/3 facings, `longshade_rsw_frilledgorg_v2/v5`, `gorg_v5`); art exists so no new subject regen, but north+south must be derived (`derive_from` job) before install. The sheet snapshot carries only an east sha for these columns.
- Live columns flagged by the lead (Gorg variant B, FrilledGorg variant B, LongtailGorg variant E): EXECUTED (== the in-game art, installed by the close).
- RSW_Bantha _byname E is the same render as Bantha variant E (covered in A4; ruling 5f89cbbb7b6a987349ec). RSW_Bantha main redo: EXECUTED (`done/leaningscrub_bantha_v1_*`).

## lanterndeeps_sheet_2026-10-05
Leads: 1 (redo_done).
- RM_Blinker redo ("three arms radiating out, legless, clumsy"): EXECUTED. artpipe `done/deeps_blinker_v2_{east,north,south}` all present, none in `failed/`. Live art is still the old B (b5cff32443b7 etc.); the v2 render awaits review/install by item LANTERNDEEPS_SHEET_ART_REDO_1 (FOUNDRY) — a redo produces a candidate, not a replacement.

## gelatinousslime_sheet_2026-10-05
Leads: 2 (keep_not_live).
- RM_Plant_Bellows (A main, pick _byname B): EXECUTED. Decision A is donor prefill; his real act was the `_byname` B pick plus purging the donor sha. B sha 4c2f39c6562d is on disk at `src/RimMandrake/GelatinousSlime/Textures/Things/Plant/RM_Bellows/RM_Bellows/RM_Bellows_a.png` and `SlimeFlora.xml:71` texPath = `Things/Plant/RM_Bellows/RM_Bellows`. The close note ("defs left on donor paths") is stale. Lead is a false positive (it checked the donor column A).
- RM_Plant_Readerbloom: EXECUTED. Same: B sha e0d843944abc at `.../RM_Readerbloom/RM_Readerbloom/RM_Readerbloom_a.png`, `SlimeFlora.xml:151` texPath matches.

## contagion_sheet_2026-10-04
Leads: 2 rows (RM_ContagionIkee main + _byname, one decision).
- RM_ContagionIkee: NEEDS-OWNER. Decision B (2026-10-06 05:20, after the 10-05 close) = `stillsand_regen_RSW_Ikee_v2`, a fresh render, but his typed note says "Not again! Where's the ikee art I had before? I liked it!" (prefill was A = the rejected 09-29 render). Live art is column C (0a52fabd2e89 / f124c52df712 / a336837e6bad, PROTECTED), the restored liked render installed 10-05 per `contagion_close_progress_2026-10-05.md` section "Ikee". Installing B would replace the art his note says he wants; leaving it ignores his click. Ask which; if "B", command would be `art.py install` of B shas from artpipe `done/stillsand_regen_RSW_Ikee_v2_*` under Textures/Things/Pawn/Animal/RM_ContagionIkee/ with the 2026-10-06 keep ruling id (see `art.py variants RM_ContagionIkee`).

## nightsideice_sheet_2026-10-05
Leads: 4 (1 keep_not_live, 3 redo_done).
- Tauntaun juvenile keep C (`swanimals/Tauntaun/Tauntaun_j`): EXECUTED/no-op. It is the donor graphic from `mlie.starwarsanimalcollection` (`art.py status`: "slots: (none in our defs)"); the picked shas dd44f62b3b53/7c6c193a9b5f/f600c0a4770b are donor bundle PNGs, so there is nothing to install and they will never be under src. False positive.
- Tauntaun redo ("Follow the canon art CLOSELY"): EXECUTED. artpipe `done/nightsideice_tauntaun_v1_{east,north,south}` all present (and `failed/` has none). Renders await review (column D on the sheet), not auto-installed by design.
- AA_ShockGoat redo: EXECUTED. `done/nightsideice_shockgoat_v1_{east,north,south}` present.
- RSW_CaveLemming redo: EXECUTED. `done/nightsideice_cavelemming_v1_{east,north,south}` present; description fix was also done (close note B4).
Also confirmed by the close note: RSW_Wampa B installed and C = already-live Wampa_j (these were keep_live).

## Summary

| sheet | leads | executed | unexecuted-mechanical | needs-owner | proposed-regen |
|---|---|---|---|---|---|
| leaningscrub_sheet_2026-10-05 | 58 (30 keep_not_live + 24 redo_done + 4 redo_failed) | 21 | 23 | 11 | 3 |
| lanterndeeps_sheet_2026-10-05 | 1 | 1 | 0 | 0 | 0 |
| gelatinousslime_sheet_2026-10-05 | 2 | 2 | 0 | 0 | 0 |
| contagion_sheet_2026-10-04 | 2 | 0 | 0 | 2 | 0 |
| nightsideice_sheet_2026-10-05 | 4 | 4 | 0 | 0 | 0 |
| total | 67 | 28 | 23 | 13 | 3 |

Notes: the 3 "proposed-regen" are north/south derive jobs for east-only variant renders (art exists, not a new regen). Leaning Scrub needs-owner = Scurrier C, Gorg E, LongtailGorg B, 4 partial-facing redos (Anooba, Kreetle, Massiff, Qormot), 4 canon-failed redos (Grank, Lothcat, Whisperbird, Nysyllin). Nothing was installed, queued or changed by this pass; the install commands were not dry-run.

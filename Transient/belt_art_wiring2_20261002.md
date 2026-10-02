# Belt art wiring pass 2 2026-10-02

Skeleton. Part 1 = queue-log jobs finished; Part 2 = 9 swap-skipped creatures.

## Part 1

| def | source job | dest | validator |
|---|---|---|---|
| RUT_DyingCreep | rut_dyingcreep_v1 | src/RimUtinni/UtinniPatches/Textures/Things/Plant/RUT_DyingCreep/RUT_DyingCreep_a.png | PASS 256 (Graphic_Single, folder form as batch 1) |
| RUT_DeadCreep | rut_deadcreep_v1 | src/RimUtinni/UtinniPatches/Textures/Things/Filth/RUT_DeadCreep/RUT_DeadCreep_a.png | PASS 256 (Graphic_Cluster folder) |
| RUT_MetalSaltBezoar | rut_metalsaltbezoar_v1 | src/RimUtinni/UtinniPatches/Textures/Things/Item/Resource/RUT_MetalSaltBezoar/RUT_MetalSaltBezoar_a.png | PASS 256 (StackCount) |
| RSW_SurraGrass | rsw_surragrass_v1 | src/RimStarWars/SWBestiary/Textures/Things/Plant/RSW_SurraGrass/RSW_SurraGrass_a.png | PASS 256 |
| RSW_DommoTree | rsw_dommotree_v1 | src/RimStarWars/SWBestiary/Textures/Things/Plant/RSW_DommoTree/RSW_DommoTree_a.png | PASS 256 |
| RM_ColdWax | rm_coldwax_v1 | src/RimMandrake/BlueDesert/Textures/Things/Item/Resource/RM_ColdWax/RM_ColdWax.png | PASS 256 |
| RM_DeltaSalt | rm_deltasalt_v1 | src/RimMandrake/Miasma/Textures/Things/Item/Resource/RM_DeltaSalt/RM_DeltaSalt.png | PASS 256 |
| RM_DeltaSilt | rm_deltasilt_v1 | src/RimMandrake/Miasma/Textures/Things/Item/Resource/RM_DeltaSilt/RM_DeltaSilt.png | PASS 256 |
| RM_CinderCrust | rm_cindercrust_v1 | src/RimMandrake/TheForge/Textures/Things/Plant/RM_CinderCrust/RM_CinderCrust_a.png | PASS 256 |
| RM_FineSand | rm_finesand_v1 | src/RimMandrake/Stillsand/Textures/Things/Item/Resource/RM_FineSand.png | PASS 256 |
| RUT_Filth_MouseTrack | rut_filth_mousetrack_v1 | src/RimMandrake/TheSump/Textures/Things/Filth/RUT_MouseTrack/RUT_MouseTrack_a.png | PASS 256 (Graphic_Cluster inherited from BaseFilth; faint by design) |
| RM_Graffiti_Glyph_Bloodfeeding | glyph_bloodfeeding_v2 | src/RimMandrake/Graffiti/Textures/Things/Filth/Art/RM_Graffiti_Glyph_Bloodfeeding/bloodfeeding_0.png | PASS 640 (matches sibling glyph canvas and naming) |
| RUT_DryAirBlower | rut_dryairblower_v1 | src/RimUtinni/UtinniPatches/Textures/Things/Building/Production/RUT_DryAirBlower.png | PASS 256 |
| RM_OasisMaker | rm_oasismaker_v1 | src/RimMandrake/OasisMaker/Textures/OasisMaker/RM_OasisMaker.png (new Textures dir; texPath OasisMaker/RM_OasisMaker is this mod's own, predecessor mis-skipped it as donor-root) | PASS 512 |
| RUT_BeastBulge | rut_beastbulge_v1 | src/RimMandrake/TheSump/Textures/Things/Building/Natural/RUT_BeastBulge/RUT_BeastBulge_a.png | PASS 512 |
| RUT_MoatFusePost | rut_moatfusepost_v1 | src/RimMandrake/TheSump/Textures/Things/Building/Production/RUT_MoatFusePost.png | PASS 256 |
| RSW_Zhakka | rsw_zhakka_v1_south/east/north | src/RimStarWars/SWBestiary/Textures/Things/Pawn/Animal/RSW_Zhakka/RSW_Zhakka_{south,east,north}.png | PASS 256, check_sprite parity ok (graphicClass assumed Multi, def omits it) |

Looked at every image on a contact sheet; all match their prompts. Existing-art check: none of the texPaths had any PNG in src before; no file overwritten.

### Part 1 not wired
| def / job | reason |
|---|---|
| RUT_SweetlineWool + RM_SweetlineWool (rut_sweetlinewool_v1) | job FAILED in artpipe (failed/) |
| RM_Greatbole hardwood item (rm_greatbolehardwood_v1) | job FAILED |
| RUT_VentSmelter/VentForge/VentKiln (all 3 facings each) | all 9 jobs FAILED (registry verdict fail) |
| RUT_LivingBolt (east/south/north) | all FAILED |
| AB_Agarilux tolluk cap (rot_agarilux_v3) | OWNER'S EYES: validates (256, clean alpha) and is a more detailed painterly mushroom, but the interim Agarilux_A.png is a different, cartoonier style the owner kept, and the texPath folder is Graphic_Random-style (a second file would add a variant, not replace). Not copied. Side by side: Transient/belt_art_agarilux_v3_compare.png |

## Part 2

Finding: the RSW_ ports whose art exists are tier-twinned: finished art and in-src PNGs exist for the RM_ twins (RM_Khorrak LongShade, RM_Vozzik + RM_Ikee Stillsand; same species, same description for Khorrak/Ikee). Predecessor precedent (AA_SandProwler -> RM_Vosska, MayRequire longshade) swaps the RM_ biome file's donor row to the RM_ twin, which also satisfies Q11 (no RSW_ name in an RM_ file). No new PNGs were needed for these three; the RSW_ twins' own texPaths (RSW_Khorrak/Vozzik/Ikee) remain unwired (job RM_*_east belongs to the other tier twin, per pass 1 rule).

### Swaps (like-for-like, validate_patch OK 0 errors/0 warnings on both files; ET.parse OK)
| file | old | new | commonality | MayRequire |
|---|---|---|---|---|
| src/RimMandrake/NightsideIce/Defs/BiomeDefs/RM_NightsideIce.xml (RM_NightsideIce wildAnimals) | AA_Terramorph | RM_Khorrak | 0.003 | mandrake.rm.longshade |
| src/RimMandrake/NightsideIce/Defs/BiomeDefs/RM_NightsideIce.xml | AA_TetraSlug | RM_Vozzik | 0.002 | mandrake.rm.stillsand |
| src/RimMandrake/WeepingStones/Defs/BiomeDefs/RM_WeepingStones_Biome.xml (RM_WeepingStones) | AA_Eyeling | RM_Ikee | 0.1 | mandrake.rm.stillsand |
Art: RM_Khorrak/RM_Vozzik/RM_Ikee each have _south/_east/_north PNGs already in src (LongShade / Stillsand Textures/Things/Pawn/Animal/<Name>/).
Not swapped: the RUT_ campaign biome files still carry the donor rows (RUT_NightsideIce etc.), untouched; the trailing comments on the swapped lines still read the donor's note.

### The other 6 of the 9
| creature | port | result |
|---|---|---|
| Cactipine | RSW_Chikka | SKIPPED: no finished art for any spelling (artpipe find chikka/cactipine: 0); texPath is donor-root AA_Cactipine; Alpha Animals creature (owner, 2026-10-02); the RSW_ port prefix is a misnomer, re-home to RM_ per Q12 first |
| Needlepost | RSW_Skorra | SKIPPED: no finished art, donor-root texPath AA_NeedlePost (Alpha Animals creature per owner; RSW_ port prefix is a misnomer, re-home to RM_ per Q12 first) |
| Terrorworm | RSW_Vurra | SKIPPED: no finished art, donor-root texPath Terrorworm/TerrorWorm (Alpha Animals creature per owner; RSW_ port prefix is a misnomer, re-home to RM_ per Q12 first) |
| Wildpawn | RSW_Durrok | SKIPPED: finished art rot_wildpawn_v2_* exists but is already wired in src/RimMandrake/TheRot/Textures/RotSpecies/Wildpawn for the DONOR AA_Wildpawn def (patched to 'durrok'); RSW_Durrok's texPath is the donor path AA_Wildpawn/AA_Wildpawn, so wiring it would mean shadowing a donor path or repointing the def (Alpha Animals creature per owner; RSW_ port prefix is a misnomer, re-home to RM_ per Q12 first) |
| Wildpod | RSW_Mullgoth | SKIPPED: same, rot_wildpod_v2 already in TheRot/RotSpecies/Wildpod and src/RimUtinni/WildpodArtOverride supplies AA_Wildpod_* at the donor path; no RM_ twin (Alpha Animals creature per owner; RSW_ port prefix is a misnomer, re-home to RM_ per Q12 first) |
| Nysyllin | RSW_Plant_Nysyllin_Wild | SKIPPED: art exists (nysyllin_v1, nysyllin_v1_r2, desertportb_plant_nysyllin_wild = multiple versions, no single unambiguous) and texPath is donor-root swplants/Nysillin; Nysyllin is a canon Star Wars plant (owner, 2026-10-02), so the RSW_ name is right and Q11 applies: canon names route through the Utinni/RSW layer, not an RM_ file |

## Skipped / owner eyes (see Part 2 tail)
- AB_Agarilux tolluk cap v3: see Part 1; comparison PNG Transient/belt_art_agarilux_v3_compare.png (left current interim, right v3).
- Failed artpipe jobs (not requeued, forbidden): sweetline wool, greatbole hardwood, vent smelter/forge/kiln (9), livingbolt (3).
- Wildpawn and Wildpod are Alpha Animals creatures (owner, 2026-10-02), not Star Wars; the RSW_Durrok/RSW_Mullgoth port names are mis-tiered. Nysyllin is canon Star Wars (owner) and correctly RSW_. Cactipine, Needlepost and Terrorworm are also Alpha Animals (owner), so RSW_Chikka, RSW_Skorra and RSW_Vurra are mis-tiered too. Open: re-home them to RM_ names (Q12) and settle art ownership between the TheRot patch and the port.

## Skipped / owner eyes (see Part 2 tail)

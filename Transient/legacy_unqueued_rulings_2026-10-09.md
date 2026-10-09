# Legacy decisions rows ruled replace/redo with no artpipe job filed — 2026-10-09

Measured, not queued (owner request via BENCH, Cauldron follow-through). Script: one-off sweep over every `*.decisions.json` in the clone that has NO `snapshot` key (the pre-ledger sheet format), rows whose decision normalises to `redo` or `replace`/`replace-donor` and carry his stamp (`at` / file `approvedAt`/`savedBy`). A row counts as QUEUED when any artpipe job (pending/active/done/failed/_withdrawn, 5,726 jobs) names the subject by `target_def`/`target_original` or by job id, created on/after the ruling; the registry's queued events are checked too. Duplicate copies of one ruling (Transient/ vs infrastructure/state/art_rulings/) are counted once.

Sanity probes: Neebray reads QUEUED only by today's enact jobs (first job 2026-10-09, ruling 2026-09-20); `hawkbat` 42 and `stoneback` 3 job ids found, so the job index can see.

## Why Neebray waited 19 days

1. `Transient/port_swac_2026-09-20.decisions.json` is a legacy-format file: no `snapshot` key, so `art.py ingest`/`art.py enact` REFUSE it (`snapshot … missing — cannot resolve columns to pictures`). Nothing ever turned its rows into ledger rulings or jobs.
2. Its verdict is `replace` (owner blanket ruling "Yes replace everything."), which `artledger.normalise_verdict` maps to `replace-donor`, not `redo`; even a snapshot-bound sheet only queues literal `redo` rows. The ruling was executed as DONOR_DEFS_PORT_TO_OURS_1 (def ported to RSW_Neebray) with the donor's art carried along, so the def work closed and the art half had no owner.
3. Neebray was only queued today because the Cauldron sheet carried a fresh `redo` on RSW_Neebray (`enact_cabe4675_neebray_v1`).

## Count

**229 ruled rows** (unique subject+verdict+time) across 15 legacy files have no job filed after the ruling (201 have no job for that subject at all). Of 453 legacy replace/redo rows, 224 were queued at some point after the ruling. Verdicts among the unqueued: replace 149, regen 49, redo 12, resize 10, improve 4, redraw 3, revise 1, rerender 1.

Caveats: a subject renamed since (a port to a new invented name) is matched only if the job names the old def or contains the old key, so some rows here may have been redrawn under the new name — check before queuing. A `replace` on a donor port may have been satisfied by OUR earlier art for that subject; `jobs_any` > 0 flags subjects that do have pre-ruling jobs.

## Rows

### `Transient/port_tail_2026-09-20.decisions.json` (67)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| AB_AgaricusDomeCap | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Agarilux | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_AgariluxPrime | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_AlienGrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_AlienTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_AlienTree_Polluted | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_ArbuscularMycorrhiza | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_BloodBouquet | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Bryolux | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_CrystalFlower | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_CrystalHorn | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_DribblingCap | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_EyeGrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_FrostLeaf | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GargantuanLithops | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GiantAgariTox | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GiantAgarilux | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GlobularPlant | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GlowingAgarilux | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Glowstool | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Gomphoeria | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_GreenRockFern | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_HalfAlienTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Iashiphus | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_JungleTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_KeeningCordax | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_LargeSlimyTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_LilacBeacon | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_MangrovePalm | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_MangroveTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_ParasiticMangrove | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RavenNettle | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RecurvedStropharia | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RedBugloss | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RedLeaves | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RedPlantsTall | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_RimeNodules | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_Slimecasia | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_SlimyFern | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_SlimyPholiota | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_SlimyTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_SugarFamewort | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_TallSlimyGrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_TangleTea | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_TarPuddle | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_TentacularPlant | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AB_WitchesOyster | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Dewshrooms | replace | 2026-09-20 | 2 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_ScorchedStars | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_SewerReed | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_Snaketails | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_TreeMartyr | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_TreeTanglerootMangrove | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_TreeTwistingThornwood | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_TwistingThorngrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Plant_TwistingThornweed | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_RainbowTongue | replace | 2026-09-20 | 1 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| BMT_Sagecrust | replace | 2026-09-20 | 2 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GR_Chickenrabbit | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GR_Manbear | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GR_Molebear | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GR_ParagonRat | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GR_Spidercat | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| GRimMoss | replace | 2026-09-20 | 1 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Ling_Cockroach | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| RG_Plant_TropicalChokevine | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| RG_Rimclaw | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |

### `Transient/rot_flora_fauna_review_2026-09-18.decisions.json` (46)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| A_AB_AgaricusDomeCap | regen | 2026-09-19 | 0 | 7 wide, rename |
| A_AB_Agarilux | regen | 2026-09-19 | 0 | rename |
| A_AB_AgariluxPrime | regen | 2026-09-19 | 0 | 20 wide, rename |
| A_AB_ArbuscularMycorrhiza | regen | 2026-09-19 | 0 | 9 wide, rename |
| A_AB_Bryolux | regen | 2026-09-19 | 0 | rename |
| A_AB_DribblingCap | regen | 2026-09-19 | 0 | 12 wide, rename |
| A_AB_GiantAgarilux | regen | 2026-09-19 | 0 | wrong size, 6 wide, rename |
| A_AB_GlowingAgarilux | regen | 2026-09-19 | 0 | wrong size, 4 wide, rename |
| A_AB_Glowstool | regen | 2026-09-19 | 0 | rename |
| A_AB_LilacBeacon | regen | 2026-09-19 | 0 | 3 wide, rename |
| A_AB_RecurvedStropharia | regen | 2026-09-19 | 0 | 5 wide, rename |
| A_AB_SlimyPholiota | regen | 2026-09-19 | 0 | 5 wide, , rename |
| A_AB_WitchesOyster | regen | 2026-09-19 | 0 | 6 wide, rename |
| A_RUT_AgelessCap | regen | 2026-09-19 | 0 | , rename |
| A_RUT_Arpeau | regen | 2026-09-19 | 0 | 10 wide, , rename |
| A_RUT_BlastpodShroom | regen | 2026-09-19 | 0 | keep general appearance, just improve, rename |
| A_RUT_BleedingTooth | regen | 2026-09-19 | 0 | 2 wlde, , rename |
| A_RUT_Brightbell | regen | 2026-09-19 | 0 | 1.5 wide, rename |
| A_RUT_CrimsonCap | regen | 2026-09-19 | 0 | 2 cells, rename |
| A_RUT_Dewshrooms | regen | 2026-09-19 | 0 | , rename |
| A_RUT_DulcisPlant | regen | 2026-09-19 | 0 | 3 cells, rename |
| A_RUT_EuphoricCrown | regen | 2026-09-19 | 0 | , rename |
| A_RUT_FalseFruit | regen | 2026-09-19 | 0 | , rename |
| A_RUT_FlakespireFungus | regen | 2026-09-19 | 0 | 3 wide, , rename |
| A_RUT_FruitingBodies | regen | 2026-09-19 | 0 | , rename |
| A_RUT_FurnaceCap | regen | 2026-09-19 | 0 | 2 cells, rename |
| A_RUT_GreyLady | regen | 2026-09-19 | 0 | , rename |
| A_RUT_MortalMorelPlant | regen | 2026-09-19 | 0 | 0.8, rename |
| A_RUT_Nogtyl | regen | 2026-09-19 | 0 | 12 wide, rename |
| A_RUT_Nuitae | regen | 2026-09-19 | 0 | 1 wide, rename |
| A_RUT_PaleMoss | regen | 2026-09-19 | 0 | make look really like moss, rename |
| A_RUT_PaleTree | regen | 2026-09-19 | 0 | 6 wide, rename |
| A_RUT_Pusmelon | regen | 2026-09-19 | 0 | 1 wide, rename |
| A_RUT_RegenerantVeil | regen | 2026-09-19 | 0 | , rename |
| A_RUT_RustPuff | regen | 2026-09-19 | 0 |  |
| A_RUT_Sagecrust | regen | 2026-09-19 | 0 | , rename |
| A_RUT_Shinecap | regen | 2026-09-19 | 0 | 4 wide, rename |
| A_RUT_Skulltop | regen | 2026-09-19 | 0 | , rename |
| A_RUT_VioletWimple | regen | 2026-09-19 | 0 | 2 cells, rename |
| A_RUT_Wrinklecap | regen | 2026-09-19 | 0 | .9 wide, rename |
| B_AA_Agaripawn | regen | 2026-09-19 | 0 | 7 wide, rename |
| B_AA_MycoidColossus | regen | 2026-09-19 | 0 | 15 wide, , rename |
| B_AA_Swarmling | regen | 2026-09-19 | 0 | 0.5 wide, rename |
| B_AA_Wildpawn | regen | 2026-09-19 | 0 | 6 wide, , rename |
| B_AA_Wildpod | regen | 2026-09-19 | 0 | 5 wide, rename |
| B_RSW_FungalWeevil | regen | 2026-09-19 | 0 | disgusting fungus bug hybrid, rename, 4 cells wide |

### `Transient/desert_family_review_2026-09-20.decisions.json` (42)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| A_AA_BoulderMit | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Cactipine | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_DesertAve | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Eyeling | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Gigantelope | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_MammothWorm | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Needlepost | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Needleroll | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_SandProwler | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_SandSquid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Terramorph | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_TetraSlug | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Wildpawn | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_AA_Wildpod | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_DUMDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_DestroyerDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_FX7Droid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_GNKDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_MSEDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_MuckrakerDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_OuterRim_SalvageAssistDroid | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_RSW_ImperialToad | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_RSW_Jellypot | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_RSW_MossBeetle | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| A_VFEI2_Fuelmite | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_AB_Aaklac | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_AB_DessertTree | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_AB_GiantStikehr | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_AB_HardyGrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Bloddle | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Brambles | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Bush | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Chakroot_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_HealrootWild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_HubbaGourd_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Nysyllin_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_Ripthorn | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_Plant_ShrubLow | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_RG_Plant_AridGrass | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_RG_Plant_CreepStern | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_RG_Plant_CrimsonCushion | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |
| P_RG_Plant_Dervish | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: keep the creature, replace with our o |

### `Transient/port_alphaanimals_2026-09-20.decisions.json` (24)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| AA_AcanthamoebaGiganteaLarge | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_AcanthamoebaGiganteaSmall | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Agaripawn | replace | 2026-09-20 | 3 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Agaripod | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_BloodShrimp | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Bumbledrone | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_BumbledroneHierophant | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Drainer | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_DrainerLarva | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_FissionMouse | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_FrostboundBehemoth | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Frostling | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Frostmite | replace | 2026-09-20 | 3 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_GreenGoo | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Mime | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_MycoidColossus | replace | 2026-09-20 | 5 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_NightAve | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_RaptorShrimp | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_RedGoo | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_RedSpore | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_RoughPlatedMonitor | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_SummitCrab | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_TarGuzzler | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| AA_Thermadon | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |

### `Transient/port_swac_2026-09-20.decisions.json` (13)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| Borcatu | replace | 2026-09-20 | 6 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| CanCell | replace | 2026-09-20 | 3 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Dactillion | replace | 2026-09-20 | 3 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Dianoga | replace | 2026-09-20 | 3 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Fanback | replace | 2026-09-20 | 6 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Gornt | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| LavaFlea | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Ollopom | replace | 2026-09-20 | 4 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Plant_Bubblespore_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Plant_FelucianGlowspore_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Plant_MujaFruit_Wild | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Woolamander | replace | 2026-09-20 | 0 | Owner blanket ruling 2026-09-20: replace applied to every row. |
| Wyyyschokk | replace | 2026-09-20 | 4 | Owner blanket ruling 2026-09-20: replace applied to every row. |

### `Transient/desert_art_review_2026-10-03.decisions.json` (12)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| A_AA_Cactipine | redo | 2026-10-04 | 0 | The needles should be very long, more like a porcupine |
| A_AA_DesertAve | redo | 2026-10-04 | 0 | Tint bird more golden, and North face is wrong creature? |
| A_AA_Gigantelope | redo | 2026-10-04 | 0 | Unify beast faces |
| A_AA_Needlepost | redo | 2026-10-04 | 0 | This is absurd. It is not a four legged beast at all, but supposedly a |
| A_AA_Needleroll | redo | 2026-10-04 | 0 | This is incoherent. Please make it look like a large tumbleweed with o |
| A_AA_SandSquid | redo | 2026-10-04 | 0 | No, it should look like a huge squid, not have elephant-like legs at a |
| A_AA_TetraSlug | redo | 2026-10-04 | 0 | Each face looks like a different creature. |
| A_Gizka | redo | 2026-10-04 | 14 | We had a good Gizka.... it didn't need to be redone, and it isn't a fr |
| A_Mudhorn | redo | 2026-10-04 | 3 | This is very good except that it needs to have shaggy hide. |
| A_Scavrat | redo | 2026-10-04 | 3 | more alien |
| P_AB_GiantStikehr | redo | 2026-10-04 | 0 |  |
| P_Plant_HealrootWild | redo | 2026-10-04 | 0 | This needs to be instantly recognizable on the map in appearance and c |

### `Transient/rot_size_rejudge_2026-09-19.decisions.json` (10)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| AB_AgaricusDomeCap | resize | 2026-09-19 | 0 | 2 |
| AB_ArbuscularMycorrhiza | resize | 2026-09-19 | 0 | 8 |
| AB_DribblingCap | resize | 2026-09-19 | 0 | 9 |
| AB_GiantAgarilux | resize | 2026-09-19 | 0 | 6 still, but make sure to keep the sparkling luminous violet spots |
| AB_WitchesOyster | resize | 2026-09-19 | 0 | 3 |
| RUT_BleedingTooth | resize | 2026-09-19 | 2 | 1.5 |
| RUT_CrimsonCap | resize | 2026-09-19 | 2 | .9 |
| RUT_FlakespireFungus | resize | 2026-09-19 | 2 | 2 |
| RUT_Shinecap | resize | 2026-09-19 | 2 | 3 |
| RUT_VioletWimple | resize | 2026-09-19 | 2 | 1 |

### `Transient/deeps_flora_fauna_review_2026-09-18.decisions.json` (3)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| RSW_BovineBeetle | regen | 2026-09-19 | 0 | Horrible, total remake. This should be huge, bodysize 4. A small room- |
| RSW_GlowSlug | regen | 2026-09-19 | 0 | Make it the glowing pale blue with yellow internal liquids of hydrocar |
| RSW_ShatterjawBeetle | regen | 2026-09-19 | 0 | A shiny black beetle, strangely conventional and out of place in this  |

### `Transient/donor_code_creatures_sheet_2026-10-09.decisions.json` (3)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| AA_CrescendoAnole | replace | 2026-10-09 | 6 |  |
| AA_LuciferBug | replace | 2026-10-09 | 6 |  |
| VFEI2_BlackSwarmling | replace | None | 3 |  |

### `infrastructure/state/art_rulings/2026-09-12_art_review_2026-09-12__decisions.decisions.json` (3)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| aa_frostmite_v1_east | redraw | 2026-09-12 | 0 | The
  Frostmite is interesting and I like most of its body and alien
  |
| aa_frostmite_v1_north | redraw | 2026-09-12 | 0 | The
  Frostmite is interesting and I like most of its body and alien
  |
| aa_frostmite_v1_south | redraw | 2026-09-12 | 0 | The
  Frostmite is interesting and I like most of its body and alien
  |

### `Transient/contagion_cast_art_review/sheet.decisions.json` (2)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| coalescence_stage2 | improve | 2026-09-29 | 0 | keep more of the gelatinous goop with eyes and random limbs, less of t |
| coalescence_stage3 | improve | 2026-09-29 | 0 | keep more of the gelatinous goop with eyes and random limbs, less of t |

### `Transient/art_review_2026-09-06.decisions.json` (1)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| Capybara | revise | None | 0 |  |

### `Transient/bedazzle_art_sheets_2026-09-28/cracked_lands/sheet.decisions.json` (1)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| RM_Veqma | improve | 2026-09-29 | 1 | You should not be able to see the taproot if this is supposed to be th |

### `Transient/bedazzle_art_sheets_2026-09-28/wasteland/sheet.decisions.json` (1)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| RM_Middenbeetle | improve | 2026-09-29 | 3 | This beast is capable of stealing. Needs a new name to deconflict Midd |

### `infrastructure/state/art_rulings/2026-09-15_pyrelands_art_review__pyrelands_art_decisions.decisions.json` (1)

| row | verdict | ruled | jobs before ruling | note |
|---|---|---|---|---|
| mantistanis | rerender | 2026-09-16 | 11 | Coloration varies between Eastn and N/S |


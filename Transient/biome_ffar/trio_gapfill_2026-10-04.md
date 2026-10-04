# Trio gap-fill 2026-10-04 (BIOME_FLORAFAUNA_ART_REVIEW_1)

Result: NO jobs queued. Zero genuine gaps in scope. Jobs json: none (nothing queued; the prior helper's 21 `desert_gap_*` jobs are untouched).

Scope (owner change): only RM_ BiomeDefs. Census placements show desert rows (3) and deep_desert rows (2) sit ONLY on RUT_Desert / RUT_ExtremeDesert, so they are out of scope; their RM_ twins have art (artpipe done/RM_GreatDevourer, RM_Groundrunner, RM_MatureFleshbeast, RM_Drazzik, all 3 facings). RSW_SandLion has no RM_ placement. Nothing queued for them. The re-scoped census (RM_LongShade / RM_Stillsand keys) had not landed on origin when I stopped; re-check those two biomes from it.

| biome | defName | RM_ placement | verdict | source |
|---|---|---|---|---|
| desert | RSW_GreatDevourer / Groundrunner / MatureFleshbeast | none (RUT_Desert only) | OUT OF SCOPE; RM_ twins HAD ART (artpipe done/) | artpipe find |
| deep_desert | RSW_Drazzik / RSW_SandLion | none (RUT_ExtremeDesert only) | OUT OF SCOPE; RM_Drazzik HAD ART | artpipe find |
| blue_desert | RM_Dorrak | inline | HAD ART: artpipe done/bluedesert_dorrak_{east,north,south,dessicated} (census saw only vanilla Thrumbo texPath) | artpipe find |
| blue_desert | RM_Krissek | inline | HAD ART: done/bluedesert_krissek_* | artpipe find |
| blue_desert | RM_Vekkit | inline | HAD ART: done/bluedesert_vekkit_* | artpipe find |
| blue_desert | RM_Chimeglobe | inline | HAD ART: done/bluedesert_chimeglobe, _b | artpipe find |
| blue_desert | RM_Glassfern | inline | HAD ART: done/bluedesert_glassfern, _b, _c | artpipe find |
| blue_desert | RM_Palefloss | inline | HAD ART: done/bluedesert_palefloss, _b, _c | artpipe find |
| blue_desert | AA_Thunderbeast | inline on RM_BlueDesert | DONOR ART EXISTS, not a generation gap: Alpha Animals (workshop 1541721856) defines it, texPath `Things/Pawn/Animal/AA_Thunderbeast/AA_Thunderbeast`. Census "no texPath resolved" is an instrument limit. Owner ruled `replace` 2026-09-20 (port_alphaanimals decisions) - replacement is a separate item, not queued here. | def read |
| blue_desert | Vapaad | patch-added (WildAnimals_BlueDesert.xml) | DONOR ART EXISTS: SW Animal Collection (workshop 3497316713) texPath `swanimals/Vapaad/Vapaad` (+Dessicated). Canon Legends "Vaapad", no canon_references entry. Not queued; if the owner wants our own, that is a new job. | def read |
| blue_desert | AB_CrystalHorn, AB_ToxiGrass, PoisonPlantTallGrass | RUT_BlueDesert only | OUT OF SCOPE (cast doc turn-2 ruling 1 takes them off anyway) | bedazzle_cast 2026-09-28 |

Action owed to the census builder (not mine to edit): the six RM_ blue-desert rows were mis-flagged because the ledger join keyed on the vanilla texPath and ignored the bluedesert_* artpipe renders; Thunderbeast/Vapaad need donor-texture resolution.

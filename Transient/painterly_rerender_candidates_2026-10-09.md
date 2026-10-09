# Painterly re-render candidates 2026-10-09 (read-only; nothing installed or filed)

Verifies the 28 census rows marked "painterly re-render exists" (`Transient/cartoonish_era_art_census_2026-10-09.md`). Contact image: `D:\Luke\dev\RimMandrake\Transient\painterly_swap_candidates_2026-10-09.png` (seat clone: `/home/mandrake/rm/bench/Transient/painterly_swap_candidates_2026-10-09.png`).

## Method
Live sha from the art ledger `live` index (mod, rel); candidate shas from artpipe variant events by job id; binding via `subject.py` (`bound` = ledger variant of the subject's texPath or a `binding` event for the subject; the candidate sha also live under a same-subject RM-tier texPath counts as a twin). Job dates from `_artpipe/done/<job>.json`. Every pair LOOKED at side by side. Name-match alone was not accepted. Corrections to the census: `pyre_quickgrass_leafless_v3` and `ambrosia_v2` have no stored picture; `AgariluxA` was matched to the PRIME job by name only.

Every candidate job is dated 2026-09-18 or later (all after the 09-14 cartoonish window; none is a toyfig job). Boma/Borcatu candidates still carry a black outline but are the post-ruling canon renders.

## Verified pairs (17 rows in the PNG, 13 subjects)
Binding: B = subject binding/ledger bound, T = name token + same-subject Rot/RM twin. Facings: creatures east/north/south all present in both live and candidate.
| subject | live texture | candidate job (date) | bind | facings | note |
|---|---|---|---|---|---|
| RSW_Boma | Boma_{east,north,south} | canon_boma_v1_* (09-23) | B | 3/3 | NEW DESIGN: brown armoured hog to green horned canon boma |
| RSW_Borcatu | Borcatu_{east,north,south} | canon_borcatu_v1_* (09-18) | B | 3/3 | NEW DESIGN: furry burrower to red lynx-like canon borcatu |
| AB_BloodBouquet | AB_BloodBouquet.png | bloodbouquet_v2 (10-04); v3 darker alt | B | single | same design |
| AB_FirevineTreeA | AB_FirevineTreeA.png | gapbs_ab_firevinetree_v1 (10-05) | B | single | same design, more painterly |
| AB_GiantAgariTox | AB_GiantAgariTox.png | giantagaritox_v2 (10-04); v3 darker alt | B | single | same design |
| AB_KeeningCordaxA | AB_KeeningCordaxA.png | keeningcordax_v2 (10-04); v3 alt | B | single | same design |
| Ambrosia_A | Ambrosia_A.png | sheet_redo_plant_ambrosia_v3 (10-07) | B | single | same; ambrosia_v2 bytes not in store |
| FireweedA | FireweedA.png | gapfin_plant_fireweed_v1 (10-05) | B | single | same species, fuller |
| BMT_BleedingToothA | BMT_BleedingToothA.png | rot_bleedingtooth_v2 (09-19) | T | single | same concept, squatter |
| CrimsonCap_a | CrimsonCap_a.png | rot_crimsoncap_v2 (09-19) | T | single | same |
| AB_DribblingCapA | AB_DribblingCapA.png | rot_dribblingcap_v2 (09-19) | T | single | NEW DESIGN (pink/gold jelly cap) |
| AB_AgaricusDomeCap | AB_AgaricusDomeCap.png | rot_agaricusdomecap_v2 (09-19) | B | single | NEW DESIGN: stalked cap to flat dome (deliberate rot size rejudge) |
| IronScruff_BindweedA | IronScruff_BindweedA.png | gapall_ironscruff_bindweed_v1 (10-05) | B | single | NEW DESIGN: dark vine to white-flowered bindweed |

## Rejected from the 28 (15 rows): why
- RM_FE_EmberGrass_LeaflessA, RM_FE_Quickgrass_LeaflessA: candidates are bound to the full plant defs (`RM_FE_Plant_*`), not the Leafless stage; stage/design mismatch.
- AgariluxA: job is `agariluxprime` (name match only); live is a small mushroom cluster, candidate a huge prime. AB_AgariluxPrime: v2 is an outlined white blob (itself cartoonish, not a mushroom), v3 a purple coral mass; neither is the live subject's design.
- AB_ArbuscularMycorrhizaA (root web vs white tiered tree), AB_GiantAgariluxA (green cap vs thin lilac stalk), AB_LilacBeaconA (glowing bulb lost), BryoluxA (green moss vs blue frost web), GlowstoolA (glowing pale vs plain brown), GreyLadyGrownA (grey umbrella vs blue lace), Arpeau_A (pink bracket vs blue crystal): different subject concept; a re-render of another idea, not a swap.

## The other 42 rows plus the 15 rejected (no usable candidate), by group
"Sheet mention" = a Transient sheet/decisions file or art_rulings file names the subject (substring; says it was shown, NOT that it was ruled). Group is the census mod group, not a biome.


### Miasma
- RSW_AaroxisDendoria (3 tex): sheets: Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html; items: BIOME_TIER_CLEANUP_1

### Pyrelands
- RM_FE_ScorchFruitYield (1 tex): sheets: Transient/sheet_orphan_audit_2026-09-12.md

### SWBestiary
- RSW_AaroxisDendoria (3 tex): sheets: Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html; items: BIOME_TIER_CLEANUP_1
- RSW_BloodletterPetrel (3 tex): sheets: Transient/biome_ffar/wasteland_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html
- RSW_CrestedDragon (3 tex): sheets: Transient/art_verdict_sheet_2026-09-12.html, Transient/biome_ffar/miasma_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json; items: BIOME_TIER_CLEANUP_1
- RSW_Dactillion (3 tex): sheets: Transient/art_doubles_compare_2026-10-04.html, Transient/art_verdict_sheet_2026-09-12.html, Transient/biome_ffar/weepingstones_sheet_2026-10-05.decisions.json; items: CANON_CREATURE_REGEN_1, DONOR_DEFS_PORT_TO_OURS_1
- RSW_FoundryBeetle (3 tex): sheets: Transient/art_verdict_sheet_2026-09-12.html, Transient/biome_ffar/warscar_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json; items: SCARLANDS_MECHANICS_2
- RSW_FungalMantis (3 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/rot_flora_fauna_review_2026-09-18.decisions.json; items: CUT_FALLOUT_GENERATED_DATA_1, DONOR_DEFS_PORT_TO_OURS_1
- RSW_Screecher (3 tex): sheets: Transient/biome_ffar/cauldron_sheet_2026-10-04.decisions.json, Transient/biome_ffar/wasteland_sheet_2026-10-05.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json; items: BIOME_SPECIFIC_FAUNA_LAW_1, COMMISSION_LEDGER_CLEANUP_1

### UtinniPatches
- AB_AaklacA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- AB_GlobularPlant (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json
- AB_Gomphoeria (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json; items: DONOR_DEFS_PORT_TO_OURS_1
- AB_GreenRockFern (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json
- AB_Iashiphus (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json; items: DONOR_DEFS_PORT_TO_OURS_1
- AB_LargeSlimyTree (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json
- AB_MangroveTreeA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- AB_OcularTreeA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- AB_PollutedAlienTree (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- AB_SugarFamewort (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/port_tail_2026-09-20.decisions.json; items: DONOR_DEFS_PORT_TO_OURS_1
- AB_ToxiGrass (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, Transient/sheet_orphan_audit_2026-09-12.md
- AB_WildRadagast (1 tex): sheets: Transient/biome_ffar/abyss_sheet_2026-10-04.decisions.json, Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html; items: ABYSS_SHEET_DONOR_PORT_1
- BMT_SeadewA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- BrightbellsA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- FruitingBodyA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- GU_AlienGrassA (1 tex): sheets: Transient/bulk_art_misroute_2026-09-19.decisions.json, Transient/bulk_art_misroute_2026-09-19.html, infrastructure/state/art_rulings/2026-09-19_bulk_art_misroute_2026-09-19.decisions.json
- RM_SaltCameo (1 tex): sheets: Transient/codebase_health.html, Transient/codebase_health_artifact.html

Notable: RM_FE_ScorchFruitYield only appears in `sheet_orphan_audit_2026-09-12.md` (no review sheet), `RM_SaltCameo` only in codebase_health pages. Everything else was at least shown in `bulk_art_misroute_2026-09-19` and/or a 10-04/10-05 biome sheet.
Not covered: the rejected 15 rows above have no candidate; they need fresh renders or stay owed.

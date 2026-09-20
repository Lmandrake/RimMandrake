# Flora Art Improvement Pre-Queue Audit
**Date:** 2026-09-20  
**Purpose:** Verify which of 148 approved flora improvements are already done, queued, or genuinely owed before regeneration work begins.

## Source & Selection
- Source file: `design/Jawa/worldbuilding/review/flora_assignment_register.decisions.json`
- Selection criterion: rows with `art: "improve"` in the decisions data
- Measured row count: **148** (verified by scanning decisions dict; all assigned 2026-09-11)

## Audit Results

### Status Summary
| Status | Count |
|--------|-------|
| ALREADY-DONE | 3 |
| ALREADY-QUEUED | 4 |
| OWED | 141 |
| UNRESOLVED | 0 |

**Total: 148** ✓

### Already-Done Flora (3)
| defName | Found In | Evidence |
|---------|----------|----------|
| flora:the_cracked_lands:GRimMoss | infrastructure/artpipe/done/ | grimmoss_v1.json |
| flora:wasteland:PoisonPlantTallGrass | infrastructure/artpipe/done/ | poisonplanttallgrass_v1.json |
| flora:wasteland:PoisonShrub | infrastructure/artpipe/done/ | poisonshrub_v1.json |

### Already-Queued Flora (4)
| defName | Found In | Evidence |
|---------|----------|----------|
| flora:arid_shrubland:Plant_Nysyllin_Wild | infrastructure/artpipe/pending/ | desertportb_plant_nysyllin_wild.json |
| flora:desert:Plant_Chakroot_Wild | infrastructure/artpipe/pending/ | desertportb_plant_chakroot_wild.json |
| flora:desert:Plant_HubbaGourd_Wild | infrastructure/artpipe/pending/ | desertportb_plant_hubbagourd_wild.json |
| flora:dune_sea + deep_desert:Plant_Bloddle | infrastructure/artpipe/pending/ | desertportb_plant_bloddle.json |

### RSW_ Rename Findings
No flora in the improve set use BMT_ or AB_ prefixes. Zero renames checked.

### Unresolved Items
None. All 148 flora improvement rows were successfully categorized.

---

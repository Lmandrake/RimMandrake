# COLLECTION_GRAPHIC_ON_FLAT_PNG_1 — Collection graphic classes over single flat PNGs, and two textures absent entirely

## the defect, MEASURED 2026-09-26 (Scald load round)

`Collection cannot init: No textures found at path X` fires when a
`Graphic_Random`/`Graphic_StackCount` def points at a path with no `_a`/`_b`/`_c`
siblings. ⚠️ **The bare file being present does not satisfy it** — a collection graphic
class ignores `X.png` entirely. So this log line does NOT mean "art is missing".

| def | graphicClass | texPath | bare PNG on disk? |
|---|---|---|---|
| `RM_CrowncarpetFresh` | Graphic_StackCount | `Things/Item/Resource/RM_Deepfire/RM_CrowncarpetFresh` | YES (repo + game) |
| `RM_CrowncarpetDead` | Graphic_StackCount | `.../RM_CrowncarpetDead` | YES (repo + game) |
| `RM_Deepfire` | Graphic_StackCount | `.../RM_Deepfire` | YES (repo + game) |
| `RM_SaltCrystalItem` path (5 log lines) | collection | `Things/Item/RM_GreySea/RM_SaltCrystalItem` | YES (repo + game) |
| `RM_Leachmoss` | Graphic_Random | `Things/Plant/RM_Leachmoss` | **NO — absent everywhere** |
| `RM_Venomvine` | Graphic_Random | `Things/Plant/RM_Venomvine` | **NO — absent everywhere** |

Two different problems wearing one log line:
- the first four **have** art and the wrong graphic class — ship `_a`/`_b`/`_c`, or drop
  to `Graphic_Single`
- the last two have no art at all in any `Textures/` root, repo or game folder

🔑 Before generating anything for the last two, search `infrastructure/artpipe/done/`
and `_artsrc/` by subject — art regularly exists unwired (owner, 2026-09-20).

## criteria
- [ ] Zero `Collection cannot init` lines naming an `RM_`/`RUT_` path on a clean load.

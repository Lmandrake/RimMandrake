# ROT_CARTOON_VARIANT_REPAINT_1 — Rot plants: painted replacements for retired cartoon variants

Owner decision by question card, 2026-10-09: the Rot's plant `Graphic_Random` folders mixed painted
variants with cartoon ones (thick outlines, flat fills); delete the cartoon ones, render painted
replacements. Folders: `src/RimMandrake/TheRot/Textures/RotSporeKit/Things/Plant/`.

## done
- 19 cartoon variants retired through the art ledger at `1eab83286` (each folder kept its painted
  variant): ShinecapGrown_b, Brightbell_B/C, BMT_BleedingToothA/B, BMT_SeadewA-D, Wrinkle1-4,
  Arpeau_B, BMT_VioletWimpleA/B, CavernalMorel_A/B, Nuitae_B.
- 22 artpipe jobs filed, `rot_<subject>_v3a|b`, no reference (restyle), `install_to` = `<folder>/<folder>_p3a|b.png`.

## owed
- **Collect** each finished job into its folder through the ledger (`artpipe_state.py collect --from-jobs`
  / `art.py install`), look at it beside the kept variant, reject anything cartoonish.
- **Retire on install, not before** (no painted variant remains in these folders yet):
  `Shinecap/ShinecapImmature/ShinecapImmature_a.png` + `_b.png` (cartoon young cap; replaced by
  `rot_shinecapimmature_v3a|b`), `ArpeauGreen/ArpeauGreen_A.png` + `_B.png` (RM_GreenArpeau, both
  cartoon; replaced by `rot_arpeaugreen_v3a|b`).
- Not in scope: the black-outline ITEM icons (owner has not ruled).

## verify
Every folder above holds only painted variants (2-3 each) and `art.py guard worktree` is clean.

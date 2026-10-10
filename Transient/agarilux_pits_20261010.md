# Agarilux render + Pits capability, 2026-10-10

- (A) `rimflow capability retire Pits` (decision taken by question card). The orphan was a rimflow capability row, not a modcheck registry key (`modcheck forget-key Pits` found nothing). `modcheck doctor` no longer flags ORPHAN_CAPABILITY Pits. Still shown: CAPABILITY_WITHOUT_WALK Pits is gone with the row.
- (B) Render installed via art.py install (--reason artpipe-collect) at TheRot Textures `RotSporeKit/Things/Plant/TollukCap/TollukCap_A.png`, sha a3dff283...
- OUTLINE CLASH: the render has a near-black outline on 100% of edge pixels (edge lum 5 vs interior 156). Siblings: RustPuff 1% dark edge, Sagecrust 9%, Pusmelon 64% (softer). It will read heavier than RustPuff/Sagecrust.
- Design: roster row "tolluk cap" = donor AB_Agarilux, commonality 2 (biome_flora_rosters.md); Agarilux Prime is "grath elder". New def `RM_TollukCap` (all numbers PROVISIONAL, copied from RustPuff).
- Open design questions: (1) is RM_TollukCap the RM_-tier replacement of donor AB_Agarilux, and should it be wired into RM_TheRot wildPlants (commonality 2) and the donor texPath patch retired? (2) harvest: old description promised edible purple caps, none defined; (3) size/glow/fertility numbers; (4) outline: accept or regen without.
- Side effect: first install attempt used a wrong mod arg and wrote a stray event for a repo-root path to infrastructure/state/art/events/FOUNDRY.jsonl (file deleted; event remains, harmless).

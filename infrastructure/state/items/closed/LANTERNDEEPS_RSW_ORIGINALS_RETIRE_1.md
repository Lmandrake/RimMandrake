# LANTERNDEEPS_RSW_ORIGINALS_RETIRE_1 — the RSW_ originals of the five Lantern Deeps residents

On the 2026-10-05 sheet the owner kept RSW_BloodropMoth, RSW_FacetMothLarvae, RSW_Megapleura, RSW_MossBeetleLarvae and
RSW_Gembug with "RimMandrake tier" (MossBeetleLarvae's note omits it, but he cut its RM_ duplicate). The RM-tier
creature already exists for all five as `RM_<same>` (port_fauna.py, aeaa3caf0). It is cast inline in RM_LanternDeeps and
draws the byte-identical picture he kept. So the move is done for the RM tier, and the RSW_ originals remain in
`src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/`.

## spec

The rulings do not settle whether the RSW_ originals should now be deleted:
- `port_fauna.py` regenerates the RM_ defs FROM them. To delete them, first hand-own the five generated
  `RM_LanternDeeps_Fauna_*.xml` files and retire the generator.
- RSW_Gembug is still cast in the frozen `RUT_Miasma` twin (0.5) and pinned in `AnimalTolerances_Ashkarr.xml`. Q12 makes
  that the Miasma sitting's call.
- The SWBestiary copies carry the same eyes his notes ask removed. The repaints (LANTERNDEEPS_SHEET_ART_REDO_1) install
  only on the RM_ paths.

Decide one of these: (a) delete the five RSW_ defs, plus their closure that nothing else uses, once the generator is retired;
or (b) keep them as Star Wars-tier copies, and decide whether they take the repaints.

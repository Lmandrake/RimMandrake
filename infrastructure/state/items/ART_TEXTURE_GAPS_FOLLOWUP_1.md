# ART_TEXTURE_GAPS_FOLLOWUP_1

## spec
Four texture gaps found by the whole-game texture_audit (bridge6/bridge7, 2026-10-09). None is caused by
ART_OVERRIDE_FOLD_ALL_1. Each needs art installed through the art ledger, so none was cheap to fix in a bridge pass.

- **RM_Braskeen, RM_Ismerrow** (Miasma plants): texPath `Things/Plant/RM_<Name>/RM_<Name>` has no PNG in src.
  Finished artpipe renders exist (`artpipe_state.py find braskeen ismerrow`: done/miasma_ismerrow_a..d and the
  braskeen jobs). Owner pick between the variants (if any sheet has not ruled), then `art install`.
- **KOTOR_SmallCrystal_<colour>** x7 (+7 GravTide roofed twins), Armoury: texPath
  `Buildings/Crystal_Formations/small_dyeable` exists only in the absorbed donor (workshop 3254370945), which is
  not loaded. Armoury carries only `colored/{large,medium}_*`. Needs our own small crystal render (no donor art kept).
- **AA_Swarmling** (Alpha Animals): TheRot `RotSpecies_NamesAndSizes.xml` points all three life stages at
  `RotSpecies/Swarmling/Swarmling`, whose art was deleted by the 2026-10-08 card enactment (07ff006d0, "live x'd art
  deleted"). Owed a regen, or the redirect removed so the donor's own art draws until then.

Fixed in the same pass, not part of this item: RUT_Fuzz -> RM_Fuzz art; RSW_Zakkro dessicated -> vanilla Bear dessicated.

## criteria
- A1 L1: a full-list texture_audit lists none of RM_Braskeen, RM_Ismerrow, KOTOR_SmallCrystal_*, AA_Swarmling

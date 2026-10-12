# Night fixes 2026-10-12

## 1 FACE_PATCH_FIX_ADDS_TO_A_GHOST
Cause: HeadSetForFA_Revive.xml's top-level Conditional is "guarded" per validation.GUARDS but its nomatch Add hits a def that only exists with the FA Compatability Project. Fix: wrapped in PatchOperationFindMod (name "Facial Animation Compatability Project"); a8c9d7a980. selftest_mandrakepatches ghost_target_ops check (with break cases).
Live proof: load a tier without FACP; no "[RimMandrake Patches] ... FaceAdjustmentDef ... failed" line in Player.log.

## 2 THEFT_ROW_REPAIR_WITNESS_WALKS_OFF
Cause: harness spawned witnesses at watch start; lordless villagers walked off before TicksGame%250==7. Fix: src/RimMandrake/FlowWorks/northstar/liquid_checks.py (L2+L6 promoted), witness spawned at %250==4, position read at the check, retries up to 4 cycles, witness absent/dead/downed => UNMEASURED(HARNESS) never FAIL; day loop drafts colonists and refills every 2000 ticks. 2d82f7fb6c. selftest_liquid_checks 21/21.
Live: python.exe src/RimMandrake/FlowWorks/northstar/liquid_checks.py --only L2,L6 --theft-day

## 3 WEIR_POOL_DIAGNOSE_DAMMED_AT_THE_EDGE
Edge hypothesis refuted (FindWeirSite margin 12; z=12 pooled 14/16/23 cells on earlier tiles). Candidate MOD (RM_Weir.cs Upstream brittle at weak edge-lane flow). C# - written up on the item, not fixed.

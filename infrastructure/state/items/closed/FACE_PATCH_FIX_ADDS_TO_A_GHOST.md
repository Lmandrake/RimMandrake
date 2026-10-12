# FACE_PATCH_FIX_ADDS_TO_A_GHOST (MOD, MandrakePatches)

Found live by BENCH 2026-10-12 (ratchet_pilot tier + mandrake.rm.patches, 23 mods; no Facial Animation mods active).

`src/RimMandrake/MandrakePatches/Patches/HeadSetForFA_Revive.xml:108` is a `PatchOperationConditional` whose `<nomatch>` is a
`PatchOperationAdd` into `/Defs/FacialAnimation.FaceAdjustmentDef[defName="BS_InsectoidHumanoid_FourArmed_FaceAdjustment"]`.
When Facial Animation Compatability Project is not loaded the def does not exist, the nomatch Add matches nothing, and every
load prints:

    [RimMandrake Patches] Patch operation Verse.PatchOperationConditional(/Defs/FacialAnimation.FaceAdjustmentDef[defName="BS_InsectoidHumanoid_FourArmed_FaceAdjustment"]/AgeBasedParams) failed

Evidence: `Transient/bench_live_20261012/Player.pilot_startup.log` (the only new failure line against the 22-mod pilot baseline,
`Transient/bench_live_20261011/Player.pilot_startup.log`). Harmless on the owner's full list (FACP is active there), but any tier or
player list without FACP gets a red patch-failure line from our mod.

Fix: wrap the operation in `PatchOperationFindMod` (DanZinagri.FacialAnimationCompatabilityProject), per CLAUDE.md's
"MayRequire on a top-level Operation is ignored" rule. Then a tier load without FACP shows no `[RimMandrake Patches]` failure line.

DONE a8c9d7a980 (FindMod guard + selftest). Live proof: a no-FACP tier load prints no MandrakePatches failure line.

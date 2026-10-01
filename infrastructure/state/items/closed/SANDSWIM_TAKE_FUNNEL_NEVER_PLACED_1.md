# SANDSWIM_TAKE_FUNNEL_NEVER_PLACED_1 — the take funnel and drag mark are never laid on sand

Found live 2026-10-01 (FOUNDRY live session, `Transient/LIVE_SESSION_2026-10-01.md`, RM_Stillsand quicktest
on the full list, deployed commit `cc4bc992243`).

A submerged vekka killed a player chicken on Sand. The letter `Taken under: Pilot` arrived, so
`RM_CompSandSwim.Notify_SwimmerKilled` ran past its swim-terrain check. No `RM_Filth_DisturbedSand` exists
anywhere on the map (`jawa/list_things defName=RM_Filth_DisturbedSand`: 0 of 14,387 things).

Measured (`jawa/get_defs`): `Sand`, `SoftSand` and `RM_DeepSand` all have `filthAcceptanceMask = Unnatural`.
`RM_Filth_DisturbedSand` and `RM_Filth_DragMark` (`CreatureBehaviors/Defs/ThingDefs_Misc/RM_KillSigns_Filth.xml`)
declare `placementMask` `Terrain` only. Vanilla `FilthMaker.TryMakeFilth` therefore refuses on every swim
terrain, so neither sign can ever appear where it is meant to.

Also seen: the victim's corpse stays on the surface, though the letter text says the body was pulled down.

## spec
1. Give both filth defs a placement mask that sand accepts (add `Unnatural`), or place them in a way that
   bypasses the acceptance check.
2. Decide whether a take removes the corpse (the letter text says it does).

## criteria
- On a Stillsand quicktest, a swimmer kill on Sand leaves `RM_Filth_DisturbedSand` at the victim's cell
  (state read: `jawa/list_things defName=RM_Filth_DisturbedSand`), and a submerged swimmer carrying a corpse
  lays `RM_Filth_DragMark`.

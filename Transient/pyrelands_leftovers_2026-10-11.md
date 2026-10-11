# Pyrelands leftovers 2026-10-11

## 1 RSW_Dalgo - DONE
H east installed over the kept east (ruling b9fbaaf27a12876609e8). North/south queued: canonregen_rsw_dalgo_v1b_{north,south}
(derive_from the failed-canon master canonregen_rsw_dalgo_v1_east = H). `--mark-done RSW_Dalgo` applied.

## 2 RSW_Nuna - PARTIAL
E installed as Nuna_m (owner-said "Use E for all MALES."), B as Nuna_f, C placed as Nuna_fV_C_{east,north,south}
(female variant path, NOT wired). A and D purged (A with --release-keep). Not wired: PawnKindDef.alternateGraphics replaces
texPath for BOTH genders (AlternateGraphic.GetGraphic(other), PawnGraphicUtils.TryGetAlternate), so a female-only variant would
also show on males. Needs owner choice. Not marked done.

## 3 RSW_Orray - DONE
J installed over Orray_{east,north,south} (ruling 5d7ec3e7b4819cab7fe8).

## 4 Quickgrass - DONE
enact had deleted the old QuickgrassB (not owner-purged). Restored it. Pool now: RM_FE_QuickgrassB.png, RM_FE_Quickgrass_b.png (render B).

## 5 RM_Ashwallow - DONE (def half)
Art redo job exists and is rendered: enact_f6734fd2_ashwallow_v1_{east,north,south} (awaiting owner pick).
Def: PROVISIONAL ComfyTemperatureMax 120, ArmorRating_Heat 1.0, Flammability 0.05; description updated for face/teeth/curled legs.
Dome stance already exists: RM_BurrowOnFireExtension + RM_JobGiver_BurrowOnFire + RM_JobDriver_Burrow (RM_Burrowed hediff while burrowed).
Stale comment in RM_JobDriver_Burrow.cs ("ThingDef carries no such stats") is now false; left (editing .cs invalidates the DLL stamp).

## 6 RM_FireWasp - already done
pyrelands_firewasp_flight8_* jobs done; FireWasp_Fly_{1-8}_{east,north,south}.png installed; PawnKindDef wired (RM_PyrelandsPortedFauna.xml).

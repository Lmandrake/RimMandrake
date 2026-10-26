# HOSE_SHADOW_FIX_CARRIED_STRAND_STALE

## spec
Confirmed by reading (2026-10-26): RM_MapComponent_Hoses.cs DrawAll's Carrying branch (:817) drew the carried tail and
continued without dropping meshes[r]; PickUp (CompHoseReel.cs:517) -> HoseChanged (:360) nulls only the lay; SetCarry makes
laid=false so the tick loop (`if (!r.laid) continue`, :666) skips the 250-tick EnsureLay that would have dropped it.
poseVersion did bump (Layered sees the lay change) but DrawCrossShadow iterates `meshes`, which still held the laid strand.
Fix 300816d5f4: the Carrying branch drops the cached strand (non-legacy only; FrameLegacy unchanged).

## criteria
- O1 L0: FlowWorks builds 0 errors; SelfTest HoseCarryChecks row7 (premise + source order + can-fail) passes, hose suites 431/431 (done in 300816d5f4)
- A1 L2: after the FlowWorks deploy at the next game-down, live: two crossing laid hoses, pick up the lower one; the upper hose's crossing shadow over the old strand is gone while it is carried, and comes back over the new strand when it is set down

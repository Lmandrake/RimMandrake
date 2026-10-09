# Watcher stalk vertical slice — progress (2026-10-08)

Item: WATCHER_CREATURES_MOD_1. Helper: FOUNDRY, offline only.

## Steps
- [ ] read pitch + kit
- [x] read pitch §3.2/§5/§5.7 + kit + living bolt; RimSage reads: PawnRenderTree (AnimationTick, AnimationFinished, TryGetMatrix: per-frame transforms, draw requests cached until SetDirty), PawnRenderer.SetAnimation, AnimationDef/AnimationPart(pivot)/Keyframe, PawnRenderNodeWorker (OffsetFor/PivotFor/RotationFor/ScaleFor/CanDrawNow), PawnRenderNodeWorker_AnimalBody (stationary only when no animation), PawnRenderNode_AnimalPart (corpseGraphicData when dead), GraphicMeshSet (west mesh flipped), TurretTop (ArtworkRotation -90, idle 0.26 deg/tick)
- Design: own job driver/giver/think tree (kit's RM_JobDriver_Watch untouched); kit kernel DecideStep reused; new Verse-free RM_WatcherStalkKernel (phase machine: hide only after retract completes; angle easing; octant); one-line kit-core change owed in RM_CompWatcher orphan guard (it would strip the hidden hediff from any job but RM_WatcherWatch)
- Brief says LARGER flinch radius (very shy); item/pitch text says "small flinch radius" - followed the brief
- [x] new files written: kernel, comp, driver+giver (subclass of RM_JobDriver_Watch), render nodes/workers, settings section, render tree, 2 AnimationDefs, race/kind/sign/husk/smelt recipe, think tree, job def, keyed, fuzz family "stalk"; adapted to the other helper's uncommitted kit (no flush, alarm, remainsDef, fragility ceiling 5 -> baseHealthScale 0.03)
- [x] art: artpipe_state find RM_Watcher/camerastalk/watcher_stalk = 0 hits (probe hawkbat 128); queued 9 jobs (heads E/NE/N/SE/S, stalk, hatch, husk, seam-glint sign) at priority 50, install_to src/RimMandrake/Watchers/Textures/...; placeholders wired meanwhile
- [x] kit hooks already landed by the other helper at 5de62aeab (virtual Sign, RM_JobDriver_Watch.InWatchJob): no kit-core logic change needed from me; registered compile lines, settings section (2 lines), fuzz family. Fuzz all families OK; stalk mutation (hide at half retract) caught 963 failures
- [x] published 21d276478 (slice), cec3c6d5e (pitch/item), 401edef2c (ledger: implemented -> built, owes W1/W2/W3 L2 via bridge). DONE

# WEEPINGSTONES_NET_TARGET_FLEES_1 — a wild skarrin outruns the netting handler and leaves the map; how should capture work?

Found by the Weeping Stones first script (`src/RimMandrake/WeepingStones/validation.py`, chain `job_net`), live poke 2026-10-03. Left RED on purpose; the test is not padded.

## What exists

`RM_NetPoolBreeder` (`Defs/JobDefs/RM_StockedPoolJobs.xml`, driver `RM_JobDriver_NetPoolBreeder`) takes 200 ticks of netting. The wild skarrin flees the handler at flight speed (about 13 cells per 100 ticks against the colonist's 5) and leaves the map before the net completes, so no `RM_SkarrinBreedingStock` item is ever made. The same shape probably holds for the other stockable natives. `leaveMapOnFleeChance` is 0.6 on the skarrin.

## spec

Ruled by the owner 2026-10-07: capture is not a custom 200-tick channel. Success follows the target's speed and whether the net lands, using the game's existing net mechanics. Replace `RM_NetPoolBreeder`'s channel with vanilla net behaviour.

Also the same chain family has cull (`job_cull`: 0 vhorrin left, 0 meat) and stock (`job_stock`) reds from the same session; they may be unrelated script or load-state faults and are being re-run on the fresh load first.

## criteria

- A0 L0: offline - WeepingStones builds 0/0; `selftest_weepingstones_fuzz.py` family `net` and `selftest_weepingstones.py` pass (DONE d110033b2f).
- A1 L1: a handler ordered to net a wild, NON-FLEEING stockable pawn on a quicktest map ends with the pawn gone and exactly one breeding-stock item, in at least 5 of 5 tries.
- A2 L1: the `job_net` chain goes green without any change to the test.

## Watch out

Since d110033b2f capture is a thrown vanilla Projectile (`RM_Projectile_PoolNet`): a FLEEING target outruns the net by design (owner's ruling), so a 5-of-5 run needs a target that is not fleeing. Read the target's job before calling a red a driver bug.

The ruling above changes feel (how hard it is to farm the pools).

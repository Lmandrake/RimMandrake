# Art requeue 2026-10-02

(skeleton) classification, requeue, results below.

## Causes (failed/, today's queue)
- bad_job_file x9 (rut_vent{smelter,forge,kiln}_v1 x3 facings): prompt said "three-quarter top-down" while job declares a facing; common.py refuses overhead wording on facing jobs. Fix: dropped it, "seen from the side at its own eye level".
- worker_error x4 of today's list (rm_greatbolehardwood_v1, rut_sweetlinewool_v1, rut_livingbolt_v1_east): codex worker emitted its schema/manifest before calling image_gen (transient harness flub, quota fine at 73%, no prompt fault). Fix: refile unchanged as v2.
- master_failed x2 (livingbolt north/south): derive from failed east master; refiled with v2 set.
- Messy Conduit: all 8 RM_MessyConduit_Jawa_* in done/ PASS; nothing to requeue.
- Same worker_error also hit 7 jobs NOT in today's lists (RM_Borehulk_south, RM_Hwelgrue_north, RM_Selvix, RM_TractionLance_Base, RM_Yammeth_south, rot_illoth_b_south, rot_thozzik_b_south): left alone.

## Requeued (Transient/requeue_20261002/b{1,2,3}.json via fill_queue.py)
b1: rm_greatbolehardwood_v2, rut_sweetlinewool_v2, rut_livingbolt_v2 (e/s/n). b2: rut_ventsmelter_v2, rut_ventforge_v2 (e/s/n). b3: rut_ventkiln_v2 (e/s/n) filed when queue drains.
- t~10min: b3 filed
- Result: all done/PASS. rm_greatbolehardwood_v2 and rut_ventsmelter_v2_south hit the same worker flub again; refiled as rm_greatbolehardwood_v3 (reworded) and rut_ventsmelter_v3_south (derive_from rut_ventsmelter_v2_east): done. Finished art NOT wired.

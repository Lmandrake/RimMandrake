---
state: built
needs: bridge
---

# HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Hose routing should prefer bare ground around a hose reel over passing through it (water-scene S3: pond loses 6.98 levels, canal gains 6.00; log Transient/fw_scenes/live/S3_*.txt)

Built at `86e8a90bfe2d` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-20: Offline fix landed 86e8a90bfe (BENCH): reel/pump cells cost HoseMath.BuildingCrossCost=6 in the hose CordWorld (were 0, PassThroughOnly read walkable, so a hose out of a west nozzle to an east end U-turned over the rig); Lay/LayAlong shaping prefers poses off reel/pump cells the plan avoided, cost never refuses. Selftest HoseGptFix.ScenicRoute (S3 rig, can-fails) 347/347. DLL built, NOT deployed. LIVE ROW OWED: deploy, re-run water_scenes_walk S3 and look that both hoses lie on bare ground; then

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=HOSE_PATHING_REPAIR_SCENIC_ROUTE_PLEASE` first: another commit may already do it.

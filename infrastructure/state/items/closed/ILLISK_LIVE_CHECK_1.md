## spec
Live proof of the Illisk shoal built under GREENTIDE_ILLISK_BUILD_1 (closed with nothing owed; its live checks were never run). Needs the bridge.

## criteria
- [ ] L1: RM_Illisk spawns as a shoal of 6-12 in RM_Greentide water.
- [ ] L1: A non-blast hit (bullet, melee) on an Illisk is scaled to 4% by RM_CompShoalHide (`shoalNonBlastFactor`).
- [ ] L1: A Bomb-def blast does full damage and kills it.
- [ ] L1: With roster commonality 1.0 a wading colonist crossing Greentide water is not made impossible; tune wildGroupSize/commonality from what is seen.

## verify
- Live (bridge free): spawn RM_Illisk x10 on Greentide water; count the shoal; shoot one and read damage; explode a Bomb and read death; `jawa/get_defs` with defs as the STRING "PawnKindDef/RM_Illisk" returns success true.
- Crossing: send a colonist across Greentide water with a shoal present and read whether it is reached and survives; record the tuning.
- Offline reference: `python3 src/RimMandrake/Greentide/validation.py`.

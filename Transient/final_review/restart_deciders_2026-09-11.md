# Restart deciders — nursery-fix reboot 2026-09-11 (BENCH, owner AFK, standing authorization)
Written BEFORE launch per rimworld-load-round §2. Strings that decide each item:
1. NURSERY FIX (this reboot's reason): `grep -c "has null thingClass"` == 0 AND
   `grep -c 'Could not find parent node named "RSW_'` == 0 → juveniles inherit; else REGRESSED.
2. GAME STARTS WORK AGAIN: after load, jawa/load_stall_probe programState==Playing on the
   canonical save → QUICKTEST_MAPGEN_NRE_1 likely resolved by same fix (verify quicktest later).
3. QUICKGRASS: `RM_FE_Plant_Quickgrass` def loads (no config error naming it); visible in
   Pyrelands wildPlants at next map visit.
4. RESTORE FALLOUT BASELINE: `grep -c "^Config error in"` — expect ~95 minus the 12 juvenile
   errors (≈83); ZBiome duplicate-record errors PERSIST (untouched, RESTORE_FALLOUT_TRIAGE_1).
5. FOUNDRY content staged in src but NOT deployed by BENCH (their port/Law3/SandStalker):
   absent from log by design this load.

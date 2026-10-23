# CONTAGION_STRAYS_HARDEN_ZHOOL_WANDERS_OFF — the two other non-passing Contagion rows from the 2026-10-23 sweep

Source: `Transient/fwsweep/contagion_ns3.json` / `contagion_run3.log` (untracked, FOUNDRY clone), the run that
filed CONTAGION_BURN_DIAGNOSE_NATIVE_FEELS_NOTHING and COALESCENCE_STAGE_DIAGNOSE_STUCK_AT_ONE.

1. `zhool_haze.conversion_off_turns_nothing` UNMEASURED: the zhool (RM_OcularJelly) was at (12,117), far off its
   pad, with the grass fill intact (225). Likely the same CreatureBehaviors sun escape / shade hop that took the
   Coalescence walkers (RM_Contagion carries RM_SunHeatExtension): the off arm waits 3000 ticks with the zhool
   free to dash for shade. Harness fix, not a mod fault: give the pad shade the zhool will stay in, or read its
   track and judge only while it sat on the fill (the on arm already does this).
2. `touched.sunbeam_hit_arrests` UNMEASURED: the toggle-off Sunbeam hit (jawa/damage RM_UVBeam 5) left no
   RM_UVSunburn on the player colonist (hediffs RM_ContagionTouched, Scarification), while the uv chain's
   visitor took 5.0. Read why a hit on this colonist lands nothing (apparel armour? a deflect) and retry/raise
   the amount, as the on arm already retries.

## criteria
- O1 L0: both rows' harness changes pass selftest_contagion with a site break per cause
- A1 L1: both rows PASS (or UNMEASURED naming a new, filed cause) on the next live Contagion run

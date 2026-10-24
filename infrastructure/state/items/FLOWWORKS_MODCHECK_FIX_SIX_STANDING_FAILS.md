# FLOWWORKS_MODCHECK_FIX_SIX_STANDING_FAILS

The modcheck run of FlowWorks on 2026-10-24 (live, minimal list) gave six FAIL rows. Four of them also
failed at 09:27Z the same day, so they are standing, not flaky. Each is classed MOD, presumed and not yet
traced. Trace each one to MOD, SITE or HARNESS before fixing anything.

| chain | row | detail | 09:27Z |
|---|---|---|---|
| plot_D_limited_pond | pond_shoreline_recedes | far-edge pond cell still a source cell after the draw | UNMEASURED |
| toggle_fill_in | fill_in_on | filled-in cell (129,131): D=1 expected 0 | PASS |
| toggle_recession | recession_on | no pond cell dried with recession ON | FAIL |
| all_off_still_digs | all_off_digs_dry_channel | all-off dug cell (169,174): F=1 expected 0 | FAIL |
| slime_slip | slime_slips_the_wader | 20 s in slime, slip 1.00, slips 0, moving False | FAIL |
| liquid_pump | pump_unpowered_idle | an unpowered pump moved liquid? (moved 0, running False) at level 3 | FAIL |

Leads:
- Three rows involve recession or the shore receding: pond_shoreline_recedes, recession_on, and the
  all-off channel that kept F=1. They may share one cause. Related item: RECESSION_SCAN_TAME_RERUN_PER_CANDIDATE.
- In slime_slip the wader reports moving=False, so the pawn may never have walked. That would make it
  presumed SITE/HARNESS: the pawn was idle or drafted.
- In pump_unpowered_idle the payload reads moved 0, yet the row says the pump moved liquid. The check may be
  reading the level, not the pump. That would make it presumed HARNESS.

Evidence: Transient/modcheck/FlowWorks_20261024T191345Z.json (+ .html); prior Transient/modcheck/FlowWorks_20261024T092758Z.json

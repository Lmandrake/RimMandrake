# PYRE_HERD_DRIVE_BUILD_TWO_DAYS_LATER

## drive (68049f4519) — compressed/decomposed, never two days stepped
1. anchor MEASURED: burn A at (30,100), recorded; `MapComponent_BurnLine.BackdateBurnHistory(lag+2500)`; burn B at
   (220,100) recorded fresh; `ProbeBurnHistory` BurnCenterAgo(2 d) must be A with B the newest sample.
2. decision MEASURED: `RM_JobGiver_FollowBurn.ProbeHerd(RM_Ullai, issue)` reads the giver's own decision (shared `JobFor`
   -> `RM_BurnKernel.FollowBurnDecision`) for 10 spawned wild ullai, chance roll set aside; all must GoAnchor to A.
3. motion MEASURED: one 2500-tick step; centroid closes >=30% toward A and more on A than on B (`herd_verdict`).
4. cadence INFERRED: chancePerCheck 0.04 per think brings the herd unforced within two days.
Offline: fuzz (decision table vs spec; backdate makes HistoryIndexAgo pick A over B), site selftest (pure parts, wiring).

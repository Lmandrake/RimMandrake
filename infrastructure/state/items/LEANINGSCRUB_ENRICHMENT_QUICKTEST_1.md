# LEANINGSCRUB_ENRICHMENT_QUICKTEST_1 — quicktest-prove the Leaning Scrub enrichment on a Scrub map

From `LEANINGSCRUB_GPT_ENRICHMENT_1`'s criterion "quicktest-proven on a Scrub map". The build was
offline and compiled clean, but nothing has been proven live yet. Prove each part by STATE READ.
Never use an unattended screenshot or flight hunt (owner, said three times 2026-09-25).

## checks

1. **Dripping venomvine:** harvest an `RM_DrippingVenomvine`. The plant survives and its growth
   reads 0.3. Turn the "Dripping venomvine regrows" setting off and restart (it is applied at
   startup or on settings write), and a harvest destroys the plant.
2. **Crown mob:** on a map with an `RM_CrownVenomvine` and wild `RM_Dustflutter`, force weather
   `RM_Stall`. Within an in-game hour, dustflutters within 40 cells hold `Goto` jobs targeting cells
   within 3 of the crown, or stand there.
3. **Runway bloom:** walk a colonist through fuzz near wild crustweevils, fuzzrunners, visslers
   and dustflutters. They take `Flee` jobs staged 0/30/15/60 ticks after. Dustflutters read
   `flight.Flying` true right after (`Pawn_FlightTracker` state, via a debug `[Tool]`). An
   `RM_VisslerArm` appears beside some visslers.
4. **Sweetline tree:** spawn `RM_SweetlineTree` (mature). Its label carries a generated name, the
   History gizmo opens, the inspect string counts down the wool, and after the timer 5
   `RM_SweetlineWool` lie beside it. Damage it and a "struck by" entry appears. The name survives
   save/load.
5. `Player.log` shows no errors from `RimMandrake.LeaningScrub`.

# Slime / Contagion live-rerun fix dispositions (2026-10-03)
No C# change; no real regression found (Slimification.cs rate/Dissolve/alert logic unchanged by today's commits except the clock-scaling, which is 1.0 at the default 7 days).
- growth_rate_on_slime, stage1_wipes_off_stages_2_3_hold, standing_alert_lists_pawn: HARNESS. Seeded pawns were absent from list_pawns (dead/gone on the shared map; only exposed+control survived), read as "hediff vanished". Now `_require_alive` -> UNMEASURED naming dead/absent. Needs a live rerun to prove the rates.
- returned_to_the_flow: HARNESS/UNATTRIBUTABLE. Pawn gone with no corpse, no smear, no raw slime = Dissolve never ran. Now UNMEASURED in that case; products missing while pawn dissolved still FAILs.
- marked_colonist_is_liked_less: HARNESS. Situational social thoughts are cached ~100 ticks; same-tick re-read returned 0. Added 150-tick waits before each read.
- Contagion extraction_surgery_yields_sample: the 30 s timeout was the un-wrapped LayDown ordered_job (waitTicks=300) before the surgery loop; the 240 s `_patient` helper covered only the surgery calls. Wrapped LayDown + its wait in `_patient`.

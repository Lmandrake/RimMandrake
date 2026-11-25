The SteveDesktop worker started the game on whatever ModsConfig held, and modcheck composed its own list only inside run, so half the jobs (226 in 7 days) cold-started on the wrong list and restarted. Compose the job's list before the first load (modcheck compose) and keep a game only when its launch list equals the composed one.
item: RIMMANDRAKE_FIX_STEVEDESKTOP_TOP_WASTE_HE_SAID_END_THIS
home: infrastructure/stevedesktop/RUNBOOK.md

# Pyrelands 0.1.0: in-game acceptance, visit 9 (Archmagi, ArchBig)

Detached BENCH helper, item RIMMANDRAKE_DRIVE_PYRELANDS_IN_GAME_ACCEPTANCE_VISIT_NINE. Started 2026-11-24 07:40 PST. Bound 3 hours (10:40).

## Progress

- 07:45 skeleton; item claimed; ArchBig bridge taken (was free, game up); evidence/compose_dry.log next.
- 07:55 ArchBig is already up on his full list with the a6f05380df DLL (all tier mods in sync); full-list smoke and the walk save run first on this load.
- 08:05 full list (313 loadable mods): site NS_Pyrelands_site_1_417df172fdb5_visit9full (tile 49); sc_full_list_smoke PASS; labelled walk save written; stations being looked at. Two full-list mods are no longer installed (kutte.stairs among them), so visit 8's full-list site no longer loads.
- 08:10 walk save PYRELANDS_0.1.0_VISIT9_WALK_FULL.rws written twice (second: the creatures spawn after the 600-tick advance, so none has walked off), every station looked at; now the tier.
- 08:25 tier pyrelands (18 mods) up; gate A all PASS but loadavg 14; site tile 193, gate B CLEAN; batch 1 of the short checks running.
- 08:30 sc_ash_watered shrunk (five reads over 50,000 ticks instead of five days); cheaper_why written for burn_line, burn_compounds, grass_regreens, heat_dome. burrowers, heat_dome, fire_tick_effects PASS.
- 08:42 batch 1 done: burrowers, heat_dome (naive GPT judge told the dome from the standing body), fire_tick_effects, scorchfruit, no_ordinary_rain, mapgen_log, grass_cover, ambient_ash_drift, blackrain, gate, ullai_and_giant, reload_keeps_the_burn, wind_burn_live 9/9: all PASS. Batch 2 (ash_fertility_watered, fresh_burn_bonus, regrow, burn_line) running.

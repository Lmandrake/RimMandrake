# FlowWorks northstar notes 2026-10-05

- [start] skeleton created
- [prep] offline preflight: P-O2 fails 1/31 toggle (pitExposureEnabled); P-O3 deploy drift; P-O4 list diff; P-O5 no golden yet. selftest 88/88 pass
- [prep] added toggle_pit_exposure chain (validation.py) -> P-O2 PASS 31/31 toggles. bridge held by FOUNDRY (belt suite rerun) at 21:xx
- [prep] runsheet.py + design/RimMandrake/northstar_trials/FlowWorks_runsheet.md (103 comps, 43 bars)
- [prep] validation_v2.py offline repaired: O2 census 31 (+pitExposureEnabled), O8 job_probe kwargs, sluice/spikes dropped from UNBUILT (landed; validation.py stages them). Offline tier all PASS
- [live] 14:20 took bridge
- [live] 14:2x killed game for tier swap; ModsConfig backup deployed/config/ns_flowworks_backup.20261005T142015.json
- [live] deployed FlowWorks + JawaBench(81b853a2f201), tier flowworks applied (10 mods). launching
- [live] map up 250x250 TemperateForest; all new tools registered; running prep_site
- [live] 14:5x prep_site rc=0: golden NS_FlowWorks_TrialSite_v1 saved. Fixes: destroy_bulk for pawns (destroy_batch skips pawns), WeatherController lock excluded, weather dict, roof 'None', VoidMonolith pre-check, step 60 ticks for temp cache, ABSENT settings fields (spec newer than loaded DLL)
- [live] preflight live CLEAN 17 rows (fixes: tier list via resolve_tier incl zoom mod, body cells exempt D/F, autosave>=14d, jawa/prefs autosave=14 set -- RESTORE to 0.25 at release). next: dirty proof
- [live] dirty proof: rain+stray steel+stray pawn -> P-E1,P-S1,P-E4 refused (cold snap not injected: game_condition param is durationTicks). also plants regrow in plots after ticks (K Brambles, S Grass) -> bars must clear via _prep_plot

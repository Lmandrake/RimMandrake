# FlowWorks UX fixes (BENCH helper, 2026-10-22)

| item | state | sha | live look owed |
|---|---|---|---|
| FLOWWORKS_SETTINGS_UNTANGLE_THE_JUNK_DRAWER | done | 9544ea0571 | open settings, each section, reset, search |
| FLOWWORKS_SETTINGS_POLISH_SUPERDEEP_LEAKS | done | b5e1142258 | read settings page for wraps; hover dig/fill |
| SLUICE_GATE_SETTINGS_EXCISE_KNOBS_ON_NOTHING | done | 747c9290c9 | architect label "sluice gate"; sluice box inspect line |
| HOSE_FITTING_RENAME_CAP_IS_NOT_CAPPED | done | 11aec7495c | reel gizmos + inspect; dropped-end message click |
| DEEP_DIG_EXPLAIN_WAITING_ON_NO_DROID | done | 5c92b4a9cf | dig to 4 m with no mech: alert + menu note |
| DRILL_SURVEY_EXPLAIN_BEFORE_STEEL_IS_SPENT | done | 4e090d7ba1 | place drill on yield / no-yield map, read mouse text |
| 3 red selftests | done | 2038122711 (+review_map seed in 9544ea0571) | none |

All edited .cs files are DIRTY under code_review_status.py. C# SelfTest 773/773; FlowWorks py 50/50 + selftest_settings_screens 854/854. Nothing deployed.

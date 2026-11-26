# WB-pipeline-operations-20261126-093208 state

Worker on SteveDesktop; the Dispatcher, ops_watch and the role runs live on Archmagi (`ssh mandrake@archmagi-wsl`,
dispatch clone `/home/mandrake/rm/dispatch`, state `/mnt/d/ClaudeWork/rimmandrake/dispatcher/state.json`).
Scratch (SteveDesktop): `/mnt/d/ClaudeWork/scratch/sonnetrev/` (diff, fresh read), `sonnetrev_tests*.txt`.

## Members (class, outcome, commit)
| member | class | outcome |
|---|---|---|
| RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT | KEEP | fixed 45c29d1a14 (selftest_ops_escalate 5 of 5; fresh read via the Codex door on Archmagi: NOTHING SIGNIFICANT) |
| PAWNTWEENER_DIAGNOSE_ROOT_NRE_ON_HOSE_SAVE | STALE (pre-pipeline; its save and log are gone, 0 sightings today) | dropped 5feb2e3b69 |
| OPS_DESIGNER_UNSTICK_READY_AND_WAITING_GZKV | ROUTED to the Conductor: the owed guard lift is its act; no fix fault on its last ring | shape route 65f7e9e878 |

## Learned about the system
- Before 45c29d1a14 a revisit-only incident run asked `incident_run` with model None, so it launched on Opus
  (`mode_model(Operations, "run")`). Now it is marked `revisit` and `job_model` reads `model_by_mode["revisit"]`.
- The broad-grep guard of the ticket's spec item 3 was already in `roles/operations.md` §Run hygiene (inlined for
  alarm and incident runs).
- `selftest_incident` was red on origin/main from 426b0b83c4 (login_watch's computed alarm kind); 886f19ec7d fixed it
  the same way while this run worked. `selftest_guiding_prose` cannot run on SteveDesktop (the clear-findings tool is
  absent): filed RIMMANDRAKE_INSTALL_CLEAR_FINDINGS_ON_STEVEDESKTOP_GUIDING_PROSE_BLIND.
- SteveDesktop's `~/dev/Dispatch` clone is diverged from its origin (no fast-forward), so `gpt_consult.py` fails there
  with "Codex door is absent". Run it on Archmagi.

## Next, in order
1. After the 07:30 PST Operations run of 2026-11-26 (dated wait to 16:30Z), close
   RIMMANDRAKE_SONNET_OPS_REVISITS_SIX_GREPS_TIMED_OUT with `--sha 45c29d1a14c50fbd27dc696986937c2245df00b5 --live
   "role=Operations max_age=2d"`. The close of 02:18 PST was refused only on that live line (no Operations launch since
   the commit). Use `--no-remainder`: spec 1 and 2 are built and tested; spec 3's grep guard was already in
   operations.md Run hygiene; the live line ">=5 Sonnet revisit runs, grep-timeout rate no worse than 6/64" is not
   built, because 5 runs against a 9% base rate cannot tell a change apart. `--why` names "a line a program can check:
   filed RIMMANDRAKE_CLERK_OPEN_INCIDENTS_FIFTY_SEVEN_RUNS_ONLY_NOTED".
2. Nothing else: the other two members have their outcome.

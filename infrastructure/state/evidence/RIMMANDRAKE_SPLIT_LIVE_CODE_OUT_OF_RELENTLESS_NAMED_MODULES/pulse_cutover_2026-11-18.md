# Pulse package cut and move: evidence (2026-11-18, BENCH detached run)

Landings: 7dccb4188c (dead code deleted in place), 7ab8a45321 (move to Utils/ops_core + unit cutover).

## Selftests of every touched or importing file, on 7ab8a45321's tree (run_selftests.py --only, 30 tests)
```
PASS          0.2s  src/RimMandrake/Utils/ops_core/selftest_deploy_on_ext4.py
PASS          6.3s  src/RimMandrake/Utils/ops_core/selftest_deploy_sparse_dirs.py
PASS          5.1s  src/RimMandrake/Utils/ops_core/selftest_ops_core.py
PASS          0.1s  src/RimMandrake/Utils/ops_core/selftest_phone_push.py
PASS          1.3s  src/RimMandrake/Utils/ops_core/selftest_streams.py
PASS          4.2s  src/RimMandrake/Utils/ops_core/selftest_streams_rules_drift.py
PASS          0.1s  src/RimMandrake/Utils/ops_core/selftest_testing_metrics.py
PASS          0.1s  src/RimMandrake/Utils/ops_core/selftest_usage.py
PASS          0.1s  src/RimMandrake/Utils/selftest_account_usage.py
PASS          0.3s  src/RimMandrake/Utils/selftest_deadman_check.py
PASS          0.3s  src/RimMandrake/Utils/selftest_era_reach.py
PASS          5.7s  src/RimMandrake/Utils/selftest_findings_retype_outcome.py
PASS          0.2s  src/RimMandrake/Utils/selftest_live_retired.py
PASS          3.4s  src/RimMandrake/Utils/selftest_model_week_limits.py
PASS          0.4s  src/RimMandrake/Utils/selftest_ops_clocks_check.py
PASS          0.2s  src/RimMandrake/Utils/selftest_ops_clocks_deploy_default.py
PASS          0.3s  src/RimMandrake/Utils/selftest_ops_health_stamp.py
PASS         36.3s  src/RimMandrake/Utils/selftest_ops_watch.py
PASS          0.1s  src/RimMandrake/Utils/selftest_ops_watch_alarm_names.py
PASS          0.6s  src/RimMandrake/Utils/selftest_ops_watch_designer_stall.py
PASS         24.4s  src/RimMandrake/Utils/selftest_ops_watch_whea.py
PASS          2.6s  src/RimMandrake/Utils/selftest_role_use.py
PASS          2.8s  src/RimMandrake/Utils/selftest_switching_plan.py
PASS          0.2s  src/RimMandrake/Utils/selftest_switching_plan_notice.py
PASS        123.8s  src/RimMandrake/Utils/testq/selftest_brake_release.py
PASS         10.3s  src/RimMandrake/Utils/testq/selftest_brake_release_beat.py
PASS         90.1s  src/RimMandrake/rimflow/selftest_conductor_authority.py
PASS          1.4s  src/RimMandrake/rimflow/selftest_login_watch.py
PASS          0.2s  src/RimMandrake/rimflow/selftest_retired_era_gone.py
PASS          0.4s  src/RimMandrake/rimflow/selftest_stop_resume.py
PASS 30/30  FAIL 0/30  UNMEASURED 0/30  CRASH 0/30  SKIPPED 0/30  (wall 124.3s) — contained in rm-harness.slice (max 24G), 6 workers
RESULT: GREEN (green = FAIL 0 and CRASH 0)
```

Red on the untouched base b49cac1bcf as well (not caused here): selftest_known_reds.py (2 WIRE checks), rimflow/selftest_incident.py (stage_void, system_fault unreviewed).

## Cutover readings (journalctl --user)
```
2026-11-18T23:02:29-08:00 Archmagi python3[2131834]: pulse update: /home/mandrake/rm/pulse-deploy 7dccb4188c4c -> 7dccb4188c4c (already current)
2026-11-18T23:10:38-08:00 Archmagi python3[2162643]: deploy update: /home/mandrake/rm/pulse-deploy 7ab8a4532114 -> 7ab8a4532114 (already current)
2026-11-18T23:11:08-08:00 Archmagi python3[2162981]: streams: you: 73 picks, 72 waits over 3 d; Steve PAUSED; Archmagi UP  (20.5 s; 21 measured, 11 unmeasured)
rm-deploy-update Result=success ExecMainStatus=0
rm-streams-collect Result=success ExecMainStatus=0
rm-ops-watch Result=success ExecMainStatus=0
rm-deadman Result=success ExecMainStatus=0
pulse-deploy HEAD 7ab8a45321; sparse: src/RimMandrake/Utils/art src/RimMandrake/Utils/artpipe src/RimMandrake/Utils/modcheck src/RimMandrake/Utils/ops_core src/RimMandrake/Utils/sim src/RimMandrake/Utils/testq src/RimMandrake/contracts src/RimMandrake/rimflow 
```

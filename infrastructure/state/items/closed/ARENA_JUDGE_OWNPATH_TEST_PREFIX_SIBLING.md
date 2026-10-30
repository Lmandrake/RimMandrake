Found by BENCH verifying ARENA_GPTJUDGE_HARDEN_ISOLATED_CODEX_HOME at 62d8f964f2 (minor, test gaps).
1. Mutant SURVIVED both selftests: arena_judge.judge_env owned() `v.startswith(ownr + os.sep)` -> `v.startswith(ownr)`
   (a sibling dir sharing the work dir's name prefix passes the clone-root filter). Add a sibling-prefix case.
   Evidence: D:\ClaudeWork\rimmandrake\arena\verify_judge_harden\mut\ (bench_mut.py, result1.txt).
2. arena_judge_calib.JudgeCritic.review copies votes as {judge, verdict, why} only, dropping the GPT vote's `tools`
   record (n_tools/web/refused_tool_calls/wiped); the calibration cannot report tool attempts. Keep `tools`.

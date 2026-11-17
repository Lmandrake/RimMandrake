# RIMMANDRAKE_FIX_GSS_PLAYTEST_RUNNER_CODEX_REVIEW_FINDINGS

## spec
Codex full-file review 2026-11-17. med l.139-144: resume_loop checks its deadline only after wait() and start_b(), and each retry gets a fresh full wait budget, so --load-wait 60 can run far past 60 s (not probed).
Raw review: /mnt/d/ClaudeWork/rimmandrake/conductor/cr/r_gr.txt. Not fixed at filing.

## refs
file: src/RimMandrake/GimmeSomeSlack/northstar/gss_playtest_runner.py

## criteria
- Each finding has a case that failed on base and passes after, or is ruled not-a-bug.

## verify
add a selftest with a fake clock showing total time <= load-wait

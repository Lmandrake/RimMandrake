# ARENA_KILLED_TESTER_FIX_VOIDS_WHOLE_TRIAL

Can change a verdict: YES (one kill means no verdict at all).

`capture_tester` runs in a `finally` (v3_control.py:440, ralph_a_loop.py:1276) that SIGKILL or a WSL crash never reaches. The test_start stays signed with no capture. The next start empties the tester tmp (`arena_replay_run.tester_tmp_done`, "emptied before the task"), so the transcript is destroyed too. `arena_spend.tester_captures` then reports blocking and `spend_doc_problem` refuses the WHOLE spend file.

The spend loss itself is fail-closed and honest; the defect is that nothing recovers it. A single killed tester makes all arms UNMEASURED permanently, and a resume cannot clear it. A WSL crash has already happened on this machine (commit f86a34faf2).

Proof: k3 kill on the real v3 runner, resume fine, then real arena_spend and arena_analysis: rc=3, `spend metering incomplete: arm v3 tester v3-test-a35530e3f5c0 ... no capture`. Evidence: `D:\ClaudeWork\rimmandrake\arena_readiness\logs\an_spend3.txt`, `spend3.json`, `k3_*.txt`. Limit: my stub was held before it wrote a transcript, so transcript recovery itself is not shown; the absence of a capture and the rc=3 are.

Fix direction: at start under runner.lock, capture any orphan tester root BEFORE emptying the tmp, and record a signed void of that tester so the meter can distinguish an accounted loss.

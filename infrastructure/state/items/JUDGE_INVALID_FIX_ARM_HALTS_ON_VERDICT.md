# JUDGE_INVALID_FIX_ARM_HALTS_ON_VERDICT

The replay runner (arena_replay_run.run_arm) raised RunRefused on any invalid judge verdict. v3 stopped at
2026-10-31 19:25 PDT on RP_RIVERSITE_FIX_RETILE_NONE_CRASH because the gpt judge call failed (judge J2c06f79798f9:
opus accept, gpt "exit 1 ... no answer ... WSL UtilAcceptVsock"). That was an infra failure, not the arm's work.
73202b5dc2 fixed only the measured-invalid gate case.

## spec
Implemented at ad865deadb (Conductor brief, per CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM):
- default_judge never raises for a verdict.
- classify_invalid reads the judge's verdict.json and sorts each invalid into one of four classes:
  infra, arm_retry, harness or arm.
- judge_policy:
  - retries infra and arm_retry up to 3 times, with a 120 s then 600 s backoff;
  - an infra or harness invalid that persists parks the task not_completed (unscored, not rerun);
  - an arm or arm_retry invalid emits a signed runner `invalid` event with verdict not_accepted.
- arena_analysis.judge_invalid_of counts that event as completed NOT accepted.
- Decision record: D:\ClaudeWork\rimmandrake\foundry_arena\replay\launcher.log (lines "judgefix:").

## criteria
- A1 L0: offline proof, 3 arms (v3, ralph_a, trio): infra retry then accept; infra x3 parked without a halt; prompt
  leak signed NOT accepted and the next task ran; real gate invalid NOT accepted. ALL_EXPECTED true in
  D:\ClaudeWork\rimmandrake\foundry_arena\judgefix\proof_verify.json. Arena selftests --only 7/7 GREEN.
- A2 L1: after the next coordinated runner start, launcher.log/runner output shows a judge invalid logged as
  "judge try i/n <class>" and the arm continuing (no RunRefused "judge verdict invalid"). Running ralph_a pid 1823450
  keeps its loaded 8ff2858a8c code until then.

# RELENTLESS_RESUME_BUILD_ACCOUNT_LOST_RUNS

## Why
The 2026-11-04 token outage ran from 14:47Z to 20:07Z. The account hit its weekly limit and reset at 20:00Z. Owner, 22:16Z: "You could just poke the agents to continue where they were." Relentless cannot do that today. `account_lost()` (relentless.py) already costs the item no strike, no return and no change of approach. But it requeues the item for a FRESH worker, so whatever context a worker, checker or consult built before the account cut it off is lost. No `--resume` exists anywhere in relentless*.py.

## Spec
- When a worker, checker or diagnostic consult ends on the account's own error (relentless_account.loss) after real usage, record its session id. When the breaker closes, relaunch it through the same unit and slice with `claude -p --resume <session> "Tokens are back; continue where you were."` instead of starting a fresh worker. A run that died with no usage stays a plain requeue, because there is nothing to resume.
- Add a verb to re-run a failed diagnostic consult on an `attribution` hold. Today `unhold` re-validates the same sha, which by its own wait class "can only say it again", and no other verb re-runs the consult.
- Help "no room in N s" while the launch breaker is open on an account error should read as account loss, not as a failed consult. PROOF_HARNESS_BUILD_SAVELOAD_TRIPLET was held at 14:56:24Z inside the window this way. Its wait had started at 14:15Z, so the last 9 minutes were the breaker.

## Evidence
- Relentless store journal.jsonl: 10 jam rows reading "the run ended on the account's own error: rate_limit", from 14:56Z to 19:43Z.
- jam class account_limit was added in df842f2f0f.

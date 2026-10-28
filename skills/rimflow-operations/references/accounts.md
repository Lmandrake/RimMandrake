# Accounts, caps and constraints

Registry (non-secret): `~/.claude-accounts/accounts.tsv` (name, email). Live login: `~/.claude/.credentials.json`;
dormant logins: `~/.claude-accounts/<acct>/`. Each account has two caps, both from `/usage`:
- **Current week (all models)** - the cap that matters; refills at its weekly reset (a fixed clock time per account).
- **Current session** - the 5-hour cap; resets inside hours; seldom binding.
The meter (`account_usage.py`, timer rm-account-usage) polls every account and writes
`/mnt/d/ClaudeWork/rimmandrake/account_usage/{series.jsonl,latest.json}`. A reading whose email does not match the
registry is discarded. Read order: live here, live remote (ssh), vault here (token valid 15+ min), RimPulse (<20 min),
ESTIMATE, UNMEASURED.

Per account (rules in switching_plan.json; verify with `status`, times change weekly):
- `system`, `lukas`: plain; switch-away floor 0%, wait floor 2%.
- `steven`: lent, not ours. Owner 2026-10-27: use up to 50% used, only after a fresh reset. We leave at 52% left
  (card 10:20). "Fresh" = 48 h after his reset (delegated reading); outside it the engine never switches to him and
  switches off him if live. His budget "expires" at the end of that window for ordering purposes. The meter cannot
  tell his use from ours, so all use counts against us. Last 10 min of the window: no switch to him.
`slot_allocator.py plan --account A --draw PCT` checks a draw against a lent rule.

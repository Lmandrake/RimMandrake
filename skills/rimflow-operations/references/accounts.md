# Accounts, caps and constraints

Registry (non-secret): `~/.claude-accounts/accounts.tsv` (name, email). Live login: `~/.claude/.credentials.json`;
dormant logins: `~/.claude-accounts/<acct>/`. Each account has two caps, both from `/usage`:
- **Current week (all models)** - the cap that matters; refills at its weekly reset (a fixed clock time per account).
- **Current session** - the 5-hour cap; resets inside hours; seldom binding.
The meter (`account_usage.py`, timer rm-account-usage) polls every account and writes
`/mnt/d/ClaudeWork/rimmandrake/account_usage/{series.jsonl,latest.json}`. A reading whose email does not match the
registry is discarded. Read order: live here, live remote (ssh), vault here (token valid 15+ min),
ESTIMATE, UNMEASURED.

Per account: the rules are steps of the account plan (`./acct plan` prints each step: use, leave line, window, life).
- The lent account belongs to someone else. Its step carries his leave line and his window after a reset; outside the
  window no step uses it, so the plan never switches to it and leaves it when its live runs end. The meter cannot tell
  his use from ours, so all use counts against us.
`slot_allocator.py plan --account A --draw PCT` checks a draw against the lent rule of `slot_rules.json`.

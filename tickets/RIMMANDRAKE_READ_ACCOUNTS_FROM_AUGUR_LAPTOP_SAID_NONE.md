---
id: RIMMANDRAKE_READ_ACCOUNTS_FROM_AUGUR_LAPTOP_SAID_NONE
title: account_usage.py reads no accounts on the Laptop while Augur holds them
project: rimmaster
type: bug
status: open
owner: lukas
created: 2026-11-24T16:59:44-08:00
updated: 2026-11-24T16:59:44-08:00
source: manual
check: "{\"reason\":\"bug ticket: no mechanical outcome check given\",\"review_by\":\"2026-12-08\",\"type\":\"gap\"}"
---

On the Laptop (2026-11-24 16:51 PST), `python3 ~/dev/RimMandrake/src/RimMandrake/Utils/account_usage.py now` printed 'no account could be read / no reading yet (account_usage.py poll)', while Augur's snapshot (~/ClaudeWork/augur/live/snapshot.json, fleet.accounts, via archmagi) held MEASURED readings for lukas, steven and system from 4:50 PM. The global CLAUDE.md names account_usage.py as the route, so an agent following it reports UNMEASURED for accounts that are measured. Fix: fall back to Augur fleet.accounts (respecting valid_until) when there is no local poll, or have CLAUDE.md name Augur. Acceptance test: none yet, needs a fixture snapshot; not watched failing.

## Log
- 2026-11-24T16:59 mt-400028/ticket: new (manual)

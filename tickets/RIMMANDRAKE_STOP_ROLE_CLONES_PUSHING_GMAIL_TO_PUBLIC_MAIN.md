---
id: RIMMANDRAKE_STOP_ROLE_CLONES_PUSHING_GMAIL_TO_PUBLIC_MAIN
title: Gmail-authored commits still land on PUBLIC RimMandrake main
project: rimmaster
type: bug
status: open
owner: lukas
created: 2026-11-24T19:53:11-08:00
updated: 2026-11-24T19:53:11-08:00
source: agent
check: "{\"reason\":\"bug ticket: no mechanical outcome check given\",\"review_by\":\"2026-12-08\",\"type\":\"gap\"}"
---

identity_check.py 2026-11-24: github.com/Lmandrake/RimMandrake is PUBLIC and holds 16,501 commits authored with the owner's personal Gmail address (2026-09-01..2026-11-24), and 44 of the last 400 on main, e.g. a84c8399f0 'ledger: DISPATCHER notes (1)' at 19:50 PST today. The Laptop checkout has the repo-local noreply; the committer is a clone outside it (subjects name 'role clone Operations'; likely the bench role clones, unverified). Needs: the noreply set repo-local in every role clone/bench clone that pushes here, and an owner decision on rewriting public history (no force-push done). Acceptance test: none, the fix spans machines; recheck: identity_check.py shows no Gmail commit on RimMandrake newer than the fix date.

## Log
- 2026-11-24T19:53 mt-400028/ticket: new (agent)

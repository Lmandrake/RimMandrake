---
id: RIMFLOW_SAID_FLAGS_RETIRE_GATE
title: Remove the owner-word (said) requirement from rimflow and ./game
project: rimmaster
type: build
status: proposed
owner: lukas
created: 2026-10-31T12:50:17-07:00
updated: 2026-10-31T12:50:17-07:00
requested_by: project:lodestar
source: need:lodestar
check: "{\"reason\":\"build ticket: no mechanical outcome check given\",\"review_by\":\"2026-11-14\",\"type\":\"gap\"}"
---

Owner ruling 2026-10-31 (Lodestar docs/DECISIONS.md D31), verbatim: "I would also like you to remove the whole 'said' restriction. I have found zero evidence that any agent has impersonated me or attempted odd behavior in this way. Making everything constantly check on whether the Owner said this seems pedantic at best and dangerously burdensome beyond that." Lodestar made every --said flag optional provenance. In RimMandrake: rimflow --owner-said / --by-card / --per-ruling should become optional (still recorded when given), ./game --said likewise, and hooks that refuse without owner words (.claude/hooks/block_forged_validation.py, warn_close_live_proof_owed.py, selftest_documented_commands.py, others matching owner.said or by.card) need review. Keep anything that is real authentication or protects the act itself.

## Log
- 2026-10-31T12:50 mt-400028/ticket: new (need:lodestar)

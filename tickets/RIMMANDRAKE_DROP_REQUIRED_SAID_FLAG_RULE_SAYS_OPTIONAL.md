---
id: RIMMANDRAKE_DROP_REQUIRED_SAID_FLAG_RULE_SAYS_OPTIONAL
title: title Two tools still require --said though the rule says no tool needs his words
project: rimmaster
type: bug
status: open
owner: lukas
created: 2026-11-24T17:00:27-08:00
updated: 2026-11-24T17:00:27-08:00
source: manual
check: "{\"reason\":\"bug ticket: no mechanical outcome check given\",\"review_by\":\"2026-12-08\",\"type\":\"gap\"}"
---

The global rule (20-no-pasting, "no tool needs his words", 2026-10-31) says a --said flag is optional provenance, never demanded. Two tools still demand it: `~/dev/RimMandrake/src/RimMandrake/rimflow/mod_owner_hold.py` lines 409 and 413 (`--said`, required=True), and `~/dev/Lodestar/bin/lode25_collect.py` line 262 (`--said`, required=True) [measured 2026-11-24 17:00 PST]. Found by the crystallize repair end-to-end on section 20. Acceptance test: `grep -n "\"--said\", required=True" ~/dev/RimMandrake/src/RimMandrake/rimflow/mod_owner_hold.py ~/dev/Lodestar/bin/lode25_collect.py` prints nothing (fails now: 3 lines), and each tool runs with --said omitted.

## Log
- 2026-11-24T17:00 mt-400028/ticket: new (manual)

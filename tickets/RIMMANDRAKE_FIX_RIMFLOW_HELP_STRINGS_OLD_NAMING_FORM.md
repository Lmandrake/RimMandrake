---
id: RIMMANDRAKE_FIX_RIMFLOW_HELP_STRINGS_OLD_NAMING_FORM
title: RimMandrake rimflow help strings still state the retired naming rule
project: rimmaster
type: bug
status: open
owner: lukas
created: 2026-11-25T11:00:27-08:00
updated: 2026-11-25T11:00:27-08:00
source: manual
check: "{\"reason\":\"bug ticket: no mechanical outcome check given\",\"review_by\":\"2026-12-09\",\"type\":\"gap\"}"
---

rimflow still restates the retired naming rule. Fix: src/RimMandrake/rimflow/cli.py ~lines 5052 and 5207 say SUBJECT_INTENT_TWIST (must be RIMMANDRAKE_VERB_INTENTION_TWIST / PROJECT_VERB_INTENTION_TWIST); src/RimMandrake/rimflow/incident.py ~line 535 says "at most 44 characters" (rule is <= 64). Acceptance test: from ~/dev/RimMandrake run `grep -nE "SUBJECT_INTENT_TWIST|at most 44 char" src/RimMandrake/rimflow/cli.py src/RimMandrake/rimflow/incident.py`; it prints 3 lines now (fails the "no match" expectation) and must print nothing (exit 1) after the fix. Also check incident.py code enforces 64 not 44 if it enforces a length.

## Log
- 2026-11-25T11:00 mt-400028/ticket: new (manual)

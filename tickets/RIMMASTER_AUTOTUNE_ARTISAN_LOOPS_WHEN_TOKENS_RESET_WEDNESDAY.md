---
id: RIMMASTER_AUTOTUNE_ARTISAN_LOOPS_WHEN_TOKENS_RESET_WEDNESDAY
title: "Wednesday (tokens reset): autotune the Artisan loop on RimMandrake work"
project: rimmaster
type: build
status: open
owner: lukas
created: 2026-11-08T20:26:23-08:00
updated: 2026-11-08T20:26:23-08:00
due: 2026-11-11
act_by: 2026-11-11
source: manual
check: "{\"reason\":\"experiment not yet run; closes on a tuned-vs-untuned result\",\"review_by\":\"2026-11-22\",\"type\":\"gap\"}"
---

Owner 2026-11-08: specifically for Wednesday 2026-11-11 when tokens reset, and for Artisan optimization. First live self-tuning testbed: tune the Artisan loop (skill ~/dev/MandrakeWorkflows/skills/artisan, run on RimMandrake mods). Pick one Artisan knob (effort level, token review point, a PROMPT.md section, pass budget), the measurement that judges it, and run tuned vs untuned passes on the fresh weekly budget. Follow the provenance rules in design/RimMandrake/testing_policy_2026-10-28.md (the tuner moves only D/A values, writes provenance A). Related: PILLAR-dev #107 (self-tuning harness).

## Log
- 2026-11-08T20:26 mt-400028/ticket: new (manual)

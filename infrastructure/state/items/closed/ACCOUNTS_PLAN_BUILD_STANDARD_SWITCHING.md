# ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING

## Spec
Owner 2026-10-28 10:15 PDT: "Use up both lukas.mandrake and mandrake.system of course down to ~2% for safety. Make sure
not to overshoot and get stuck even if there is a surprise long-running subagent. then go idle until 1pm when you switch
over to system.mandrake. Once steven.lewis resets, switch over to it and use it until 50%. Then use up system.mandrake to
2%, then lukas.mandrake to 2%. That's our first "standard switching plan." ... capture this plan as a new rimflow
operations skill ..."
Card 10:20: floor [No preference] -> delegated (1% on an account switched away from at once, 2% on one waited on until a
reset); overshoot "Soft line, then hard stop"; pacing "Pace the whole pool"; Steven "Leave at 52% left".

Build:
1. `src/RimMandrake/Utils/switching_plan.json` (rules as data, provenance per rule) + `switching_plan.py` engine
   (check/status/install; no LLM; durable user timer `account-plan.timer`, outside the rm-*/testq-* glob). Replaces
   account_failover.py's hard-coded dates; passive until account_failover's stage 3 marker reads done.
2. Pool pacing in slot_allocator.py (pool = what the plan still spends; paced to each phase deadline).
3. Stand-down/stand-up cost review, in the skill.
4. Skill `skills/rimflow-operations/` (accounts: levels, constraints, plan, guards, pacing, costs, traps).

## Verify
- selftest_switching_plan.py and selftest_slot_allocator.py green (red-first commits).
- `switching_plan.py check --dry-run` on live meter names the phase and a no-op while account_failover is unfinished.
- After 13:00 stage 3 done: timer installed and passing; rm-account-failover.timer stopped; the 14:45ish steven
  reset produces exactly one logged switch to steven (journal/log under /mnt/d/ClaudeWork/rimmandrake/switching_plan/).

## Notes
Progress: /mnt/d/ClaudeWork/rimmandrake/switching_plan/PROGRESS.md

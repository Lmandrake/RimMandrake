# AGENT_IMPROVE_BUILD_JUDGED_DAILY_DIFFS

The owner, 2026-11-01: "Every day we should ask if each agent can be improved based on our evidence. That's the beauty
of making them agents. Same with reusable skills not agent specific."

Design: design/RimMandrake/daily_agent_improvement_2026-11-02.md (transfer audit counts in its section 1).

## built (BENCH, 2026-11-02)
- Step 0 gather: src/RimMandrake/Utils/agent_improve.py, selftest_agent_improve.py (mutation-proven), paused
  `measure` row `agent_improve` in dispatcher_schedule.json (no unit installed).
- It is also the harvest of Relentless learned.md (107 files) and reject reasons, which nothing read before.

## owed
1. Step 1 Curator prompt (fresh claude -p, one diff <= ~15 lines per signalled target, pointer not paste, a recheck each;
   never rulings, gates, caps, schedule, CLAUDE.md or global skills: those are proposal lines).
2. Step 2 Judge (a different fresh agent, delegation_policy.md section 4): verdict JSON to infrastructure/state/delegated/<day>/.
3. Step 3 apply program: KEEP only, git apply --check, skills/validate_skills.py, the target's selftests, commit body
   `Delegated: technical — agent improvement <target>`, land.sh.
4. Next-day recheck of yesterday's applied diffs; systemd unit rm-agent-improve.{service,timer}.
5. One hand-run day whose packet a human reads; then the owner enables the timer.

## verify
- selftest_agent_improve GREEN; a dry gather of 2026-11-01 gives <= 6 targets, agents first, <= 25 pieces each.
- After step 3: one day's applied diff appears in Transient/delegated_digest_<day>.md.

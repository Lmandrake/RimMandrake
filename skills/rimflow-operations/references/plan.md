# The engine in more detail

Source: `src/RimMandrake/Utils/switching_plan.py` (+ `.json`, selftest_switching_plan.py, `slot_allocator.py` pool()).
Item: ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING. Build log: `D:\ClaudeWork\rimmandrake\switching_plan\PROGRESS.md`; 15 GPT
review rounds in `...\review\gpt_review*.md`.

Owner's words 2026-10-28 10:15 PDT: "Use up both lukas.mandrake and mandrake.system of course down to ~2% for safety.
Make sure not to overshoot and get stuck even if there is a surprise long-running subagent. then go idle until 1pm when
you switch over to system.mandrake. Once steven.lewis resets, switch over to it and use it until 50%. Then use up
system.mandrake to 2%, then lukas.mandrake to 2%. That's our first 'standard switching plan.'"
The fixed order was superseded 10:58 by soonest-expiry (relayed by coordinator, not owner verbatim).

Per pass: target = soonest-expiring account that is MEASURED, fresh (<6 min, polled if within 3% of a line), in window,
above its line. target != live: arm, use, disarm (marker per transition and target-week). target == live: normal, or SOFT
at line+2 or when an earlier account's reset is within 20 min. No target: one hard fleet-stop per account-week;
fleet-start when a reset gives headroom. Under-line accounts are no target until their reset (anti-flap). Stale pending
marker after 2400 s = a dead pass. Output dir files: markers/, notice.json (readers ignore it after 20 min), HOLD.
Commands: `switching_plan.py check [--dry-run] | status | install`. Unit timeout 2700 s.

Cutover: account_failover.py (one-off, 2026-10-28; stages system->lukas, lukas burn, back to system after 13:00 reset)
owned the machine; the plan stays passive until its `switched_back.json` says done, then retire
rm-account-failover.timer (ACCOUNT_FAILOVER_RETIRE_AFTER_DEADLINE).

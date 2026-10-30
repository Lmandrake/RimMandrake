# The engine in more detail

Source: `src/RimMandrake/Utils/switching_plan.py` (+ `.json`, selftest_switching_plan.py, `slot_allocator.py` pool()).
Item: ACCOUNTS_PLAN_BUILD_STANDARD_SWITCHING. Build logs: `D:\ClaudeWork\rimmandrake\switching_plan\PROGRESS.md` and
`FIX2_PROGRESS.md`; GPT review rounds in `...\review\gpt_review*.md` (15) and `...\gpt_review.txt` (final round).

Owner's words 2026-10-28 10:15 PDT: "Use up both lukas.mandrake and mandrake.system of course down to ~2% for safety.
Make sure not to overshoot and get stuck even if there is a surprise long-running subagent. then go idle until 1pm when
you switch over to system.mandrake. Once steven.lewis resets, switch over to it and use it until 50%. Then use up
system.mandrake to 2%, then lukas.mandrake to 2%. That's our first 'standard switching plan.'"
A 10:58 relayed rule (soonest-expiry first) briefly replaced the fixed order; the owner's 15:20 review restored his
fixed priority, which is what `order` in the JSON now means.

Per pass: target = the first account in plan `order` that is MEASURED, fresh (<6 min, polled if within 3% of a line), in window,
above its line. target != live: arm, use, disarm (marker per transition and target-week). target == live: normal, or SOFT
at line+2 or within 20 min of a reset that will cause a switch. No target: one hard fleet-stop per account-week;
fleet-start when a reset gives headroom. Under-line accounts are no target until their reset (anti-flap). Stale pending
marker after 2400 s = a dead pass. Output dir files: markers/, notice.json (readers ignore it after 20 min), HOLD.
Commands: `switching_plan.py check [--dry-run] | status | install`. Unit timeout 2700 s.

Pool pacing (`pool()`, read by slot_allocator): each account's budget down to its line is due at its expiry (next
reset; steven's at his window end); a lower account's budget is kept only if, at the pace without it, the higher
accounts finish first; a kept one pulls the higher budgets forward to its expiry.

History: account_failover.py (one-off, 2026-10-28) owned the machine first; it is retired
(ACCOUNT_FAILOVER_RETIRE_AFTER_DEADLINE done) and the engine no longer gates on it. HOLD is the only brake.

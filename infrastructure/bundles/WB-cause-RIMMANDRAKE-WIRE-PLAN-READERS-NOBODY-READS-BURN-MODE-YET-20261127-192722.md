# Work bundle WB-cause-RIMMANDRAKE-WIRE-PLAN-READERS-NOBODY-READS-BURN-MODE-YET-20261127-192722

State: done (one member, one group).

| member | outcome | commit | live reading |
|---|---|---|---|
| RIMMANDRAKE_SPLIT_ACTUATOR_OUT_SO_OLD_ENGINE_CAN_GO_AFTER_FIRST_REAL_SWITCH | closed | d82260b948e6 (split + deletion, one commit); polish bd60a39818c6, 2a8c5a3b6eea | Archmagi deploy has account_actuator.py and no switching_plan.py since 12:56 PST 2026-11-27; passes 13:00 to 13:20 PST finished, do normal, no fallback, no error in the journal |

Found and fixed in the run: an unread live level inside the warning zone refused starts but warned no run (account_plan.decide);
selftest_lease's peek probe red in every publish tree check (535e346de5db).
Not tested live: a real switch through account_actuator.py (the next one is the plan's; offline: selftest_account_plan, _end,
_actuator_drain, the sweep, 118 + 50 planted faults caught).

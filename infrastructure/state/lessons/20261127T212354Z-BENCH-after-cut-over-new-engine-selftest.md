After a cut-over to a new engine, a selftest that still drives the old engine stays green and proves nothing about the live one. selftest_account_end tested switching_plan.decide for three days after ./acct driver new; ported onto account_plan.decide it went red at once: an unread live level inside the warning zone refused new starts but sent the live runs no warning. Port the tests at the cut-over, not at the deletion.
item: RIMMANDRAKE_SPLIT_ACTUATOR_OUT_SO_OLD_ENGINE_CAN_GO_AFTER_FIRST_REAL_SWITCH
home: design/specs/2026-11-24-account-plan-one-file/boundary.md

A selftest that calls left_open_continue.run (or anything that reaches detached_helper.drain_refusal) must pass plan_dir to a test folder. Without it, the test reads the live account notice and goes red whenever an account drains (seen 2026-11-26: selftest_item_packet and selftest_cap_stop_resume_blind, PRE-EXISTING red at ./publish).
item: RIMMANDRAKE_REMOVE_VISIT_BRIEF_HOUR_BOUND_FOOTER_SAYS_NONE
home: skills/using-rimflow

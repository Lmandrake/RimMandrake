A selftest that calls maturation_dispatch.tick must set RM_MATURATION_DISPATCH_DIR to a temp dir. Without it the tick reads the live state.json, and a real builder watch turns the test red for a reason that is not in the code (selftest_mod_model_pin, 2026-11-27).
item: RIMMANDRAKE_LET_CLEAR_PASS_CHAIN_STOP_THREE_CLEARS_NO_LAUNCH
home: NONE

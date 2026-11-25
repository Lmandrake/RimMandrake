The maturation tick's folder (RM_MATURATION_DISPATCH_DIR) must hold files only: selftest_one_live_run_per_mod.py resets it with os.remove on every entry, so an observer that keeps its state in a subfolder turns 6 of its 7 checks red (IsADirectoryError). Keep a tick observer's state as a flat file beside reading.json.
item: RIMMANDRAKE_PEEK_AT_LIVE_MOD_RUNS_HE_SAID_IT_IS_THE_CONDUCTORS_JOB
home: NONE

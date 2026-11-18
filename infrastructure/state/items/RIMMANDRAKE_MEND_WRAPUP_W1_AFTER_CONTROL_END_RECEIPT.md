# RIMMANDRAKE_MEND_WRAPUP_W1_AFTER_CONTROL_END_RECEIPT

## spec
`selftest_wrapup.py` check "W1 detached_helper: finish, the wrap-up and the clone return all run at stop" is red on
origin/main 93f3e5687e (measured 2026-11-18 13:35 PST in a throwaway clone; also red on 8fadb63af7). It asserts
`len(post3) == 3` ExecStopPost entries in `detached_helper.launch_argv`; the control builder's 1cf299d075 ("every
systemd-run launch site goes through launch_unit ... end receipt") changed that shape. Either the test is out of date
(the end receipt is added by control.launch_unit, not launch_argv) or a stop step was lost: read 1cf299d075 and decide
which, keeping the finish / wrap-up / return promise. Found by the RIMMANDRAKE_MOVE_SEAT_CLONE_WRITERS_INTO_OWN_POOL_CLONES
lane (not caused by it: red with its paths absent).

## verify
Acceptance test: `python3 src/RimMandrake/rimflow/selftest_wrapup.py` exits 0 (FAIL 0). Watched failing on base
93f3e5687e: FAIL 1 (W1 detached_helper).

## criteria
- selftest_wrapup.py is green, and a detached run still runs finish, the wrap-up and the clone return at stop.

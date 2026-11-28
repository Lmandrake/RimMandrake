A selftest that races a fixed mock run time (MOCK_SLEEP=4 s) against how long a real tick takes goes red on a correct build when the machine is loaded (2 of 3 runs at load average 15, selftest_testq_steve2 both-busy). Hold the mock job open with a release file that the test lets go after its readings, not a sleep.
item: RIMMANDRAKE_READ_FIX_CE3DADED9B_WITH_FRESH_EYES

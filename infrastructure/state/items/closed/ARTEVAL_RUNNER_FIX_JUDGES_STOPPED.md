# ARTEVAL_RUNNER_FIX_JUDGES_STOPPED

round_series.resets() says a stopped series is over: "nothing is filed, judged or installed for it until a new reset".
fauna_drive enforces this for `rows`, `candidates` and `install`. runner.run (src/RimMandrake/Utils/art_eval/runner.py
about line 346) does not. A spec for a stopped def given to runner.run is judged anyway: a REGEN verdict writes
regen_jobs.json and raises the subject's count in regen_rounds.json. Only `rows` filters that job out later.

Harm: low. Nothing is installed, but model calls are spent and the decision logs grow. regen_counts after the stop
counts those REGENs, so a later reset's series starts from the right place only because a reset re-dates the count.

Failing-test sketch (selftest_round_series or selftest_art_eval): write a resets file with a reset and then a stop for
D, give runner.run([spec D], test=False with STATE redirected) a REGEN reviewer, and assert that no decisions.jsonl
line exists for D and that the run prints "series STOPPED".
Found by review of 3a69bd5110/3a0e1161a7 (FOUNDRY 2026-10-24).

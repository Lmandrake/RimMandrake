## spec
The void rule (run_void.py, item RIMMANDRAKE_VOID_SYSTEM_KILLED_RUNS_NO_TRIAL_SPENT; the owner 2026-11-18: "I will not accept ANY system that pointlessly expends such statistical measurements based on failed system calls or behavior") reaches the dispatch books and a hand void reaches stage.json; these counters are not yet reached (census: design/RimMandrake/pipeline_trial_counters_census_2026-11-18.md, "UNBUILT"):
- an errored coverage-judge round (error set, no verdict: a timeout, a dead call) counts toward JUDGE_RUNS_MAX and JUDGE_SPEND_MAX: class it void_system in coverage_judge.rounds, counted apart;
- a Designer stage run rejected for "no result.json" after a kill counts as a retry/rejection: class it void_system;
- refusal_contract counts a dead judge call's malformed verdict;
- the Designer chain count (Dispatcher state roles.<Designer>.chain_day) has no unit, so a void cannot reach it;
- a certificate rerun (zero-token unit, no detached record) is reached only by a hand void;
- a Test Pilot verify recorded fail because of a harness fault has no void.
## verify
Acceptance test (watched failing on f93b15709a: prints "stop_reason: 4 judge runs (limit 4)", exit 1; expected exit 0 on a fix, 1 check):
python3 -c "import sys; sys.path.insert(0,'src/RimMandrake/rimflow'); import coverage_judge as CJ; st={'coverage_rounds':[{'judge':'rm-coverage-judge-%d'%n,'verdict':None,'error':'TimeoutExpired: judge call timed out','at':'2026-11-18T00:0%d:00Z'%n,'tokens':0} for n in range(4)]}; r=CJ.stop_reason(st); print('stop_reason:', r); sys.exit(0 if r is None else 1)"
The other parts each get a check in selftest_run_void.py, watched failing first.
## criteria
Each counter above either ignores a void_system run or names why it cannot, in the census doc.
## refs
file: src/RimMandrake/rimflow/coverage_judge.py
file: src/RimMandrake/rimflow/run_void.py
file: src/RimMandrake/rimflow/designer_stage.py
file: src/RimMandrake/rimflow/refusal_contract.py

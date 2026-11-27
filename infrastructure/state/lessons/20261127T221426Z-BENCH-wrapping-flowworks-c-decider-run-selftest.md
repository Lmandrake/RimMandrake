Wrapping a FlowWorks C# decider run (selftest_flowworks_stock.py, 4-15 min a suite) in 'timeout 540' kills it on a slow tree-check queue or a cold build; a killed red-seen also left its planted fault in the tree before 79815237e7. Run any FlowWorks suite, red-seen, ./publish or land.sh through waitalive.py run, not a bare timeout.
item: RIMMANDRAKE_JUDGE_FLOWWORKS_BLIND_CYCLE_FIVE_TESTS_FIRST
home: infrastructure/state/facts/tool_traps.md

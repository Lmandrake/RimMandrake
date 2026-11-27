time_budget_lint.py and could_not_look_lint.py run green in a clone while ./publish's tree check of the same change runs red: measured 3 times on 2026-11-26; the cause is a guess (~70%): run alone, they do not read a new untracked file. Run them after git add, or expect the publish to name the new budget; give every new timeout a # budget: block (danger=, longest=) or use time_budget.CALL_S before the first publish.
item: RIMMANDRAKE_BUILD_STUCK_STOP_REPAIRS_HE_RULED_SIX
home: infrastructure/state/facts/tool_traps.md

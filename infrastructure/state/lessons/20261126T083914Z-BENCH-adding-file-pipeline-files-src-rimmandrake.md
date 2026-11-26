Adding a file to pipeline_files in src/RimMandrake/Utils/pipeline_tests.json makes ./publish run the whole-tree lints (selftest_time_budget_lint.py, could_not_look_lint.py) over ALL of that file's old code, not only your lines. Run both lints yourself before the first ./publish: on ticket_preflight.py they found 5 old timeouts with no danger named and 2 could-not-look places, three publish rounds of 8 minutes each.
item: RIMMANDRAKE_PREFLIGHT_TICKETS_BEFORE_ANY_TOKEN_IS_SPENT
home: skills/clone-landing-commits

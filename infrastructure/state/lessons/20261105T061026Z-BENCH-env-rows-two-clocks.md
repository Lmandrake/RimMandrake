Relentless game lane: a runs.jsonl row's 'at' is its own clock, the lane's staged_at/now is the supervisor clock (fake in selftests, can differ live). Comparing a row time to a lane time to mean 'read after the fix' routes stale rows; compare a row to the row the fix was made on (env_tried keeps [lane time, row time]).
home: src/RimMandrake/rimflow/relentless_game.py _env

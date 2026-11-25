Grepping ~/.claude/projects transcripts: the JSONL is compact (no space after the colon), so a pattern like '"ephemeral_1h_input_tokens": [1-9]' matches nothing, and the glob */*.jsonl fails because the folder names start with '-'. Both returned a confident 0. Use '": ?[1-9]' and ./*/*.jsonl, and check the count on one known file first.
item: RIMMANDRAKE_STUDY_SLEEP_AND_RESUME_AGAINST_FRESH_RUN_COLD_COST
home: infrastructure/state/facts/instrument_traps.md

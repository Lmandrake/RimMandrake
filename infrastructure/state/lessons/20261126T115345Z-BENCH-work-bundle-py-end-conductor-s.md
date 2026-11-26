work_bundle.py end is the Conductor's end of a bundle whose run died; a worker never calls it. It writes state=ended (ended_by_hand) BEFORE it tells the Conductor log, so on SteveDesktop (no /mnt/d/ClaudeWork/rimmandrake/conductor/log.md) it crashes after the write and a retry overwrites the record's 'was'. A worker ends by its run exiting with every member's outcome in the ledger.
item: RIMMASTER_TEACH_FLYER_JUDGE_PARTS_SHEET_STILLS_MISSED_IT
home: src/RimMandrake/rimflow/roles/builder.md

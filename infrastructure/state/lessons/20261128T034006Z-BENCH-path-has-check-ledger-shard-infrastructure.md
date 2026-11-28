A path-has check on a ledger shard (infrastructure/state/ledger/events/<SEAT>.jsonl) is fooled by its own shape event: cli.py shape writes the check text into that same shard, so the check holds the moment the item is shaped, with no note written. Check a note or class record by a cmd: that replays the ledger and reads the item's notes, never by path-has on the shard.
item: RIMMANDRAKE_CLASS_DOUBTFUL_FACTION_TICKETS_WORKER_LEFT_ABOUT_TWENTY
home: skills/using-rimflow

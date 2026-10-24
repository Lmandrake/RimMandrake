./publish -F <msgfile> with the ledger shard BENCH.jsonl as a path is refused by the PreToolUse ledger-write hook ('being written by something that is not rimflow'), even with no redirect; the same commit with -m passes. Commit ledger shards with ./publish -m.
home: NONE

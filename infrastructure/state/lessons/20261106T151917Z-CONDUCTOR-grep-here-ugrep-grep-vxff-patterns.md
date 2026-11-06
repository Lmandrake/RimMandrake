grep here is ugrep: 'grep -vxFf patterns big_file' on a large ledger shard (8 MB pattern set) fails with 'exceeds complexity limits' on stderr and prints a count of 0, which reads as 'all lines present'. For line-membership checks against a big file use a Python set, never grep -Ff.
home: infrastructure/state/facts/instrument_traps.md

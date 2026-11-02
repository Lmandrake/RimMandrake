rimflow append() does not check the shard ends in a newline, so a write torn at the tail gets the NEXT good event glued onto the same physical line. A repair that deletes every unparseable line deletes that good event too; repair_torn_ledger.py now keeps a trailing complete event (keys event/seat/ts) and drops only the fragment (wave 81).
home: skills/using-rimflow

Verse LogMessageQueue holds 1000 entries and stops incrementing a repeated message's count at 99, dropping further repeats silently; a log check bounded by messageCount delta must treat a message at repeat 99 and any buffer rollover/Log.Clear (count drops) as BLIND, not clean (src/RimMandrake/bridgetools/deepfire_log_check.py).
home: live-debugging-proof-harness

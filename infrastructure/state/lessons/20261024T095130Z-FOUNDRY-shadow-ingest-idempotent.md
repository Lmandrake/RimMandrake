Any ingest that appends to a log a streak is counted from must be idempotent: shadow.py ingest re-run on the same decisions file used to append duplicate rows, inflating consecutive_clean toward eligible_to_turn_off and re-filing criteria-ledger entries/reverts. Key on (run, subject, answer, note) (cb6c332768).
home: rimworld-art-evaluation

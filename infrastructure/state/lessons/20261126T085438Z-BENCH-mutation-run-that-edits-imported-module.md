A mutation run that edits an IMPORTED module and restores it can read a stale .pyc: Python checks a pyc by source mtime (whole seconds) and size, so a same-length mutant written in the same second as the restore runs on after the restore and makes the real code read FAIL (or a mutant read PASS). Run each mutant and the final real run with python3 -B (or delete __pycache__) when the selftest imports the mutated file.
item: RIMMANDRAKE_LABEL_CHANGED_SINCE_LAST_LOOK_IN_REVIEW_SAVES
home: skills/mutate-your-checker

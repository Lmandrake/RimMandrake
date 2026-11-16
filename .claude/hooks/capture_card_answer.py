#!/usr/bin/env python3
"""PostToolUse/AskUserQuestion hook - store every answered card WHOLE (RIMMANDRAKE_RECORD_CARD_OPTION_TEXT_LABEL_LOST_THE_ART).

Every question, every option's label and description, what he picked or typed, into the host's card store, so a
`rimflow … --by-card` stamps the full text on the ledger without anyone retyping it. Never blocks; prints nothing.
Logic and store: src/RimMandrake/rimflow/card_capture.py; test: src/RimMandrake/rimflow/selftest_card_capture.py.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src", "RimMandrake", "rimflow"))
try:
    import card_capture
except Exception as e:  # noqa: BLE001
    sys.stderr.write("capture_card_answer: %s\n" % e)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(card_capture.hook_main())

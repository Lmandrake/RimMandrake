#!/usr/bin/env python3
"""selftest: the blind judge's brief states the same exit the reader enforces
(item RIMMANDRAKE_ALIGN_BLIND_BRIEF_EXIT_WITH_JUDGE_OWED_READER).

The reader (blind exit, RIMMANDRAKE_SEND_FIXES_TO_NEW_BLIND_JUDGE) never passes a cycle whose own Problems were FIXED:
"send it back to just before Stage 4 again for a new blind judgement pass". ExplosiveKnockback cycle 3's judge followed
the brief's older text ("A Problem FIXED red-first is closed") and wrote exit_met true against that reader.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)

import maturation as M  # noqa: E402

fails = []
got = M.blind_brief_text(ROOT, "ExplosiveKnockback")
text = got[0] if isinstance(got, tuple) else got
exit_part = text[text.find("## The exit, and who reads it"):]
if "## The exit, and who reads it" not in text:
    fails.append("blind brief has no exit section")
if "A Problem FIXED red-first is closed." in exit_part:
    fails.append("blind brief still says a FIXED Problem closes the exit")
if "new blind judge is owed" not in exit_part:
    fails.append("blind brief does not say a cycle's own fixes owe a new blind judge")
if "exit_met: false" not in exit_part:
    fails.append("blind brief does not tell the judge to write exit_met: false when it fixed a Problem")

if fails:
    print("FAIL selftest_blind_brief_exit_owed: %d" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("PASS selftest_blind_brief_exit_owed")

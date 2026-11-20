#!/usr/bin/env python3
"""selftest: the blind judge's brief states the same exit the reader enforces
(item RIMMANDRAKE_ALIGN_BLIND_BRIEF_EXIT_WITH_JUDGE_OWED_READER).

Since the owner's ruling of 2026-11-20 ("I agree with your blind judge -> fresh reader argument."; item
RIMMANDRAKE_RESUME_WRONG_CHECK_WORKER_WITH_MOD_FIX_EXTENSION), a cycle whose judge fixed the mod owes ONE fresh reader
of each fix, never a whole new blind cycle; the judge writes exit_met true and the reader (read_exit, review_sound)
waits for that review. ExplosiveKnockback cycle 3 showed what a brief that disagrees with its reader costs.
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
if "new blind judge is owed" in exit_part:
    fails.append("blind brief still says a cycle's own fixes owe a new blind judge")
if "one fresh reader" not in exit_part:
    fails.append("blind brief does not say a mod fix owes one fresh reader")
if "exit_met: true when that holds, also when you fixed the mod" not in " ".join(exit_part.split()):
    fails.append("blind brief does not tell the judge to write exit_met: true when it fixed the mod")

if fails:
    print("FAIL selftest_blind_brief_exit_owed: %d" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("PASS selftest_blind_brief_exit_owed")

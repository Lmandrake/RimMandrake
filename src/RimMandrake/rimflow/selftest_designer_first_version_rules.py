#!/usr/bin/env python3
"""Selftest: the owner's cleanse card answers reach every Designer stage packet, word for word.

Item RIMMANDRAKE_TEACH_DESIGNER_CLEANSE_RULES_BRIEF_ONLY_KNEW. His card answers (2026-11-17T06:24:09Z, 10:24 PM
PST 2026-11-16; on RIMMANDRAKE_UPGRADE_DESIGNER_CLEANSE_SIXTY_FOUR_BARS_LOCKED) were written only into
roles/designer_cleanse.md, which no stage of roles/designer_manifest.json injects, so an ordinary Designer run never
read the first-version scope rule. The packet a stage injects is the manifest's file list, read in order
(designer_stage.packet); this test reads the same list.

  python3 src/RimMandrake/rimflow/selftest_designer_first_version_rules.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import designer_stage as DS  # noqa: E402

ROLES = os.path.join(HERE, "roles")
CLEANSE = os.path.join(ROLES, "designer_cleanse.md")
CORE = os.path.join(ROLES, "designer.md")
FIRST = "## What a first version may contain"
FATE = "## The fate of an extra"
AFTER = "## What a bar is"
# his card answer of 2026-11-23 on what gates a cleansed design, picked label as the card store holds it
CHECK_LABEL = "All three, as today"

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  -- %s" % (detail,)))
    if not ok:
        FAILS.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def cleanse_block(text):
    """The two sections of designer_cleanse.md that carry his first two answers, from FIRST up to AFTER, stripped of
    surrounding blank lines. None = a heading is missing (the source moved; the test cannot say what to compare)."""
    a, b = text.find(FIRST), text.find(AFTER)
    if a < 0 or b < 0 or text.find(FATE, a) < 0 or not a < text.find(FATE, a) < b:
        return None
    return text[a:b].strip()


def stage_packet(stage):
    """The text of every file the manifest injects at `stage`, joined as designer_stage.packet joins them."""
    names = DS.load_manifest()["stage_%d" % stage]
    return "\n".join(read(os.path.join(ROLES, n)) for n in names)


def test_cleanse_block_found():
    check("test_cleanse_block_found: designer_cleanse.md still holds both sections, in order",
          cleanse_block(read(CLEANSE)) is not None)


def test_every_stage_packet_carries_the_first_two_answers():
    block = cleanse_block(read(CLEANSE))
    for s in DS.STAGES:
        check("test_every_stage_packet_carries_the_first_two_answers: stage %d" % s,
              block is not None and block in stage_packet(s), "the verbatim block is absent from the packet")


def test_every_stage_packet_carries_all_three_checks():
    for s in DS.STAGES:
        p = stage_packet(s)
        check("test_every_stage_packet_carries_all_three_checks: stage %d" % s,
              CHECK_LABEL in p and "2026-11-23" in p and "One whole-mod check instead" not in p,
              "his card answer of 2026-11-23 is absent, or the 2026-11-16 reading is back")


def test_gates_answer_keeps_the_stage_gates():
    """Stages 4 and 5 still end on the exam and coverage (the launcher enforces them); the packet must say so beside
    the answer, or a run reads it as leave to skip a gate the launcher will hold it to."""
    core = read(CORE)
    at = core.find(CHECK_LABEL)
    near = core[at:at + 1400] if at >= 0 else ""
    check("test_gates_answer_keeps_the_stage_gates",
          at >= 0 and "stage 4" in near and "stage 5" in near and "still" in near, near[:200])


def test_a_locked_version_keeps_its_scope():
    """A Design Version locked before his answers keeps its bars (a Divergent change never moves the current bars):
    the packet says the rules bind its next version."""
    core = read(CORE)
    check("test_a_locked_version_keeps_its_scope",
          "locked before" in core and "next version" in core.split(FIRST)[0][-1600:], "no locked-version line")


def test_one_copy_drift_is_caught():
    """Mutation: a one-word edit to the copy in designer.md must break the word-for-word match."""
    block = cleanse_block(read(CLEANSE))
    core = read(CORE)
    mutated = core.replace("one signature", "two signatures", 1)
    check("test_one_copy_drift_is_caught", block is not None and block not in mutated)


TESTS = (test_cleanse_block_found, test_every_stage_packet_carries_the_first_two_answers,
         test_every_stage_packet_carries_all_three_checks, test_gates_answer_keeps_the_stage_gates,
         test_a_locked_version_keeps_its_scope, test_one_copy_drift_is_caught)

if __name__ == "__main__":
    for t in TESTS:
        t()
    print("selftest_designer_first_version_rules: %s (%d failure(s))" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    sys.exit(1 if FAILS else 0)

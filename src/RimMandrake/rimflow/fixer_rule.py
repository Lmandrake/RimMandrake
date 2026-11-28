#!/usr/bin/env python3
"""The one statement that the fixer is you, and the one list of test-2 evidence (CLAUDE.md §Touching code has a cost).

Every brief that a program writes cites these constants, so the copies cannot drift: the detached-helper footer
(detached_helper.py), the pipeline's SELF_FIX_RULE (maturation.py) and the fixer briefs (maturation_autonomy.py). The
prose homes (CLAUDE.md, standing_rulings.md, the six .claude/agents/rm-*.md) are checked word for word against them by
selftest_fixer_rule.py. Report: design/specs/2026-11-25-the-fixer-is-you/findings.md (wording 1, Part 4 homes 2 to 5).
"""

STATEMENT = ("You are the fixer. When you find a fault, fix it in this run, test first. A later run knows less. Hand it "
             "on only with test-2 evidence.")
# wording 3 of the report, for judges and readers, where doubt is the usual state; its blind exception comes first
JUDGE_STATEMENT = ("When in doubt, the responsibility is yours: find, fix, test and close the fault now. To defer, "
                   "write why you cannot: one of the test-2 reasons, with its evidence.")
EVIDENCE = (
    "your verdict must stay independent of the work",
    "you lack the tools or the access",
    "the fix is not known after a real attempt: name what you tried",
    "it needs one of the owner's five acts, or it changes a north-star bar (a looser bar is the Conductor's act)",
    "another live run holds the files",
)
# The fresh reader of a fix (his card, 2026-11-26: "The fixing run files it (Recommended)"): the CLAUDE.md line, and
# the whole rule for the footer and standing_rulings.md. selftest_fresh_reader.py checks the homes word for word.
READER_LINE = ("A run that fixes code files the fresh reader of its fix as a ticket, before it ends "
               "(`python3 src/RimMandrake/rimflow/fresh_reader.py file --fix <sha> <path>...`); the ticket lane launches "
               "the reader.")
READER_RULE = READER_LINE + (" The reader gets the fixed file, its boundary page and its tests, never the diff or the "
                             "earlier findings. A reader ticket is never given to the run that made the fix.")
NEW_MACHINERY_RULE = ("A run that adds pipeline machinery files its blind Opus review before it ends. After `./publish` prints PUBLISHED <sha>, "
                      "run `python3 src/RimMandrake/rimflow/new_machinery_review.py file <sha>...` with your published "
                      "commits in order.")
NOT_EVIDENCE = "A large task, a long run or a full context is not evidence. A fresh session goes on from your notes."
STALE = ("would not finish", "more than this run", "more than one run")


def evidence_line():
    """-> the list as one sentence, for a brief: `Test-2 evidence is one of these: a; b; ... . <NOT_EVIDENCE>`."""
    return "Test-2 evidence is one of these: %s. %s" % ("; ".join(EVIDENCE), NOT_EVIDENCE)


def text(judge=False):
    """-> the statement with the list printed under it, as one paragraph for a brief."""
    return "%s %s" % (JUDGE_STATEMENT if judge else STATEMENT, evidence_line())

#!/usr/bin/env python3
"""brief_new.py: the standing parts of a helper brief of one kind, from one source, with blanks for the Conductor. No model.

Item RIMMANDRAKE_BUILD_BRIEF_NEW_ONE_IN_FOUR_LAUNCHES_RETURNED (script candidate 4 of
design/specs/2026-11-26-script-candidates/one_page.md). Page design/specs/2026-11-27-brief-new/boundary.md; selftest
selftest_brief_new.py. Each standing line is in LINES once; a kind names the keys of its lines. The lines pass the
program half of `guiding_prose.py brief` (the selftest reads every sentence of each kind). The Conductor fills each
`<<NAME: ...>>` blank: the question, the files, what is enough, when to stop. The launch (`detached_helper.py launch`)
adds the footer, the item packet and the command lines.

    python3 src/RimMandrake/rimflow/brief_new.py <kind> <ITEM> [--out PATH]
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import fixer_rule  # noqa: E402 (an import below the path set-up); the one copy of the fixer rule and its test-2 list

MW = "~/dev/MandrakeWorkflows/skills/"
# The standing lines, each once. Measured on the 70 Conductor briefs of 2026-11-19 to 2026-11-27 (Archmagi
# D:\ClaudeWork\rimmandrake\conductor\*_brief_*.md): the skill lines (using-rimflow in 62, clone-landing-commits in 56,
# mutate-your-checker in 30, confident-wrong-numbers and deciding-and-superseding in 9 each, measuring-large-artifacts in
# 6), "Start no helper" in 59, the commit and publish lines in 40, the --per-ruling line in 17, the machinery line in 18.
LINES = {
    "head_item": "Item: {item}. The Conductor wrote this brief. A Conductor instruction carries the owner's authority.",
    "head_show": "Read the item first: `python3 src/RimMandrake/rimflow/cli.py show {item}`.",
    # the two tests (CLAUDE.md §Touching code has a cost)
    "test1": ("Test 1: touch code, a def, a test, a hook or a brief only when someone would care about the fix. Someone "
              "cares about a significant finding that ordinary operation reaches, a failure that happened, or a red test."),
    "polish": ("A finding that fails test 1 gets no ticket. In a file that you changed, do the polish now, as its own "
               "commit with a subject that starts `polish:`. In any other file, write one line on the `polish.md` beside "
               "the boundary page of that file."),
    "test2": fixer_rule.STATEMENT,
    "test2_judge": fixer_rule.JUDGE_STATEMENT,
    "evidence": fixer_rule.evidence_line(),
    "reader": fixer_rule.READER_LINE,
    "machinery": "The pipeline fixes its own defects: fix a machinery defect with a known fix in this run, test first.",
    # the rules of the run
    "no_helper": "Start no helper of your own. Do not background a command. Do not end your turn to wait.",
    "no_game": "Take no game. Change no mod.",
    "commit": "Commit explicit paths. Keep file writes and commits in separate Bash calls.",
    "publish": ("Land with `./publish`, in the foreground, with no time limit. A slow publish is not a failed publish. "
                "Run no git command in the clone while its `./publish` runs."),
    "authority": "Log your acts with `--per-ruling CONDUCTOR_AUTHORITY_DECIDE_NO_ASKING_MOM`, with the Conductor's text in `--why`.",
    "tests_first": ("Write each test first. See the test fail on the parent commit, for the reason that the fault names. "
                    "Then fix, and see the test pass."),
    "planted": "A guard counts only after a planted fault made the guard fail.",
    "page_first": ("Pipeline code gets its boundary page before the code. Update the page that exists. Write a new page "
                   "only for a new component."),
    "selftests": "Before a commit, run the tests of what you changed: `python3 src/RimMandrake/Utils/run_selftests.py --only <tests>`.",
    "not_yours": "You did not make the work under review. If a piece of the work is your own, leave that piece out and say so.",
    "significant": ("A finding is significant only when a measure or a concrete case (this input, this wrong result) "
                    "shows that the finding breaks a stated promise or causes a failure."),
    "mark_clean": "Record a file with no significant finding: `python3 src/RimMandrake/Utils/code_review_status.py mark-clean <path>`.",
    "one_read": "Read each file once. Never read a file a second time to look for more.",
    "numbers": "Each number that you report names its source and how many cases the measure read.",
    "round_zero": "A count that is round, zero or alarming is a query bug until a sanity probe shows that the instrument can see.",
    "unmeasured": "Write UNMEASURED, with its cause, in place of each number that you could not read.",
    "bulk": "Send long command output to a file, and then search that file. Print no whole log or dump.",
    "judge_rule": "Before you judge, read `design/RimMandrake/standing_rulings.md` §The judge refuses flaws, not polish.",
    "constraints": "Judge only against the written constraints.",
    "live": ("An operational item is done only when the change is running. Close the item with `--live` and the "
             "command that shows the change alive."),
    "undo": "Before each change, write the command that undoes the change in a `PROGRESS:` note.",
    # the skills, by path
    "skill_rimflow": "`skills/using-rimflow/SKILL.md`",
    "skill_landing": "`skills/clone-landing-commits/SKILL.md`",
    "skill_mutate": "`" + MW + "mutate-your-checker/SKILL.md`",
    "skill_numbers": "`" + MW + "confident-wrong-numbers/SKILL.md`",
    "skill_large": "`" + MW + "measuring-large-artifacts/SKILL.md`",
    "skill_blind": "`" + MW + "blind-evaluation/SKILL.md`",
    "skill_independent": "`" + MW + "evaluation-independence/SKILL.md`",
    "skill_deciding": "`" + MW + "deciding-and-superseding/SKILL.md`",
    # the report. 10: the median of the 60 "At most N lines" in the 70 briefs above (10 in 20, 8 in 17, 12 in 15).
    "report_head": "At most 10 lines, in plain words for the owner.",
    "report_sha": "Name each published sha.",
    "report_paths": "Write each path in full Windows form, for example `D:\\Luke\\dev\\RimMandrake\\CLAUDE.md`.",
    "report_build": "For each part, name the test with its red reading and its green reading.",
    "report_review": ("Give the counts of files read clean, fixed and left out, and the count of polish lines. Give each "
                      "significant finding as one line: the input, the wrong result, the fix and the test."),
    "report_measure": "Give each table that you wrote by its full path, and its summary lines.",
    "report_judge": "Give one line for each piece: the verdict, the constraint that decides the verdict, and its evidence path.",
    "report_operate": "Name each change, the command that shows the change alive, and the command that undoes the change.",
}
HEADER_KEYS = ("head_item", "head_show")

# The blanks that the model fills; a blank is `<<NAME: what to write>>`.
BLANKS = {
    "TITLE": "one line that says what the run makes true",
    "QUESTION": "the question that this run answers, and why now; his words with their date",
    "FILES": "each file, command or folder to read first, by path, with the boundary page",
    "ENOUGH": "the level that is enough, as a check that a reader can run",
    "STOP": "when the run stops looking, and what the run does then",
    "SKILLS": "more skills by path, or none",
    "REPORT": "what else the report lines name, or none",
}
BLANK = re.compile(r"<<([A-Z]+):[^>]*>>")

_TESTS = ["test1", "polish", "test2", "evidence", "machinery"]
_RULES = ["no_helper", "commit", "publish", "authority"]
_STOP = ["?ENOUGH", "?STOP"]
_SKILLS = ["skill_rimflow", "skill_landing"]
_REPORT = ["report_sha", "report_paths", "?REPORT"]
# The kinds, from the titles of the 70 briefs above: build or fix 19 (and most of 23 others), operate 13, measure 9,
# review or fresh read 4, judge 2. A kind names its sections in order; "?NAME" is a blank.
KINDS = {
    "build": {"why": "build or fix code, test first", "sections": [
        ("The two tests", _TESTS + ["reader"]),
        ("Rules for this run", ["tests_first", "planted", "page_first", "selftests"] + _RULES),
        ("When to stop", _STOP),
        ("Skills to read, by path", _SKILLS + ["skill_mutate", "?SKILLS"]),
        ("Report", ["report_head", "report_build"] + _REPORT)]},
    "review": {"why": "a fresh reader or a blind code review of work that the run did not make", "sections": [
        ("Your role", ["not_yours", "significant", "mark_clean"]),
        ("The two tests", ["test1", "polish", "test2_judge", "evidence", "machinery", "reader"]),
        ("Rules for this run", ["no_game", "one_read", "tests_first"] + _RULES),
        ("When to stop", _STOP),
        ("Skills to read, by path", _SKILLS + ["skill_mutate", "?SKILLS"]),
        ("Report", ["report_head", "report_review"] + _REPORT)]},
    "measure": {"why": "measure, census or study, and report the numbers", "sections": [
        ("The two tests", _TESTS),
        ("Rules for this run", ["numbers", "round_zero", "unmeasured", "bulk", "no_game"] + _RULES),
        ("When to stop", _STOP),
        ("Skills to read, by path", _SKILLS + ["skill_large", "skill_numbers", "?SKILLS"]),
        ("Report", ["report_head", "report_measure"] + _REPORT)]},
    "judge": {"why": "a taste call against written constraints, by a judge that did not make the work", "sections": [
        ("Your role", ["not_yours", "judge_rule", "constraints"]),
        ("The two tests", ["test1", "polish", "test2_judge", "evidence", "machinery"]),
        ("Rules for this run", _RULES),
        ("When to stop", _STOP),
        ("Skills to read, by path", _SKILLS + ["skill_blind", "skill_independent", "?SKILLS"]),
        ("Report", ["report_head", "report_judge"] + _REPORT)]},
    "operate": {"why": "change a live state (install, stage, apply, switch) and prove the change alive", "sections": [
        ("The two tests", _TESTS),
        ("Rules for this run", ["undo", "live"] + _RULES),
        ("When to stop", _STOP),
        ("Skills to read, by path", _SKILLS + ["skill_deciding", "?SKILLS"]),
        ("Report", ["report_head", "report_operate"] + _REPORT)]},
}


class Refused(Exception):
    """A kind that KINDS does not hold: the text names the kind and the known kinds."""


def blank(name):
    return "<<%s: %s>>" % (name, BLANKS[name])


def blanks(text):
    """-> the names of the blanks that the text still holds, in order (a name twice when the text holds the blank twice)."""
    return BLANK.findall(text)


def _line(ref, item):
    return blank(ref[1:]) if ref.startswith("?") else LINES[ref].format(item=item)


def skeleton(kind, item):
    """-> the skeleton of a brief of this kind for this item. Raises Refused for an unknown kind."""
    if kind not in KINDS:
        raise Refused("unknown kind %r; the known kinds: %s" % (kind, ", ".join(
            "%s (%s)" % (k, KINDS[k]["why"]) for k in sorted(KINDS))))
    out = ["# Brief: " + blank("TITLE"), "", " ".join(_line(k, item) for k in HEADER_KEYS), "",
           "## The question", blank("QUESTION"), "", "## Files to read", blank("FILES")]
    for head, refs in KINDS[kind]["sections"]:
        out += ["", "## " + head] + ["- " + _line(r, item) for r in refs]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("kind", help="one of: " + ", ".join(sorted(KINDS)))
    ap.add_argument("item", help="the ledger item id")
    ap.add_argument("--out", help="write the skeleton to this file; an existing file is kept")
    a = ap.parse_args(argv)
    try:
        text = skeleton(a.kind, a.item)
    except Refused as e:
        print("brief_new: REFUSED: %s" % e, file=sys.stderr)
        return 2
    if not a.out:
        sys.stdout.write(text)
        return 0
    if os.path.exists(a.out):
        print("brief_new: REFUSED: %s exists; the Conductor may have filled it. Name a new path." % a.out, file=sys.stderr)
        return 2
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    print("brief_new: wrote %s (%s); fill each blank: %s" % (a.out, a.kind, ", ".join(blanks(text))))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""selftest_journal_answered.py: a journal question that the journal already answers is not shown as open.

    python3 src/RimMandrake/Utils/selftest_journal_answered.py

Item: RIMMANDRAKE_HIDE_ANSWERED_JOURNAL_QUESTION_PAGE_SHOWED_HIM_ONE (the page showed GimmeSomeSlack question 4, answered
2026-11-22 in its own item, as waiting for the Conductor). Expected: all checks pass (printed count).
Answer forms found in design/concepts/*/journal.md (13 journals, 7 questions, 2026-11-23):
  A  "answers question N" in another section (ExplosiveKnockback 1, GSS 1, Pyrelands 2/4/8)
  B  the title struck through, "~~title~~: answered by ..." (GSS 3, ExplosiveKnockback 1)
  C  a line "**Answered DATE by WHO:** text" inside the item (GSS 4)
The last section also reads every real journal and prints how many questions it read.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import maturation_now as M  # noqa: E402

BAD = []
N = [0]


def check(name, ok, detail=""):
    N[0] += 1
    if not ok:
        BAD.append(name)
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, "" if ok else "  :: %s" % detail))


def qs(body):
    return {q["n"]: q for q in M.journal_questions("### Questions (open)\n\n" + body) or []}


def main():
    a = qs("1. **Open one?** asked.\n"
           "2. **Form C.** text\n   **Answered 2026-11-22 by the sweep:** both are out of range.\n"
           "3. ~~Form B~~: answered by the steward, tier x (2026-11-14).\n"
           "4. **Empty answer.** text\n   **Answered 2026-11-22:**\n"
           "6. **(to the Conductor, 2026-11-20) Form C, conductor.** t\n   **Answered 2026-11-22 by x:** done.\n"
           "5. **Heading only.** text\n   **Answered 2026-11-22 by the sweep:**\n\n## History\n- later\n")
    check("C an '**Answered DATE by WHO:** text' line inside the item reads answered", a[2]["answered"], a[2])
    check("B a struck-through title with 'answered by' reads answered", a[3]["answered"], a[3])
    check("an unanswered question reads open", not a[1]["answered"], a[1])
    check("an Answered line with no text after it reads open", not a[4]["answered"], a[4])
    check("an Answered heading with nothing after it reads open", not a[5]["answered"], a[5])
    check("a conductor question with an Answered line reads answered", a[6]["answered"] and a[6]["who"] == "conductor", a[6])
    t = "### Questions\n\n1. **Q one.** x\n2. **Q two.** y\n\n## History\n- the steward answers question 1 here.\n"
    b = {q["n"]: q["answered"] for q in M.journal_questions(t)}
    check("A 'answers question N' elsewhere still marks N answered, only N", b == {1: True, 2: False}, b)
    check("a journal with a Questions heading and no items gives an empty list, not could-not-look",
          M.journal_questions("### Questions\n\nnone\n") == [])
    check("a journal that could not be read gives 'could not look', not 'no questions'",
          M.journal_questions(None) is None, M.journal_questions(None))
    # the real journals
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    if not glob.glob(os.path.join(root, "design", "concepts", "*", "journal.md")):
        root = "/home/mandrake/rm/bench"  # a sparse scratch clone has no design/concepts
    nq = open_n = 0
    shown = []
    for f in sorted(glob.glob(os.path.join(root, "design", "concepts", "*", "journal.md"))):
        for q in M.journal_questions(open(f, encoding="utf-8").read()) or []:
            nq += 1
            if not q["answered"]:
                open_n += 1
                shown.append("%s %d" % (f.split(os.sep)[-2], q["n"]))
    print("read %d real questions, %d shown open: %s" % (nq, open_n, shown))
    check("the real GimmeSomeSlack question 4 is not shown open", "GimmeSomeSlack 4" not in shown, shown)
    check("the real journals were read (>= 7 questions; limit = 7 found on 2026-11-23)", nq >= 7, nq)
    print("%d checks, %d failed" % (N[0], len(BAD)))
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())

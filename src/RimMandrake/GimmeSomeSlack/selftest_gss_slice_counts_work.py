#!/usr/bin/env python3
"""Class guard of SELFTEST_FIX_GIMMESOMESLACK_NWML_JLWY: the GSS slice check decides in work, never in wall-clock ms.

The slice check (SliceGateChecks.Slices) guards one danger: a planned build holds one frame on the caller. It was a 30 ms
bound on the slowest Build, and a loaded host turned it red on 2026-11-22, -23 and -25 with no change to the lay: it
measured the host, not the mod. It now counts work under a lay budget that is spent the moment a Build starts
(SpentBudgetMs): edges laid on the caller per Build, draws per Build, the run's draws against one unbudgeted Build, and
draws per edge. This guard reads Slices() and fails when:
  - a Program.Check in it decides on a ms reading (a Stopwatch, an Elapsed, a `worst`, an identifier ending in Ms);
  - one of the four work counts is gone.
A ms reading printed with Console.WriteLine is information and is allowed.

    python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_slice_counts_work.py [--rev <git rev>]

--rev reads SliceGateChecks.cs as it was at that commit (the instance: the parent of the fix fails here). The run also
plants a ms bound into today's text and must see it refused (a guard that cannot fail proves nothing).
Exit 0 PASS, 1 FAIL."""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "src/RimMandrake/GimmeSomeSlack/Source/SelfTest/SliceGateChecks.cs"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))

MS = re.compile(r"Stopwatch|Elapsed|TotalMilliseconds|\bworst\w*|\w*Ms\b")
COUNTS = {
    "a Build under the spent budget lays one edge": r"\.maxEdges\s*==\s*1",
    "a Build draws no more than one edge may": r"\.maxDraws\s*<=\s*drawCap",
    "the run draws what one unbudgeted Build draws": r"\.draws\s*==\s*wantDraws",
    "draws per edge stay under their bound": r"DrawsPerEdgeBound\s*\*\s*edges",
    "the counted run uses the spent budget": r"CountedConverge\([^;]*SpentBudgetMs|LayBudgetMs\s*=\s*SpentBudgetMs",
}


def slices_body(text):
    i = text.index("void Slices()")
    j = text.index("\n        }\n", i)
    return text[i:j]


def check_conditions(body):
    """-> the first argument of every Program.Check( in body (paren-balanced)."""
    out = []
    for m in re.finditer(r"Program\.Check\(", body):
        k, depth, start = m.end(), 1, m.end()
        while k < len(body):
            c = body[k]
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
                if depth == 0:
                    break
            elif c == "," and depth == 1:
                break
            k += 1
        out.append(body[start:k].strip())
    return out


def problems(text):
    try:
        body = slices_body(text)
    except ValueError:
        return ["SliceGateChecks.cs has no Slices() method: the guard cannot read the slice check"]
    out = []
    for cond in check_conditions(body):
        hit = MS.search(cond)
        if hit:
            out.append("Slices() decides on a wall-clock reading (%s): %s" % (hit.group(0), cond))
    for what, rx in COUNTS.items():
        if not re.search(rx, body):
            out.append("Slices() lost a work count: %s (%s)" % (what, rx))
    return out


def main(argv):
    if "--rev" in argv:
        rev = argv[argv.index("--rev") + 1]
        r = subprocess.run(["git", "show", "%s:%s" % (rev, REL)], cwd=REPO, capture_output=True, text=True)
        if r.returncode:
            print("COULD NOT LOOK: git show %s:%s: %s" % (rev, REL, r.stderr.strip()))
            return 2
        text, where = r.stdout, "%s at %s" % (REL, rev)
    else:
        with open(os.path.join(REPO, REL), encoding="utf-8") as f:
            text, where = f.read(), REL
    bad = problems(text)
    for b in bad:
        print("FAIL " + b)
    # the guard can fail: a planted ms bound in today's text is refused
    try:
        body = slices_body(text)
        planted = text.replace(body, body + "\n            Program.Check(worst <= 30.0, \"planted ms bound\");", 1)
        seen = any("wall-clock" in p for p in problems(planted))
    except ValueError:
        seen = False
    if not seen:
        print("FAIL the guard did not refuse a planted ms bound (instrument blind)")
    print("%s: %s" % (where, "PASS" if not bad and seen else "FAIL"))
    return 0 if not bad and seen else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""selftest_ab_census_fixture_class.py -- a made-up AB_ name in ANY selftest is a fixture, not a census row.

    python3 src/RimMandrake/Utils/selftest_ab_census_fixture_class.py [<file> <token>]

Class guard for NIGHTLY_COP_FIX_RED_ODAKND_UFTV: alpha_biomes_census kept a hand list of fixture
files, so every new selftest that invented an AB_ name (selftest_status_board.py's AB_ONE_XY was
the fifth) turned the nightly census red. Default instance: that file and token, in a temp tree.
A non-selftest file still counts, so the census stays able to see.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import alpha_biomes_census as C  # noqa: E402

FAILS = []


def check(cond, what, detail=""):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  -- %s" % (detail,)))
    if not cond:
        FAILS.append(what)


def undecided(files):
    """files {rel: text} -> the census's UNDECIDED_TOKEN findings on a small fake repo holding them."""
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(["git", "init", "-q", t], check=True)
        fill = "".join("<!-- AB_Fill%03d -->\n" % i for i in range(120))
        files = dict(files, **{"src/M/Defs/T.xml": "<Defs>\n" + fill + "</Defs>"})
        for rel, body in files.items():
            p = os.path.join(t, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(body)
        subprocess.run(["git", "-C", t, "add", "src"], check=True)
        dec = {"categories": {c: {} for c in C.CATEGORIES}, "donor_counts": {c: 0 for c in C.CATEGORIES},
               "tokens": {"AB_Fill%03d" % i: "fragment" for i in range(120)}, "live_allowed": []}
        inv = {"defs": ["AB_Filler%02d" % i for i in range(60)], "abstracts": []}
        status, finds, _ = C.verify(dec, inv, C.tracked(t), t, donor_root=os.path.join(t, "no_donor"))
    return status, [f for f in finds if f.startswith("UNDECIDED_TOKEN")]


def main(argv):
    rel, token = argv[:2] if len(argv) >= 2 else ("src/RimMandrake/Utils/selftest_status_board.py", "AB_ONE_XY")
    status, und = undecided({rel: 'X = "wait for %s"\n' % token})
    check(status != "UNMEASURED", "the fake repo is measurable", status)
    check(not und, "a made-up %s only in %s needs no census decision" % (token, os.path.basename(rel)), und)
    _, und = undecided({"src/RimMandrake/Utils/some_tool.py": 'Y = "%s"\n' % token})
    check(any(token in f for f in und), "the same name in a non-selftest file is still refused (the census can see)", und)
    print("RESULT: " + ("FAIL" if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

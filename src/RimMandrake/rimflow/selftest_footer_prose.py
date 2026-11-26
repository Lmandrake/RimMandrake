#!/usr/bin/env python3
"""selftest_footer_prose.py - the footer of every detached brief passes the program half of the guiding-prose check.

Item RIMMANDRAKE_REWRITE_BRIEF_TEXT_INSIDE_CODE_FOURTEEN_MODULES; page design/specs/2026-11-26-footer-prose/boundary.md
(each t_ function is one promise of it, by name). The launch check (guiding_prose.before_launch, after_launch) reads a
brief before detached_helper.brief_message adds the footer, so this test is the only reader of the footer. Offline, no
model. Exit 0 pass, 1 a fault, 3 UNMEASURED (the STE lint clarify.py cannot be loaded here).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _p in (HERE, os.path.join(REPO, "src", "RimMandrake", "Utils")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
os.environ["RM_UNDER_SELFTEST"] = "1"
FAILS = []
# a filed item, so the footer's item id is one that the ledger holds (a real launch always names a filed item)
ITEM = "RIMMANDRAKE_REWRITE_BRIEF_TEXT_INSIDE_CODE_FOURTEEN_MODULES"
SEAT = "BENCH"


class Unmeasured(Exception):
    pass


def chk(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def GP():
    import guiding_prose
    try:
        guiding_prose.lint()
    except guiding_prose.CouldNotLook as e:
        raise Unmeasured(str(e))
    return guiding_prose


def footer(bound_text):
    """-> the footer text that detached_helper.brief_message adds after the item packet, for a slim clone and no card
    work (card_footer is the item's own data, not text of this code)."""
    import detached_helper as DH
    import scratch_clone
    return (DH.FOOTER.format(clone=REPO, item=ITEM, seat=SEAT, bound_text=bound_text)
            + DH.SLIM_LINE % ", ".join(scratch_clone.SLIM_MEDIA) + DH.command_lines(ITEM, SEAT))


def faults(text):
    gp = GP()
    res = gp.check_files(gp.TOP, {gp.BRIEF_PATH: text}, {}, "brief", None)
    return res["faults"], res["sentences"]


def t_the_footer_reads_no_program_fault():
    for bound in ("no wall-time bound", "Wall-time bound: 10800 s"):
        got, n = faults(footer(bound))
        chk(n > 30 and not got, "the footer (%s) reads no program fault in %d sentences%s" % (
            bound, n, "".join("\n       %s [%s] %r" % (f["line"], f["kind"], f["term"]) for f in got)))


def t_a_planted_fault_is_seen():
    planted = footer("no wall-time bound") + "- It waits for the next tick and you should look at it again later on.\n"
    got, _ = faults(planted)
    kinds = sorted({f["kind"] for f in got})
    chk("pronoun" in kinds, "a planted pronoun sentence in the footer is seen (%s)" % kinds)
    if os.environ.get("RM_FOOTER_PROSE_INNER"):
        return
    import subprocess
    env = dict(os.environ, CLEAR_FINDINGS_TOOLS="/nonexistent", RM_FOOTER_PROSE_INNER="1")
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, capture_output=True, text=True,
                       timeout=300)  # hang guard: a whole run of this test takes about 5 s
    chk(r.returncode == 3 and "UNMEASURED" in r.stdout, "with no STE lint the test exits 3 and says UNMEASURED (rc %s)" % r.returncode)


def main():
    try:
        for t in (t_the_footer_reads_no_program_fault, t_a_planted_fault_is_seen):
            t()
    except Unmeasured as e:
        print("UNMEASURED: %s" % e)
        return 3
    print("%s: %d failed" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

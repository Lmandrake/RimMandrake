"""Selftest for vacuity.py: a component that never reads anything back is found; delegation to an
asserting local helper (even through another helper) is NOT a false positive. Run: python3 selftest_vacuity.py"""
# selftest temp containment (wave 7, DIRTY_CODE_REVIEW_STANDING_LOOP_1): every mkdtemp/mkstemp below,
# and every child process via TMPDIR, lands in one private dir removed at exit — this
# test used to leave its temp dirs behind in the seat TMPDIR on every run.
import atexit as _st_atexit, os as _st_os, shutil as _st_shutil, tempfile as _st_tempfile  # noqa: E401
_st_tempfile.tempdir = _st_os.environ["TMPDIR"] = _st_tempfile.mkdtemp(prefix="st_selftest_vacuity_")
_st_atexit.register(_st_shutil.rmtree, _st_tempfile.tempdir, True)
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vacuity   # noqa: E402

SRC = '''
from modcheck import Suite, ExpectationFailed
suite = Suite("X")

def _inner(t):
    raise ExpectationFailed("nope")

def _outer(t):
    _inner(t)

def _noop(t):
    return 1

@suite.chain("c")
def c(t):
    """Intent paragraph.

    More."""
    with t.component("vacuous"):
        t.wait_ticks(10)
        t.bridge_call("jawa/prefs")
    with t.component("direct"):
        t.expect_pawn_despawned("x")
    with t.component("via_helper_chain"):
        _outer(t)
    with t.component("helper_that_does_not_assert"):
        _noop(t)
    with t.component("flip"):
        t.set_setting("T", {"a": 1})
    with t.component("raises"):
        raise ExpectationFailed("x")
'''


def main():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "validation.py")
    open(p, "w").write(SRC)
    rows = dict((r["component"], r) for r in vacuity.analyse(p))
    res = []

    def check(n, c):
        res.append(bool(c))
        print("%s %s" % ("ok  " if c else "FAIL", n))
    check("six components found", len(rows) == 6)
    check("a component with only a wait and a ping asserts nothing (found)", not rows["vacuous"]["asserts"])
    check("a direct expect_* call counts", rows["direct"]["asserts"])
    check("delegation through TWO helpers counts (no false positive)", rows["via_helper_chain"]["asserts"])
    check("control: a helper that asserts nothing does NOT launder vacuity", not rows["helper_that_does_not_assert"]["asserts"])
    check("set_setting (reads back and raises) counts", rows["flip"]["asserts"])
    check("a raise ExpectationFailed counts", rows["raises"]["asserts"])
    check("the chain's docstring first paragraph is the intent", rows["vacuous"]["intent"] == "Intent paragraph.")
    n = sum(res)
    print("\n%d/%d passed" % (n, len(res)))
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())

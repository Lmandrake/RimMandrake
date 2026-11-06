#!/usr/bin/env python3
"""selftest_row_return_lint.py -- VALIDATION_ROWRETURN_AUDIT_CHAINS_CUT_SHORT: a `return` inside a non-final
`with t.component(...)` row leaves the whole chain, so later rows are never recorded (live or in the offline probe).
  * row_return_lint flags a return in a non-final row and in a looped row, and spares the last row, a nested def and a
    function with one row (sanity: it must SEE the pattern before its 0 over src/ means anything);
  * every validation.py under src/ is clean;
  * RowDone through modcheck's real TestContext and the offline probe: it ends only its row (PASS), later rows are
    recorded, an `except Exception` in the row cannot swallow it, and a latched UNMEASURED still cascades.
Offline.

    python3 src/RimMandrake/Utils/modcheck/selftest_row_return_lint.py
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import row_return_lint as L  # noqa: E402
from modcheck import Suite, RowDone  # noqa: E402
from modcheck.suite import TestContext, PASS, UNMEASURED  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, "" if cond else detail))
    if not cond:
        FAILS.append(name)


FIXTURE = '''
def chain(t):
    with t.component("a"):
        if x:
            return                      # 5: flagged, row a is not the last
        def inner():
            return 1                    # nested def: not flagged
    with _comp(t, "b"):
        return _unmeasured(t, "why")    # 9: flagged
    with t.component("c"):
        return                          # last row: not flagged

def looped(t):
    for f in fields:
        with t.component(f):
            return                      # 16: flagged, the loop has more rows

def single(t):
    with t.component("only"):
        return                          # one row: not flagged
'''

with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
    fh.write(FIXTURE)
try:
    got = [line for line, _ in L.findings(fh.name)]
finally:
    os.unlink(fh.name)
check("lint flags non-final and looped rows only", got == [5, 9, 16], got)

files = L.validation_files()
check("lint sees the repo's validation scripts", len(files) >= 50, len(files))
dirty = [(os.path.relpath(p, L.REPO), L.findings(p)) for p in files if L.findings(p)]
check("no validation.py has a chain-ending row return", not dirty, dirty[:5])


def build():
    suite = Suite("RowDoneFixture")

    @suite.chain("c")
    def c(t):
        with t.component("first"):
            try:
                raise RowDone
            except Exception:           # a row's own handler must not swallow it
                raise AssertionError("swallowed")
        with t.component("second"):
            if t.session is None:
                raise RowDone
        with t.component("third_latches"):
            t.upstream_failed, t.upstream_reason = True, "UNMEASURED: fixture"
            raise RowDone
        with t.component("fourth"):
            pass
    return suite


suite = build()
check("probe records every row after a RowDone", len(suite.components_declared()) == 4, suite.components_declared())
t = TestContext(session=None)
suite.chains[0][1](t)
names = [(c.name, c.verdict) for c in t.components]
check("RowDone ends only its row: rows 1-2 PASS, latch cascades to row 4",
      names == [("first", PASS), ("second", PASS), ("third_latches", UNMEASURED), ("fourth", UNMEASURED)], names)

print("selftest_row_return_lint: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)

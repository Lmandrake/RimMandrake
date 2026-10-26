#!/usr/bin/env python3
"""selftest_diptych_host.py -- a diptych that cannot be composed because the HOST lacks Pillow is UNMEASURED, not FAIL.

Sweep J20261026T004751Z-6e5292 (SteveDesktop, 2026-10-26): the runner's Windows python has no PIL, so four live rows
(plot_C canal_fill_front, plot_C2 tar_front_lags_water, plot_D pond_drawn_down, plot_H pawn_height_ladder_look) read
FAIL "diptych could not be composed (No module named 'PIL')" and their chains' later rows went "upstream failed". A
missing instrument is not a mod verdict. An unreadable frame stays a FAIL (the mod or the screenshot gave a bad file).
No game, no bridge.
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(os.path.dirname(os.path.dirname(HERE)), "Utils"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extensions as E  # noqa: E402
from modcheck import ExpectationFailed  # noqa: E402

FAILS = []


def check(what, ok):
    print("%s  %s" % ("ok  " if ok else "FAIL", what))
    if not ok:
        FAILS.append(what)


class _T(object):
    _current = None

    def _guard(self):
        return True


def _why(before, after):
    try:
        E._diptych(_T(), before, after, "selftest")
        return ""
    except ExpectationFailed as ex:
        return str(ex)


def main():
    d = tempfile.mkdtemp(prefix="diptych_host_")
    a, b = os.path.join(d, "a.png"), os.path.join(d, "b.png")
    saved = {k: sys.modules[k] for k in list(sys.modules) if k == "PIL" or k.startswith("PIL.")}
    for k in saved:
        del sys.modules[k]
    sys.modules["PIL"] = None            # `from PIL import ...` now raises ImportError, as on a host without Pillow
    try:
        why = _why(a, b)
    finally:
        del sys.modules["PIL"]
        sys.modules.update(saved)
    check("no Pillow on the host -> UNMEASURED (%s)" % why[:80], why.startswith("UNMEASURED"))
    check("... and it names Pillow as the missing piece", "Pillow" in why)
    try:
        import PIL  # noqa: F401
        have_pil = True
    except ImportError:
        have_pil = False
    if have_pil:
        with open(a, "wb") as f:
            f.write(b"not a png")
        with open(b, "wb") as f:
            f.write(b"not a png")
        why = _why(a, b)
        check("an unreadable frame is still a FAIL (%s)" % why[:80], why.startswith("diptych could not be composed"))
    else:
        print("skip  unreadable-frame case (this python has no Pillow)")
    print("\n%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

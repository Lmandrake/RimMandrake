#!/usr/bin/env python3
"""selftest_make_hose_binding.py -- mockups/messy_conduit/make_hose_binding.py reads and writes where the hose art
actually ships, and refuses before writing anything when an input is gone.

  1. H is the directory that holds the SHIPPED hose art (Binding.png, Mouth.png and the BARE_FROM originals).
     Before 2026-10-26 it still pointed at GimmeSomeSlack/Textures/.../Hose, retired when the hose moved to
     FlowWorks, so a run died on the first fitting it opened.
  2. With the source render missing (it was not kept after 2026-10-04), main() returns non-zero and writes
     no *_Bare.png: the old main wrote all three, then died in binding().
"""
import importlib.util
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE / "mockups" / "messy_conduit" / "make_hose_binding.py"
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def load():
    spec = importlib.util.spec_from_file_location("make_hose_binding", MOD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    M = load()
    h = os.path.normpath(M.H)
    shipped = HERE.parent / "FlowWorks" / "Textures" / "RimMandrake" / "FlowWorks" / "Hose"
    check(shipped.joinpath("Binding.png").is_file(), "probe: the shipped Binding.png exists at %s" % shipped)
    check(os.path.isdir(h) and os.path.samefile(h, shipped), "H is the shipped hose art directory (%s)" % h)
    for n in M.BARE_FROM:
        check(os.path.isfile(os.path.join(h, n + ".png")), "fitting original %s.png is under H" % n)

    with tempfile.TemporaryDirectory() as td:
        for n in M.BARE_FROM:
            src = os.path.join(h, n + ".png")
            if os.path.isfile(src):
                shutil.copy(src, td)
        M.H, M.SRC = td, os.path.join(td, "no_such_render.png")
        before = sorted(os.listdir(td))
        try:
            rc = M.main()
        except Exception as e:      # the old code crashes here, after writing
            rc = "crash: %s" % type(e).__name__
        after = sorted(os.listdir(td))
        check(rc == 1, "a missing source render refuses with exit 1 (got %r)" % (rc,))
        check(after == before, "a refused run writes nothing (new files: %s)" % sorted(set(after) - set(before)))
    print("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

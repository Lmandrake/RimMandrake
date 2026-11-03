#!/usr/bin/env python3
"""FAUNA_TOLERANCE_NORMALIZATION_1: the proof goes red when a ruled number is broken.

Each mutant changes one constant of fauna_normalization.py, regenerates the manifest and the
three FaunaNorm_* patches into a temp dir (what a mutant `generate` would commit), points
selftest_fauna_normalization at them and runs it. The unmutated run must PASS; every mutant must
FAIL, and must fail on the literal-band checks (`ruled Law…`) as well as on the constant pin, so
the band check is proven to see the breakage on its own. Nothing in the repo is written.
"""
import contextlib
import importlib
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MUTANTS = [(None, None), ("MARGIN", 5.0), ("MARGIN", 14.0), ("K_LO", 10.0), ("K_HI", 20.0),
           ("MEAT_BASE", 100.0), ("LEATHER_BASE", 30.0)]


def run(name, val):
    for m in ("fauna_normalization", "selftest_fauna_normalization"):
        sys.modules.pop(m, None)
    fn = importlib.import_module("fauna_normalization")
    if name:
        setattr(fn, name, val)
        if name == "K_HI":
            fn.K_SET = val                      # the rescale target follows the band top
    d = tempfile.mkdtemp(prefix="fn_mutant_")
    try:
        outs = fn.outputs(fn.build_all())
        for attr in ("MANIFEST", "PATCH_LAW3", "PATCH_LAW5", "PATCH_LAW6"):
            old = getattr(fn, attr)
            new = os.path.join(d, os.path.basename(old))
            with open(new, "w", encoding="utf-8") as f:
                f.write(outs[old])
            setattr(fn, attr, new)
        st = importlib.import_module("selftest_fauna_normalization")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = st.main()
    finally:
        shutil.rmtree(d, ignore_errors=True)
    lines = [ln for ln in buf.getvalue().splitlines() if ln.startswith("FAIL")]
    return rc, sum("ruled Law" in ln for ln in lines), sum("ruling:" in ln for ln in lines), len(lines)


def main():
    fails = []
    for name, val in MUTANTS:
        rc, band, pin, total = run(name, val)
        label = "%s=%s" % (name, val) if name else "unmutated"
        print("%-18s rc=%d fails=%d ruled-band=%d const-pin=%d" % (label, rc, total, band, pin))
        if name is None and rc != 0:
            fails.append("the unmutated regeneration does not pass")
        elif name and (rc == 0 or band == 0 or pin == 0):
            fails.append("mutant %s survived (rc=%d, band fails %d, pin fails %d)" % (label, rc, band, pin))
    for f in fails:
        print("FAIL", f)
    if fails:
        return 1
    print("PASS: %d mutants of the ruled constants all go red on the literal bands and the pin" % (len(MUTANTS) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

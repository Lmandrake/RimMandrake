#!/usr/bin/env python3
"""Selftest for the descent site (CATHEDRAL_DESCENT_REVEAL_SITE_1), offline.

  1. The shipped Defs/CathedralDescent passes Source/CathedralDescent/audit_descent_layout.py.
  2. The generator is deterministic and the committed files are its output (regenerated into a temp dir).
  3. Every label/description in Defs/CathedralDescent passes cathedral_arc_lint at stage 3 (and the linter read some).
  4. The audit can fail: a second terminus, an unknown symbol, and a hole in the line are each caught.

    python3 src/RimMandrake/Utils/run_selftests.py --only selftest_cathedral_descent_site
"""
import contextlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "CathedralDescent")
DEFS = os.path.join(HERE, "Defs", "CathedralDescent")
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
LINT = os.path.join(REPO, "src", "RimMandrake", "RustCathedral", "cathedral_arc_lint.py")
LAYOUT_FILE = "StructureLayoutDefs_CathedralDescent.xml"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def quiet(fn, *args):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def main():
    audit = load("audit_descent_layout", os.path.join(SRC, "audit_descent_layout.py"))
    gen = load("gen_descent_layout", os.path.join(SRC, "gen_descent_layout.py"))
    lint = load("cathedral_arc_lint", LINT)
    fails = []

    rc, out = quiet(audit.main, ["audit", DEFS])
    last = [l for l in out.splitlines() if l.startswith(("PASS", "FAIL", "walk:", "UNMEASURED"))]
    print("\n".join("  audit: " + l for l in last))
    if rc != 0:
        fails.append("audit of the shipped defs failed")

    tmp = tempfile.mkdtemp(prefix="descent_selftest_")
    try:
        gen.DEFS = os.path.join(tmp, "gen")
        rc, _ = quiet(gen.main)
        names = sorted(os.listdir(DEFS))
        same = rc == 0 and sorted(os.listdir(gen.DEFS)) == names and all(
            open(os.path.join(DEFS, n), "rb").read() == open(os.path.join(gen.DEFS, n), "rb").read() for n in names)
        print("  %s committed defs are the generator's output (%d files)" % ("ok  " if same else "FAIL", len(names)))
        if not same:
            fails.append("committed defs differ from a fresh generation")

        seen, findings = [], []
        for n in names:
            findings += lint.xml_findings(os.path.join(DEFS, n), 3, seen)
        ok = not findings and len(seen) >= 8
        print("  %s lint stage 3: %d strings read, %d findings" % ("ok  " if ok else "FAIL", len(seen), len(findings)))
        if not ok:
            fails.append("lint: %s" % findings[:3])

        layout_text = open(os.path.join(DEFS, LAYOUT_FILE), encoding="utf-8").read()
        mutations = {
            "second terminus": layout_text.replace("<li>RM_CathedralDeckPlate,", "<li>RUT_CathedralDescent_SymTerminus,", 1),
            "unknown symbol": layout_text.replace("<li>RM_CathedralDeckPlate,", "<li>RM_NoSuchRock,", 1),
            "hole in the line": layout_text.replace("RUT_CathedralDescent_SymLineHousing,", ".,", 7 * 250 // 2),
        }
        for label, text in mutations.items():
            d = os.path.join(tmp, label.replace(" ", "_"))
            shutil.copytree(DEFS, d)
            assert text != layout_text, label
            with open(os.path.join(d, LAYOUT_FILE), "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
            rc, _ = quiet(audit.main, ["audit", d])
            print("  %s planted %s is caught" % ("ok  " if rc != 0 else "FAIL", label))
            if rc == 0:
                fails.append("audit missed the planted %s" % label)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("FAIL: %s" % fails if fails else "PASS: selftest_cathedral_descent_site (audit, determinism, lint, 3 planted faults caught)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

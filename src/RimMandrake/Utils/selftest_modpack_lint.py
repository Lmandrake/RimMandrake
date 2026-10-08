#!/usr/bin/env python3
"""Shared planted-defect harness for the per-mod def lints (lint_feverwood_defs.py, lint_theforge_defs.py,
lint_cauldron_defs.py). Copies the mod to a temp dir, proves the lint is clean on the untouched copy, then plants ONE
defect at a time and requires the lint to report a given ERROR text. A lint that cannot fail proves nothing.

Used as a library by selftest_<mod>_lint.py:  run(mod_name, lint_script, plants) -> exit code
plants = [(label, relative file under the mod, old text, new text, expected substring of an ERROR line)]
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)


def run(mod, script, plants, keep=()):
    tmp = tempfile.mkdtemp(prefix="lintplant_")
    copy = os.path.join(tmp, mod)
    shutil.copytree(os.path.join(SRC, mod), copy, ignore=shutil.ignore_patterns(*[x for x in ("Textures", "Assemblies", "__pycache__", "obj", "bin", "Languages", "About") if x not in keep]))

    def lint():
        p = subprocess.run([sys.executable, os.path.join(HERE, script), "--mod-dir", copy, "--quiet"], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    bad = 0
    try:
        rc, out = lint()
        clean = rc == 0
        print(("ok   " if clean else "FAIL ") + "untouched copy is clean" + ("" if clean else " | " + out.strip().splitlines()[0][:160]))
        bad += not clean
        for label, rel, old, new, want in plants:
            path = os.path.join(copy, rel.replace("/", os.sep))
            orig = open(path, "rb").read()
            text = orig.decode("utf-8")
            if text.count(old) < 1:
                print(f"FAIL {label}: pattern not found in {rel}")
                bad += 1
                continue
            try:
                open(path, "wb").write(text.replace(old, new, 1).encode("utf-8"))
                rc, out = lint()
                hit = rc == 1 and any(l.startswith("ERROR") and want in l for l in out.splitlines())
                print(("ok   " if hit else "FAIL ") + label + ("" if hit else f" | rc={rc} wanted ERROR containing {want!r}; got {out.strip().splitlines()[-1][:140] if out.strip() else ''}"))
                bad += not hit
            finally:
                open(path, "wb").write(orig)
        rc, out = lint()
        print(("ok   " if rc == 0 else "FAIL ") + "restored copy is clean again")
        bad += rc != 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"{mod} lint planted-defect selftest: {len(plants) + 2 - bad}/{len(plants) + 2} ok")
    return 1 if bad else 0

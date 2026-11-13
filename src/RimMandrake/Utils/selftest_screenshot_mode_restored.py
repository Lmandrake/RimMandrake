#!/usr/bin/env python3
"""HELD MATERIAL, built early, awaiting ingest (design/RimMandrake/validation_holding/README.md); wired into no ladder stage or gate.

Every harness that turns screenshot mode ON turns it OFF in a `finally:` block.

Owner, 2026-11-12 ~6:15 PM PST: "The game is no longer allowing me to select objects at all..." Measured cause
(selection_dead/FINDINGS.md): jawa/screenshot_mode was left ON, and ScreenshotModeHandler.FiltersCurrentEvent eats every
map click. That night it was most likely an F11 keypress, not a harness [guess ~75%, FINDINGS.md]; this guard keeps a
harness from ever being the cause: a run that dies between the ON and the OFF must still restore it. The in-game half is
owner_look_regressions.py's OL_screenshot_mode_off row (off at the end of a run, and not left on before it).

Can it fail: a planted file that enables without a finally-block disable, and one whose disable sits outside the finally,
must each be refused; a correct file must pass."""
import os
import re
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
ON = re.compile(r"""screenshot_mode["']\s*,\s*enabled\s*=\s*True""")
OFF = re.compile(r"""screenshot_mode["']\s*,\s*enabled\s*=\s*False""")


def finally_blocks(lines):
    """-> [(first, last)] line ranges of every `finally:` block body (by indentation)."""
    out = []
    for i, ln in enumerate(lines):
        m = re.match(r"^(\s*)finally\s*:\s*(#.*)?$", ln)
        if not m:
            continue
        ind = len(m.group(1))
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or len(lines[j]) - len(lines[j].lstrip()) > ind):
            j += 1
        out.append((i + 1, j - 1))
    return out


def offenders(root):
    """-> [(path, line of the ON)] for every ON with no OFF inside any finally block of the same file."""
    bad = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in (".git", "__pycache__", "node_modules")]
        for fn in fns:
            if not fn.endswith(".py") or fn.startswith("selftest"):
                continue
            p = os.path.join(dp, fn)
            try:
                lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
            except OSError:
                continue
            ons = [i for i, ln in enumerate(lines) if ON.search(ln) and not ln.lstrip().startswith("#")]
            if not ons:
                continue
            fb = finally_blocks(lines)
            guarded = any(OFF.search(lines[k]) for a, b in fb for k in range(a, b + 1))
            if not guarded:
                bad.extend((os.path.relpath(p, root), i + 1) for i in ons)
    return bad


GOOD = '''def run(B):
    B.call("jawa/screenshot_mode", enabled=True)
    try:
        shoot()
    finally:
        B.call("jawa/screenshot_mode", enabled=False)
'''
NO_FINALLY = '''def run(B):
    B.call("jawa/screenshot_mode", enabled=True)
    shoot()
    B.call("jawa/screenshot_mode", enabled=False)
'''
OFF_OUTSIDE = '''def run(B):
    B.call("jawa/screenshot_mode", enabled=True)
    try:
        shoot()
    finally:
        log("done")
    B.call("jawa/screenshot_mode", enabled=False)
'''


def main():
    bad = 0

    def check(name, ok, got=""):
        nonlocal bad
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else "  " + str(got)[:400]))
        bad += not ok

    for label, text, want in (("correct file", GOOD, 0), ("no finally", NO_FINALLY, 1), ("disable outside finally", OFF_OUTSIDE, 1)):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "h.py"), "w").write(text)
            got = offenders(d)
            check("can-fail: %s -> %d offender(s)" % (label, want), len(got) == want, got)
    src = os.path.join(REPO, "src")
    n_on = 0
    for dp, dns, fns in os.walk(src):
        dns[:] = [x for x in dns if x not in (".git", "__pycache__")]
        n_on += sum(1 for fn in fns if fn.endswith(".py") and not fn.startswith("selftest")
                    and ON.search(open(os.path.join(dp, fn), encoding="utf-8", errors="replace").read()))
    check("the scan can see: at least one harness in src/ turns screenshot mode on (%d)" % n_on, n_on >= 1)
    got = offenders(src)
    check("every harness that turns screenshot mode on turns it off in a finally block", not got, got)
    print("selftest_screenshot_mode_restored: %s (%d bad)" % ("PASS" if not bad else "FAIL", bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

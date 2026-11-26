#!/usr/bin/env python3
"""selftest_menushell.py -- shell_files_static is green on the shipped mod and red on each planted break
(run against a temp copy of the mod, so the chain reads the copy's own files)."""
import importlib.util
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
UTILS = os.path.abspath(os.path.join(HERE, "..", "..", "RimMandrake", "Utils"))
for p in (UTILS, os.path.join(UTILS, "modcheck")):
    if p not in sys.path:
        sys.path.insert(0, p)
import runner                                                  # noqa: E402
from modcheck import Suite                                     # noqa: E402
from northstar_driver.session import FastSession               # noqa: E402
from northstar_driver.transport import MockGame, MockTransport  # noqa: E402

FAILS = []
ORBIT = os.path.join("Textures", "RimUtinni", "MenuShell", "BG_AshkarrOrbit.png")


def check(name, cond, detail=""):
    print("%s  %s %s" % ("ok  " if cond else "FAIL", name, ("" if cond else detail)))
    if not cond:
        FAILS.append(name)


def run(mod_dir):
    spec = importlib.util.spec_from_file_location("ms_v_%d" % id(mod_dir), os.path.join(mod_dir, "validation.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    suite = Suite("MSStatic")
    for name in ("shell_files_static", "shell_orbit_static", "shell_theme_static"):
        suite.chain(name)([f for n, f in m.suite.chains if n == name][0])
    with FastSession(transport=MockTransport(MockGame()), strict=False) as s:
        res = runner.run_suite(suite, s, anchor=None, mod=None)
    return [c["verdict"] for ch in res["chains"] for c in ch["components"]]


def planted(edit):
    tmp = tempfile.mkdtemp()
    dst = os.path.join(tmp, "MenuShell")
    shutil.copytree(HERE, dst, ignore=shutil.ignore_patterns("__pycache__", "_artsrc"))
    try:
        edit(dst)
    except (AssertionError, OSError) as e:      # the fault could not be planted: the shipped mod lacks its target
        shutil.rmtree(tmp, ignore_errors=True)
        return ["NOT PLANTED: %s" % e]
    try:
        return run(dst)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def sub(rel, old, new):
    def go(d):
        p = os.path.join(d, rel)
        s = open(p, encoding="utf-8").read()
        assert old in s, old
        open(p, "w", encoding="utf-8").write(s.replace(old, new, 1))
    return go


def main():
    check("shipped: every component PASS", run(HERE) == ["PASS", "PASS", "PASS"], run(HERE))
    bg = "Defs/BackgroundImageDefs.xml"
    for name, edit, want in (
            ("an unguarded background def reddens the defs component",
             sub(bg, '<VBE.BackgroundImageDef MayRequire="vanillaexpanded.backgrounds">', "<VBE.BackgroundImageDef>"),
             ["FAIL", "PASS", "PASS"]),
            ("path != iconPath reddens it",
             sub(bg, "<iconPath>RimUtinni/MenuShell/BG_PantheonSlide</iconPath>", "<iconPath>X/Y</iconPath>"),
             ["FAIL", "PASS", "PASS"]),
            ("a missing texture reddens it",
             lambda d: os.remove(os.path.join(d, "Textures", "RimUtinni", "MenuShell", "BG_God_Ohm.png")),
             ["FAIL", "PASS", "PASS"]),
            ("a missing webm for an animated def reddens it",
             lambda d: os.remove(os.path.join(d, "Videos", "UI", "Backgrounds", "utinni_menu_1.webm")),
             ["FAIL", "PASS", "PASS"]),
            ("no ASH'KARR orbit background reddens the orbit component",
             sub(bg, "<defName>RUT_BG_AshkarrOrbit</defName>", "<defName>RUT_BG_Gone</defName>"),
             ["PASS", "FAIL", "PASS"]),
            ("an orbit texture under 2048x1280 reddens it",
             lambda d: __import__("PIL.Image", fromlist=["Image"]).open(os.path.join(d, ORBIT)).resize((1586, 992)).save(
                 os.path.join(d, ORBIT)),
             ["PASS", "FAIL", "PASS"]),
            ("a colour out of range reddens the theme component",
             sub("RimThemes/Utinni Shell/meta.xml", "(18,21,26,235)", "(18,21,26,999)"), ["PASS", "PASS", "FAIL"]),
            ("a Source/ folder reddens the theme component",
             lambda d: os.makedirs(os.path.join(d, "Source")), ["PASS", "PASS", "FAIL"])):
        got = planted(edit)
        check(name, got == want, got)
    print("%s: %d failure(s)" % ("FAIL" if FAILS else "OK", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

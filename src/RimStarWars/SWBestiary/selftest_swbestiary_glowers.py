#!/usr/bin/env python3
"""selftest_swbestiary_glowers.py -- every CompProperties_Glower in SWBestiary's defs states its own radius and colour.

An empty glower loads the engine default (glowRadius 14, colour 369/369/369 = 1.45x white, brighter than a standing
lamp); one with a radius but no colour still shines 1.45x white. RSW_SmogMoth ("glows faintly") shipped empty and
RSW_Glowtail without a colour (SMOGMOTH_FIX_EMPTY_GLOWER_WHITE). The rule and its planted red cases live in TheRot's
selftest_rot_glowers.py; this applies the same glower_findings() to SWBestiary/Defs and proves the scan can see here.
    python3 src/RimStarWars/SWBestiary/selftest_swbestiary_glowers.py
"""
import glob
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ROT_TEST = os.path.join(ROOT, "src", "RimMandrake", "TheRot", "Tools", "selftest_rot_glowers.py")


def load_rule():
    spec = importlib.util.spec_from_file_location("selftest_rot_glowers", ROT_TEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.glower_findings


def main():
    glower_findings = load_rule()
    findings, total, files = [], 0, 0
    for path in sorted(glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True)):
        files += 1
        f, n = glower_findings(open(path, encoding="utf-8-sig").read(), os.path.relpath(path, HERE))
        findings += f
        total += n
    cases = [("shipped defs clean", not findings)]
    # The two glowers as they shipped before the fix must each read red, naming their def.
    for name, li in (("RSW_SmogMoth", '<li Class="CompProperties_Glower">\n\t\t\t\t</li>'),
                     ("RSW_Glowtail", '<li Class="CompProperties_Glower"><glowRadius>1</glowRadius></li>')):
        old = '<Defs><ThingDef><defName>%s</defName><comps>%s</comps></ThingDef></Defs>' % (name, li)
        f, n = glower_findings(old, "planted")
        cases.append(("pre-fix %s red" % name, n == 1 and len(f) == 1 and name in f[0]))
    # Sanity: SmogMoth and Glowtail both ship a glower; a blind glob or a class-name drift reads 0.
    cases.append(("sanity: >=2 glowers in >=20 files (%d in %d)" % (total, files), total >= 2 and files >= 20))
    for n, ok in cases:
        print("%s  %s" % ("ok  " if ok else "FAIL", n))
    for f in findings:
        print("  - " + f)
    bad = [n for n, ok in cases if not ok]
    print("selftest_swbestiary_glowers: %s (%d/%d)" % ("FAIL" if bad else "PASS", len(cases) - len(bad), len(cases)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Offline lint of the RustChrome mod (source + textures only, zero Defs: compile-listed and settings-scribed bite; see lint_mod_defs.py).
Plus the structure check that matters for a reflection recolour: every field it writes is captured first and restored, and the number of
texture overrides matches the table the texture validation holds.

    python3 src/RimMandrake/Utils/lint_rustchrome_defs.py [--mod-dir <dir>] [--quiet]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402


def recolour_findings(mod_dir):
    errs = []
    src = open(os.path.join(mod_dir, "Source", "RustChromeColors.cs"), encoding="utf-8-sig").read()
    body = re.sub(r"//[^\n]*", "", src)
    fields = sorted(set(re.findall(r'SetColorField\(typeof\(Widgets\), "(\w+)"', body)))
    if len(fields) < 6:
        errs.append("ERROR rustchrome-recolour: found %d Widgets colour fields written, want 6 (sanity probe)" % len(fields))
    for f in fields:
        if not re.search(r'vanilla\w+\s*=\s*GetColorField\(typeof\(Widgets\), "%s"\)' % f, body):
            errs.append("ERROR rustchrome-recolour: %s is overwritten but never captured first" % f)
        if 'RestoreColorField("%s", ' % f not in body:
            errs.append("ERROR rustchrome-recolour: %s is never restored to the captured vanilla value" % f)
    if "themedInspectTabTex ?? (themedInspectTabTex =" not in body:
        errs.append("ERROR rustchrome-recolour: the themed tab texture is no longer cached (every settings toggle leaks a texture)")
    tex = []
    for root, _, files in os.walk(os.path.join(mod_dir, "Textures")):
        tex += [f for f in files if f.endswith(".png")]
    if len(tex) != 14:
        errs.append("ERROR rustchrome-recolour: %d override textures shipped, the validation table lists 14" % len(tex))
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "RustChrome")
    rc = lint_mod_defs.run("RustChrome", argv, require_xml=False, require_settings=True, instance_settings=True)
    errs = recolour_findings(mod_dir)
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)

#!/usr/bin/env python3
"""Sweep guard: no top-level <Operation MayRequire=...> anywhere under src/**/Patches.

The 1.6 engine ignores MayRequire on a top-level Operation (PATCH_MAYREQUIRE_GUARD_INERT_1):
the op runs on every mod list, and one that never succeeds logs 'Patch operation ... failed'
as a red error. Gate on PatchOperationFindMod (exact About <name>) instead.

Control: a synthetic file carrying the inert shape must be found, so a clean sweep is
proven able to see the defect before it is believed.
"""
import os
import sys
import tempfile
import xml.etree.ElementTree as ET

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def inert_ops(root):
    out, scanned = [], 0
    for d, _dirs, files in os.walk(root):
        if os.sep + "Patches" not in d + os.sep:
            continue
        for fn in files:
            if not fn.endswith(".xml"):
                continue
            p = os.path.join(d, fn)
            try:
                r = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            if r.tag != "Patch":
                continue
            for i, op in enumerate(r.findall("Operation")):
                scanned += 1
                if op.get("MayRequire") or op.get("MayRequireAnyOf"):
                    out.append((os.path.relpath(p, root), i))
    return out, scanned


def main():
    with tempfile.TemporaryDirectory() as t:
        os.makedirs(os.path.join(t, "Mod", "Patches"))
        with open(os.path.join(t, "Mod", "Patches", "bad.xml"), "w") as f:
            f.write('<Patch><Operation Class="PatchOperationAdd" MayRequire="x.y">'
                    '<xpath>/Defs</xpath><value><a/></value></Operation></Patch>')
        found, _ = inert_ops(t)
        if len(found) != 1:
            print("FAIL control: synthetic inert op not detected (%r)" % (found,))
            return 1
    hits, scanned = inert_ops(os.path.join(REPO, "src"))
    if scanned < 1000:
        print("FAIL sanity: only %d top-level ops scanned; wrong root?" % scanned)
        return 1
    if hits:
        for h in hits:
            print("FAIL inert top-level MayRequire: %s op %d" % h)
        return 1
    print("PASS %d top-level ops scanned, 0 inert Operation MayRequire (control detected)" % scanned)
    return 0


if __name__ == "__main__":
    sys.exit(main())

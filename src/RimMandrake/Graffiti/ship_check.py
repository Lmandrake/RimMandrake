"""ship_check.py -- the offline half of GRAFFITI_NORTHSTAR_SHIP_1's acceptance, as one command.

    python3 src/RimMandrake/Graffiti/ship_check.py      # exit 0 = every offline clause holds

Clauses (each prints PASS/FAIL):
  art        every *texPath in Defs/ and Patches/ resolves to a PNG under Textures/
             (Graphic_Single file, Graphic_Random folder, or Graphic_Multi _north/... set),
             plus the designator icon path named in C#
  settings   all 6 RM_GraffitiSettings controls carry a tooltip; viewerReactionEnabled's
             label says it needs Sacred Marks (its only consumer is SacredGraffiti's ThoughtDef)
  review     code_review_status.py check is CLEAN on Source/*.cs, Source/Kernel/*.cs,
             validation.py, northstar_site.py
  stamp      dll_source_stamp.py check reads MATCH for RimMandrakeGraffiti.dll
  deploy     deploy_custom_mods.py --mod Graffiti (dry run) reads "in sync"

Not offline, so not here: the two GREEN rungs (their own items) and the owner's re-validation
of the hashed walk prose (plan section 5.7). Never deployed (deploy excludes .py).
"""
import glob
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
UTILS = os.path.join(REPO, "src", "RimMandrake", "Utils")
TEX = os.path.join(HERE, "Textures")
DLL = "src/RimMandrake/Graffiti/Assemblies/RimMandrakeGraffiti.dll"
SETTINGS_CS = os.path.join(HERE, "Source", "RM_GraffitiMod.cs")


def _resolves(p):
    base = os.path.join(TEX, p)
    return (os.path.isfile(base + ".png") or bool(glob.glob(os.path.join(base, "*.png")))
            or bool(glob.glob(base + "_*.png")))


def check_art():
    paths = []
    for f in sorted(glob.glob(os.path.join(HERE, "Defs", "*.xml")) + glob.glob(os.path.join(HERE, "Patches", "*.xml"))):
        for el in ET.parse(f).iter():
            if el.tag.lower().endswith("texpath") and el.text and el.text.strip():
                paths.append((os.path.basename(f), el.text.strip()))
    for f in glob.glob(os.path.join(HERE, "Source", "*.cs")):
        for m in re.finditer(r'ContentFinder<Texture2D>\.Get\("([^"]+)"', open(f, encoding="utf-8").read()):
            paths.append((os.path.basename(f), m.group(1)))
    if not paths:
        return False, "no texPath found at all: the instrument is blind"
    bad = [(f, p) for f, p in paths if not _resolves(p)]
    return not bad, "%d texture paths, %d unresolved %s" % (len(paths), len(bad), bad[:5])


def check_settings():
    src = open(SETTINGS_CS, encoding="utf-8").read()
    fields = re.findall(r"public static (?:bool|int|float) (\w+) =", src)
    body = src[src.index("DoWindowContents"):]
    # a CheckboxLabeled(label, ref field, "tooltip") or a Label(..., -1f, "tooltip") naming the field
    tipped = set(re.findall(r'CheckboxLabeled\([^;]*?ref (\w+),\s*"', body, re.S))
    for m in re.finditer(r'list\.Label\(([^;]*?)-1f,\s*"', body, re.S):
        tipped.update(f for f in fields if f in m.group(1))
    missing = [f for f in fields if f not in tipped]
    viewer = re.search(r'CheckboxLabeled\("([^"]*)", ref viewerReactionEnabled', body)
    labelled = bool(viewer and "Sacred Marks" in viewer.group(1))
    ok = len(fields) == 6 and not missing and labelled
    return ok, "%d settings, untipped %s, viewerReaction labelled=%s" % (len(fields), missing, labelled)


def check_review():
    files = (sorted(glob.glob(os.path.join(HERE, "Source", "*.cs")))
             + sorted(glob.glob(os.path.join(HERE, "Source", "Kernel", "*.cs")))
             + [os.path.join(HERE, "validation.py"), os.path.join(HERE, "northstar_site.py")])
    dirty = []
    for f in files:
        r = subprocess.run([sys.executable, os.path.join(UTILS, "code_review_status.py"), "check",
                            os.path.relpath(f, REPO)], cwd=REPO, capture_output=True, text=True)
        if not (r.stdout.strip().startswith("CLEAN") and r.returncode == 0):
            dirty.append(os.path.relpath(f, HERE))
    return not dirty, "%d files, not CLEAN: %s" % (len(files), dirty)


def check_stamp():
    r = subprocess.run([sys.executable, os.path.join(UTILS, "dll_source_stamp.py"), "check"],
                       cwd=REPO, capture_output=True, text=True)
    line = [ln for ln in r.stdout.splitlines() if ln.rstrip().endswith(DLL)]
    ok = bool(line) and line[0].startswith("MATCH")
    return ok, line[0] if line else "Graffiti DLL absent from the stamp report (exit %d)" % r.returncode


def check_deploy():
    r = subprocess.run([sys.executable, os.path.join(UTILS, "deploy_custom_mods.py"), "--mod", "Graffiti"],
                       cwd=REPO, capture_output=True, text=True)
    m = re.search(r"in sync \(\d+ files\)", r.stdout)
    return r.returncode == 0 and bool(m), m.group(0) if m else "not in sync: " + r.stdout.strip()[-300:]


def main():
    fails = 0
    for name, fn in (("art", check_art), ("settings", check_settings), ("review", check_review),
                     ("stamp", check_stamp), ("deploy", check_deploy)):
        ok, detail = fn()
        fails += not ok
        print("%-4s %-8s %s" % ("PASS" if ok else "FAIL", name, detail))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

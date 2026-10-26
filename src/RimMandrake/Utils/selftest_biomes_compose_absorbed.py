#!/usr/bin/env python3
"""biomes_compose on a synthetic src root (DIRTY_CODE_REVIEW_STANDING_LOOP_1 wave 8). Offline, private TMPDIR.

1. build() treats a manifest "absorbed" packageId as folded, the same as folded_ids() does: a composed member's
   MayRequire naming it is rewritten to the composed id, and a member's modDependencies/loadAfter on it is dropped
   from the composed About.xml (old code rewrote and dropped only the members' own ids).
2. stage_rewritten() strands no mrfix_ dir when building its link farm fails after its mkdtemp.
3. build() refuses a member whose About.xml does not parse with ComposeError (deploy_custom_mods catches only
   that), not a raw ParseError traceback.
"""
import atexit
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_priv = tempfile.mkdtemp(prefix="st_biomes_compose_absorbed_")
atexit.register(shutil.rmtree, _priv, True)
tempfile.tempdir = os.environ["TMPDIR"] = _priv

import biomes_compose as BC  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + (" " + str(detail) if not cond else ""))
    if not cond:
        FAILS.append(name)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def tree(root):
    out = set()
    for dp, _, fns in os.walk(root):
        for f in fns:
            out.add(os.path.relpath(os.path.join(dp, f), root))
    return out


QUIET = lambda *a, **k: None  # noqa: E731
src = os.path.join(_priv, "src")
tier = os.path.join(src, "RimMandrake")
write(os.path.join(tier, "Biomes.compose.json"), """{
  "target": "Fake.Biomes", "compose_wave": 0, "absorbed": ["old.absorbed"],
  "about": {"name": "Fake Biomes", "packageId": "x.composed", "author": "t", "supportedVersions": ["1.6"],
            "description": "d"},
  "shell": {"source": "Shell", "assemblies": ["Shell.dll"]},
  "entries": [{"key": "A", "source": "ModA", "label": "A", "wave": 0}]
}""")
write(os.path.join(tier, "Shell", "Assemblies", "Shell.dll"), "dll")
write(os.path.join(tier, "ModA", "About", "About.xml"),
      "<ModMetaData><name>Mod A</name><packageId>a.member</packageId>"
      "<modDependencies><li><packageId>old.absorbed</packageId><displayName>Old</displayName></li>"
      "<li><packageId>keep.dep</packageId><displayName>Keep</displayName></li></modDependencies>"
      "<loadAfter><li>old.absorbed</li><li>keep.after</li></loadAfter></ModMetaData>")
write(os.path.join(tier, "ModA", "Defs", "a.xml"),
      '<Defs><ThingDef MayRequire="old.absorbed"><defName>X</defName></ThingDef>'
      '<ThingDef MayRequire="keep.dep"><defName>Y</defName></ThingDef></Defs>')

# sanity: folded_ids already counts the absorbed id (the instrument the build must agree with)
check("sanity: folded_ids maps the absorbed id", BC.folded_ids(src).get("old.absorbed") == "x.composed",
      BC.folded_ids(src))

name, out, extra = BC.build(src, tree, [], log=QUIET)
try:
    txt = open(os.path.join(out, "Biomes", "A", "Defs", "a.xml"), encoding="utf-8").read()
    check("member MayRequire on an absorbed id is rewritten to the composed id",
          'MayRequire="x.composed"' in txt and "old.absorbed" not in txt, txt)
    check("unrelated MayRequire untouched", 'MayRequire="keep.dep"' in txt, txt)
    ab = ET.parse(os.path.join(out, "About", "About.xml")).getroot()
    deps = [(li.findtext("packageId") or "").strip() for li in ab.findall("modDependencies/li")]
    after = [(li.text or "").strip() for li in ab.findall("loadAfter/li")]
    check("absorbed id dropped from composed modDependencies", deps == ["keep.dep"], deps)
    check("absorbed id dropped from composed loadAfter", after == ["keep.after"], after)
finally:
    shutil.rmtree(os.path.dirname(out), ignore_errors=True)
check("good build's dir removed by the caller", os.listdir(_priv) == ["src"], os.listdir(_priv))

# 2. stage_rewritten: a failing link farm strands nothing
mod = os.path.join(_priv, "src", "Plain")
write(os.path.join(mod, "Defs", "bad.xml"), '<Defs><X MayRequire="a.member"/></Defs>')
write(os.path.join(mod, "Defs", "ok.xml"), "<Defs/>")
real = BC.os.symlink


def boom(*a, **k):
    raise OSError("injected: symlink not permitted")


BC.os.symlink = boom
try:
    BC.stage_rewritten(mod, {"a.member": "x.composed"}, log=QUIET)
    check("injected symlink failure propagates", False, "returned")
except OSError:
    check("injected symlink failure propagates", True)
finally:
    BC.os.symlink = real
check("failed stage strands no mrfix_ dir", os.listdir(_priv) == ["src"], os.listdir(_priv))

# 3. a member About.xml that does not parse is a ComposeError
write(os.path.join(tier, "ModA", "About", "About.xml"), "<ModMetaData><name>broken & </ModMetaData>")
try:
    BC.build(src, tree, [], log=QUIET)
    check("malformed member About.xml refused", False, "build returned")
except BC.ComposeError as e:
    check("malformed member About.xml refused with ComposeError", "About.xml" in str(e), e)
except ET.ParseError as e:
    check("malformed member About.xml refused with ComposeError", False, "raw ParseError: %s" % e)

print("ALL PASS" if not FAILS else "FAILED: %s" % FAILS)
sys.exit(1 if FAILS else 0)

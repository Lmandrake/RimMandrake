#!/usr/bin/env python3
"""Selftest for armoury_donor_class_guard.py and donor_class_guard.py.

    python3 src/RimMandrake/Utils/selftest_armoury_donor_class_guard.py

Item RIMMANDRAKE_LOAD_ARMOURY_ABSORBED_DEFS_WITHOUT_LIGHTSABER_TYPES. The live fault: on the 26-mod tier
explosiveknockback_visit, Armoury's absorbed Lightsaber / BigAndSmall / XmlExtensions / WHands nodes failed their defs at
load. Checked here:
  real mod     the shipped Armoury reads PASS, and it read files and donor-class nodes (an instrument that sees nothing
               must not pass)
  planted      each shape of the fault goes red: an unguarded comp <li>, a def type, a *Class field, a guard on a field
               RimWorld ignores, a guard naming the wrong mod, a MayRequireAnyOf with a non-donor member, a top-level
               patch Operation, a FindMod (<match> or <nomatch>: the patch is parsed before FindMod runs), a reference
               to a def only the donor defines
  green        each honoured guard stays green: <li> guard, an ancestor <li> or def guard, a def a patch adds, a
               MayRequireAnyOf of donor ids only, a FindMod <match>, a sequence <li>, a non-donor class
  blind        no XML file, or a file that does not parse -> exit 2 UNMEASURED
  --fix        repairs a planted copy to PASS and keeps its comments
  generator    guard_element (the hook in absorption_content_fixes / the kyber generator) rebuilds the shipped guard on
               the parent's Kyber def
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import armoury_donor_class_guard as L  # noqa: E402
import donor_class_guard as G  # noqa: E402

FAILS = []
REPO = L.REPO


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def run(mod, *extra):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = L.main(["--mod-dir", mod] + list(extra))
    return rc, buf.getvalue()


def mod_with(defs=None, patches=None):
    d = tempfile.mkdtemp(prefix="donor_guard_")
    for sub, body in (("Defs", defs), ("Patches", patches)):
        if body is not None:
            os.makedirs(os.path.join(d, sub))
            root = "Defs" if sub == "Defs" else "Patch"
            with open(os.path.join(d, sub, "t.xml"), "w") as f:
                f.write('<?xml version="1.0" encoding="utf-8"?>\n<!-- keep me -->\n<%s>\n%s\n</%s>\n' % (root, body, root))
    return d


THING = '<ThingDef><defName>X</defName><comps>%s</comps></ThingDef>'
BAD = {
    "comp li": (THING % '<li Class="Lightsaber.CompProperties_GlowerOptions"><glowRadius>1</glowRadius></li>', None),
    "def type": ('<Lightsaber.HiltPartDef><defName>H</defName></Lightsaber.HiltPartDef>', None),
    "Class field": (THING % '<li><nodeClass>BigAndSmall.PawnRenderNode_UltimateApparel</nodeClass></li>', None),
    "guard on ignored field": ('<GenStepDef><defName>G</defName><genStep MayRequire="lee.theforce.lightsaber" '
                               'Class="Lightsaber.GenStep_ScatterLightsaberCrystals"/></GenStepDef>', None),
    "wrong mod": (THING % '<li MayRequire="lee.theforce.standalone" Class="Lightsaber.CompProperties_ColorCrystal"/>', None),
    "AnyOf with non-donor": (THING % '<li MayRequireAnyOf="lee.theforce.lightsaber,ludeon.rimworld.royalty" '
                                     'Class="Lightsaber.CompProperties_ColorCrystal"/>', None),
    "top-level patch Operation": (None, '<Operation Class="XmlExtensions.OptionalPatch"><key>k</key></Operation>'),
    "FindMod nomatch only": (None, '<Operation Class="PatchOperationFindMod"><mods><li>XML Extensions</li></mods>'
                                   '<nomatch Class="XmlExtensions.OptionalPatch"/></Operation>'),
    # the live miss: ArchBig cold load 2026-11-26 04:40 PST still logged the class under a FindMod <match>
    "FindMod match": (None, '<Operation Class="PatchOperationFindMod"><mods><li>XML Extensions</li></mods>'
                            '<match Class="XmlExtensions.OptionalPatch"/></Operation>'),
    # the second live line of that load: a reference to the donor-only ThingCategoryDef
    "donor-only def ref": ('<ThingDef><defName>K</defName><thingCategories><li>Force_KyberCrystals</li></thingCategories>'
                           '</ThingDef>', None),
}
GOOD = {
    "li guard": (THING % '<li MayRequire="lee.theforce.lightsaber" Class="Lightsaber.CompProperties_GlowerOptions"/>', None),
    "mixed-case guard": (THING % '<li MayRequire="RedMattis.BetterPrerequisites"><nodeClass>BigAndSmall.X</nodeClass></li>', None),
    "def guard": ('<GenStepDef MayRequire="lee.theforce.lightsaber"><defName>G</defName>'
                  '<genStep Class="Lightsaber.GenStep_ScatterLightsaberCrystals"/></GenStepDef>', None),
    "ancestor li": (THING % '<li MayRequire="redmattis.betterprerequisites" Class="BigAndSmall.P">'
                            '<nodeClass>BigAndSmall.N</nodeClass></li>', None),
    "AnyOf of donor ids": (THING % '<li MayRequireAnyOf="guy762.kotordroids,killathon.artificialbeings" '
                                   'Class="ArtificialBeings.StockGenerator_Colonists"/>', None),
    "non-donor class": (THING % '<li Class="VEF.AnimalBehaviours.CompProperties_HediffEffecter"/>', None),
    "guarded donor-only def ref": ('<ThingDef><defName>K</defName><thingCategories>'
                                   '<li MayRequire="lee.theforce.lightsaber">Force_KyberCrystals</li></thingCategories></ThingDef>', None),
    "patch value li": (None, '<Operation Class="PatchOperationAdd"><xpath>Defs/ThingDef</xpath><value>'
                             '<li MayRequire="lee.theforce.lightsaber" Class="Lightsaber.C"/></value></Operation>'),
    "patch adds a guarded def": (None, '<Operation Class="PatchOperationAdd"><xpath>Defs</xpath><value>'
                                       '<Lightsaber.HiltPartDef MayRequire="lee.theforce.lightsaber"/></value></Operation>'),
    "sequence li": (None, '<Operation Class="PatchOperationSequence"><operations>'
                          '<li MayRequire="imranfish.xmlextensions" Class="XmlExtensions.OptionalPatch"/></operations></Operation>'),
}

# real mod
rc, out = run(L.DEFAULT_MOD)
last = out.strip().splitlines()[-1] if out.strip() else ""
nums = [int(w) for w in last.replace(",", " ").split() if w.isdigit()]
check(rc == 0 and len(nums) == 3 and nums[0] > 100 and nums[1] > 50 and nums[2] == 0,
      "real Armoury: PASS with files and donor-class nodes seen (%s)" % last)

for name, (defs, patches) in BAD.items():
    rc, out = run(mod_with(defs, patches))
    check(rc == 1 and "UNGUARDED" in out, "planted red: %s (exit %d)" % (name, rc))
for name, (defs, patches) in GOOD.items():
    rc, out = run(mod_with(defs, patches))
    check(rc == 0, "stays green: %s (exit %d)%s" % (name, rc, "" if rc == 0 else " " + out.strip()[:200]))

check(run(tempfile.mkdtemp(prefix="donor_guard_empty_"))[0] == 2, "blind: no XML file -> exit 2 UNMEASURED")
d = mod_with("<ThingDef>")
check(run(d)[0] == 2, "blind: a file that does not parse -> exit 2 UNMEASURED")

# --fix on every fixable planted shape at once
d = mod_with("\n".join(v[0] for k, v in BAD.items() if v[0] and k not in ("wrong mod",)))
rc, out = run(d, "--fix")
txt = open(os.path.join(d, "Defs", "t.xml")).read()
check(rc == 0 and "<!-- keep me -->" in txt, "--fix repairs the planted defs to PASS and keeps comments (exit %d)" % rc)
rc, out = run(mod_with(BAD["wrong mod"][0]), "--fix")
check(rc == 0, "--fix adds the donor beside a wrong-mod MayRequire (exit %d)" % rc)
rc, out = run(mod_with(None, BAD["top-level patch Operation"][1]), "--fix")
check(rc == 1 and "PatchOperationSequence" in out, "--fix leaves a top-level patch Operation red, naming the sequence <li> it needs")

# generator hook on the Kyber def as it was before the guards (216f6e0395, the parent of the fix)
KY = "src/RimStarWars/Armoury/Defs/Absorbed_TheForceLightsaber/ThingDefs_Misc/Absorbed_TheForceLightsaber_Kyber.xml"
old = subprocess.run(["git", "-C", REPO, "show", "216f6e03952cb0a17cf428215e1740e5029a58b8:" + KY],
                     capture_output=True, text=True, timeout=120).stdout   # hang guard; a git show takes under 1 s
check(bool(old) and 'Class="Lightsaber.CompProperties_GlowerOptions"' in old and 'MayRequire="lee.theforce.lightsaber" Class' not in old,
      "the pre-fix Kyber file is readable and unguarded")
if old:
    root = ET.fromstring(old.encode("utf-8"))
    added = sum(G.guard_element(el, note=lambda m: None) for el in list(root))
    check(added >= 1 and not G.unguarded(root, False), "guard_element guards the pre-fix Kyber def (%d guards)" % added)
    again = sum(G.guard_element(el, note=lambda m: None) for el in list(root))
    check(again == 0, "guard_element is idempotent: a second pass adds nothing")

print("FAILED %d" % len(FAILS) if FAILS else "PASS")
sys.exit(1 if FAILS else 0)

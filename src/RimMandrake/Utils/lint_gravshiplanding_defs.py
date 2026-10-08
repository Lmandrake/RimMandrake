#!/usr/bin/env python3
"""Offline structure lint of GravshipLanding (mandrake.rm.gravshiplanding). The mod has no Defs: it is one Harmony postfix, one
setting and a live proof hook. Generic lint via lint_mod_defs.py (settings, compile-listed), plus:

  gl-harmony-id    GravshipLandingMod.HarmonyId equals the About packageId (two ids would let a second copy double-patch)
  gl-patch-target  exactly one [HarmonyPatch] and it targets GenStep_GravshipMarker.Generate with a [HarmonyPostfix]
  gl-gates-shared  the postfix and the live proof both go through RevealIfArrival, which calls the kernel's Enabled and Reveal
                   (a second copy of the gate in the proof would make the proof test something the game does not run)
  gl-about         About names Harmony as a dependency and supports 1.6; the packageId is lowercase mandrake.rm.*
  gl-kernel-pure   Kernel/*.cs names no Verse / RimWorld / UnityEngine / HarmonyLib

    python3 src/RimMandrake/Utils/lint_gravshiplanding_defs.py [--quiet] [--mod-dir D]
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))


def main(argv):
    rc = lint_mod_defs.run("GravshipLanding", argv, require_xml=False)
    if rc == 2:
        return 2
    mod = os.path.join(REPO, "src", "RimMandrake", "GravshipLanding")
    if "--mod-dir" in argv:
        mod = argv[argv.index("--mod-dir") + 1]
    errs = []
    E = lambda c, m: errs.append("ERROR %s: %s" % (c, m))
    rd = lambda *p: open(os.path.join(mod, *p), encoding="utf-8-sig").read()
    mod_cs, patch_cs, proof_cs = rd("Source", "GravshipLandingMod.cs"), rd("Source", "Patch_GenStep_GravshipMarker.cs"), rd("Source", "GravshipLandingProof.cs")
    try:
        about = ET.fromstring(rd("About", "About.xml"))
    except (OSError, ET.ParseError):
        about = None
    hid = re.search(r'HarmonyId = "([^"]+)"', mod_cs)
    pkg = (about.findtext("packageId") if about is not None else None)
    if about is None:
        # --mod-dir copies drop About: read the repo's
        about = ET.parse(os.path.join(REPO, "src", "RimMandrake", "GravshipLanding", "About", "About.xml")).getroot()
        pkg = about.findtext("packageId")
    if not hid or hid.group(1) != (pkg or "").strip():
        E("gl-harmony-id", "HarmonyId %r differs from the About packageId %r" % (hid.group(1) if hid else None, pkg))
    attrs = re.findall(r"^\s*\[HarmonyPatch\((.*)\)\]\s*$", "\n".join(open(f, encoding="utf-8-sig").read() for f in glob.glob(os.path.join(mod, "Source", "*.cs"))), re.M)
    if attrs != ["typeof(GenStep_GravshipMarker), nameof(GenStep_GravshipMarker.Generate)"]:
        E("gl-patch-target", "expected one patch on GenStep_GravshipMarker.Generate, found %s" % attrs)
    if "[HarmonyPostfix]" not in patch_cs:
        E("gl-patch-target", "the patch is not a postfix (the fog grid is only final after the vanilla gen step)")
    if "PatchAll(Assembly.GetExecutingAssembly())" not in mod_cs:
        E("gl-patch-target", "the mod never calls PatchAll")
    if not re.search(r"RevealIfArrival\(map, parms\.gravship != null", patch_cs):
        E("gl-gates-shared", "the postfix does not call RevealIfArrival with parms.gravship != null")
    if proof_cs.count("Patch_GenStep_GravshipMarker_Generate.RevealIfArrival(") < 3:
        E("gl-gates-shared", "the live proof no longer drives the shipped RevealIfArrival in all three arms (arrival, setting off, not an arrival)")
    if not re.search(r"RM_LandingKernel\.Enabled\(ModsConfig\.OdysseyActive, arrival, GravshipLandingSettings\.revealOutdoorsBeforeLanding\)", patch_cs):
        E("gl-gates-shared", "RevealIfArrival does not gate on the kernel's Enabled(Odyssey, arrival, setting)")
    if "RM_LandingKernel.Reveal(" not in patch_cs:
        E("gl-gates-shared", "RevealIfArrival does not use the kernel's Reveal")
    deps = [li.findtext("packageId") for li in about.findall("modDependencies/li")]
    if "brrainz.harmony" not in deps:
        E("gl-about", "About does not depend on brrainz.harmony (%s)" % deps)
    if "1.6" not in [li.text for li in about.findall("supportedVersions/li")]:
        E("gl-about", "About does not support 1.6")
    if not re.fullmatch(r"mandrake\.rm\.[a-z0-9]+", pkg or ""):
        E("gl-about", "packageId %r is not mandrake.rm.<lowercase>" % pkg)
    for kf in glob.glob(os.path.join(mod, "Source", "Kernel", "*.cs")):
        for n, line in enumerate(open(kf, encoding="utf-8-sig").read().splitlines(), 1):
            if re.match(r"\s*using\s+(Verse|RimWorld|UnityEngine|HarmonyLib)\b", line):
                E("gl-kernel-pure", "%s:%d `%s`" % (os.path.basename(kf), n, line.strip()))
    for e in errs:
        print(e)
    return 1 if (errs or rc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

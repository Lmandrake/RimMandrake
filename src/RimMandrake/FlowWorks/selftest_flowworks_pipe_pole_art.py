"""PIPE_POLES_BUILD_SAG_WITH_SUBSTANCE phase 4 stand-in art: every texPath in Defs/Machinery/RM_PipePoles.xml (the pole def
and its four ThingStyleDefs) resolves to a PNG in Gimme Some Slack's Textures folder (the stand-in is the GSS mast of that
look until LINE_WIDTH_JUDGE_ARMS_NOT_INCLUDED). The C# SelfTest's PipePole_P3 case cannot see this: the winbuild stage
copies no Textures folder (winbuild.RSYNC_EXCLUDES), so it checks the path shape only and this WSL check owns the file.

Can-fail: --canfail points one texPath at a name that does not exist and must FAIL.

    python3 src/RimMandrake/FlowWorks/selftest_flowworks_pipe_pole_art.py
"""
from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DEFS = os.path.join(HERE, "Defs", "Machinery", "RM_PipePoles.xml")
GSS_TEX = os.path.join(HERE, "..", "GimmeSomeSlack", "Textures")
LOOKS = ("Scrapper", "Industrial", "Modern", "Futuristic")


def texpaths(path=DEFS):
    root = ET.parse(path).getroot()
    out = []
    for el in root:
        tp = el.find("graphicData/texPath")
        if tp is not None and tp.text:
            out.append((el.findtext("defName"), tp.text.strip()))
    return out


def fails(paths):
    bad = []
    for name, tex in paths:
        png = os.path.join(GSS_TEX, *tex.split("/")) + ".png"
        if not os.path.isfile(png):
            bad.append("%s: %s has no PNG at %s" % (name, tex, png))
    return bad


def main():
    paths = texpaths()
    styles = [n for n, _ in paths if n and n.startswith("RM_PipePole_")]
    errs = []
    if len(paths) != 5:
        errs.append("expected 5 texPaths (pole + 4 looks), read %d" % len(paths))
    if sorted(styles) != sorted("RM_PipePole_" + l for l in LOOKS):
        errs.append("style defs are not the four looks: %r" % styles)
    errs += fails(paths)
    canfail = fails([("canfail", "RimMandrake/GimmeSomeSlack/Aerial/Styles/Scrapper/NoSuchMast")])
    if not canfail:
        errs.append("can-fail: a missing PNG was not reported")
    if "--canfail" in sys.argv:
        errs = canfail
    for e in errs:
        print("FAIL", e)
    print("pipe pole art: %d texPaths, %d failing" % (len(paths), len(errs)))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())

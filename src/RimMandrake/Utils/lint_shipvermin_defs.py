#!/usr/bin/env python3
"""Offline lint of the ShipVermin mod (its defs, patches and settings vs the C#): see lint_mod_defs.py for
the checks, plus the kernel guards (Verse-free, compiled into the mod and the fuzz project) and the nest/leech shared population ceiling.

    python3 src/RimMandrake/Utils/lint_shipvermin_defs.py [--mod-dir <dir>] [--quiet]
"""
import contextlib
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_mod_defs  # noqa: E402
from lint_kernel_guards import kernel_guards  # noqa: E402


def nest_findings(mod_dir):
    """The nest comp's defaults must keep sharing ONE pressure ceiling with the hull leech's breeder (group tag + hard cap), and the roster
    kinds the settings name must exist as PawnKindDefs of this mod."""
    errs = []
    defs = {}
    for root, _, files in os.walk(os.path.join(mod_dir, "Defs")):
        for f in files:
            if f.endswith(".xml"):
                for d in ET.parse(os.path.join(root, f)).getroot():
                    if d.findtext("defName"):
                        defs[(d.tag, d.findtext("defName"))] = d
    if len(defs) < 8:
        return ["ERROR shipvermin-nest: only %d defs parsed (sanity probe: Defs moved?)" % len(defs)]
    mod_cs = open(os.path.join(mod_dir, "Source", "RM_ShipVerminMod.cs"), encoding="utf-8-sig").read()
    for kind in re.findall(r'\("(RM_\w+)", \(\) =>', mod_cs):
        if ("PawnKindDef", kind) not in defs:
            errs.append("ERROR shipvermin-nest: nest roster names %s, which is no PawnKindDef of this mod" % kind)
    props = open(os.path.join(mod_dir, "Source", "RM_CompProperties_VerminNest.cs"), encoding="utf-8-sig").read()
    tag = re.search(r'populationGroupTag = "(\w+)"', props)
    cap = re.search(r"populationHardCap = (\d+)", props)
    if not tag or not cap:
        errs.append("ERROR shipvermin-nest: cannot read the nest comp's population defaults")
        return errs
    leech = defs.get(("PawnKindDef", "RM_Skivvik"))
    thing = defs.get(("ThingDef", "RM_Skivvik"))
    text = ET.tostring(thing, encoding="unicode") if thing is not None else ""
    m = re.search(r"<populationGroupTag>([^<]+)</populationGroupTag>", text)
    c = re.search(r"<populationHardCap>(\d+)</populationHardCap>", text)
    if m and m.group(1) != tag.group(1):
        errs.append("ERROR shipvermin-nest: the nest's group tag %s differs from the hull leech's %s, so they stop sharing a ceiling" % (tag.group(1), m.group(1)))
    if c and c.group(1) != cap.group(1):
        errs.append("ERROR shipvermin-nest: the nest's hard cap %s differs from the hull leech's %s" % (cap.group(1), c.group(1)))
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "ShipVermin")
    rc = lint_mod_defs.run("ShipVermin", argv, instance_settings=False)
    errs = nest_findings(mod_dir) + kernel_guards(mod_dir, "RM_ShipVermin.csproj", "SelfTest/RimMandrakeShipVermin.SelfTest.csproj", "shipvermin-kernel")
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)

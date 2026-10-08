#!/usr/bin/env python3
"""Offline lint of the SeaShores mod (its one TileMutatorDef, its Harmony/worker classes and settings vs the C#): see lint_mod_defs.py for
the checks, plus the kernel guards (Verse-free, compiled into the mod and the fuzz project) and the TileMutatorDef's shape.

    python3 src/RimMandrake/Utils/lint_seashores_defs.py [--mod-dir <dir>] [--quiet]
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


def mutator_findings(mod_dir):
    """RM_SeaCoast must stay a drop-in twin of vanilla Coast (same category, genOrder, priority) with no coastSidesRange."""
    errs = []
    path = os.path.join(mod_dir, "Defs", "TileMutatorDefs", "RM_SeaCoast.xml")
    if not os.path.exists(path):
        return ["ERROR seashores-mutator: Defs/TileMutatorDefs/RM_SeaCoast.xml is missing"]
    d = ET.parse(path).getroot().find("TileMutatorDef")
    if d is None or d.findtext("defName") != "RM_SeaCoast":
        return ["ERROR seashores-mutator: no TileMutatorDef RM_SeaCoast in RM_SeaCoast.xml"]
    cats = [li.text for li in d.findall("categories/li")]
    if "Coast" not in cats:
        errs.append("ERROR seashores-mutator: categories lack Coast (Tile.AddMutator would not replace a vanilla Coast)")
    if d.findtext("genOrder") != "100":
        errs.append("ERROR seashores-mutator: genOrder %s differs from vanilla Coast's 100" % d.findtext("genOrder"))
    if d.findtext("priority") != "0":
        errs.append("ERROR seashores-mutator: priority %s differs from vanilla Coast's 0 (a higher one logs conflicts, a lower one never replaces)" % d.findtext("priority"))
    if d.find("coastSidesRange") is not None:
        errs.append("ERROR seashores-mutator: coastSidesRange is set; vanilla counts only BiomeDefOf.Ocean/Lake neighbours, so the def would refuse every tile beside our seas")
    if (d.findtext("workerClass") or "") != "RimMandrake.SeaShores.RM_TileMutatorWorker_SeaCoast":
        errs.append("ERROR seashores-mutator: workerClass is not RM_TileMutatorWorker_SeaCoast")
    return errs


if __name__ == "__main__":
    argv = sys.argv[1:]
    mod_dir = argv[argv.index("--mod-dir") + 1] if "--mod-dir" in argv else os.path.join(os.path.dirname(HERE), "SeaShores")
    rc = lint_mod_defs.run("SeaShores", argv, instance_settings=True)
    errs = mutator_findings(mod_dir) + kernel_guards(mod_dir, "RM_SeaShores.csproj", "SelfTest/Fuzz/RimMandrakeSeaShores.Fuzz.csproj", "seashores-kernel")
    for e in errs:
        print(e)
    sys.exit(1 if (rc == 1 or errs) else rc)

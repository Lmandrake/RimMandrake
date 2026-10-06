#!/usr/bin/env python3
"""selftest_flowworks_swale.py — static half of the swale (CRACKEDLANDS_MECHANICS_BUILD_1 §1).

Reads the shipped source, def and validation and reds on each break the swale's bounds exist to
prevent: the tick not gated on swaleEnabled or on IsFed, the cap (top rung never stepped) gone,
excavated cells stepped, a non-water fluid feeding it, the ladder not Sand->Soil->SoilRich, the
setting missing from Scribe/UI/suite.toggles, the .cs missing from the csproj (compiles into
nothing), the placeworker not wired. Mutants are applied to in-memory copies, never the files.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FW = Path(__file__).resolve().parent
CS = FW / "Source" / "Swale" / "RM_Swale.cs"
MOD = FW / "Source" / "RimMandrakeFlowWorksMod.cs"
PROJ = FW / "Source" / "RimMandrake_FlowWorks.csproj"
DEFS = FW / "Defs" / "Canals" / "ThingDefs" / "FlowWorks_ThingDefs.xml"
VAL = FW / "northstar" / "extensions.py"   # the swale chain moved out of validation.py (densification 2026-10-05)


def findings(cs, mod, proj, defs, val):
    out = []
    tick = re.search(r"public override void CompTickRare\(\)(.*?)\n\t\t}\n", cs, re.S)
    body = tick.group(1) if tick else ""
    if "RimMandrakeFlowWorksSettings.swaleEnabled" not in body:
        out.append("CompTickRare not gated on swaleEnabled")
    if "RM_SwaleRules.IsFed(" not in body:
        out.append("CompTickRare not gated on IsFed")
    step = re.search(r"public static bool TryStep\((.*?)\n\t\t}\n", cs, re.S)
    sb = step.group(1) if step else ""
    if "r >= props.ladder.Count - 1" not in sb:
        out.append("TryStep lost the cap (top rung must never step)")
    if "IsExcavated(c)" not in sb:
        out.append("TryStep may step excavated cells")
    if "BaseTerrainAt(c)" not in sb:
        out.append("TryStep does not read base terrain")
    fed = re.search(r"public static bool IsFed\((.*?)\n\t\t}\n", cs, re.S)
    if not fed or 'fluid.defName == "RM_Fluid_Water"' not in fed.group(1):
        out.append("IsFed accepts a non-water fluid")
    if 'Scribe_Values.Look(ref swaleEnabled, "swaleEnabled", true)' not in mod:
        out.append("swaleEnabled not Scribed under its own key, default true")
    if not re.search(r'CheckboxLabeled\("[^"]*",\s*ref swaleEnabled,', mod):
        out.append("swaleEnabled has no checkbox in the settings window")
    if 'Compile Include="Swale\\RM_Swale.cs"' not in proj:
        out.append("RM_Swale.cs missing from the csproj (EnableDefaultCompileItems false)")
    root = ET.fromstring(defs.encode())
    d = next((x for x in root.iter("ThingDef") if x.findtext("defName") == "RM_Swale"), None)
    if d is None:
        out.append("RM_Swale ThingDef missing")
    else:
        ladder = [li.text for li in d.findall("comps/li/ladder/li")]
        if ladder != ["Sand", "Soil", "SoilRich"]:
            out.append("ladder is %r, ruled Sand->Soil->SoilRich" % ladder)
        if (d.findtext("tickerType") or "") != "Rare":
            out.append("RM_Swale tickerType is not Rare: CompTickRare never runs")
        if "PlaceWorker_SwaleOnExcavation" not in "".join(li.text or "" for li in d.findall("placeWorkers/li")):
            out.append("placeworker not wired")
    if '"swaleEnabled"' not in val or '@suite.chain("swale_enrichment")' not in val:
        out.append("validation lacks the swaleEnabled toggle or its chain")
    return out


def main():
    src = [p.read_text() for p in (CS, MOD, PROJ, DEFS, VAL)]
    live = findings(*src)
    print("shipped:", live or "ok")
    fails = list(live)
    cs, mod, proj, defs, val = src
    muts = {
        "tick ungated": (cs.replace("if (!RimMandrakeFlowWorksSettings.swaleEnabled || parent.Map == null)", "if (parent.Map == null)"), mod, proj, defs, val),
        "cap removed": (cs.replace("r >= props.ladder.Count - 1", "r >= props.ladder.Count"), mod, proj, defs, val),
        "tar feeds": (cs.replace('fluid.defName == "RM_Fluid_Water"', "fluid != null"), mod, proj, defs, val),
        "dropped from csproj": (cs, mod, proj.replace('Compile Include="Swale\\RM_Swale.cs"', ""), defs, val),
        "not scribed": (cs, mod.replace('Scribe_Values.Look(ref swaleEnabled, "swaleEnabled", true);', ""), proj, defs, val),
        "ladder reordered": (cs, mod, proj, defs.replace("<li>Sand</li>\n          <li>Soil</li>", "<li>Soil</li>\n          <li>Sand</li>"), val),
        "ticker never": (cs, mod, proj, defs.replace("<tickerType>Rare</tickerType>\n    <designationCategory>Structure</designationCategory>\n    <statBases>\n      <MaxHitPoints>80", "<tickerType>Never</tickerType>\n    <designationCategory>Structure</designationCategory>\n    <statBases>\n      <MaxHitPoints>80"), val),
    }
    for name, args in muts.items():
        red = bool(findings(*args))
        print("mutant %s: %s" % (name, "red" if red else "STAYED GREEN"))
        if not red:
            fails.append("mutant stayed green: " + name)
    print("FAIL" if fails else "PASS", *fails, sep="\n  ")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

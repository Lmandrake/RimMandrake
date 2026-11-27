#!/usr/bin/env python3
"""T_FORGE_GATES_GONE (tree check C_forge_gates_gone; rules R_forge and R_riders): after the alloy forge's onboarding, the projects
RM_WM_AlloyForgeRestoration and RM_WM_PlasteelAlloying and the settings alloyForgeProgressiveGate and plasteelAlloyEnabled are
absent, and ResearchRetag names neither project. The forge's early research step and its two switches end when the forge is an
ancient machine: plasteel and gravlite are then processes of the Refurbished forge alone, with no project of their own.

    python3 src/RimMandrake/WreckedMachines/selftest_wm_forge_gates_gone.py

ROWS
  forge_onboarded   the onboarding table (Defs/MachineLines) holds the line `alloyforge` for VFEFactory_AutomatedAlloyForge
  projects_gone     no def of this mod is named RM_WM_AlloyForgeRestoration or RM_WM_PlasteelAlloying
  settings_gone     this mod's C# names neither alloyForgeProgressiveGate nor plasteelAlloyEnabled, and the patch
                    Patches/WreckedMachines_AlloyForgeGates.xml is gone
  retag_clean       no file of RimUtinni/ResearchRetag names either project (comments left out)
  armoury_follows   the Armoury's durasteel patch adds its process to the forge's Kludged and Refurbished level defs

Until the forge is onboarded this check is red on forge_onboarded, and the gates are expected to be there: red first. The landing
that onboards the forge removes the gates and edits ResearchRetag and the Armoury in the same change (rule R_neighbour_names).
Exit 0 all PASS; 1 a FAIL; 2 COULD NOT LOOK. Planted faults on a made whole state show each row able to fail.
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", ".."))
PROJECTS = ("RM_WM_AlloyForgeRestoration", "RM_WM_PlasteelAlloying")
SETTINGS = ("alloyForgeProgressiveGate", "plasteelAlloyEnabled")
FORGE = "VFEFactory_AutomatedAlloyForge"
ROWS = ("forge_onboarded", "projects_gone", "settings_gone", "retag_clean", "armoury_follows")


def _text(p):
    return open(p, encoding="utf-8", errors="replace").read()


def _no_xml_comments(t):
    return re.sub(r"<!--.*?-->", "", t, flags=re.S)


def state():
    """What the rows read, as plain data (so that a fault can be planted in a copy of it)."""
    st = {"lines": {}, "defnames": set(), "cs": "", "patch": os.path.isfile(os.path.join(HERE, "Patches", "WreckedMachines_AlloyForgeGates.xml")),
          "retag": "", "armoury": "", "files": 0}
    for f in glob.glob(os.path.join(HERE, "Defs", "**", "*.xml"), recursive=True) + glob.glob(os.path.join(HERE, "Patches", "**", "*.xml"), recursive=True):
        st["files"] += 1
        root = ET.parse(f).getroot()
        for d in root.iter():
            if d.tag == "defName" and d.text:
                st["defnames"].add(d.text.strip())
            if d.tag == "RimMandrake.WreckedMachines.RM_MachineLineDef":
                st["lines"][(d.findtext("key") or "").strip()] = {k: (d.findtext(k) or "").strip() for k in ("original", "kludged", "refurbished")}
    for f in glob.glob(os.path.join(HERE, "Source", "*.cs")):
        st["cs"] += re.sub(r"//[^\n]*", "", _text(f)) + "\n"
    for f in glob.glob(os.path.join(SRC, "RimUtinni", "ResearchRetag", "**", "*.xml"), recursive=True):
        st["retag"] += _no_xml_comments(_text(f))
    for f in glob.glob(os.path.join(SRC, "RimStarWars", "Armoury", "Patches", "*.xml")):
        st["armoury"] += _no_xml_comments(_text(f))
    return st


def rows_for(st):
    bad = {r: [] for r in ROWS}
    line = st["lines"].get("alloyforge")
    if line is None or line["original"] != FORGE:
        bad["forge_onboarded"].append("the onboarding table has no line `alloyforge` for %s (lines: %s)" % (FORGE, sorted(st["lines"])))
    for p in PROJECTS:
        if p in st["defnames"]:
            bad["projects_gone"].append("the project %s is still a def of this mod" % p)
        if p in st["retag"]:
            bad["retag_clean"].append("ResearchRetag still names %s" % p)
    for s in SETTINGS:
        if re.search(r"\b%s\b" % s, st["cs"]):
            bad["settings_gone"].append("the C# still names %s" % s)
    if st["patch"]:
        bad["settings_gone"].append("Patches/WreckedMachines_AlloyForgeGates.xml is still there")
    for lvl in ("kludged", "refurbished"):
        name = (line or {}).get(lvl) or "RM_WM_AutomatedAlloyForge_%s" % lvl.capitalize()
        if not re.search(r'defName="%s"\]/comps/li\[@Class="PipeSystem\.CompProperties_AdvancedResourceProcessor"\]/processes' % re.escape(name), st["armoury"]):
            bad["armoury_follows"].append("no Armoury patch adds a process to %s" % name)
    return bad


def _whole():
    a = "".join('<xpath>/Defs/ThingDef[defName="RM_WM_AutomatedAlloyForge_%s"]/comps/li[@Class="PipeSystem.CompProperties_AdvancedResourceProcessor"]/processes</xpath>' % l
                for l in ("Kludged", "Refurbished"))
    return {"lines": {"alloyforge": {"original": FORGE, "kludged": "RM_WM_AutomatedAlloyForge_Kludged", "refurbished": "RM_WM_AutomatedAlloyForge_Refurbished"}},
            "defnames": {"RM_WM_AutomatedAlloyForgeKludging"}, "cs": "class S { bool x; }", "patch": False, "retag": "<tab>RUT_Tree_Workshop</tab>", "armoury": a, "files": 9}


PLANTS = (("forge_onboarded", lambda s: s["lines"].pop("alloyforge")), ("projects_gone", lambda s: s["defnames"].add(PROJECTS[1])),
          ("settings_gone", lambda s: s.__setitem__("cs", "public static bool plasteelAlloyEnabled = true;")),
          ("settings_gone", lambda s: s.__setitem__("patch", True)), ("retag_clean", lambda s: s.__setitem__("retag", 'defName="%s"' % PROJECTS[0])),
          ("armoury_follows", lambda s: s.__setitem__("armoury", s["armoury"].replace("_Kludged", "_Kludge"))))


def main():
    try:
        st = state()
    except (OSError, ET.ParseError) as e:
        print("T_FORGE_GATES_GONE: COULD NOT LOOK: %s" % e)
        return 2
    if st["files"] < 5 or not st["cs"] or not st["retag"] or not st["armoury"]:
        print("T_FORGE_GATES_GONE: COULD NOT LOOK: read %d def files, C# %d chars, ResearchRetag %d chars, Armoury patches %d chars (sanity probe)"
              % (st["files"], len(st["cs"]), len(st["retag"]), len(st["armoury"])))
        return 2
    bad = rows_for(st)
    for r in ROWS:
        print("%-16s %-4s worst %d faults, limit 0%s" % (r, "PASS" if not bad[r] else "FAIL", len(bad[r]), "".join("\n    " + b for b in bad[r])))
    blind = []
    if any(rows_for(_whole()).values()):
        blind.append("the made whole state does not pass: %s" % {k: v for k, v in rows_for(_whole()).items() if v})
    for want, fn in PLANTS:
        s = _whole()
        fn(s)
        if not rows_for(s)[want]:
            blind.append("a planted fault did not turn %s red" % want)
    print("planted faults: %d of %d caught%s" % (len(PLANTS) - len([b for b in blind if "planted" in b]), len(PLANTS), "; " + "; ".join(blind) if blind else ""))
    red = [r for r in ROWS if bad[r]]
    print("T_FORGE_GATES_GONE: %s (%d rows, %d not PASS)%s" % ("FAIL" if red or blind else "PASS", len(ROWS), len(red),
                                                               "; the forge is not onboarded yet, so the gates are expected to be there" if bad["forge_onboarded"] else ""))
    return 1 if red or blind else 0


if __name__ == "__main__":
    sys.exit(main())

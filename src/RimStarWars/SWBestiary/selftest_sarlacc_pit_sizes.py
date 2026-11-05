#!/usr/bin/env python3
"""selftest_sarlacc_pit_sizes.py -- SARLACC_PIT_WIDEN_THE_BIG_ONES: the sarlacc pit comes in three sizes.

Owner, 2026-10-16, of the accepted 9x6 pit art: "Superb though that is just a moderate one. They can get much bigger."
RSW_SarlaccPit (9x6) stays the moderate pit; RSW_SarlaccPitGreat and RSW_SarlaccPitColossal reuse its art.
RSW_GenStep_SarlaccPit (RSW_DonorPack_Sarlacc.xml) is RSW_GenStep_SarlaccPitSized (BeastMechanics assembly), which rolls one
size per map. This test checks, offline:
  defs     every size inherits RSW_SarlaccPitBase, grows strictly, draws at least its footprint, keeps its interaction cell
           on the first row south of its footprint, and the moderate one keeps the donor's (9,6) and (0,0,-3)
  genstep  the class, its <sizes> list (smallest first, moderate first, weights positive, clear space wider than the pit)
           and that every XML field name is a real field of the C# class
  setting  bigSarlaccPitsEnabled is declared, saved and drawn
  ring     the warning-totem ring anchors on the moderate pit only and skips a big-pit map quietly (anchorOptional)
  dlls     the two committed DLLs' .srchash stamps match the committed source (dll_source_stamp.recompute_stamp, HEAD)
  fuzz     the C# kernel RSW_SarlaccPitKernel against a brute-force reference (selftest_swbestiary_fuzz.py --fuzz-only sarlacc)
Planted red cases prove the def checks can see a broken size.
    python3 src/RimStarWars/SWBestiary/selftest_sarlacc_pit_sizes.py [--no-fuzz]
"""
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DEFS = os.path.join(HERE, "Defs", "DonorPackPort", "RSW_DonorPack_Sarlacc.xml")
BEAST = os.path.join(HERE, "Source", "BeastMechanics")
GENSTEP_CS = os.path.join(BEAST, "RSW_GenStep_SarlaccPitSized.cs")
SETTINGS_CS = os.path.join(BEAST, "RSW_BeastMechanicsSettings.cs")
CSPROJ = os.path.join(BEAST, "RimMandrakeBeastMechanicsRSW.csproj")
RING_XML = os.path.join(ROOT, "src", "RimStarWars", "StructureInjectionsSW", "Defs", "GenStepDefs_SarlaccRing.xml")
RIMPLACE_CS = os.path.join(ROOT, "src", "RimMandrake", "StructureInjections", "Source", "GenStep_RimplacePlan.cs")
STAMPS = ["src/RimStarWars/SWBestiary/Assemblies/RimMandrakeBeastMechanicsRSW.dll.srchash",
          "src/RimMandrake/StructureInjections/Assemblies/RimMandrakeStructureInjections.dll.srchash"]
SIZES = ["RSW_SarlaccPit", "RSW_SarlaccPitGreat", "RSW_SarlaccPitColossal"]
GENSTEP_CLASS = "RimMandrake.StarWars.SWBestiary.RSW_GenStep_SarlaccPitSized"


def vec(text):
    return tuple(int(round(float(x))) for x in text.strip().strip("()").split(","))


def offset_z(size_z):
    """GenAdj.OccupiedRect on a never-rotated thing: minZ = centre - (z-1)//2; the interaction row is one below."""
    return -((size_z - 1) // 2) - 1


def size_findings(name, size, draw, inter):
    """Findings for one pit size: size (x,z), drawSize (x,z), interactionCellOffset (x,y,z)."""
    out = []
    if draw[0] < size[0] or draw[1] < size[1]:
        out.append("%s drawSize %s is smaller than its footprint %s" % (name, draw, size))
    if inter != (0, 0, offset_z(size[1])):
        out.append("%s interactionCellOffset %s, want (0,0,%d): the first row south of a %d-deep footprint"
                   % (name, inter, offset_z(size[1]), size[1]))
    return out


def main(argv):
    fails, notes = [], []

    # planted red: the def check must see a broken size
    if not size_findings("planted", (9, 6), (10, 10), (0, 0, -4)) or not size_findings("planted", (15, 10), (10, 10), (0, 0, -5)):
        fails.append("planted red: size_findings missed a wrong interaction offset or a draw smaller than the footprint")
    if size_findings("planted", (9, 6), (10, 10), (0, 0, -3)):
        fails.append("planted green: size_findings flagged the donor's own 9x6 pit")

    root = ET.parse(DEFS).getroot()
    things = {t.findtext("defName"): t for t in root.findall("ThingDef") if t.findtext("defName")}
    base = [t for t in root.findall("ThingDef") if t.get("Name") == "RSW_SarlaccPitBase"]
    if len(base) != 1 or base[0].get("Abstract") != "True":
        fails.append("RSW_SarlaccPitBase: want exactly one abstract parent, got %d" % len(base))
    else:
        b = base[0]
        for tag in ("size", "interactionCellOffset", "costList", "killedLeavings"):
            if b.find(tag) is not None:
                fails.append("RSW_SarlaccPitBase sets <%s>: a child would inherit or append to it" % tag)
        if b.findtext("graphicData/texPath") != "Things/Building/Natural/RSW_SarlaccPit":
            fails.append("RSW_SarlaccPitBase texPath changed: every size shares the accepted art")
    dims = {}
    for name in SIZES:
        t = things.get(name)
        if t is None:
            fails.append("%s: no such ThingDef" % name)
            continue
        if t.get("ParentName") != "RSW_SarlaccPitBase":
            fails.append("%s: ParentName %r, want RSW_SarlaccPitBase" % (name, t.get("ParentName")))
        for tag in ("costList", "killedLeavings"):
            e = t.find(tag)
            if e is None or e.get("Inherit") != "False" or e.find("RSW_SarlacciSpore") is None:
                fails.append("%s: <%s Inherit=\"False\"> with RSW_SarlacciSpore expected" % (name, tag))
        try:
            size, draw, inter = vec(t.findtext("size")), vec(t.findtext("graphicData/drawSize")), vec(t.findtext("interactionCellOffset"))
        except (AttributeError, ValueError) as e:
            fails.append("%s: size / drawSize / interactionCellOffset unreadable (%s)" % (name, e))
            continue
        fails += size_findings(name, size, draw, inter)
        dims[name] = size
        notes.append("%s %dx%d draw %s interaction z %d" % (name, size[0], size[1], draw, inter[2]))
    if dims.get("RSW_SarlaccPit") != (9, 6):
        fails.append("RSW_SarlaccPit footprint %s: the moderate pit keeps the donor's (9,6) (the ring is measured on it)"
                     % (dims.get("RSW_SarlaccPit"),))
    areas = [dims[n][0] * dims[n][1] for n in SIZES if n in dims]
    if len(areas) == 3 and not (areas[0] < areas[1] < areas[2] and dims[SIZES[2]][0] >= 2 * dims[SIZES[0]][0]):
        fails.append("sizes do not grow strictly, or the biggest is under twice the moderate width: %s" % dims)
    labels = [things[n].findtext("label") for n in SIZES if n in things]
    if len(set(labels)) != len(labels):
        fails.append("two sizes share a label: %s" % labels)

    # genstep
    gs = [g for g in root.findall("GenStepDef") if g.findtext("defName") == "RSW_GenStep_SarlaccPit"]
    g = gs[0].find("genStep") if len(gs) == 1 else None
    if g is None or g.get("Class") != GENSTEP_CLASS:
        fails.append("RSW_GenStep_SarlaccPit genStep Class %r, want %s" % (g.get("Class") if g is not None else None, GENSTEP_CLASS))
    else:
        if g.findtext("thingDef") != "RSW_SarlaccPit":
            fails.append("the genstep's own thingDef must stay RSW_SarlaccPit (its fallback with an empty <sizes>)")
        lis = g.findall("sizes/li")
        names = [li.findtext("thingDef") for li in lis]
        if names != SIZES:
            fails.append("genstep <sizes> %s, want %s (smallest first)" % (names, SIZES))
        for li in lis:
            n = li.findtext("thingDef")
            try:
                w, clear = float(li.findtext("weight")), int(li.findtext("clearSpaceSize"))
            except (TypeError, ValueError):
                fails.append("%s: weight / clearSpaceSize unreadable" % n)
                continue
            if not w > 0:
                fails.append("%s: weight %s is not positive (it could never be rolled)" % (n, w))
            if n in dims and clear <= max(dims[n]):
                fails.append("%s: clearSpaceSize %d is not wider than its footprint %s" % (n, clear, dims[n]))
            for c in li:
                if c.tag not in ("thingDef", "weight", "clearSpaceSize"):
                    fails.append("%s: <%s> is not a field of RSW_SarlaccPitSize" % (n, c.tag))
    cs = open(GENSTEP_CS, encoding="utf-8").read()
    for pat in (r"namespace RimMandrake\.StarWars\.SWBestiary\b", r"class RSW_GenStep_SarlaccPitSized\s*:\s*GenStep_ScatterThings",
                r"public List<RSW_SarlaccPitSize> sizes", r"public ThingDef thingDef;", r"public float weight\b",
                r"public int clearSpaceSize;", r"RSW_SarlaccPitKernel\.Pick\(", r"RSW_SarlaccPitKernel\.TryOrder\(",
                r"RSW_BeastMechanicsSettings\.bigSarlaccPitsEnabled", r"finally"):
        if not re.search(pat, cs):
            fails.append("RSW_GenStep_SarlaccPitSized.cs lacks /%s/" % pat)
    if '<Compile Include="RSW_GenStep_SarlaccPitSized.cs" />' not in open(CSPROJ, encoding="utf-8").read():
        fails.append("the BeastMechanics csproj does not compile RSW_GenStep_SarlaccPitSized.cs")

    st = open(SETTINGS_CS, encoding="utf-8").read()
    for pat in (r"public static bool bigSarlaccPitsEnabled = true;", r'Scribe_Values\.Look\(ref bigSarlaccPitsEnabled, "bigSarlaccPitsEnabled", true\)',
                r"CheckboxLabeled\([^;]*ref bigSarlaccPitsEnabled"):
        if not re.search(pat, st):
            fails.append("RSW_BeastMechanicsSettings.cs lacks /%s/" % pat)
    if st.find("bigSarlaccPitsEnabled = true;") > st.find("shippedDefaults = SnapshotDefaults()"):
        fails.append("bigSarlaccPitsEnabled is declared after shippedDefaults: its reset button would not know the default")

    # ring
    ring = ET.parse(RING_XML).getroot().find("GenStepDef/genStep")
    if ring is None or ring.findtext("anchorThingDef") != "RSW_SarlaccPit" or ring.findtext("anchorOptional") != "true":
        fails.append("RSW_GenStep_SarlaccRing must anchor on RSW_SarlaccPit with <anchorOptional>true</anchorOptional>")
    rp = open(RIMPLACE_CS, encoding="utf-8").read()
    i_opt, i_warn = rp.find("if (anchorOptional) return;"), rp.find("no '\" + anchorThingDef + \"' found on the map")
    if "public bool anchorOptional;" not in rp or i_opt < 0 or not (0 <= i_opt < i_warn):
        fails.append("GenStep_RimplacePlan.cs: anchorOptional must be a field and return before the missing-anchor warning")

    # committed DLLs match committed source
    sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
    try:
        import dll_source_stamp as dss
        cat = dss.BatchCat(ROOT)
        try:
            for stamp in STAMPS:
                r = dss.recompute_stamp(cat, "HEAD", stamp, ROOT)
                if r.status != "MATCH":
                    fails.append("%s at HEAD: %s %s" % (stamp, r.status, "; ".join(r.detail)))
        finally:
            cat.close()
    except Exception as e:  # an instrument that cannot run is a failure, not a pass
        fails.append("dll_source_stamp could not run: %r" % e)

    if "--no-fuzz" not in argv:
        fz = subprocess.run([sys.executable, os.path.join(ROOT, "src", "RimMandrake", "Utils", "selftest_swbestiary_fuzz.py"),
                             "--fuzz-only", "sarlacc"], capture_output=True, text=True, timeout=520)
        line = next((ln for ln in fz.stdout.splitlines() if ln.startswith("fuzz sarlacc:")), "")
        if fz.returncode != 0 or not re.search(r"fuzz sarlacc: [1-9]\d* cases, .* 0 failures", line):
            # the child's stderr travels too: a WSL-dropped dotnet.exe launch leaves run_selftests' INTEROP_DROP marker
            # ("UtilAcceptVsock") only there, and without it the runner cannot rerun the red (NIGHTLY_COP_FIX_RED_CAHLTS_WGAG)
            err = fz.stderr.strip()[-600:]
            head = (line or fz.stdout[-600:]).strip()
            fails.append("kernel fuzz failed (rc %d): %s" % (fz.returncode, head or err)
                         + ("\n  child stderr: " + err if err and head else ""))
        else:
            notes.append(line)

    for n in notes:
        print("  " + n)
    for f in fails:
        print("FAIL " + f)
    print("selftest_sarlacc_pit_sizes: %s" % ("OK" if not fails else "%d FAILURES" % len(fails)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
